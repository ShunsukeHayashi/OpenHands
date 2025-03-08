"""
忍びAI (Shinobi AI) Agent Implementation

This module implements the ShinobiAgent class, a personal assistant agent with
long-term memory capabilities, adaptive learning, and personalized support.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from openhands.agent import Agent
from openhands.agent.config import AgentConfig
from openhands.agent.state import ConversationState
from openhands.agent.action import MessageAction
from openhands.agent.event import EventStream

from .memory.memory_system import ShinobiMemorySystem
from .dialogue.dialogue_manager import ShinobiDialogueManager
from .dialogue.emotion_analyzer import ShinobiEmotionAnalyzer
from .dialogue.response_generator import ShinobiResponseGenerator

logger = logging.getLogger(__name__)

class DialogueMode(Enum):
    """Dialogue modes for the Shinobi Agent."""
    REACTIVE = "reactive"     # Responding to user questions/requests
    PROACTIVE = "proactive"   # Situational suggestions and interventions
    REFLECTIVE = "reflective" # Progress and pattern review


class ShinobiAgent(Agent):
    """
    忍びAI (Shinobi AI) - Personal assistant agent with long-term memory,
    adaptive learning, and personalized support capabilities.
    
    The agent implements a sophisticated memory architecture and conversation
    framework that supports deep personalization and contextual understanding.
    """
    
    def __init__(self, llm, config=None):
        """
        Initialize the Shinobi Agent.
        
        Args:
            llm: Language model to use for generating responses
            config: Agent configuration
        """
        super().__init__(llm, config or AgentConfig())
        
        # Initialize components
        self.memory_system = ShinobiMemorySystem(llm, self.config)
        self.dialogue_manager = ShinobiDialogueManager(llm, self.config)
        self.emotion_analyzer = ShinobiEmotionAnalyzer(llm)
        self.response_generator = ShinobiResponseGenerator(llm, self.config)
        
        logger.info("ShinobiAgent initialized")
    
    async def step(self, state: ConversationState, event_stream: EventStream):
        """
        Process a single conversation step.
        
        Implements the 5-step conversation loop:
        1. 入力理解 (Input Understanding): Understanding user intent and emotions
        2. 文脈統合 (Context Integration): Integrating long-term memory and current situation
        3. 思考生成 (Thought Generation): Deciding appropriate responses/actions
        4. 表現最適化 (Expression Optimization): Forming responses based on user state
        5. 記憶更新 (Memory Update): Extracting and updating important information
        
        Args:
            state: Current conversation state
            event_stream: Event stream for publishing actions
        """
        # Get the last user message
        user_message = state.get_last_user_message()
        if not user_message:
            logger.debug("No user message found in state")
            return
        
        logger.debug(f"Processing user message: {user_message.content}")
        
        # 1. 入力理解 (Input Understanding)
        emotion_state = await self.emotion_analyzer.analyze(user_message.content)
        logger.debug(f"Emotion analysis: {emotion_state}")
        
        # 2. 文脈統合 (Context Integration)
        context = await self.memory_system.retrieve_relevant_context(user_message.content, state)
        logger.debug(f"Retrieved context: {len(context) if context else 0} items")
        
        # 3. 思考生成 (Thought Generation)
        dialogue_mode = self.dialogue_manager.determine_mode(state, emotion_state)
        logger.debug(f"Selected dialogue mode: {dialogue_mode}")
        
        response_plan = await self.dialogue_manager.generate_response_plan(
            user_message.content, context, dialogue_mode, state, emotion_state
        )
        
        # 4. 表現最適化 (Expression Optimization)
        response_text = await self.response_generator.generate(
            response_plan, emotion_state, dialogue_mode
        )
        logger.debug(f"Generated response: {response_text[:100]}...")
        
        # 5. 記憶更新 (Memory Update)
        await self.memory_system.update(user_message.content, response_text, emotion_state, state)
        
        # Send the response
        message_action = MessageAction(response_text)
        await event_stream.publish(message_action)
