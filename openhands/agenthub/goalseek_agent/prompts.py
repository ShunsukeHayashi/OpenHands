"""
GoalSeek Agent Prompt Templates

This module defines the prompt templates for the GoalSeek Agent that uses a
Working Backwards methodology to solve problems step by step.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Get the directory of the current file
PROMPTS_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "prompts"

def load_prompt(filename: str) -> str:
    """Load a prompt template from a file."""
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

# System prompt that defines the agent's role, methodology and approach
SYSTEM_PROMPT = load_prompt("system.txt")

# Intent analysis prompt for extracting and formalizing user intent
INTENT_ANALYSIS_PROMPT = load_prompt("intent_analysis.txt")

# Working backwards prompt for step-back questioning
WORKING_BACKWARDS_PROMPT = load_prompt("working_backwards.txt")

# Planning template for creating a structured plan
PLANNING_TEMPLATE = load_prompt("planning.txt")

# Execution status template for tracking progress
EXECUTION_STATUS_TEMPLATE = load_prompt("execution_status.txt")

# Human-in-the-loop feedback request template
FEEDBACK_REQUEST_TEMPLATE = load_prompt("feedback_request.txt")

# Tools error handling template
TOOL_ERROR_TEMPLATE = load_prompt("tool_error.txt")

def format_intent_analysis(user_input: str, **kwargs) -> str:
    """Format the intent analysis prompt with the given parameters."""
    return INTENT_ANALYSIS_PROMPT.format(user_input=user_input, **kwargs)

def format_working_backwards(goal_state: str, current_state: str, current_progress: str) -> str:
    """Format the working backwards prompt with the given parameters."""
    return WORKING_BACKWARDS_PROMPT.format(
        goal_state=goal_state,
        current_state=current_state,
        current_progress=current_progress
    )

def format_planning(goal: str, current_state: str, backwards_analysis: str, 
                   forward_plan: str, tools_required: str, success_criteria: str,
                   potential_challenges: str, monitoring_approach: str) -> str:
    """Format the planning template with the given parameters."""
    return PLANNING_TEMPLATE.format(
        goal=goal,
        current_state=current_state,
        backwards_analysis=backwards_analysis,
        forward_plan=forward_plan,
        tools_required=tools_required,
        success_criteria=success_criteria,
        potential_challenges=potential_challenges,
        monitoring_approach=monitoring_approach
    )

def format_execution_status(goal: str, plan_steps: str, current_step: str,
                           completed_steps: str, pending_steps: str,
                           observations: str, adjustments: str) -> str:
    """Format the execution status template with the given parameters."""
    return EXECUTION_STATUS_TEMPLATE.format(
        goal=goal,
        plan_steps=plan_steps,
        current_step=current_step,
        completed_steps=completed_steps,
        pending_steps=pending_steps,
        observations=observations,
        adjustments=adjustments
    )

def format_feedback_request(goal: str, plan: str, challenge: str,
                           questions: str, options: str) -> str:
    """Format the feedback request template with the given parameters."""
    return FEEDBACK_REQUEST_TEMPLATE.format(
        goal=goal,
        plan=plan,
        challenge=challenge,
        questions=questions,
        options=options
    )

def format_tool_error(tool_name: str, operation: str, error: str,
                     impact: str, recovery_steps: str, user_question: str) -> str:
    """Format the tool error template with the given parameters."""
    return TOOL_ERROR_TEMPLATE.format(
        tool_name=tool_name,
        operation=operation,
        error=error,
        impact=impact,
        recovery_steps=recovery_steps,
        user_question=user_question
    )

def format_visualization(content: str) -> str:
    """Format content with visualization border markers."""
    border = "◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢"
    return f"{border}\n{content}\n{border}"
