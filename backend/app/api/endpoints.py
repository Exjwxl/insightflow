import os
import json
import asyncio
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config.settings import settings
from app.tools.database import db_manager
from app.tools.profiler import dataset_profiler
from app.tools.sql_validator import sql_validator
from app.graph.workflow import analyst_app

router = APIRouter()

class AnalyzeRequest(BaseModel):
    question: str
    table_name: Optional[str] = "sales"

class QueryPreviewRequest(BaseModel):
    sql: str

@router.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

@router.get("/datasets")
async def list_datasets():
    tables = db_manager.list_tables()
    datasets = []
    for table in tables:
        info = db_manager.get_table_info(table)
        datasets.append(info)
    return {"datasets": datasets}

@router.get("/datasets/{table_name}/profile")
async def get_dataset_profile(table_name: str):
    tables = db_manager.list_tables()
    if table_name not in tables:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
    profile = dataset_profiler.profile_table(table_name)
    return profile

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
        
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".csv", ".xlsx", ".xls", ".parquet"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, Excel, or Parquet.")
        
    table_name = os.path.splitext(filename)[0].replace(" ", "_").replace("-", "_").lower()
    save_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(save_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    try:
        if ext == ".csv":
            db_manager.register_csv(table_name, save_path)
        elif ext in [".xlsx", ".xls"]:
            db_manager.register_excel(table_name, save_path)
        elif ext == ".parquet":
            db_manager.register_parquet(table_name, save_path)
            
        profile = dataset_profiler.profile_table(table_name)
        return {
            "message": "Dataset uploaded and profiled successfully",
            "table_name": table_name,
            "profile": profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest dataset: {str(e)}")

@router.post("/query/preview")
async def preview_query(req: QueryPreviewRequest):
    allowed_tables = db_manager.list_tables()
    is_valid, error, meta = sql_validator.validate(req.sql, allowed_tables=allowed_tables)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    res = db_manager.execute_query(req.sql, limit=100)
    return res

@router.post("/analyze")
async def analyze_dataset(req: AnalyzeRequest):
    """Synchronous analysis execution."""
    initial_state = {
        "question": req.question,
        "table_name": req.table_name or "sales",
        "logs": [],
        "investigations": []
    }
    
    final_state = analyst_app.invoke(initial_state)
    return {
        "question": req.question,
        "table_name": final_state.get("table_name"),
        "plan": final_state.get("plan"),
        "investigations": final_state.get("investigations"),
        "visualizations": final_state.get("visualizations"),
        "validation_status": final_state.get("validation_status"),
        "report": final_state.get("report"),
        "logs": final_state.get("logs")
    }

@router.get("/analyze/stream")
async def analyze_dataset_stream(question: str = Query(...), table_name: str = Query("sales")):
    """
    Real-time Server-Sent Events (SSE) streaming endpoint delivering live agent thoughts,
    queries, statistical computations, and the finalized report.
    """
    async def event_generator():
        initial_state = {
            "question": question,
            "table_name": table_name,
            "logs": [],
            "investigations": []
        }
        
        yield f"data: {json.dumps({'type': 'start', 'message': f'Starting analysis for question: {question}'})}\n\n"
        await asyncio.sleep(0.1)
        
        try:
            accumulated_state = dict(initial_state)
            accumulated_state["logs"] = []
            accumulated_state["investigations"] = []
            accumulated_state["visualizations"] = []

            # Stream state progression through LangGraph nodes
            for event in analyst_app.stream(initial_state):
                for node_name, node_output in event.items():
                    # Accumulate logs
                    logs = node_output.get("logs", [])
                    if logs:
                        accumulated_state["logs"].extend(logs)
                    for log in logs:
                        yield f"data: {json.dumps({'type': 'log', 'node': node_name, 'message': log})}\n\n"
                        await asyncio.sleep(0.04)
                        
                    if "current_sql" in node_output and node_output.get("current_sql"):
                        accumulated_state["current_sql"] = node_output["current_sql"]
                        yield f"data: {json.dumps({'type': 'sql', 'sql': node_output['current_sql']})}\n\n"
                        
                    if "plan" in node_output and node_output["plan"]:
                        accumulated_state["plan"] = node_output["plan"]

                    if "investigations" in node_output and node_output["investigations"]:
                        accumulated_state["investigations"] = node_output["investigations"]

                    if "visualizations" in node_output and node_output["visualizations"]:
                        accumulated_state["visualizations"] = node_output["visualizations"]
                        yield f"data: {json.dumps({'type': 'charts_ready', 'count': len(node_output['visualizations'])})}\n\n"
                        
                    if "report" in node_output and node_output["report"]:
                        accumulated_state["report"] = node_output["report"]
                        yield f"data: {json.dumps({'type': 'final_report', 'report': node_output['report']})}\n\n"
                        
            yield f"data: {json.dumps({'type': 'complete', 'data': { 'report': accumulated_state.get('report'), 'visualizations': accumulated_state.get('visualizations'), 'investigations': accumulated_state.get('investigations'), 'plan': accumulated_state.get('plan'), 'logs': accumulated_state.get('logs') }})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/sample-questions")
async def get_sample_questions(table_name: str = "sales"):
    return {
        "questions": [
            "Why did revenue decrease in August?",
            "What are the top 5 product categories by revenue and profit margin?",
            "Show monthly revenue and cost trends over the past 12 months.",
            "Which sales representatives generated the highest revenue?",
            "Compare customer segments by total sales and discount rates."
        ]
    }
