# Data Onboarding Journey - Technical Specification

## Overview

A visual, agent-powered data pipeline platform that enables business users and analysts to create automated data onboarding workflows. The system uses React Flow for visual pipeline building and integrates Agno framework agents to make data transformation accessible through natural language interaction.

## Core Architecture

### Framework Stack
- **Frontend**: React Flow for visual pipeline canvas
- **Backend**: Python with FastAPI for async API performance
- **Agent Framework**: Agno workflows for intelligent task automation
- **Data Processing**: pandas, polars for high-performance data manipulation
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Processing**: Python ecosystem (pandas, openpyxl, pyarrow, etc.)

### Operating Modes

#### Design Mode
- Interactive pipeline builder with drag-and-drop nodes
- Real-time data preview at each transformation step
- Agent-assisted configuration using natural language
- Test execution with sample datasets
- Validation and error highlighting
- Save/load pipeline configurations

#### Runtime Mode
- Automated execution based on file arrival triggers
- Scheduled execution via cron-like scheduling
- Real-time monitoring and status updates
- Error handling with automatic retry logic
- Execution history and audit trail

## Agent Architecture

Each node type is powered by a specialized Agno agent with domain-specific tools:

### FileDetectionAgent
**Purpose**: Monitor data sources and detect file arrivals
**Tools**:
- SFTP directory polling
- Email attachment scanning
- File naming convention matching
- Metadata extraction

### FileIngestionAgent
**Purpose**: Read and parse incoming data files
**Tools**:
- pandas file readers (pd.read_csv, pd.read_excel, pd.read_json, pd.read_fwf)
- pyarrow for Parquet files
- lxml/BeautifulSoup for XML parsing
- struct module for binary mainframe data
- Automatic schema inference with pandas dtypes
- Encoding detection and conversion utilities
- EBCDIC to ASCII conversion for mainframe files

### DataMappingAgent
**Purpose**: Handle column mapping and data transformation
**Tools**:
- pandas DataFrame transformations
- Column renaming and dtype conversions
- Custom pandas/polars operations
- Schema mapping with Pydantic models

### DataValidationAgent
**Purpose**: Ensure data quality and consistency
**Tools**:
- pandas-profiling for data quality assessment
- Built-in pandas validation methods
- Great Expectations integration
- Custom validation with pandas operations
- Data quality scoring algorithms

### DataOutputAgent
**Purpose**: Write processed data to target systems
**Tools**:
- SQLAlchemy for database operations
- pandas.to_sql() for bulk inserts
- httpx for async API calls
- Batch processing with pandas chunks
- Transaction management and rollback

### OrchestrationAgent
**Purpose**: Coordinate workflow execution and monitoring
**Tools**:
- Workflow state management
- Inter-agent communication
- Error escalation
- Logging and metrics collection

## Node Types

### Input Nodes

#### File Upload Node
- Manual file upload interface
- Drag-and-drop file selection
- Format validation and preview
- Metadata display (size, format, column count)

#### SFTP Connector Node
- Connection configuration (host, credentials, path)
- Polling schedule settings
- File naming pattern matching
- Directory monitoring

#### Email Connector Node
- Email account integration
- Attachment filtering rules
- Automatic extraction and processing
- Archive processed emails

### Transformation Nodes

#### Column Rename Node
- Interactive column mapping interface
- Agent-assisted naming suggestions
- Bulk rename operations
- Preview of renamed schema

#### Data Type Conversion Node
- Automatic type inference
- Manual type override options
- Format-specific conversions (dates, numbers)
- Error handling for conversion failures

#### Data Validation Node
- Configurable validation rules
- Quality score calculation
- Error reporting and flagging
- Data cleaning suggestions

#### Custom Transform Node
- Natural language transformation requests
- Agent-generated code snippets
- Preview transformation results
- Reusable transformation library

### Visualization Nodes

#### Chart Preview Node
- Multiple chart types (bar, line, scatter, histogram)
- Interactive axis selection
- Real-time data updates
- Export chart configurations

#### Data Table Preview Node
- Paginated data display
- Column sorting and filtering
- Sample data preview
- Row count and summary statistics

#### Summary Statistics Node
- Automated data profiling
- Distribution analysis
- Missing value reports
- Data quality metrics

### Output Nodes

#### API Writer Node
- REST endpoint configuration
- Authentication handling
- Batch size optimization
- Response validation

#### Postgres Writer Node
- Direct database connection
- Table creation and schema management
- Upsert and merge strategies
- Transaction handling

#### Data Quality Report Node
- Comprehensive quality assessment
- Lineage tracking
- Processing summary
- Error log compilation

## Technical Implementation

### Data Flow Pipeline

1. **Trigger Detection**
   - FileDetectionAgent monitors configured sources
   - File arrival triggers workflow execution
   - Naming convention matching for file identification

2. **Data Ingestion**
   - FileIngestionAgent processes detected files
   - Schema inference and data type detection
   - Initial data quality assessment

3. **Transformation Pipeline**
   - DataMappingAgent applies configured transformations
   - Sequential node execution with data passing
   - Real-time preview updates in design mode

4. **Validation & Quality Control**
   - DataValidationAgent performs quality checks
   - Error flagging and resolution suggestions
   - Data lineage tracking

5. **Output Processing**
   - DataOutputAgent writes to target systems
   - Transaction management and rollback capability
   - Success/failure notification

6. **Monitoring & Logging**
   - OrchestrationAgent coordinates execution
   - Comprehensive audit trail
   - Performance metrics collection

### Database Schema

#### Workflows Table
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    configuration JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

#### Executions Table
```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES workflows(id),
    status VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    input_metadata JSONB,
    output_metadata JSONB,
    error_log TEXT,
    processed_rows INTEGER
);
```

#### Data Lineage Table
```sql
CREATE TABLE data_lineage (
    id UUID PRIMARY KEY,
    execution_id UUID REFERENCES executions(id),
    source_file VARCHAR(500),
    target_table VARCHAR(255),
    transformation_steps JSONB,
    created_at TIMESTAMP
);
```

### API Endpoints (FastAPI)

#### Workflow Management
- `GET /api/workflows` - List all workflows (with Pydantic models)
- `POST /api/workflows` - Create new workflow (validated with Pydantic)
- `PUT /api/workflows/{workflow_id}` - Update workflow
- `DELETE /api/workflows/{workflow_id}` - Delete workflow
- `POST /api/workflows/{workflow_id}/test` - Test workflow execution

#### Execution Management
- `GET /api/executions` - List workflow executions
- `GET /api/executions/{execution_id}` - Get execution details
- `POST /api/workflows/{workflow_id}/execute` - Trigger manual execution
- `WebSocket /ws/workflows/{workflow_id}/status` - Real-time execution status

#### Data Preview
- `POST /api/data/preview` - Preview data transformation (returns pandas info)
- `POST /api/data/validate` - Validate data quality (Great Expectations)
- `GET /api/data/schema/{execution_id}` - Get processed data schema

### File Processing Configuration

#### Supported Formats (Python Ecosystem)
- **CSV**: pandas.read_csv() with configurable parameters
- **Excel**: openpyxl/xlrd for .xlsx/.xls with sheet selection
- **JSON**: pandas.read_json() with nested object normalization
- **Parquet**: pyarrow integration for high-performance processing
- **XML**: lxml/BeautifulSoup for XML parsing with pandas integration
- **Binary/Mainframe**: struct module for fixed-width binary data parsing
- **Fixed-width text**: pandas.read_fwf() for mainframe text exports

#### Schema Inference (pandas-based)
- pandas.infer_objects() for automatic dtype detection
- pd.to_datetime() with format inference for dates
- Null value pattern recognition with pandas.isna()
- Custom inference rules with pandas dtypes

#### Error Handling (Python)
- pandas error handling with on_bad_lines parameter
- Try/except blocks for encoding detection
- Partial DataFrame processing with pandas chunks
- Custom exception classes for pipeline errors

## User Experience Design

### Visual Pipeline Builder
- Intuitive drag-and-drop interface
- Real-time connection validation
- Node configuration panels with agent assistance
- Visual data flow indicators

### Agent Interaction
- Natural language configuration inputs
- Contextual suggestions and help
- Error explanation and resolution guidance
- Learning from user preferences

### Monitoring Dashboard
- Live execution status displays
- Historical performance metrics
- Data quality trends
- Alert and notification system

## Security & Compliance

### Data Protection
- Encryption in transit and at rest
- Secure credential storage
- Access logging and audit trails
- Data retention policies

### Authentication & Authorization
- Role-based access control
- Workflow sharing permissions
- API key management
- Integration with existing identity systems

## Performance Considerations (Python-specific)

### Scalability
- **Async FastAPI** for concurrent request handling
- **pandas chunking** for large file processing
- **polars** for high-performance operations when needed
- **SQLAlchemy connection pooling** for database efficiency
- **Celery** for background task processing

### Monitoring
- **Python logging** with structured logs
- **pandas memory profiling** for large datasets
- **asyncio performance monitoring**
- **Prometheus metrics** for API performance

## Future Enhancements (Second Priority)

### Advanced Collaboration
- Multi-user workflow editing
- Approval workflows for production deployments
- Comment and annotation system
- Version control for pipeline configurations

### Extended Analytics
- Advanced data quality scoring
- Comprehensive lineage visualization
- Data catalog integration
- Impact analysis for schema changes

### Additional Connectors
- Database direct connections (MySQL, MongoDB, etc.)
- Cloud storage integration (S3, Azure Blob)
- Streaming data sources (Kafka, Kinesis)
- SaaS application APIs

## Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-4)
- React Flow canvas setup
- Basic Agno agent integration
- File upload and preview functionality
- PostgreSQL schema and basic API

### Phase 2: Essential Pipeline Nodes (Weeks 5-8)
- Input nodes (Upload, SFTP)
- Transformation nodes (Rename, Validation)
- Output nodes (API, Postgres)
- Design mode testing capability

### Phase 3: Agent Intelligence (Weeks 9-12)
- Natural language configuration
- Schema inference and mapping
- Intelligent error handling
- Agent-assisted transformations

### Phase 4: Runtime System (Weeks 13-16)
- File arrival triggers
- Automated execution engine
- Monitoring and logging
- Basic data lineage tracking

This specification provides a comprehensive foundation for building an intelligent, agent-powered data onboarding platform that balances accessibility for business users with the sophistication required by data analysts.