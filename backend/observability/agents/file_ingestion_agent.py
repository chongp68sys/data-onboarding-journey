from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from ..tools.file_ingestion import FileIngestionTools

class FileIngestionAgent:
    """Agent specialized in file ingestion and parsing operations"""
    
    def __init__(self, model_id: str = "claude-sonnet-4-5-20250929", db_url: str = None):
        self.agent = Agent(
            name="FileIngestionSpecialist",
            model=Claude(id=model_id),
            storage=PostgresStorage(table_name="file_ingestion_sessions", db_url=db_url) if db_url else None,
            tools=[FileIngestionTools(working_directory="tmp/uploads")],
            description="I am a file ingestion specialist that can read, parse, and analyze various data file formats including CSV, Excel, JSON, XML, and binary mainframe files.",
            instructions=[
                "You are an expert at processing data files of various formats.",
                "Always start by detecting the actual file type using detect_file_type before processing.",
                "For text files, detect the encoding to ensure proper reading.",
                "Provide detailed analysis including schema inference, data quality insights, and processing recommendations.",
                "Handle errors gracefully and suggest alternative approaches when standard methods fail.",
                "Be thorough in your analysis but concise in your explanations.",
                "Always include metadata about the file processing results.",
                "When processing mainframe files, use EBCDIC conversion tools appropriately.",
                "For XML files, try structured parsing first before falling back to DOM parsing.",
                "Generate actionable recommendations for file processing optimization."
            ],
            add_history_to_messages=True,
            markdown=True
        )
    
    def run(self, prompt: str) -> str:
        """Execute file ingestion task"""
        return self.agent.run(prompt)
    
    def process_file(self, file_path: str, **kwargs) -> str:
        """Process a file and return structured analysis"""
        prompt = f"""
        Please process the file at: {file_path}
        
        Steps to follow:
        1. Detect the actual file type using detect_file_type
        2. Detect encoding if it's a text-based file
        3. Choose and execute the appropriate reading method
        4. Infer the schema and analyze data structure
        5. Provide processing summary with recommendations
        
        Additional parameters: {kwargs}
        
        Return a comprehensive analysis including:
        - File type and characteristics
        - Data dimensions and structure
        - Schema information
        - Data quality observations
        - Processing recommendations
        """
        
        return self.agent.run(prompt)