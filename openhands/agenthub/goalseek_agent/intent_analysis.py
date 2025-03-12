"""
Intent Analysis System for GoalSeek Agent.

This module provides functionality for analyzing user input and extracting intent
using the [Input] → [User Intent] → [Intent] structure.
"""

from typing import Dict, List, Any, Optional
import logging

from openhands.core.message import Message
from openhands.llm.llm import LLM
from openhands.agenthub.goalseek_agent.prompts import format_intent_analysis, format_visualization

logger = logging.getLogger(__name__)

class IntentAnalysisSystem:
    """
    System for analyzing user input and extracting intent.
    
    This system uses the [Input] → [User Intent] → [Intent] structure to
    extract and formalize user intent into clear goals.
    """
    
    def __init__(self):
        """Initialize the IntentAnalysisSystem."""
        self.current_intent = None
        self.fixed_goal = None
        self.tasks = []
        self.required_tools = []
        
    async def analyze_intent(self, user_input: str, llm: LLM, 
                           messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze user input and extract intent.
        
        Args:
            user_input: The user input to analyze
            llm: The LLM to use for analysis
            messages: The conversation history
            
        Returns:
            Dict containing the analysis results
        """
        logger.info("Analyzing user intent")
        
        # Create intent analysis prompt
        intent_prompt = format_intent_analysis(
            user_input=user_input,
            fixed_goal="To be determined",
            task_1="To be determined",
            task_2="To be determined",
            task_3="To be determined",
            required_tools="To be determined",
            agent_assignment="GoalSeek Agent",
            feedback_mechanism="Continuous monitoring and adaptation"
        )
        
        # Add intent analysis prompt to messages
        intent_messages = messages.copy()
        intent_messages.append(Message.user_message(intent_prompt))
        
        # Get intent analysis from LLM
        intent_analysis = await llm.ask(messages=intent_messages)
        
        # Parse intent analysis
        analysis_result = self._parse_intent_analysis(intent_analysis)
        
        # Store results
        self.current_intent = analysis_result.get("intent", "")
        self.fixed_goal = analysis_result.get("fixed_goal", "")
        self.tasks = analysis_result.get("tasks", [])
        self.required_tools = analysis_result.get("required_tools", [])
        
        # Format visualization
        visualization = self._format_visualization(analysis_result)
        
        # Return results
        return {
            "intent": self.current_intent,
            "fixed_goal": self.fixed_goal,
            "tasks": self.tasks,
            "required_tools": self.required_tools,
            "visualization": visualization,
            "raw_analysis": intent_analysis
        }
    
    def _parse_intent_analysis(self, analysis: str) -> Dict[str, Any]:
        """
        Parse the intent analysis from the LLM.
        
        Args:
            analysis: The intent analysis from the LLM
            
        Returns:
            Dict containing the parsed analysis
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = analysis.split("\n")
        
        intent = ""
        fixed_goal = ""
        tasks = []
        required_tools = []
        
        for i, line in enumerate(lines):
            if "[Intent]" in line:
                # Extract intent from this line or the next
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith("["):
                    intent = lines[i + 1].strip()
            
            if "[Fixed User want intent]" in line:
                # Extract fixed goal
                fixed_goal = line.split("=")[-1].strip()
            
            if "Task" in line and ":" in line:
                # Extract task
                task = line.split(":", 1)[-1].strip()
                if task and task != "To be determined":
                    tasks.append(task)
            
            if "Required tools:" in line:
                # Extract required tools
                tools_str = line.split(":", 1)[-1].strip()
                required_tools = [t.strip() for t in tools_str.split(",")]
        
        return {
            "intent": intent,
            "fixed_goal": fixed_goal,
            "tasks": tasks,
            "required_tools": required_tools
        }
    
    def _format_visualization(self, analysis_result: Dict[str, Any]) -> str:
        """
        Format the intent analysis visualization.
        
        Args:
            analysis_result: The parsed intent analysis
            
        Returns:
            Formatted visualization
        """
        intent = analysis_result.get("intent", "")
        fixed_goal = analysis_result.get("fixed_goal", "")
        tasks = analysis_result.get("tasks", [])
        
        # Format tasks
        tasks_str = ""
        for i, task in enumerate(tasks):
            tasks_str += f"  Task {i+1}: {task}\n"
        
        # Create visualization content
        content = f"[Input] → [User Intent] → [Intent]({intent})\n\n"
        content += f"[Fixed User want intent] = {fixed_goal}\n\n"
        content += "Achieve Goal == Need Tasks\n"
        content += f"[Goal]=[Tasks](\n{tasks_str})"
        
        # Return formatted visualization
        return format_visualization(content)
    
    def get_fixed_goal(self) -> str:
        """Get the fixed goal."""
        return self.fixed_goal
    
    def get_tasks(self) -> List[str]:
        """Get the tasks."""
        return self.tasks
    
    def get_required_tools(self) -> List[str]:
        """Get the required tools."""
        return self.required_tools
