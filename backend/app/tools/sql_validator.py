import sqlglot
from sqlglot import exp
from typing import Tuple, List, Optional, Set, Dict

class SQLValidator:
    """
    Strict AST-level SQL security & correctness validator using SQLGlot.
    Enforces:
    1. Read-only permissions (SELECT / WITH only).
    2. Zero DDL/DML mutations (rejection of DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, EXEC).
    3. Verification of referenced tables against active registered tables (accounting for CTE aliases).
    """
    
    ALLOWED_STATEMENT_TYPES = (
        exp.Select,
        exp.Union,
        exp.Intersect,
        exp.Except,
    )
    
    FORBIDDEN_OPERATIONS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
    )
    
    def __init__(self, dialect: str = "duckdb"):
        self.dialect = dialect
        
    def validate(
        self, 
        sql: str, 
        allowed_tables: Optional[List[str]] = None,
        table_schemas: Optional[Dict[str, List[str]]] = None
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Validates the SQL query.
        Returns: (is_valid: bool, error_message: Optional[str], metadata: Optional[dict])
        """
        if not sql or not sql.strip():
            return False, "SQL query cannot be empty.", None
            
        clean_sql = sql.strip()
        
        # Parse expressions
        try:
            parsed_statements = sqlglot.parse(clean_sql, read=self.dialect)
        except Exception as e:
            return False, f"SQL syntax parsing error: {str(e)}", None
            
        if not parsed_statements:
            return False, "Failed to parse any valid SQL statements.", None
            
        if len(parsed_statements) > 1:
            return False, "Multiple SQL statements (semicolon chaining) are forbidden for security.", None
            
        statement = parsed_statements[0]
        
        # Check forbidden mutations
        for forbidden in self.FORBIDDEN_OPERATIONS:
            if statement.find(forbidden):
                return False, f"Dangerous SQL operation detected: {forbidden.__name__.upper()} is strictly forbidden in analytical read-only mode.", None
                
        # Check top-level statement type
        if not isinstance(statement, self.ALLOWED_STATEMENT_TYPES):
            # Check if it is a CTE/WITH statement containing Select
            if isinstance(statement, exp.Select) or (hasattr(statement, 'this') and isinstance(statement.this, exp.Select)):
                pass
            else:
                return False, f"Invalid statement type '{type(statement).__name__}'. Only SELECT queries are permitted.", None

        # Extract CTE aliases so they aren't flagged as missing base tables
        cte_aliases: Set[str] = set()
        for cte in statement.find_all(exp.CTE):
            if cte.alias:
                cte_aliases.add(cte.alias.lower())

        # Extract referenced tables
        referenced_tables: Set[str] = set()
        for table in statement.find_all(exp.Table):
            table_name = table.name.lower()
            if table_name not in cte_aliases:
                referenced_tables.add(table_name)
            
        # Verify base tables exist in schema
        if allowed_tables is not None:
            allowed_set = {t.lower() for t in allowed_tables}
            for ref in referenced_tables:
                if ref not in allowed_set:
                    return False, f"Table '{ref}' does not exist in active dataset schema. Available tables: {list(allowed_tables)}", None

        metadata = {
            "referenced_tables": list(referenced_tables),
            "has_group_by": bool(statement.find(exp.Group)),
            "has_order_by": bool(statement.find(exp.Order)),
            "has_where": bool(statement.find(exp.Where)),
            "has_join": bool(statement.find(exp.Join)),
            "has_limit": bool(statement.find(exp.Limit)),
        }
        
        return True, None, metadata

sql_validator = SQLValidator(dialect="duckdb")
