from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uvicorn
import os
from contextlib import asynccontextmanager

from database import get_db, create_tables
from models import Workflow, Execution, DataLineage
from schemas import WorkflowCreate, WorkflowResponse, ExecutionResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="Data Onboarding Journey API",
    description="Agent-powered data pipeline platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Data Onboarding Journey API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Workflow endpoints
@app.get("/api/workflows", response_model=List[WorkflowResponse])
async def list_workflows(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).where(Workflow.is_active == True))
    workflows = result.scalars().all()
    return workflows

@app.post("/api/workflows", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    db_workflow = Workflow(**workflow.dict())
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    return db_workflow

@app.get("/api/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.put("/api/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    db_workflow = result.scalar_one_or_none()
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    for field, value in workflow.dict().items():
        setattr(db_workflow, field, value)
    
    await db.commit()
    await db.refresh(db_workflow)
    return db_workflow

@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.is_active = False
    await db.commit()
    return {"message": "Workflow deleted successfully"}

# Execution endpoints
@app.get("/api/executions", response_model=List[ExecutionResponse])
async def list_executions(workflow_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Execution)
    if workflow_id:
        query = query.where(Execution.workflow_id == workflow_id)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    return executions

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    # TODO: Implement workflow execution with Agno agents
    return {"message": f"Workflow {workflow_id} execution started", "execution_id": "placeholder"}

# File upload endpoint
@app.post("/api/data/upload")
async def upload_file(file: UploadFile = File(...)):
    # TODO: Implement file upload and processing
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "message": "File uploaded successfully"
    }

# Data preview endpoint
@app.post("/api/data/preview")
async def preview_data(file_path: str):
    # TODO: Implement data preview with pandas
    return {
        "columns": ["sample", "columns"],
        "rows": [{"sample": "data", "columns": "here"}],
        "total_rows": 1000,
        "file_path": file_path
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )