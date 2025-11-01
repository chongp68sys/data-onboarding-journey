from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from ..tools.data_validation import DataValidationTools

class DataValidationAgent:
    """Agent specialized in data quality validation and assessment"""
    
    def __init__(self, model_id: str = "claude-sonnet-4-5-20250929", db_url: str = None):
        self.agent = Agent(
            name="DataQualitySpecialist",
            model=Claude(id=model_id),
            storage=PostgresStorage(table_name="data_validation_sessions", db_url=db_url) if db_url else None,
            tools=[DataValidationTools(working_directory="tmp/validation")],
            description="I am a data quality specialist that performs comprehensive data validation, quality assessment, and anomaly detection.",
            instructions=[
                "You are an expert at assessing and improving data quality.",
                "Perform thorough data quality analysis including completeness, consistency, validity, and accuracy checks.",
                "Detect and analyze duplicates, outliers, and pattern violations.",
                "Provide actionable recommendations for data quality improvement.",
                "Generate comprehensive reports with executive summaries for stakeholders.",
                "Use appropriate statistical methods for outlier detection based on data characteristics.",
                "Be specific about quality issues and suggest concrete remediation steps.",
                "Calculate overall quality scores and explain the methodology.",
                "Prioritize quality issues by business impact and data criticality.",
                "Provide both technical and business-friendly explanations of quality issues."
            ],
            add_history_to_messages=True,
            markdown=True
        )
    
    def run(self, prompt: str) -> str:
        """Execute data validation task"""
        return self.agent.run(prompt)
    
    def analyze_quality(self, csv_file_path: str) -> str:
        """Perform comprehensive data quality analysis"""
        prompt = f"""
        Please perform a comprehensive data quality analysis on: {csv_file_path}
        
        Use analyze_data_quality tool to:
        1. Assess completeness, consistency, and validity
        2. Calculate overall quality scores
        3. Identify critical data issues
        4. Generate actionable recommendations
        5. Provide executive summary for stakeholders
        
        Focus on business impact and prioritize issues by severity.
        """
        
        return self.agent.run(prompt)
    
    def detect_duplicates(self, csv_file_path: str, key_columns: str = None) -> str:
        """Detect and analyze duplicate records"""
        prompt = f"""
        Please detect duplicates in: {csv_file_path}
        Key columns for analysis: {key_columns or "All columns"}
        
        Use detect_duplicates tool to:
        1. Find full row and key column duplicates
        2. Calculate duplicate percentages
        3. Provide examples of duplicate records
        4. Suggest deduplication strategies
        5. Assess impact on data quality
        """
        
        return self.agent.run(prompt)
    
    def validate_patterns(self, csv_file_path: str, pattern_rules: str) -> str:
        """Validate data against specific patterns"""
        prompt = f"""
        Please validate data patterns in: {csv_file_path}
        Pattern rules: {pattern_rules}
        
        Use validate_data_patterns tool to:
        1. Check each column against specified patterns
        2. Calculate match percentages
        3. Provide examples of violations
        4. Suggest data cleaning approaches
        5. Assess pattern compliance trends
        """
        
        return self.agent.run(prompt)
    
    def detect_outliers(self, csv_file_path: str, method: str = "iqr", threshold: float = 1.5) -> str:
        """Detect statistical outliers"""
        prompt = f"""
        Please detect outliers in: {csv_file_path}
        Method: {method}
        Threshold: {threshold}
        
        Use detect_outliers tool to:
        1. Identify statistical outliers in numeric columns
        2. Provide statistical context and explanations
        3. Assess outlier impact on data distribution
        4. Recommend outlier handling strategies
        5. Generate outlier summary statistics
        """
        
        return self.agent.run(prompt)
    
    def generate_comprehensive_report(self, csv_file_path: str) -> str:
        """Generate a complete data quality report"""
        prompt = f"""
        Please generate a comprehensive data quality report for: {csv_file_path}
        
        Use generate_data_report tool to:
        1. Combine all quality analyses into one report
        2. Create executive summary with key findings
        3. Prioritize issues by business impact
        4. Provide detailed technical analysis
        5. Generate actionable improvement roadmap
        
        Structure the report for both technical and business stakeholders.
        """
        
        return self.agent.run(prompt)