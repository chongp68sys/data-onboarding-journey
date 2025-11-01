from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class WorkflowBase(BaseModel):
    name: str = Field(..., description="Name of the workflow")
    description: Optional[str] = Field(None, description="Description of the workflow")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Workflow configuration as JSON")

class WorkflowCreate(WorkflowBase):
    created_by: Optional[str] = Field(None, description="User who created the workflow")

class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class ExecutionBase(BaseModel):
    workflow_id: uuid.UUID
    status: Optional[str] = Field(None, description="Execution status")
    input_metadata: Optional[Dict[str, Any]] = Field(None, description="Input metadata as JSON")
    output_metadata: Optional[Dict[str, Any]] = Field(None, description="Output metadata as JSON")
    error_log: Optional[str] = Field(None, description="Error log if execution failed")
    processed_rows: Optional[int] = Field(None, description="Number of rows processed")

class ExecutionCreate(ExecutionBase):
    pass

class ExecutionResponse(ExecutionBase):
    id: uuid.UUID
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DataLineageBase(BaseModel):
    execution_id: uuid.UUID
    source_file: Optional[str] = Field(None, description="Source file path")
    target_table: Optional[str] = Field(None, description="Target table name")
    transformation_steps: Optional[Dict[str, Any]] = Field(None, description="Transformation steps as JSON")

class DataLineageCreate(DataLineageBase):
    pass

class DataLineageResponse(DataLineageBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    filename: str
    content_type: str
    size: int
    file_path: str
    schema_info: Optional[Dict[str, Any]] = None

class DataPreviewResponse(BaseModel):
    columns: list[str]
    rows: list[Dict[str, Any]]
    total_rows: int
    file_path: str
    data_types: Optional[Dict[str, str]] = None