import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightFlow AI Data Analyst"
    API_V1_STR: str = "/api"
    
    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", "anthropic", "mock"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # Data & Database Settings
    DATA_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/uploads"))
    DUCKDB_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/insightflow.duckdb"))
    
    # Security
    MAX_EXECUTION_TIME_SECONDS: int = 15
    MAX_ROW_LIMIT: int = 10000
    
    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
