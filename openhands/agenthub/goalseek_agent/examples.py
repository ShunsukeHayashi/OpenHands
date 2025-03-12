"""
Example usage of the GoalSeek Agent.

This module provides examples of how to use the GoalSeek Agent to solve problems
using the Working Backwards methodology.
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging

from openhands.controller.agent import Agent
from openhands.core.config.agent_config import AgentConfig
from openhands.llm.llm import LLM
from openhands.agenthub.goalseek_agent.goalseek_agent import GoalSeekAgent

logger = logging.getLogger(__name__)

async def run_goalseek_agent_example(goal: str, llm: LLM, config: AgentConfig) -> None:
    """
    Run an example of the GoalSeek Agent with a specific goal.
    
    Args:
        goal: The goal to achieve
        llm: The LLM to use
        config: The agent configuration
    """
    # Create the GoalSeek agent
    agent = GoalSeekAgent(llm=llm, config=config)
    
    # Set the goal
    agent.goal_state = goal
    
    # Log the goal
    logger.info(f"Running GoalSeek Agent with goal: {goal}")
    
    # Start the agent
    # Note: In a real application, the agent would be run through the OpenHands runtime
    # This is just a simplified example
    
    # Create a simple working backwards plan
    backwards_steps = [
        {
            "description": "Achieve the final goal",
            "tools_needed": ["Tool1", "Tool2"],
            "prerequisites": ["Complete prerequisite step"]
        },
        {
            "description": "Complete prerequisite step",
            "tools_needed": ["Tool3"],
            "prerequisites": ["Set up initial conditions"]
        },
        {
            "description": "Set up initial conditions",
            "tools_needed": ["Tool4"],
            "prerequisites": ["Start from current state"]
        }
    ]
    
    # Add steps to the agent
    for step in backwards_steps:
        agent.backwards_steps.append(step)
    
    # Create forward plan
    agent.forward_plan = list(reversed(agent.backwards_steps))
    agent.plan_ready = True
    agent.pending_steps = agent.forward_plan.copy()
    
    # Print the plan
    print("\n=== WORKING BACKWARDS PLAN ===")
    for i, step in enumerate(agent.backwards_steps):
        print(f"{i+1}. {step.get('description', 'Step')}")
    
    print("\n=== FORWARD EXECUTION PLAN ===")
    for i, step in enumerate(agent.forward_plan):
        print(f"{i+1}. {step.get('description', 'Step')}")
    
    # Print the execution status
    status = agent._get_execution_status()
    print("\n=== EXECUTION STATUS ===")
    print(status)

def main():
    """Run the example."""
    # This is a placeholder for running the example
    # In a real application, this would be run through the OpenHands runtime
    print("GoalSeek Agent Example")
    print("This example demonstrates how to use the GoalSeek Agent to solve problems")
    print("using the Working Backwards methodology.")
    print("\nTo run this example, you need to use the OpenHands runtime.")
    print("See the OpenHands documentation for more information.")

if __name__ == "__main__":
    main()
