"""
Response Generator for Shinobi AI Agent

This module implements the response generation system for the Shinobi AI agent,
creating responses that match the agent's unique communication style and adapt
to the user's emotional state and dialogue context.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Union

from ..agent import DialogueMode

logger = logging.getLogger(__name__)

class ShinobiResponseGenerator:
    """
    Response Generator for Shinobi AI Agent.
    
    Responsible for:
    - Generating responses based on dialogue mode and emotion state
    - Adapting response style to user needs
    - Incorporating unique expressions
    """
    
    def __init__(self, llm, config):
        """
        Initialize the response generator.
        
        Args:
            llm: Language model for response generation
            config: Configuration for the response generator
        """
        self.llm = llm
        self.config = config
        self.expression_library = self._initialize_expression_library()
        
        logger.info("ShinobiResponseGenerator initialized")
    
    def _initialize_expression_library(self):
        """Initialize unique expression library."""
        return {
            "memory_storage": [
                "記憶しておきました",
                "覚えておきますね",
                "大切な情報として記録しました",
                "今後の会話で活用させていただきます"
            ],
            "context_retrieval": [
                "前回の続きから",
                "以前の会話を思い出しました",
                "前にお話しいただいた内容を踏まえると",
                "これまでの経緯を考慮すると"
            ],
            "pattern_sharing": [
                "パターンが見えてきました",
                "傾向が見えてきましたね",
                "一定の規則性が見られます",
                "興味深い習慣が観察されます"
            ],
            "support_offering": [
                "お力になれるでしょうか",
                "何かお手伝いできることはありますか",
                "サポートできることがあれば教えてください",
                "どのようにお手伝いできるか考えています"
            ],
            "empathy": [
                "その気持ち、理解できます",
                "大変な状況ですね",
                "それは難しい経験だったのですね",
                "その困難を乗り越えるのは容易ではないですね"
            ],
            "encouragement": [
                "小さな一歩から始めることが大切です",
                "着実に進んでいることを評価してください",
                "その努力は必ず実を結ぶでしょう",
                "一緒に前進していきましょう"
            ]
        }
    
    async def generate(self, response_plan, emotion_state, dialogue_mode):
        """
        Generate a response based on the response plan.
        
        Args:
            response_plan: Plan for the response
            emotion_state: User's emotional state
            dialogue_mode: Current dialogue mode
            
        Returns:
            str: Generated response
        """
        # In a full implementation, this would use the LLM to generate a response
        # based on the response plan, emotion state, and dialogue mode
        
        # For now, we'll create a template-based response
        response = self._create_template_response(response_plan, emotion_state, dialogue_mode)
        
        # Add unique expression based on dialogue mode
        expression = self._select_unique_expression(dialogue_mode)
        if expression:
            response = f"{response} {expression}"
        
        logger.debug(f"Generated response for mode {dialogue_mode.value}")
        
        return response
    
    def _create_template_response(self, response_plan, emotion_state, dialogue_mode):
        """
        Create a template-based response.
        
        Args:
            response_plan: Plan for the response
            emotion_state: User's emotional state
            dialogue_mode: Current dialogue mode
            
        Returns:
            str: Template-based response
        """
        # Get base response template based on dialogue mode
        base_templates = {
            DialogueMode.REACTIVE: [
                "はい、{topic}については{explanation}です。",
                "{topic}に関しては、{explanation}と言えるでしょう。",
                "{explanation}というのが{topic}についての一般的な見解です。"
            ],
            DialogueMode.PROACTIVE: [
                "もしよろしければ、{suggestion}してみてはいかがでしょうか。",
                "{observation}から、{suggestion}すると効果的かもしれません。",
                "{suggestion}することで、{benefit}が期待できます。"
            ],
            DialogueMode.REFLECTIVE: [
                "これまでの{activity}を振り返ると、{pattern}という傾向が見られます。",
                "{timeframe}の{activity}を分析すると、{pattern}ということがわかります。",
                "{pattern}というパターンが{activity}に見られます。これは{implication}を示唆しています。"
            ]
        }
        
        # Select a random template from the appropriate set
        templates = base_templates.get(dialogue_mode, base_templates[DialogueMode.REACTIVE])
        template = random.choice(templates)
        
        # Fill in placeholders with mock content
        # In a full implementation, this would use actual content from the response plan
        fillers = {
            "topic": "ご質問の件",
            "explanation": "様々な要素を考慮することが重要",
            "suggestion": "短い時間でも毎日継続すること",
            "observation": "これまでの学習パターン",
            "benefit": "習慣化しやすくなる",
            "activity": "学習活動",
            "pattern": "短時間の集中セッションが効果的",
            "timeframe": "過去2週間",
            "implication": "学習効率の向上"
        }
        
        for key, value in fillers.items():
            template = template.replace(f"{{{key}}}", value)
        
        # Adjust response based on emotion state
        response = self._adjust_for_emotion(template, emotion_state)
        
        return response
    
    def _adjust_for_emotion(self, response, emotion_state):
        """
        Adjust response based on emotion state.
        
        Args:
            response: Base response
            emotion_state: User's emotional state
            
        Returns:
            str: Emotion-adjusted response
        """
        valence = emotion_state.valence
        primary_emotion = emotion_state.primary_emotion
        
        # Add empathetic prefix for negative emotions
        if valence < 0.3:
            empathy_expression = random.choice(self.expression_library["empathy"])
            response = f"{empathy_expression}。{response}"
        
        # Add encouragement for certain emotions
        if primary_emotion in ["sadness", "fear", "disappointment"]:
            encouragement = random.choice(self.expression_library["encouragement"])
            response = f"{response} {encouragement}"
        
        return response
    
    def _select_unique_expression(self, dialogue_mode):
        """
        Select a unique expression based on dialogue mode.
        
        Args:
            dialogue_mode: Current dialogue mode
            
        Returns:
            str: Selected unique expression
        """
        # Select expression category based on dialogue mode
        categories = {
            DialogueMode.REACTIVE: ["memory_storage"],
            DialogueMode.PROACTIVE: ["support_offering"],
            DialogueMode.REFLECTIVE: ["pattern_sharing", "context_retrieval"]
        }
        
        selected_categories = categories.get(dialogue_mode, ["memory_storage"])
        category = random.choice(selected_categories)
        
        # Select a random expression from the category
        expressions = self.expression_library[category]
        expression = random.choice(expressions)
        
        return expression
