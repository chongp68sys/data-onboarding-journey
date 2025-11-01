from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from typing import Dict, Any

class OrchestrationAgent:
    """Master agent that coordinates data processing workflows"""
    
    def __init__(self, model_id: str = "claude-sonnet-4-5-20250929", db_url: str = None):
        self.agent = Agent(
            name="DataPipelineOrchestrator",
            model=Claude(id=model_id),
            storage=PostgresStorage(table_name="orchestration_sessions", db_url=db_url) if db_url else None,
            # Orchestration agent coordinates other agents, no direct tools
            tools=[],
            description="I am a data pipeline orchestrator that coordinates complex data processing workflows by managing and directing specialized agents.",
            instructions=[
                "You are the master coordinator for data processing workflows.",
                "Break down complex data processing requests into sequential steps.",
                "Delegate specific tasks to appropriate specialist agents (FileIngestionSpecialist, DataMappingSpecialist, DataQualitySpecialist).",
                "Maintain context and state across the entire workflow execution.",
                "Provide progress updates and handle error recovery between processing steps.",
                "Generate comprehensive final reports that combine results from all processing steps.",
                "Ensure data flows correctly between different processing phases.",
                "Make intelligent decisions about which agents to use and in what order.",
                "Consider dependencies between workflow steps and optimize execution order.",
                "Provide clear status updates and estimated completion times.",
                "Handle exceptions gracefully and suggest alternative approaches when needed."
            ],
            add_history_to_messages=True,
            markdown=True
        )
        
        # References to other agents (to be injected)
        self.file_ingestion_agent = None
        self.data_mapping_agent = None  
        self.data_validation_agent = None
    
    def set_agents(self, file_ingestion_agent, data_mapping_agent, data_validation_agent):
        """Inject references to specialist agents"""
        self.file_ingestion_agent = file_ingestion_agent
        self.data_mapping_agent = data_mapping_agent
        self.data_validation_agent = data_validation_agent
    
    def run(self, prompt: str) -> str:
        """Execute orchestration task"""
        return self.agent.run(prompt)
    
    def execute_data_pipeline(self, config: Dict[str, Any]) -> str:
        """Execute a complete data processing pipeline"""
        
        file_path = config.get("file_path", "")
        mapping_requirements = config.get("mapping", {})
        validation_requirements = config.get("validation", {})
        
        prompt = f"""
        Execute a comprehensive data processing pipeline with this configuration:
        
        File Path: {file_path}
        Mapping Requirements: {mapping_requirements}
        Validation Requirements: {validation_requirements}
        
        Workflow Steps:
        1. **File Ingestion**: Process and analyze the input file
        2. **Data Mapping**: Apply column mappings and transformations
        3. **Data Validation**: Perform quality checks and validation
        4. **Final Report**: Generate comprehensive results summary
        
        For each step:
        - Provide clear status updates
        - Handle any errors or issues gracefully
        - Pass relevant context to the next step
        - Generate intermediate summaries
        
        Coordinate with specialist agents to complete each phase and provide a final comprehensive report.
        """
        
        return self.agent.run(prompt)
    
    def plan_workflow(self, requirements: str) -> str:
        """Plan and design a data processing workflow"""
        prompt = f"""
        Please analyze these requirements and design an optimal data processing workflow:
        
        Requirements: {requirements}
        
        Provide:
        1. **Workflow Design**: Step-by-step execution plan
        2. **Agent Assignment**: Which specialist agents to use for each step
        3. **Dependencies**: Required inputs/outputs between steps
        4. **Risk Assessment**: Potential issues and mitigation strategies
        5. **Estimated Timeline**: Expected duration for each phase
        6. **Success Criteria**: How to measure successful completion
        
        Design the workflow to be efficient, robust, and scalable.
        """
        
        return self.agent.run(prompt)
    
    def monitor_execution(self, execution_id: str, step: str) -> str:
        """Monitor and report on workflow execution status"""
        prompt = f"""
        Monitor the execution status for:
        
        Execution ID: {execution_id}
        Current Step: {step}
        
        Provide:
        1. **Current Status**: Progress summary and completion percentage
        2. **Next Steps**: Upcoming workflow phases
        3. **Issues Detected**: Any problems or bottlenecks
        4. **Performance Metrics**: Execution time and resource usage
        5. **Recommendations**: Optimization suggestions if applicable
        
        Generate a clear status update for stakeholders.
        """
        
        return self.agent.run(prompt)
    
    def handle_workflow_error(self, error_details: str, workflow_context: str) -> str:
        """Handle errors and provide recovery strategies"""
        prompt = f"""
        An error occurred during workflow execution:
        
        Error Details: {error_details}
        Workflow Context: {workflow_context}
        
        Provide:
        1. **Error Analysis**: Root cause and impact assessment
        2. **Recovery Options**: Available remediation strategies
        3. **Rollback Plan**: How to safely revert if needed
        4. **Prevention**: Steps to avoid similar issues
        5. **Next Actions**: Recommended immediate steps
        
        Focus on minimizing disruption and maintaining data integrity.
        """
        
        return self.agent.run(prompt)