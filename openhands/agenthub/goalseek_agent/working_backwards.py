"""
Working Backwards Planner for GoalSeek Agent.

This module provides functionality for implementing the Working Backwards methodology
to solve problems step by step.
"""

from typing import Dict, List, Any, Optional
import logging

from openhands.core.message import Message
from openhands.llm.llm import LLM
from openhands.agenthub.goalseek_agent.prompts import (
    format_working_backwards, 
    format_planning,
    format_execution_status
)

logger = logging.getLogger(__name__)

class WorkingBackwardsPlanner:
    """
    Planner that implements the Working Backwards methodology.
    
    This planner uses step-back questioning to trace backwards from goal to initial state,
    then reorders steps for forward execution.
    """
    
    def __init__(self, max_steps: int = 10):
        """
        Initialize the WorkingBackwardsPlanner.
        
        Args:
            max_steps: Maximum number of steps in the plan
        """
        self.max_steps = max_steps
        self.goal_state = ""
        self.current_state = "Initial state"
        self.current_progress = "No progress yet. Planning phase."
        
        # Working backwards tracking
        self.backwards_steps = []
        self.forward_plan = []
        
        # Execution tracking
        self.plan_ready = False
        self.current_step_index = 0
        self.completed_steps = []
        self.pending_steps = []
    
    async def analyze_backwards(self, goal: str, llm: LLM, 
                              messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze the goal using Working Backwards methodology.
        
        Args:
            goal: The goal to analyze
            llm: The LLM to use for analysis
            messages: The conversation history
            
        Returns:
            Dict containing the analysis results
        """
        logger.info(f"Analyzing goal using Working Backwards: {goal}")
        
        # Set goal state
        self.goal_state = goal
        
        # Create working backwards prompt
        backwards_prompt = format_working_backwards(
            goal_state=self.goal_state,
            current_state=self.current_state,
            current_progress=self.current_progress
        )
        
        # Add working backwards prompt to messages
        backwards_messages = messages.copy()
        backwards_messages.append(Message.user_message(backwards_prompt))
        
        # Get working backwards analysis from LLM
        backwards_analysis = await llm.ask(messages=backwards_messages)
        
        # Parse working backwards analysis
        analysis_result = self._parse_backwards_analysis(backwards_analysis)
        
        # Add steps to backwards steps
        for step in analysis_result.get("steps", []):
            self.add_backward_step(
                description=step.get("description", ""),
                tools_needed=step.get("tools_needed", []),
                prerequisites=step.get("prerequisites", [])
            )
        
        # Return results
        return {
            "backwards_steps": self.backwards_steps,
            "next_action": analysis_result.get("next_action", {}),
            "raw_analysis": backwards_analysis
        }
    
    def add_backward_step(self, description: str, tools_needed: List[str], 
                         prerequisites: List[str]) -> None:
        """
        Add a step to the backwards planning process.
        
        Args:
            description: Description of this step
            tools_needed: Tools required for this step
            prerequisites: What must be true before this step
        """
        self.backwards_steps.append({
            "description": description,
            "tools_needed": tools_needed,
            "prerequisites": prerequisites
        })
    
    async def create_forward_plan(self, llm: LLM, messages: List[Message]) -> Dict[str, Any]:
        """
        Create a forward execution plan from the backwards steps.
        
        Args:
            llm: The LLM to use for planning
            messages: The conversation history
            
        Returns:
            Dict containing the planning results
        """
        logger.info("Creating forward execution plan")
        
        if not self.backwards_steps:
            logger.warning("No backwards steps to create forward plan from")
            return {
                "forward_plan": [],
                "raw_planning": ""
            }
        
        # Create backwards analysis string
        backwards_analysis = "\n".join([
            f"{i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.backwards_steps)
        ])
        
        # Create planning prompt
        planning_prompt = format_planning(
            goal=self.goal_state,
            current_state=self.current_state,
            backwards_analysis=backwards_analysis,
            forward_plan="To be determined",
            tools_required=", ".join([
                tool for step in self.backwards_steps 
                for tool in step.get("tools_needed", [])
            ]),
            success_criteria="To be determined",
            potential_challenges="To be determined",
            monitoring_approach="To be determined"
        )
        
        # Add planning prompt to messages
        planning_messages = messages.copy()
        planning_messages.append(Message.user_message(planning_prompt))
        
        # Get planning from LLM
        planning = await llm.ask(messages=planning_messages)
        
        # Create forward plan by reversing backwards steps
        self.forward_plan = list(reversed(self.backwards_steps))
        
        # Mark the plan as ready
        self.plan_ready = True
        self.pending_steps = self.forward_plan.copy()
        
        # Log the plan creation
        plan_summary = "\n".join([
            f"{i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.forward_plan)
        ])
        logger.info(f"Forward execution plan created with {len(self.forward_plan)} steps:\n{plan_summary}")
        
        # Return results
        return {
            "forward_plan": self.forward_plan,
            "raw_planning": planning
        }
    
    def get_current_step(self) -> Dict[str, Any]:
        """
        Get the current step in the forward plan.
        
        Returns:
            Dict containing the current step
        """
        if not self.plan_ready or not self.forward_plan:
            return {}
        
        if self.current_step_index >= len(self.forward_plan):
            return {}
        
        return self.forward_plan[self.current_step_index]
    
    def mark_step_completed(self, result: str) -> None:
        """
        Mark the current step as completed.
        
        Args:
            result: The result of the step execution
        """
        if not self.plan_ready or not self.forward_plan:
            return
        
        if self.current_step_index >= len(self.forward_plan):
            return
        
        # Mark step as completed
        completed_step = self.forward_plan[self.current_step_index].copy()
        completed_step["result"] = result
        self.completed_steps.append(completed_step)
        
        # Update progress tracking
        self.current_progress = (
            f"Completed {len(self.completed_steps)}/{len(self.forward_plan)} steps. "
            f"Last completed: {completed_step.get('description', 'Step')}"
        )
        
        # Move to next step
        self.current_step_index += 1
        
        # Update pending steps
        self.pending_steps = (
            self.forward_plan[self.current_step_index:] 
            if self.current_step_index < len(self.forward_plan) 
            else []
        )
        
        logger.info(
            f"Completed step {self.current_step_index}/{len(self.forward_plan)}: "
            f"{result[:100]}..."
        )
    
    def get_execution_status(self) -> str:
        """
        Get the current execution status.
        
        Returns:
            Formatted execution status
        """
        if not self.plan_ready:
            return "Plan is still being formulated."
        
        plan_steps = "\n".join([
            f"{i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.forward_plan)
        ])
        
        completed_steps = "\n".join([
            f"✓ {i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.completed_steps)
        ])
        
        pending_steps = "\n".join([
            f"○ {self.current_step_index+i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.pending_steps)
        ])
        
        current_step = (
            f"Currently executing step {self.current_step_index+1}/{len(self.forward_plan)}: "
            f"{self.forward_plan[self.current_step_index].get('description', 'Step')}"
            if self.current_step_index < len(self.forward_plan) 
            else "All steps completed."
        )
        
        return format_execution_status(
            goal=self.goal_state,
            plan_steps=plan_steps,
            current_step=current_step,
            completed_steps=completed_steps if self.completed_steps else "None yet.",
            pending_steps=pending_steps if self.pending_steps else "None remaining.",
            observations=self.current_progress,
            adjustments="None required at this time."
        )
    
    def is_plan_complete(self) -> bool:
        """
        Check if the plan is complete.
        
        Returns:
            True if the plan is complete, False otherwise
        """
        if not self.plan_ready:
            return False
        
        return self.current_step_index >= len(self.forward_plan)
    
    def _parse_backwards_analysis(self, analysis: str) -> Dict[str, Any]:
        """
        Parse the backwards analysis from the LLM.
        
        Args:
            analysis: The backwards analysis from the LLM
            
        Returns:
            Dict containing the parsed analysis
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = analysis.split("\n")
        
        steps = []
        next_action = {}
        
        current_section = None
        current_step = {}
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith("# ") or line.startswith("## "):
                current_section = line.lstrip("# ")
                
                # If we were parsing a step, add it to steps
                if current_step and "description" in current_step:
                    steps.append(current_step)
                    current_step = {}
                
                continue
            
            if current_section == "Working Backwards Analysis" or current_section == "Step-Back Analysis":
                if line.startswith("1.") and "prerequisite" in line:
                    # Start of a new step
                    if current_step and "description" in current_step:
                        steps.append(current_step)
                    
                    current_step = {
                        "description": line.split(".", 1)[1].strip(),
                        "tools_needed": [],
                        "prerequisites": []
                    }
                
                elif line.startswith("2.") and "tools" in line and current_step:
                    # Tools needed for the step
                    tools_str = line.split(":", 1)[-1].strip() if ":" in line else line.split(".", 1)[1].strip()
                    current_step["tools_needed"] = [t.strip() for t in tools_str.split(",")]
                
                elif line.startswith("3.") and "prerequisite" in line and current_step:
                    # Prerequisites for the step
                    prereq_str = line.split(":", 1)[-1].strip() if ":" in line else line.split(".", 1)[1].strip()
                    current_step["prerequisites"] = [p.strip() for p in prereq_str.split(",")]
            
            elif current_section == "Next Action Decision":
                if "tool" in line.lower():
                    next_action["tool"] = line.split(":", 1)[-1].strip() if ":" in line else line
                
                elif "parameter" in line.lower():
                    next_action["parameters"] = line.split(":", 1)[-1].strip() if ":" in line else line
                
                elif "information" in line.lower():
                    next_action["information"] = line.split(":", 1)[-1].strip() if ":" in line else line
                
                elif "advance" in line.lower():
                    next_action["advances"] = line.split(":", 1)[-1].strip() if ":" in line else line
        
        # Add the last step if there is one
        if current_step and "description" in current_step:
            steps.append(current_step)
        
        return {
            "steps": steps,
            "next_action": next_action
        }
