"""
Task Execution System for GoalSeek Agent.

This module provides functionality for executing tasks and managing feedback loop
based on the plan created by the Working Backwards Planner.
"""

from typing import Dict, List, Any, Optional
import logging

from openhands.core.message import Message
from openhands.llm.llm import LLM
from openhands.events.action.action import Action
from openhands.events.observation.observation import Observation
from openhands.agenthub.goalseek_agent.prompts import (
    format_feedback_request,
    format_tool_error
)

logger = logging.getLogger(__name__)

class TaskExecutionSystem:
    """
    System for executing tasks and managing feedback loop.
    
    This system executes tasks based on the plan created by the Working Backwards Planner
    and manages the feedback loop for task execution.
    """
    
    def __init__(self):
        """Initialize the TaskExecutionSystem."""
        self.current_task = None
        self.task_results = {}
        self.feedback_history = []
        self.error_history = []
    
    async def execute_task(self, task: Dict[str, Any], llm: LLM, 
                         messages: List[Message]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: The task to execute
            llm: The LLM to use for execution
            messages: The conversation history
            
        Returns:
            Dict containing the execution results
        """
        logger.info(f"Executing task: {task.get('description', 'Unknown task')}")
        
        # Set current task
        self.current_task = task
        
        # Create task execution prompt
        task_prompt = f"# Task Execution\n\n"
        task_prompt += f"## Task Description\n{task.get('description', 'Unknown task')}\n\n"
        task_prompt += f"## Tools Needed\n{', '.join(task.get('tools_needed', []))}\n\n"
        task_prompt += f"## Prerequisites\n{', '.join(task.get('prerequisites', []))}\n\n"
        task_prompt += "Please execute this task using the available tools. Provide a detailed explanation of your approach and results."
        
        # Add task execution prompt to messages
        task_messages = messages.copy()
        task_messages.append(Message.user_message(task_prompt))
        
        # Get task execution from LLM
        task_execution = await llm.ask(messages=task_messages)
        
        # Store task result
        task_result = {
            "task": task,
            "execution": task_execution,
            "status": "completed"
        }
        
        self.task_results[task.get("description", "Unknown task")] = task_result
        
        # Return results
        return {
            "task": task,
            "execution": task_execution,
            "status": "completed"
        }
    
    async def handle_tool_error(self, tool_name: str, operation: str, error: str,
                              llm: LLM, messages: List[Message]) -> Dict[str, Any]:
        """
        Handle a tool execution error.
        
        Args:
            tool_name: The name of the tool that encountered an error
            operation: The operation that was attempted
            error: The error message
            llm: The LLM to use for error handling
            messages: The conversation history
            
        Returns:
            Dict containing the error handling results
        """
        logger.error(f"Tool error: {tool_name} - {error}")
        
        # Create tool error prompt
        error_prompt = format_tool_error(
            tool_name=tool_name,
            operation=operation,
            error=error,
            impact="To be determined",
            recovery_steps="To be determined",
            user_question="How would you like to proceed?"
        )
        
        # Add tool error prompt to messages
        error_messages = messages.copy()
        error_messages.append(Message.user_message(error_prompt))
        
        # Get error handling from LLM
        error_handling = await llm.ask(messages=error_messages)
        
        # Store error
        error_record = {
            "tool_name": tool_name,
            "operation": operation,
            "error": error,
            "handling": error_handling
        }
        
        self.error_history.append(error_record)
        
        # Return results
        return {
            "tool_name": tool_name,
            "operation": operation,
            "error": error,
            "handling": error_handling
        }
    
    async def request_feedback(self, goal: str, plan: str, challenge: str,
                             llm: LLM, messages: List[Message]) -> Dict[str, Any]:
        """
        Request feedback from the user.
        
        Args:
            goal: The goal being pursued
            plan: The current plan
            challenge: The current challenge
            llm: The LLM to use for feedback request
            messages: The conversation history
            
        Returns:
            Dict containing the feedback request results
        """
        logger.info(f"Requesting feedback for challenge: {challenge}")
        
        # Create feedback request prompt
        feedback_prompt = format_feedback_request(
            goal=goal,
            plan=plan,
            challenge=challenge,
            questions="What approach would you recommend for addressing this challenge?",
            options="1. Continue with the current approach\n2. Try an alternative approach\n3. Modify the goal"
        )
        
        # Add feedback request prompt to messages
        feedback_messages = messages.copy()
        feedback_messages.append(Message.user_message(feedback_prompt))
        
        # Get feedback request from LLM
        feedback_request = await llm.ask(messages=feedback_messages)
        
        # Store feedback request
        feedback_record = {
            "goal": goal,
            "plan": plan,
            "challenge": challenge,
            "request": feedback_request
        }
        
        self.feedback_history.append(feedback_record)
        
        # Return results
        return {
            "goal": goal,
            "plan": plan,
            "challenge": challenge,
            "request": feedback_request
        }
    
    def get_task_results(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the task results.
        
        Returns:
            Dict containing the task results
        """
        return self.task_results
    
    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """
        Get the feedback history.
        
        Returns:
            List containing the feedback history
        """
        return self.feedback_history
    
    def get_error_history(self) -> List[Dict[str, Any]]:
        """
        Get the error history.
        
        Returns:
            List containing the error history
        """
        return self.error_history
