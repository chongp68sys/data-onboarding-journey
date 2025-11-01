from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    configuration = Column(JSON)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(50))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    input_metadata = Column(JSON)
    output_metadata = Column(JSON)
    error_log = Column(Text)
    processed_rows = Column(Integer)

class DataLineage(Base):
    __tablename__ = "data_lineage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False)
    source_file = Column(String(500))
    target_table = Column(String(255))
    transformation_steps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)