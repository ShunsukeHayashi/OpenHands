"""
Test script for Shinobi AI Agent

This script provides a simplified test environment for the Shinobi AI agent,
demonstrating its core functionality without requiring the full OpenHands framework.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock OpenHands framework classes
class Message:
    """Mock Message class."""
    def __init__(self, content, role="user"):
        self.content = content
        self.role = role

class ConversationState:
    """Mock ConversationState class."""
    def __init__(self):
        self.messages = []
    
    def add_message(self, content, role="user"):
        """Add a message to the conversation."""
        self.messages.append(Message(content, role))
    
    def get_last_user_message(self):
        """Get the last user message."""
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None

class EventStream:
    """Mock EventStream class."""
    def __init__(self):
        self.actions = []
    
    async def publish(self, action):
        """Publish an action to the event stream."""
        self.actions.append(action)
        logger.info(f"Action published: {action}")

class MessageAction:
    """Mock MessageAction class."""
    def __init__(self, content):
        self.content = content
    
    def __str__(self):
        return f"MessageAction(content='{self.content[:50]}...')" if len(self.content) > 50 else f"MessageAction(content='{self.content}')"

class AgentConfig:
    """Mock AgentConfig class."""
    def __init__(self):
        self.config = {
            "memory": {
                "vector_db": "mock",
                "persistence": True
            },
            "dialogue": {
                "default_mode": "reactive",
                "proactive_threshold": 0.7
            },
            "emotion": {
                "analysis_enabled": True,
                "adaptation_level": 0.8
            }
        }
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)

# Import Shinobi Agent
from agent import ShinobiAgent, DialogueMode
from dialogue.emotion_analyzer import EmotionState

class MockLLM:
    """Mock LLM for testing."""
    async def generate(self, prompt, **kwargs):
        """Generate a response."""
        # Return a simple response based on the input
        if "学習" in prompt or "勉強" in prompt:
            return "はい、AIについての学習方法としては、オンラインコースや書籍から基礎を学び、実践的なプロジェクトに取り組むことをお勧めします。特に、基本的な概念を理解した後は、実際に小さなプロジェクトを作ることで理解が深まります。"
        elif "モチベーション" in prompt or "やる気" in prompt:
            return "モチベーションが続かないことは誰にでもあります。短い時間でも毎日続けることで、習慣化しやすくなります。また、小さな成功体験を積み重ねることも効果的です。"
        elif "続け" in prompt or "毎日" in prompt:
            return "これまでの学習パターンを分析すると、短時間の集中セッションが効果的なようです。特に午前中の学習で理解度が高まっています。"
        else:
            return "ご質問やお手伝いできることがあれば、お気軽にお知らせください。"

async def test_shinobi_agent():
    """Test the Shinobi AI agent."""
    logger.info("Starting Shinobi AI agent test")
    
    # Initialize mock LLM
    llm = MockLLM()
    
    # Initialize agent
    agent = ShinobiAgent(llm)
    
    # Initialize conversation state and event stream
    state = ConversationState()
    event_stream = EventStream()
    
    # Test conversation
    test_messages = [
        "はじめまして、AIについて学んでいます。おすすめの学習方法はありますか？",
        "ありがとう。でも最近モチベーションが続かなくて困っています。",
        "そうですね、短い時間でも毎日続けることを意識してみます。"
    ]
    
    for message in test_messages:
        logger.info(f"User: {message}")
        
        # Add message to state
        state.add_message(message)
        
        # Process message
        await agent.step(state, event_stream)
        
        # Get agent response
        if event_stream.actions:
            action = event_stream.actions[-1]
            logger.info(f"忍びAI: {action.content}")
            
            # Add agent response to state
            state.add_message(action.content, role="assistant")
        
        # Clear event stream for next message
        event_stream.actions = []
        
        # Pause between messages
        await asyncio.sleep(1)
    
    logger.info("Shinobi AI agent test completed")

if __name__ == "__main__":
    asyncio.run(test_shinobi_agent())
