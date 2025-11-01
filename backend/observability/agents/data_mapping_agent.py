from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from ..tools.data_mapping import DataMappingTools

class DataMappingAgent:
    """Agent specialized in data mapping and transformation operations"""
    
    def __init__(self, model_id: str = "claude-sonnet-4-5-20250929", db_url: str = None):
        self.agent = Agent(
            name="DataMappingSpecialist",
            model=Claude(id=model_id),
            storage=PostgresStorage(table_name="data_mapping_sessions", db_url=db_url) if db_url else None,
            tools=[DataMappingTools(working_directory="tmp/mappings")],
            description="I am a data mapping specialist that handles column mapping, data transformation, and schema standardization tasks.",
            instructions=[
                "You are an expert at mapping data between different schemas and formats.",
                "Use intelligent similarity algorithms to suggest column mappings between source and target schemas.",
                "Always clean and standardize column names following best practices (snake_case by default).",
                "Provide confidence scores for mapping suggestions and explain your reasoning.",
                "Generate reusable transformation code when requested.",
                "Validate mappings before applying them and warn about potential issues.",
                "Be helpful in resolving schema conflicts and data type mismatches.",
                "Consider semantic similarity, not just string matching, when suggesting mappings.",
                "Generate mapping templates for manual completion when needed.",
                "Provide clear documentation for all mapping decisions."
            ],
            add_history_to_messages=True,
            markdown=True
        )
    
    def run(self, prompt: str) -> str:
        """Execute data mapping task"""
        return self.agent.run(prompt)
    
    def suggest_mappings(self, source_columns: str, target_schema: str, similarity_threshold: float = 0.6) -> str:
        """Suggest intelligent column mappings"""
        prompt = f"""
        Please analyze and suggest column mappings between:
        
        Source columns: {source_columns}
        Target schema: {target_schema}
        Similarity threshold: {similarity_threshold}
        
        Use the suggest_column_mapping tool to:
        1. Calculate similarity scores using multiple algorithms
        2. Provide confidence ratings for each suggestion
        3. Identify unmapped columns and explain why
        4. Suggest alternative mappings for low-confidence matches
        5. Provide mapping recommendations and next steps
        """
        
        return self.agent.run(prompt)
    
    def clean_columns(self, column_names: str, convention: str = "snake_case") -> str:
        """Clean and standardize column names"""
        prompt = f"""
        Please clean and standardize these column names: {column_names}
        
        Apply the {convention} naming convention using clean_column_names tool.
        
        Provide:
        1. Cleaned column mapping
        2. Explanation of changes made
        3. Any potential issues identified
        4. Recommendations for further improvements
        """
        
        return self.agent.run(prompt)
    
    def generate_transformation_code(self, transformation_rules: str) -> str:
        """Generate code for data transformations"""
        prompt = f"""
        Generate Python transformation code for these rules: {transformation_rules}
        
        Use apply_data_transformations tool to:
        1. Create executable Python code
        2. Include proper error handling
        3. Add documentation and comments
        4. Provide usage instructions
        5. Include testing recommendations
        """
        
        return self.agent.run(prompt)