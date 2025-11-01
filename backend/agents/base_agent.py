from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AgentTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class AgentResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Base class for all Agno workflow agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools: List[AgentTool] = []
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def get_available_tools(self) -> List[AgentTool]:
        """Return list of available tools for this agent"""
        pass
    
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute a task with given context"""
        pass
    
    def register_tool(self, tool: AgentTool):
        """Register a new tool for this agent"""
        self.tools.append(tool)
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[AgentTool]:
        """Get a specific tool by name"""
        return next((tool for tool in self.tools if tool.name == name), None)
    
    def log_execution(self, task: str, result: AgentResult):
        """Log agent execution"""
        if result.success:
            self.logger.info(f"Task '{task}' completed successfully")
        else:
            self.logger.error(f"Task '{task}' failed: {result.error}")

class AgentOrchestrator:
    """Orchestrates communication between agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("orchestrator")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    async def execute_workflow_step(self, agent_name: str, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute a single workflow step using the specified agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            return AgentResult(
                success=False,
                error=f"Agent '{agent_name}' not found"
            )
        
        try:
            result = await agent.execute(task, context)
            agent.log_execution(task, result)
            return result
        except Exception as e:
            error_result = AgentResult(
                success=False,
                error=f"Agent execution failed: {str(e)}"
            )
            agent.log_execution(task, error_result)
            return error_result