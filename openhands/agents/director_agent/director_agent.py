"""
Director Agent implementation.

This module implements the Director Agent that orchestrates workflows
based on user requests.
"""

from typing import Dict, List, Optional, Any, Literal, Union
import asyncio
import json

from agents import Agent, Runner, function_tool, trace, custom_span
from agents.tracing import Span

from ..prompts.director_prompts import (
    DIRECTOR_AGENT_INSTRUCTIONS,
    RESULT_EVALUATION_TEMPLATE,
    FINAL_RESPONSE_TEMPLATE,
    ERROR_HANDLING_TEMPLATE,
    WORKFLOW_SELECTION_TEMPLATE,
)


class WorkflowResult:
    """
    Represents the result of a workflow execution.
    """
    
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.data = data or {}
        self.message = message
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow result to a dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowResult":
        """Create a WorkflowResult from a dictionary."""
        return cls(
            success=data.get("success", False),
            data=data.get("data", {}),
            message=data.get("message"),
            error=data.get("error"),
        )
    
    def __str__(self) -> str:
        """String representation of the workflow result."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class DirectorAgent:
    """
    Director Agent that orchestrates workflows based on user requests.
    
    The Director Agent analyzes user requests, determines the appropriate
    workflow to call, executes the workflow, evaluates results, and provides
    a final response to the user.
    """
    
    def __init__(
        self,
        name: str = "DirectorAgent",
        description: str = "A director agent that orchestrates workflows",
        workflow_tools: Optional[List[Any]] = None,
        specialized_agents: Optional[List[Agent]] = None,
    ):
        """
        Initialize the Director Agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent
            workflow_tools: List of workflow tools available to the agent
            specialized_agents: List of specialized agents for handoffs
        """
        self.name = name
        self.description = description
        self.workflow_tools = workflow_tools or []
        self.specialized_agents = specialized_agents or []
        
        # Create the OpenAI Agent
        self.agent = Agent(
            name=name,
            instructions=DIRECTOR_AGENT_INSTRUCTIONS,
            tools=self.workflow_tools,
            handoffs=self.specialized_agents,
        )
    
    async def process_request(
        self,
        user_request: str,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Process a user request through the Director Agent workflow.
        
        Args:
            user_request: The user's request
            trace_id: Optional trace ID for tracking
            context: Optional context information
            
        Returns:
            The final response to the user
        """
        context = context or {}
        
        # Create a trace for the entire process
        with trace("Director Agent Workflow", trace_id=trace_id):
            with custom_span("Request Analysis"):
                # Step B: LLM analyzes and classifies the request
                result = await Runner.run(
                    self.agent,
                    input=user_request,
                )
                
                # Steps C-E: Agent determines which API to call and calls it
                # (This happens automatically through the OpenAI function calling)
                
                # Steps G-H: Get API results
                # (Results are returned from the function tool)
                
            with custom_span("Result Evaluation"):
                # Steps I-J: LLM re-evaluates results and determines if additional processing is needed
                if self._needs_additional_processing(result, user_request):
                    # Call another workflow or process further
                    additional_input = self._create_additional_input(result, user_request)
                    result = await Runner.run(
                        self.agent,
                        input=additional_input,
                    )
            
            # Steps K-L: LLM creates final answer and returns to user
            return str(result.final_output)
    
    def _needs_additional_processing(self, result, user_request: str) -> bool:
        """
        Determine if additional processing is needed based on the result.
        
        Args:
            result: The result from the agent
            user_request: The original user request
            
        Returns:
            True if additional processing is needed, False otherwise
        """
        # This is a simplified implementation
        # In a real implementation, you would analyze the result more thoroughly
        
        # Check if the result contains a specific indicator for additional processing
        if hasattr(result, "final_output") and isinstance(result.final_output, dict):
            return result.final_output.get("needs_additional_processing", False)
        
        return False
    
    def _create_additional_input(self, result, user_request: str) -> str:
        """
        Create input for additional processing.
        
        Args:
            result: The result from the agent
            user_request: The original user request
            
        Returns:
            Input for additional processing
        """
        # This is a simplified implementation
        # In a real implementation, you would create a more sophisticated input
        
        return (
            f"Original request: {user_request}\n\n"
            f"Previous result: {result.final_output}\n\n"
            "Please continue processing this request with additional information or workflows."
        )
    
    async def run_streamed(
        self,
        user_request: str,
        trace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Process a user request with streaming output.
        
        Args:
            user_request: The user's request
            trace_id: Optional trace ID for tracking
            context: Optional context information
            
        Returns:
            A streaming result
        """
        context = context or {}
        
        # Create a trace for the entire process
        with trace("Director Agent Workflow (Streamed)", trace_id=trace_id):
            # Run the agent with streaming
            return Runner.run_streamed(
                self.agent,
                input=user_request,
            )


def create_director_agent(
    workflow_tools: List[Any],
    specialized_agents: Optional[List[Agent]] = None,
    name: str = "DirectorAgent",
    description: str = "A director agent that orchestrates workflows",
) -> DirectorAgent:
    """
    Create a Director Agent with the specified tools and agents.
    
    Args:
        workflow_tools: List of workflow tools available to the agent
        specialized_agents: List of specialized agents for handoffs
        name: Name of the agent
        description: Description of the agent
        
    Returns:
        A configured Director Agent
    """
    return DirectorAgent(
        name=name,
        description=description,
        workflow_tools=workflow_tools,
        specialized_agents=specialized_agents or [],
    )
