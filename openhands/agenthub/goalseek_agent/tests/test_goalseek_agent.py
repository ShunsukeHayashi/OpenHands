"""
Tests for the GoalSeek Agent.

This module provides tests for the GoalSeek Agent to ensure it correctly implements
the Working Backwards methodology.
"""

import unittest
from unittest.mock import MagicMock, patch
import json

from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config.agent_config import AgentConfig
from openhands.core.message import Message
from openhands.events.action import MessageAction, AgentFinishAction, CmdRunAction
from openhands.llm.llm import LLM
from openhands.agenthub.goalseek_agent.goalseek_agent import GoalSeekAgent


class TestGoalSeekAgent(unittest.TestCase):
    """Tests for the GoalSeek Agent."""
    
    def setUp(self):
        """Set up the test environment."""
        # Mock LLM
        self.llm = MagicMock(spec=LLM)
        
        # Mock completion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        self.llm.completion.return_value = mock_response
        
        # Mock format_messages_for_llm
        self.llm.format_messages_for_llm.return_value = []
        
        # Mock config
        self.config = MagicMock(spec=AgentConfig)
        self.config.goalseek_max_plan_steps = 5
        
        # Create agent
        self.agent = GoalSeekAgent(llm=self.llm, config=self.config)
        
        # Mock state
        self.state = MagicMock(spec=State)
        self.state.history = []
    
    def test_initial_step(self):
        """Test the initial step of the agent."""
        # Call step with empty state
        action = self.agent.step(self.state)
        
        # Check that the action is a MessageAction
        self.assertIsInstance(action, MessageAction)
        self.assertIn("Hello! I'm the GoalSeek Agent", action.content)
    
    def test_analyze_intent(self):
        """Test the intent analysis."""
        # Mock user message
        user_message = MagicMock()
        user_message.content = "I want to build a simple web application"
        self.state.history = [user_message]
        
        # Mock LLM response for intent analysis
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = (
            "[Input] → [User Intent] → [Intent](Build a web application)\n\n"
            "[Fixed User want intent] = Build a simple web application\n\n"
            "Achieve Goal == Need Tasks\n"
            "[Goal]=[Tasks](\n"
            "  Task 1: Set up the development environment,\n"
            "  Task 2: Create the frontend,\n"
            "  Task 3: Create the backend,\n"
            "  Task 4: Deploy the application\n"
            ")"
        )
        self.llm.completion.return_value = mock_response
        
        # Call step
        action = self.agent.step(self.state)
        
        # Check that the action is a MessageAction
        self.assertIsInstance(action, MessageAction)
        self.assertIn("I've analyzed your request", action.content)
        self.assertIn("Goal:", action.content)
        
        # Check that the goal was set
        self.assertEqual(self.agent.goal_state, "Build a simple web application")
        
        # Check that the agent is in planning mode
        self.assertTrue(self.agent.is_planning)
    
    def test_working_backwards(self):
        """Test the working backwards planning."""
        # Set up agent with a goal
        self.agent.goal_state = "Build a simple web application"
        self.agent.is_planning = True
        
        # Mock user message
        user_message = MagicMock()
        user_message.content = "Let's start planning"
        self.state.history = [user_message]
        
        # Mock LLM response for working backwards
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = (
            "# Working Backwards Analysis\n\n"
            "1. Looking at our goal, the immediate prerequisite state is to have all components integrated.\n"
            "2. Tools needed: Web browser, deployment tools.\n"
            "3. Before that, we need to have the frontend and backend developed separately.\n"
            "4. We haven't reached actions that can be taken from our current state yet.\n"
            "5. The next concrete action is to set up the development environment.\n"
        )
        self.llm.completion.return_value = mock_response
        
        # Call step
        action = self.agent.step(self.state)
        
        # Check that the action is a MessageAction
        self.assertIsInstance(action, MessageAction)
        self.assertIn("I've started working backwards", action.content)
        
        # Check that backwards steps were created
        self.assertEqual(len(self.agent.backwards_steps), 1)
        self.assertEqual(
            self.agent.backwards_steps[0]["description"],
            "Looking at our goal, the immediate prerequisite state is to have all components integrated."
        )
    
    def test_create_forward_plan(self):
        """Test creating a forward plan from backwards steps."""
        # Set up agent with backwards steps
        self.agent.goal_state = "Build a simple web application"
        self.agent.is_planning = True
        self.agent.backwards_steps = [
            {
                "description": "Have all components integrated",
                "tools_needed": ["Web browser", "Deployment tools"],
                "prerequisites": ["Have frontend and backend developed"]
            },
            {
                "description": "Have frontend and backend developed",
                "tools_needed": ["Code editor", "Terminal"],
                "prerequisites": ["Have development environment set up"]
            },
            {
                "description": "Have development environment set up",
                "tools_needed": ["Package manager", "Git"],
                "prerequisites": ["Start from current state"]
            }
        ]
        
        # Mock user message
        user_message = MagicMock()
        user_message.content = "Let's create a forward plan"
        self.state.history = [user_message]
        
        # Mock LLM response for planning
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = (
            "# Comprehensive Working Backwards Plan\n\n"
            "## Forward Execution Plan\n"
            "1. Set up development environment\n"
            "2. Develop frontend and backend\n"
            "3. Integrate components\n"
        )
        self.llm.completion.return_value = mock_response
        
        # Call step
        action = self.agent.step(self.state)
        
        # Check that the action is a MessageAction
        self.assertIsInstance(action, MessageAction)
        self.assertIn("I've created a forward execution plan", action.content)
        
        # Check that forward plan was created
        self.assertEqual(len(self.agent.forward_plan), 3)
        self.assertEqual(
            self.agent.forward_plan[0]["description"],
            "Have development environment set up"
        )
        self.assertEqual(
            self.agent.forward_plan[1]["description"],
            "Have frontend and backend developed"
        )
        self.assertEqual(
            self.agent.forward_plan[2]["description"],
            "Have all components integrated"
        )
        
        # Check that the plan is ready
        self.assertTrue(self.agent.plan_ready)
        self.assertEqual(len(self.agent.pending_steps), 3)
    
    def test_execute_step(self):
        """Test executing a step in the plan."""
        # Set up agent with a forward plan
        self.agent.goal_state = "Build a simple web application"
        self.agent.is_planning = False
        self.agent.is_executing = True
        self.agent.forward_plan = [
            {
                "description": "Set up development environment",
                "tools_needed": ["Package manager", "Git"],
                "prerequisites": ["Start from current state"]
            },
            {
                "description": "Develop frontend and backend",
                "tools_needed": ["Code editor", "Terminal"],
                "prerequisites": ["Have development environment set up"]
            },
            {
                "description": "Integrate components",
                "tools_needed": ["Web browser", "Deployment tools"],
                "prerequisites": ["Have frontend and backend developed"]
            }
        ]
        self.agent.plan_ready = True
        self.agent.pending_steps = self.agent.forward_plan.copy()
        
        # Mock user message
        user_message = MagicMock()
        user_message.content = "Let's execute the plan"
        self.state.history = [user_message]
        
        # Mock LLM response for step execution
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = (
            "# Step Execution\n\n"
            "I'll set up the development environment by installing the necessary packages.\n\n"
            "```bash\n"
            "npm init -y && npm install express\n"
            "```\n"
        )
        self.llm.completion.return_value = mock_response
        
        # Call step
        action = self.agent.step(self.state)
        
        # Check that the action is a CmdRunAction
        self.assertIsInstance(action, CmdRunAction)
        self.assertEqual(action.command, "npm init -y && npm install express")
    
    def test_finish_execution(self):
        """Test finishing execution."""
        # Set up agent with a completed plan
        self.agent.goal_state = "Build a simple web application"
        self.agent.is_planning = False
        self.agent.is_executing = True
        self.agent.forward_plan = [
            {
                "description": "Set up development environment",
                "tools_needed": ["Package manager", "Git"],
                "prerequisites": ["Start from current state"]
            }
        ]
        self.agent.plan_ready = True
        self.agent.pending_steps = []
        self.agent.completed_steps = [
            {
                "description": "Set up development environment",
                "tools_needed": ["Package manager", "Git"],
                "prerequisites": ["Start from current state"],
                "result": "Development environment set up successfully"
            }
        ]
        self.agent.current_step_index = 1  # Beyond the end of the plan
        
        # Mock user message
        user_message = MagicMock()
        user_message.content = "Let's finish execution"
        self.state.history = [user_message]
        
        # Call step
        action = self.agent.step(self.state)
        
        # Check that the action is an AgentFinishAction
        self.assertIsInstance(action, AgentFinishAction)
        self.assertIn("I've completed all 1 steps of the plan", action.final_thought)
        
        # Check that the agent is marked as complete
        self.assertTrue(self.agent._complete)


if __name__ == "__main__":
    unittest.main()
