from agno.app.fastapi import FastAPIApp
from .agents import (
    FileIngestionAgent,
    DataMappingAgent,
    DataValidationAgent, 
    OrchestrationAgent
)
from .workflows.data_pipeline_workflow import create_data_pipeline_workflow
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../config/.env")

def setup_data_onboarding_platform():
    """Setup and configure the complete data onboarding platform with Agno control-plane"""
    
    # Ensure tmp directories exist
    os.makedirs("tmp/uploads", exist_ok=True)
    os.makedirs("tmp/mappings", exist_ok=True) 
    os.makedirs("tmp/validation", exist_ok=True)
    
    # Create individual agents
    file_agent = FileIngestionAgent()
    mapping_agent = DataMappingAgent()
    validation_agent = DataValidationAgent()
    orchestrator = OrchestrationAgent()
    
    # Set up agent coordination
    orchestrator.set_agents(file_agent, mapping_agent, validation_agent)
    
    agents = {
        "file_ingestion": file_agent.agent,
        "data_mapping": mapping_agent.agent,
        "data_validation": validation_agent.agent,
        "orchestration": orchestrator.agent
    }
    
    # Create workflow
    workflow = create_data_pipeline_workflow()
    
    # Create FastAPI app with agents and workflows
    agent_os = FastAPIApp(
        agents=list(agents.values()),
        workflows=[workflow],
        name="DataOnboardingControlPlane",
        description="AI-powered data onboarding platform with intelligent workflow orchestration"
    )
    
    return agent_os, agents, workflow

def get_control_plane_app():
    """Get the FastAPI app for the data onboarding control-plane"""
    agent_os, agents, workflow = setup_data_onboarding_platform()
    return agent_os  # Return the FastAPIApp instance directly

# For running the control-plane server
if __name__ == "__main__":
    agent_os, agents, workflow = setup_data_onboarding_platform()
    
    print("🚀 Starting Data Onboarding Control-Plane...")
    print(f"📊 Agents available: {list(agents.keys())}")
    print(f"🔄 Workflows available: [DataPipelineWorkflow]")
    print("🎛️  Control-plane features:")
    print("   • Multi-agent coordination")
    print("   • Structured workflow execution") 
    print("   • Real-time monitoring")
    print("   • Error handling & recovery")
    
    # Start the control-plane server
    agent_os.serve(
        host="0.0.0.0",
        port=8001,
        reload=True
    )