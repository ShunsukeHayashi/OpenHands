"""
GoalSeek Agent implementation for OpenHands.

This agent implements the Working Backwards methodology to solve problems step by step.
It starts with the end goal and works backward to the initial state, then reorders
steps for forward execution.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json
import logging
from pathlib import Path

from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config.agent_config import AgentConfig
from openhands.core.message import Message
from openhands.events.action.action import Action
from openhands.events.action import (
    AgentFinishAction,
    CmdRunAction,
    MessageAction,
)
from openhands.events.observation.observation import Observation
from openhands.events.observation import CmdOutputObservation
from openhands.llm.llm import LLM

# Import GoalSeek Agent components
from openhands.agenthub.goalseek_agent.prompts import (
    SYSTEM_PROMPT,
    format_intent_analysis,
    format_working_backwards,
    format_planning,
    format_execution_status,
    format_feedback_request,
    format_tool_error,
    format_visualization,
)
from openhands.agenthub.goalseek_agent.tools import get_tools

logger = logging.getLogger(__name__)

class GoalSeekAgent(Agent):
    """
    GoalSeek Agent: Working Backwards Methodology Agent
    
    This agent implements the Working Backwards methodology to solve problems step by step.
    It starts with the end goal and works backward to the initial state, then reorders
    steps for forward execution.
    """
    
    sandbox_plugins = get_tools(enable_browsing=True, enable_jupyter=True)
    
    def __init__(self, llm: LLM, config: AgentConfig):
        """
        Initialize the GoalSeek Agent.
        
        Args:
            llm: The LLM to use
            config: The agent configuration
        """
        super().__init__(llm, config)
        
        # Initialize state
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
        
        # Agent state
        self.is_analyzing_intent = False
        self.is_planning = False
        self.is_executing = False
        self.current_task = None
        
        # Messages
        self.messages = [Message.system_message(SYSTEM_PROMPT)]
        
        # Max steps
        self.max_steps = getattr(config, "goalseek_max_plan_steps", 10)
        
        logger.info("GoalSeek Agent initialized")
    
    def step(self, state: State) -> Action:
        """
        Perform a step in the agent's execution.
        
        Args:
            state: The current state
            
        Returns:
            The next action to take
        """
        # Get the latest observation from the state history
        observations = state.history if hasattr(state, 'history') else []
        observation = observations[-1] if observations else None
        
        # If there's no observation, this is the first step
        if observation is None:
            # Start by greeting the user
            return MessageAction(
                content="Hello! I'm the GoalSeek Agent. I use the Working Backwards methodology to solve problems. "
                "Please tell me what you'd like to achieve, and I'll help you break it down into actionable steps."
            )
        
        # Process the observation
        if hasattr(observation, 'content'):
            # User message - analyze intent and start planning
            return self._handle_user_message(observation, state)
        elif isinstance(observation, CmdOutputObservation):
            # Command output - process and continue execution
            return self._handle_cmd_output(observation, state)
        else:
            # Unknown observation type
            return self._handle_unknown_observation(observation, state)
    
    def _handle_user_message(self, observation: Observation, state: State) -> Action:
        """
        Handle a user message.
        
        Args:
            observation: The user message observation
            state: The current state
            
        Returns:
            The next action to take
        """
        # Add user message to messages
        content = observation.content if hasattr(observation, 'content') else str(observation)
        user_message = Message.user_message(content)
        self.messages.append(user_message)
        
        # If we don't have a goal yet, analyze intent
        if not self.goal_state:
            return self._analyze_intent(content)
        else:
            # We already have a goal, treat this as feedback
            return self._process_feedback(content)
    
    def _analyze_intent(self, user_input: str) -> Action:
        """
        Analyze user intent and set goal.
        
        Args:
            user_input: The user input
            
        Returns:
            The next action to take
        """
        logger.info("Analyzing user intent")
        
        # Set state
        self.is_analyzing_intent = True
        
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
        intent_messages = self.messages.copy()
        intent_messages.append(Message.user_message(intent_prompt))
        
        # Get intent analysis from LLM
        response = self.llm.completion(
            messages=self.llm.format_messages_for_llm(intent_messages),
            temperature=0.7,
        )
        
        # Parse intent analysis
        intent_analysis = response.choices[0].message.content
        
        # Extract goal from intent analysis
        self.goal_state = self._extract_goal_from_analysis(intent_analysis)
        
        # Set current state
        self.current_state = "Initial state after intent analysis"
        
        # Add intent analysis to messages
        self.messages.append(Message.assistant_message(intent_analysis))
        
        # Format visualization
        visualization = self._format_intent_visualization(intent_analysis)
        
        # Start planning
        self.is_analyzing_intent = False
        self.is_planning = True
        
        # Return intent analysis
        return MessageAction(
            content=f"I've analyzed your request and identified the following goal:\n\n"
                   f"**Goal:** {self.goal_state}\n\n"
                   f"{visualization}\n\n"
                   f"Now I'll work backwards from this goal to create a plan. Let me think about what steps are needed..."
        )
    
    def _extract_goal_from_analysis(self, analysis: str) -> str:
        """
        Extract goal from intent analysis.
        
        Args:
            analysis: The intent analysis
            
        Returns:
            The extracted goal
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = analysis.split("\n")
        
        for line in lines:
            if "[Fixed User want intent]" in line:
                # Extract fixed goal
                return line.split("=")[-1].strip()
        
        # If we can't find a goal, use a default
        return "Achieve the user's request"
    
    def _format_intent_visualization(self, analysis: str) -> str:
        """
        Format intent visualization.
        
        Args:
            analysis: The intent analysis
            
        Returns:
            Formatted visualization
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = analysis.split("\n")
        
        intent_line = ""
        fixed_goal = ""
        tasks = []
        
        for i, line in enumerate(lines):
            if "[Input]" in line and "[User Intent]" in line and "[Intent]" in line:
                intent_line = line
            
            if "[Fixed User want intent]" in line:
                fixed_goal = line
            
            if "Task" in line and ":" in line:
                tasks.append(line)
        
        # Create visualization content
        content = f"{intent_line}\n\n"
        content += f"{fixed_goal}\n\n"
        content += "Achieve Goal == Need Tasks\n"
        content += f"[Goal]=[Tasks](\n  " + "\n  ".join(tasks) + "\n)"
        
        # Return formatted visualization
        return format_visualization(content)
    
    def _process_feedback(self, feedback: str) -> Action:
        """
        Process user feedback.
        
        Args:
            feedback: The user feedback
            
        Returns:
            The next action to take
        """
        logger.info("Processing user feedback")
        
        # Add feedback to messages
        self.messages.append(Message.user_message(feedback))
        
        # If we're planning, continue planning
        if self.is_planning:
            return self._continue_planning()
        
        # If we're executing, continue execution
        if self.is_executing:
            return self._continue_execution()
        
        # If we're done, start a new goal
        if self._complete:
            # Reset state
            self.goal_state = ""
            self.current_state = "Initial state"
            self.current_progress = "No progress yet. Planning phase."
            self.backwards_steps = []
            self.forward_plan = []
            self.plan_ready = False
            self.current_step_index = 0
            self.completed_steps = []
            self.pending_steps = []
            self.is_analyzing_intent = False
            self.is_planning = False
            self.is_executing = False
            self.current_task = None
            self._complete = False
            
            # Analyze new intent
            return self._analyze_intent(feedback)
        
        # Default: continue with current state
        return MessageAction(
            content="I'm not sure how to proceed. Could you please provide more guidance?"
        )
    
    def _continue_planning(self) -> Action:
        """
        Continue planning.
        
        Returns:
            The next action to take
        """
        logger.info("Continuing planning")
        
        # If we don't have backwards steps yet, start working backwards
        if not self.backwards_steps:
            return self._start_working_backwards()
        
        # If we have backwards steps but no forward plan, create forward plan
        if self.backwards_steps and not self.plan_ready:
            return self._create_forward_plan()
        
        # If we have a forward plan, start execution
        if self.plan_ready:
            return self._start_execution()
        
        # Default: continue working backwards
        return self._continue_working_backwards()
    
    def _start_working_backwards(self) -> Action:
        """
        Start working backwards from the goal.
        
        Returns:
            The next action to take
        """
        logger.info("Starting working backwards")
        
        # Create working backwards prompt
        backwards_prompt = format_working_backwards(
            goal_state=self.goal_state,
            current_state=self.current_state,
            current_progress=self.current_progress
        )
        
        # Add working backwards prompt to messages
        backwards_messages = self.messages.copy()
        backwards_messages.append(Message.user_message(backwards_prompt))
        
        # Get working backwards analysis from LLM
        response = self.llm.completion(
            messages=self.llm.format_messages_for_llm(backwards_messages),
            temperature=0.7,
        )
        
        # Parse working backwards analysis
        backwards_analysis = response.choices[0].message.content
        
        # Add backwards analysis to messages
        self.messages.append(Message.assistant_message(backwards_analysis))
        
        # Parse backwards analysis to extract steps
        steps = self._parse_backwards_analysis(backwards_analysis)
        
        # Add steps to backwards steps
        for step in steps:
            self.backwards_steps.append(step)
        
        # Return backwards analysis
        return MessageAction(
            content=f"I've started working backwards from the goal. Here's my analysis:\n\n"
                   f"{backwards_analysis}\n\n"
                   f"I'll continue working backwards to create a complete plan."
        )
    
    def _continue_working_backwards(self) -> Action:
        """
        Continue working backwards.
        
        Returns:
            The next action to take
        """
        logger.info("Continuing working backwards")
        
        # Create working backwards prompt
        backwards_prompt = format_working_backwards(
            goal_state=self.goal_state,
            current_state=self.current_state,
            current_progress=f"Working backwards: {len(self.backwards_steps)} steps identified so far."
        )
        
        # Add working backwards prompt to messages
        backwards_messages = self.messages.copy()
        backwards_messages.append(Message.user_message(backwards_prompt))
        
        # Get working backwards analysis from LLM
        response = self.llm.completion(
            messages=self.llm.format_messages_for_llm(backwards_messages),
            temperature=0.7,
        )
        
        # Parse working backwards analysis
        backwards_analysis = response.choices[0].message.content
        
        # Add backwards analysis to messages
        self.messages.append(Message.assistant_message(backwards_analysis))
        
        # Parse backwards analysis to extract steps
        steps = self._parse_backwards_analysis(backwards_analysis)
        
        # Add steps to backwards steps
        for step in steps:
            self.backwards_steps.append(step)
        
        # If we have enough steps or have reached initial state, create forward plan
        if len(self.backwards_steps) >= self.max_steps or self._has_reached_initial_state():
            return self._create_forward_plan()
        
        # Return backwards analysis
        return MessageAction(
            content=f"I'm continuing to work backwards. Here's my latest analysis:\n\n"
                   f"{backwards_analysis}\n\n"
                   f"I've identified {len(self.backwards_steps)} steps so far. I'll continue working backwards."
        )
    
    def _has_reached_initial_state(self) -> bool:
        """
        Check if we've reached the initial state.
        
        Returns:
            True if we've reached the initial state, False otherwise
        """
        # Simple check for now - in a real implementation, this would be more robust
        if not self.backwards_steps:
            return False
        
        last_step = self.backwards_steps[-1]
        
        # Check if the last step's prerequisites can be satisfied from the initial state
        prerequisites = last_step.get("prerequisites", [])
        
        for prereq in prerequisites:
            if "initial state" in prereq.lower() or "current state" in prereq.lower():
                return True
        
        return False
    
    def _create_forward_plan(self) -> Action:
        """
        Create a forward execution plan.
        
        Returns:
            The next action to take
        """
        logger.info("Creating forward execution plan")
        
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
        planning_messages = self.messages.copy()
        planning_messages.append(Message.user_message(planning_prompt))
        
        # Get planning from LLM
        response = self.llm.completion(
            messages=self.llm.format_messages_for_llm(planning_messages),
            temperature=0.7,
        )
        
        # Parse planning
        planning = response.choices[0].message.content
        
        # Add planning to messages
        self.messages.append(Message.assistant_message(planning))
        
        # Create forward plan by reversing backwards steps
        self.forward_plan = list(reversed(self.backwards_steps))
        
        # Mark the plan as ready
        self.plan_ready = True
        self.pending_steps = self.forward_plan.copy()
        
        # Create plan summary
        plan_summary = "\n".join([
            f"{i+1}. {step.get('description', 'Step')}" 
            for i, step in enumerate(self.forward_plan)
        ])
        
        # Return planning
        return MessageAction(
            content=f"I've created a forward execution plan with {len(self.forward_plan)} steps:\n\n"
                   f"{plan_summary}\n\n"
                   f"I'll now start executing this plan step by step."
        )
    
    def _start_execution(self) -> Action:
        """
        Start executing the plan.
        
        Returns:
            The next action to take
        """
        logger.info("Starting execution")
        
        # Set state
        self.is_planning = False
        self.is_executing = True
        
        # Get the first step
        if not self.forward_plan:
            # No steps to execute
            self._complete = True
            return AgentFinishAction(
                final_thought="I've completed the analysis, but there are no steps to execute. "
                "The goal may already be achieved or may not require any actions."
            )
        
        # Get the first step
        current_step = self.forward_plan[0]
        self.current_task = current_step
        
        # Return the first step
        return self._execute_step(current_step)
    
    def _continue_execution(self) -> Action:
        """
        Continue executing the plan.
        
        Returns:
            The next action to take
        """
        logger.info("Continuing execution")
        
        # If we've completed all steps, finish
        if self.current_step_index >= len(self.forward_plan):
            self._complete = True
            return AgentFinishAction(
                final_thought=f"I've completed all {len(self.forward_plan)} steps of the plan. "
                f"The goal '{self.goal_state}' has been achieved."
            )
        
        # Get the current step
        current_step = self.forward_plan[self.current_step_index]
        self.current_task = current_step
        
        # Return the current step
        return self._execute_step(current_step)
    
    def _execute_step(self, step: Dict[str, Any]) -> Action:
        """
        Execute a step.
        
        Args:
            step: The step to execute
            
        Returns:
            The next action to take
        """
        logger.info(f"Executing step: {step.get('description', 'Unknown step')}")
        
        # Create step execution prompt
        step_prompt = f"# Step Execution\n\n"
        step_prompt += f"## Step Description\n{step.get('description', 'Unknown step')}\n\n"
        step_prompt += f"## Tools Needed\n{', '.join(step.get('tools_needed', []))}\n\n"
        step_prompt += f"## Prerequisites\n{', '.join(step.get('prerequisites', []))}\n\n"
        step_prompt += "Please execute this step using the available tools. Provide a detailed explanation of your approach and results."
        
        # Add step execution prompt to messages
        step_messages = self.messages.copy()
        step_messages.append(Message.user_message(step_prompt))
        
        # Get step execution from LLM
        response = self.llm.completion(
            messages=self.llm.format_messages_for_llm(step_messages),
            temperature=0.7,
        )
        
        # Parse step execution
        step_execution = response.choices[0].message.content
        
        # Add step execution to messages
        self.messages.append(Message.assistant_message(step_execution))
        
        # Extract command if present
        command = self._extract_command_from_execution(step_execution)
        
        if command:
            # Execute command
            return CmdRunAction(command=command)
        else:
            # No command to execute, mark step as completed
            self._mark_step_completed(step_execution)
            
            # Continue execution
            return self._continue_execution()
    
    def _extract_command_from_execution(self, execution: str) -> str:
        """
        Extract command from step execution.
        
        Args:
            execution: The step execution
            
        Returns:
            The extracted command
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = execution.split("\n")
        
        for i, line in enumerate(lines):
            if "```bash" in line or "```shell" in line:
                # Extract command from code block
                command_lines = []
                j = i + 1
                while j < len(lines) and "```" not in lines[j]:
                    command_lines.append(lines[j])
                    j += 1
                
                return "\n".join(command_lines)
        
        return ""
    
    def _mark_step_completed(self, result: str) -> None:
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
    
    def _handle_cmd_output(self, observation: CmdOutputObservation, state: State) -> Action:
        """
        Handle command output.
        
        Args:
            observation: The command output observation
            state: The current state
            
        Returns:
            The next action to take
        """
        logger.info("Handling command output")
        
        # Get command output
        cmd_output = observation.command if hasattr(observation, 'command') else str(observation)
        
        # Add command output to messages
        self.messages.append(Message.user_message(f"Command output:\n```\n{cmd_output}\n```"))
        
        # Mark current step as completed
        self._mark_step_completed(f"Command executed. Output: {cmd_output[:100]}...")
        
        # Get execution status
        status = self._get_execution_status()
        
        # Continue execution
        return MessageAction(
            content=f"I've executed the command and received the output. Here's our current status:\n\n"
                   f"{status}\n\n"
                   f"I'll now continue with the next step."
        )
    
    def _handle_unknown_observation(self, observation: Observation, state: State) -> Action:
        """
        Handle unknown observation.
        
        Args:
            observation: The unknown observation
            state: The current state
            
        Returns:
            The next action to take
        """
        logger.info(f"Handling unknown observation: {type(observation).__name__}")
        
        # Add unknown observation to messages
        self.messages.append(Message.user_message(f"Received observation of type {type(observation).__name__}"))
        
        # Continue with current state
        if self.is_planning:
            return self._continue_planning()
        
        if self.is_executing:
            return self._continue_execution()
        
        # Default: ask for guidance
        return MessageAction(
            content="I received an observation I don't know how to handle. Could you please provide more guidance?"
        )
    
    def _get_execution_status(self) -> str:
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
    
    def _parse_backwards_analysis(self, analysis: str) -> List[Dict[str, Any]]:
        """
        Parse backwards analysis to extract steps.
        
        Args:
            analysis: The backwards analysis
            
        Returns:
            List of steps
        """
        # Simple parsing for now - in a real implementation, this would be more robust
        lines = analysis.split("\n")
        
        steps = []
        current_step = {}
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith("1.") and "prerequisite" in line.lower():
                # Start of a new step
                if current_step and "description" in current_step:
                    steps.append(current_step)
                
                current_step = {
                    "description": line.split(".", 1)[1].strip(),
                    "tools_needed": [],
                    "prerequisites": []
                }
            
            elif line.startswith("2.") and "tool" in line.lower() and current_step:
                # Tools needed for the step
                tools_str = line.split(":", 1)[-1].strip() if ":" in line else line.split(".", 1)[1].strip()
                current_step["tools_needed"] = [t.strip() for t in tools_str.split(",")]
            
            elif line.startswith("3.") and "prerequisite" in line.lower() and current_step:
                # Prerequisites for the step
                prereq_str = line.split(":", 1)[-1].strip() if ":" in line else line.split(".", 1)[1].strip()
                current_step["prerequisites"] = [p.strip() for p in prereq_str.split(",")]
        
        # Add the last step if there is one
        if current_step and "description" in current_step:
            steps.append(current_step)
        
        return steps
