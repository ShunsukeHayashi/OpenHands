"""
Memory System for Shinobi AI Agent

This module implements a multi-layered memory system with:
- Working Memory: Current conversation context and state
- Episodic Memory: Chronological record of past conversations and events
- Semantic Memory: Structured knowledge about the user
- Procedural Memory: Effective dialogue patterns
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class MemoryLayer:
    """Base class for memory layers."""
    
    def __init__(self, name):
        self.name = name
    
    async def store(self, content, metadata):
        """Store content in this memory layer."""
        raise NotImplementedError
    
    async def retrieve(self, query, limit=5):
        """Retrieve content from this memory layer."""
        raise NotImplementedError


class WorkingMemory(MemoryLayer):
    """
    Working Memory: Stores current conversation context and state.
    This is volatile and only persists during the current session.
    """
    
    def __init__(self):
        super().__init__("working")
        self.content = {}
    
    async def store(self, content, metadata):
        """Store content in working memory."""
        key = metadata.get("key", str(datetime.now().timestamp()))
        self.content[key] = {
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        return key
    
    async def retrieve(self, query=None, limit=None):
        """Retrieve all content from working memory."""
        # Working memory is small enough that we can return everything
        # and let the caller filter as needed
        return list(self.content.values())
    
    def clear(self):
        """Clear working memory."""
        self.content = {}


class EpisodicMemory(MemoryLayer):
    """
    Episodic Memory: Chronological record of past conversations and events.
    """
    
    def __init__(self):
        super().__init__("episodic")
        self.episodes = []
    
    async def store(self, content, metadata):
        """Store an episode in episodic memory."""
        episode = {
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "id": str(len(self.episodes))
        }
        self.episodes.append(episode)
        return episode["id"]
    
    async def retrieve(self, query=None, limit=5):
        """
        Retrieve episodes from episodic memory.
        
        For now, this is a simple recency-based retrieval.
        In a full implementation, this would use vector similarity search.
        """
        # Sort by recency (newest first)
        sorted_episodes = sorted(
            self.episodes, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        # Return the most recent episodes
        return sorted_episodes[:limit]


class SemanticMemory(MemoryLayer):
    """
    Semantic Memory: Structured knowledge about the user.
    """
    
    def __init__(self):
        super().__init__("semantic")
        self.knowledge = {}
    
    async def store(self, content, metadata):
        """Store knowledge in semantic memory."""
        category = metadata.get("category", "general")
        key = metadata.get("key")
        
        if not key:
            logger.warning("No key provided for semantic memory storage")
            return None
        
        if category not in self.knowledge:
            self.knowledge[category] = {}
        
        self.knowledge[category][key] = {
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "confidence": metadata.get("confidence", 0.5),
            "last_updated": datetime.now().isoformat()
        }
        
        return f"{category}:{key}"
    
    async def retrieve(self, query=None, limit=None):
        """
        Retrieve knowledge from semantic memory.
        
        Args:
            query: Optional category to filter by
            limit: Not used for semantic memory
        """
        if query and query in self.knowledge:
            return self.knowledge[query]
        
        # If no specific category is requested, return all knowledge
        result = {}
        for category, items in self.knowledge.items():
            result.update(items)
        
        return result


class ProceduralMemory(MemoryLayer):
    """
    Procedural Memory: Effective dialogue patterns and learned behaviors.
    """
    
    def __init__(self):
        super().__init__("procedural")
        self.patterns = []
    
    async def store(self, content, metadata):
        """Store a pattern in procedural memory."""
        pattern = {
            "pattern": content,
            "metadata": metadata,
            "effectiveness": metadata.get("effectiveness", 0.5),
            "usage_count": 0,
            "timestamp": datetime.now().isoformat(),
            "id": str(len(self.patterns))
        }
        self.patterns.append(pattern)
        return pattern["id"]
    
    async def retrieve(self, query=None, limit=5):
        """
        Retrieve patterns from procedural memory.
        
        Args:
            query: Optional pattern type to filter by
            limit: Maximum number of patterns to return
        """
        filtered_patterns = self.patterns
        
        if query:
            filtered_patterns = [
                p for p in self.patterns 
                if p["metadata"].get("type") == query
            ]
        
        # Sort by effectiveness
        sorted_patterns = sorted(
            filtered_patterns,
            key=lambda x: x["effectiveness"],
            reverse=True
        )
        
        return sorted_patterns[:limit]
    
    async def update_effectiveness(self, pattern_id, effectiveness_delta):
        """Update the effectiveness of a pattern."""
        for pattern in self.patterns:
            if pattern["id"] == pattern_id:
                pattern["effectiveness"] = max(0, min(1, 
                    pattern["effectiveness"] + effectiveness_delta
                ))
                pattern["usage_count"] += 1
                return True
        
        return False


class ShinobiMemorySystem:
    """
    Memory System for Shinobi AI Agent.
    
    Implements a 4-layer memory hierarchy:
    - Working Memory: Current conversation context and state
    - Episodic Memory: Chronological record of past conversations and events
    - Semantic Memory: Structured knowledge about the user
    - Procedural Memory: Effective dialogue patterns
    """
    
    def __init__(self, llm, config):
        """
        Initialize the memory system.
        
        Args:
            llm: Language model for memory operations
            config: Configuration for the memory system
        """
        self.llm = llm
        self.config = config
        
        # Initialize memory layers
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        
        # Vector database for semantic search
        # In a full implementation, this would use ChromaDB or similar
        self.vector_db = None
        
        logger.info("ShinobiMemorySystem initialized")
    
    async def update(self, user_input, agent_response, emotion_state, state):
        """
        Update memory with new conversation data.
        
        Args:
            user_input: User's message
            agent_response: Agent's response
            emotion_state: User's emotional state
            state: Current conversation state
        """
        # Store in working memory
        await self.working_memory.store(
            {"user_input": user_input, "agent_response": agent_response},
            {"type": "conversation", "emotion": emotion_state}
        )
        
        # Store in episodic memory
        await self.episodic_memory.store(
            {"user_input": user_input, "agent_response": agent_response},
            {"type": "conversation", "emotion": emotion_state}
        )
        
        # Extract and store important information in semantic memory
        # In a full implementation, this would use LLM to extract key information
        # For now, we'll just store a placeholder
        await self.semantic_memory.store(
            "Placeholder for extracted information",
            {"category": "user_info", "key": f"info_{datetime.now().timestamp()}", "confidence": 0.7}
        )
        
        logger.debug("Memory updated with new conversation data")
    
    async def retrieve_relevant_context(self, user_input, state):
        """
        Retrieve relevant context for the current conversation.
        
        Args:
            user_input: User's message
            state: Current conversation state
            
        Returns:
            Dict: Relevant memory items
        """
        # Get recent episodes
        recent_episodes = await self.episodic_memory.retrieve(limit=3)
        
        # Get relevant semantic knowledge
        # In a full implementation, this would use vector similarity search
        semantic_knowledge = await self.semantic_memory.retrieve()
        
        # Get relevant procedural patterns
        patterns = await self.procedural_memory.retrieve(limit=2)
        
        # Combine all relevant context
        context = {
            "recent_episodes": recent_episodes,
            "semantic_knowledge": semantic_knowledge,
            "patterns": patterns
        }
        
        logger.debug(f"Retrieved context with {len(recent_episodes)} episodes")
        
        return context
    
    async def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory.clear()
        logger.debug("Working memory cleared")
