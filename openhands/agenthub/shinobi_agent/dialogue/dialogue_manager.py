"""
Dialogue Manager for Shinobi AI Agent

This module implements the dialogue management system for the Shinobi AI agent,
supporting three dialogue modes:
- Reactive: Responding to user questions/requests
- Proactive: Situational suggestions and interventions
- Reflective: Progress and pattern review
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re

from ..agent import DialogueMode

logger = logging.getLogger(__name__)

class ShinobiDialogueManager:
    """
    Dialogue Manager for Shinobi AI Agent.
    
    Responsible for:
    - Determining appropriate dialogue mode
    - Managing dialogue patterns
    - Generating response plans
    """
    
    def __init__(self, llm, config):
        """
        Initialize the dialogue manager.
        
        Args:
            llm: Language model for dialogue operations
            config: Configuration for the dialogue manager
        """
        self.llm = llm
        self.config = config
        self.dialogue_patterns = self._initialize_dialogue_patterns()
        
        logger.info("ShinobiDialogueManager initialized")
    
    def _initialize_dialogue_patterns(self):
        """Initialize dialogue patterns."""
        return {
            "initial_relationship": {
                "description": "Building initial relationship with the user",
                "triggers": ["first_interaction", "introduction"],
                "response_templates": [
                    "はじめまして、忍びAIです。あなたのパーソナルアシスタントとしてサポートさせていただきます。",
                    "どのようなことでお力になれるか、少しずつ理解していきたいと思います。"
                ]
            },
            "motivation_support": {
                "description": "Supporting user motivation",
                "triggers": ["motivation_drop", "frustration", "challenge"],
                "response_templates": [
                    "お力になれるでしょうか？小さな一歩から始めることが大切です。",
                    "困難に感じることは自然なことです。一緒に乗り越えていきましょう。"
                ]
            },
            "learning_session": {
                "description": "Supporting learning sessions",
                "triggers": ["learning", "study", "education"],
                "response_templates": [
                    "効果的な学習のためには、短い集中セッションと適切な休憩が重要です。",
                    "記憶しておきました。次回の学習セッションで活用しましょう。"
                ]
            },
            "review_session": {
                "description": "Reviewing progress and patterns",
                "triggers": ["review", "progress", "reflection"],
                "response_templates": [
                    "パターンが見えてきました。特に[pattern]の傾向があります。",
                    "前回の続きから、[topic]について進展がありましたね。"
                ]
            },
            "emotional_support": {
                "description": "Providing emotional support",
                "triggers": ["negative_emotion", "stress", "anxiety"],
                "response_templates": [
                    "その気持ち、理解できます。一緒に考えていきましょう。",
                    "大変な状況ですね。少しでもお力になれることがあれば教えてください。"
                ]
            }
        }
    
    def determine_mode(self, state, emotion_state):
        """
        Determine appropriate dialogue mode based on state and emotion.
        
        Args:
            state: Current conversation state
            emotion_state: User's emotional state
            
        Returns:
            DialogueMode: The selected dialogue mode
        """
        # Get the last user message
        user_message = state.get_last_user_message()
        if not user_message:
            return DialogueMode.REACTIVE
        
        # Direct question detection
        if self._is_direct_question(user_message.content):
            logger.debug("Direct question detected, using REACTIVE mode")
            return DialogueMode.REACTIVE
        
        # Periodic reflection timing
        if self._is_reflection_time(state):
            logger.debug("Reflection time detected, using REFLECTIVE mode")
            return DialogueMode.REFLECTIVE
        
        # Emotion-based mode selection
        if self._is_strong_emotion(emotion_state) and emotion_state.valence < 0.4:
            logger.debug("Strong negative emotion detected, using REACTIVE mode")
            return DialogueMode.REACTIVE
        
        # Pattern detection
        if self._has_detected_patterns(state):
            logger.debug("Patterns detected, using PROACTIVE mode")
            return DialogueMode.PROACTIVE
        
        # Default to reactive mode
        logger.debug("No specific conditions met, defaulting to REACTIVE mode")
        return DialogueMode.REACTIVE
    
    def _is_direct_question(self, text):
        """Check if text contains a direct question."""
        # Simple heuristic: check for question marks or question words
        question_patterns = [
            r'\?',  # Question mark
            r'^(何|誰|どこ|いつ|なぜ|どうして|どのように|どうやって)',  # Japanese question words
            r'(教えて|わかりますか|できますか|思いますか)'  # Common question phrases
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _is_reflection_time(self, state):
        """Check if it's time for reflection."""
        # In a full implementation, this would check conversation history length,
        # time since last reflection, etc.
        
        # For now, we'll use a simple heuristic: every 5 messages
        message_count = len(state.messages)
        return message_count > 0 and message_count % 5 == 0
    
    def _is_strong_emotion(self, emotion_state):
        """Check if the emotion state indicates strong emotions."""
        # Check if arousal is high
        arousal = emotion_state.get("arousal", 0.5)
        return arousal > 0.7
    
    def _has_detected_patterns(self, state):
        """Check if patterns have been detected in user behavior."""
        # In a full implementation, this would analyze conversation history
        # and detect patterns in user behavior
        
        # For now, we'll return False to default to reactive mode
        return False
    
    async def generate_response_plan(self, user_input, context, dialogue_mode, state, emotion_state):
        """
        Generate a response plan based on the dialogue mode.
        
        Args:
            user_input: User's message
            context: Relevant context from memory
            dialogue_mode: Selected dialogue mode
            state: Current conversation state
            emotion_state: User's emotional state
            
        Returns:
            Dict: Response plan with strategy and content
        """
        # In a full implementation, this would use the LLM to generate a detailed
        # response plan based on the dialogue mode, context, and emotion state
        
        # For now, we'll create a simple response plan
        response_plan = {
            "mode": dialogue_mode.value,
            "strategy": self._get_strategy_for_mode(dialogue_mode),
            "context_items": self._select_relevant_context_items(context, user_input),
            "emotion_adaptation": self._get_emotion_adaptation(emotion_state),
            "expression_style": self._get_expression_style(dialogue_mode, emotion_state)
        }
        
        logger.debug(f"Generated response plan for mode: {dialogue_mode.value}")
        
        return response_plan
    
    def _get_strategy_for_mode(self, dialogue_mode):
        """Get response strategy for the given dialogue mode."""
        strategies = {
            DialogueMode.REACTIVE: {
                "focus": "direct_response",
                "depth": "comprehensive",
                "tone": "helpful"
            },
            DialogueMode.PROACTIVE: {
                "focus": "suggestion",
                "depth": "balanced",
                "tone": "supportive"
            },
            DialogueMode.REFLECTIVE: {
                "focus": "analysis",
                "depth": "insightful",
                "tone": "thoughtful"
            }
        }
        
        return strategies.get(dialogue_mode, strategies[DialogueMode.REACTIVE])
    
    def _select_relevant_context_items(self, context, user_input):
        """Select relevant context items for the response."""
        # In a full implementation, this would use semantic similarity
        # to select the most relevant context items
        
        # For now, we'll just return a subset of the context
        selected_items = []
        
        if "recent_episodes" in context:
            selected_items.extend(context["recent_episodes"][:1])
        
        if "semantic_knowledge" in context:
            # Convert dict to list for consistency
            knowledge_items = [
                {"key": k, "value": v} 
                for k, v in context["semantic_knowledge"].items()
            ]
            selected_items.extend(knowledge_items[:2])
        
        return selected_items
    
    def _get_emotion_adaptation(self, emotion_state):
        """Get adaptation strategy based on emotion state."""
        valence = emotion_state.get("valence", 0.5)
        arousal = emotion_state.get("arousal", 0.5)
        
        if valence < 0.3:
            # Negative emotion
            if arousal > 0.7:
                return {
                    "strategy": "calming",
                    "tone": "empathetic",
                    "response_length": "moderate"
                }
            else:
                return {
                    "strategy": "supportive",
                    "tone": "warm",
                    "response_length": "moderate"
                }
        elif valence > 0.7:
            # Positive emotion
            if arousal > 0.7:
                return {
                    "strategy": "matching",
                    "tone": "enthusiastic",
                    "response_length": "moderate"
                }
            else:
                return {
                    "strategy": "maintaining",
                    "tone": "pleasant",
                    "response_length": "moderate"
                }
        else:
            # Neutral emotion
            return {
                "strategy": "informative",
                "tone": "neutral",
                "response_length": "balanced"
            }
    
    def _get_expression_style(self, dialogue_mode, emotion_state):
        """Get expression style based on dialogue mode and emotion state."""
        base_style = {
            DialogueMode.REACTIVE: {
                "formality": "polite",
                "detail_level": "appropriate",
                "unique_expressions": ["記憶しておきました"]
            },
            DialogueMode.PROACTIVE: {
                "formality": "friendly",
                "detail_level": "concise",
                "unique_expressions": ["お力になれるでしょうか"]
            },
            DialogueMode.REFLECTIVE: {
                "formality": "thoughtful",
                "detail_level": "detailed",
                "unique_expressions": ["パターンが見えてきました", "前回の続きから"]
            }
        }
        
        style = base_style.get(dialogue_mode, base_style[DialogueMode.REACTIVE])
        
        # Adjust formality based on relationship stage
        # In a full implementation, this would be based on interaction history
        style["formality"] = "polite"
        
        return style
