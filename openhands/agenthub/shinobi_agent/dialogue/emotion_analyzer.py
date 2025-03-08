"""
Emotion Analyzer for Shinobi AI Agent

This module implements emotion analysis for the Shinobi AI agent,
using a multi-dimensional emotion model with:
- Valence: Positive vs. Negative (0-1)
- Arousal: Calm vs. Excited (0-1)
- Dominance: Submissive vs. Dominant (0-1)
"""

import logging
import re
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class EmotionState:
    """
    Represents the emotional state of the user.
    
    Attributes:
        valence: Positive vs. Negative (0-1)
        arousal: Calm vs. Excited (0-1)
        dominance: Submissive vs. Dominant (0-1)
        primary_emotion: The primary detected emotion
    """
    
    def __init__(self, valence=0.5, arousal=0.5, dominance=0.5, primary_emotion="neutral"):
        self.valence = valence
        self.arousal = arousal
        self.dominance = dominance
        self.primary_emotion = primary_emotion
    
    def __str__(self):
        return (f"EmotionState(valence={self.valence:.2f}, arousal={self.arousal:.2f}, "
                f"dominance={self.dominance:.2f}, primary_emotion='{self.primary_emotion}')")
    
    def get(self, key, default=None):
        """Get an attribute value by name."""
        return getattr(self, key, default)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "primary_emotion": self.primary_emotion
        }


class ShinobiEmotionAnalyzer:
    """
    Emotion Analyzer for Shinobi AI Agent.
    
    Analyzes user messages to detect emotional states using a
    multi-dimensional emotion model.
    """
    
    def __init__(self, llm):
        """
        Initialize the emotion analyzer.
        
        Args:
            llm: Language model for emotion analysis
        """
        self.llm = llm
        self.emotion_lexicon = self._initialize_emotion_lexicon()
        self.emotion_patterns = self._initialize_emotion_patterns()
        
        logger.info("ShinobiEmotionAnalyzer initialized")
    
    def _initialize_emotion_lexicon(self):
        """Initialize emotion lexicon."""
        # This is a simplified lexicon for demonstration
        # In a full implementation, this would be a more comprehensive lexicon
        return {
            "positive": [
                "嬉しい", "楽しい", "幸せ", "喜び", "感謝", "ありがとう", "素晴らしい",
                "良い", "好き", "愛", "希望", "期待", "興味", "満足"
            ],
            "negative": [
                "悲しい", "辛い", "苦しい", "不安", "心配", "恐れ", "怒り", "イライラ",
                "失望", "後悔", "嫌い", "憎い", "疲れた", "困った", "難しい"
            ],
            "high_arousal": [
                "興奮", "驚き", "ショック", "急", "すぐに", "早く", "とても", "非常に",
                "すごく", "激しい", "強い", "熱い", "燃える", "爆発"
            ],
            "low_arousal": [
                "穏やか", "静か", "落ち着いた", "ゆっくり", "のんびり", "リラックス",
                "平和", "安心", "安定", "冷静", "眠い", "疲れた"
            ],
            "high_dominance": [
                "必要", "すべき", "しなければ", "絶対", "確実", "決定", "命令",
                "要求", "強制", "支配", "勝利", "成功", "達成"
            ],
            "low_dominance": [
                "お願い", "できますか", "かもしれない", "たぶん", "もしかしたら",
                "助けて", "教えて", "分からない", "迷う", "困る", "失敗"
            ]
        }
    
    def _initialize_emotion_patterns(self):
        """Initialize emotion patterns."""
        # This is a simplified set of patterns for demonstration
        # In a full implementation, this would be more comprehensive
        return {
            "question": r'\?|か？|ですか|でしょうか',
            "exclamation": r'!|！|わ！|よ！',
            "gratitude": r'ありがとう|感謝|助かる',
            "apology": r'ごめん|すみません|申し訳',
            "frustration": r'難しい|できない|うまくいかない|困った',
            "satisfaction": r'できた|うまくいった|成功|良かった',
            "confusion": r'わからない|理解できない|混乱|どういうこと',
            "urgency": r'急|すぐに|早く|今すぐ'
        }
    
    async def analyze(self, text):
        """
        Analyze the emotional content of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            EmotionState: The detected emotional state
        """
        # In a full implementation, this would use the LLM for sophisticated
        # emotion analysis. For now, we'll use a rule-based approach.
        
        # Initialize with neutral values
        valence = 0.5
        arousal = 0.5
        dominance = 0.5
        primary_emotion = "neutral"
        
        # Analyze lexical content
        valence_score = self._analyze_lexical_dimension(text, "positive", "negative")
        arousal_score = self._analyze_lexical_dimension(text, "high_arousal", "low_arousal")
        dominance_score = self._analyze_lexical_dimension(text, "high_dominance", "low_dominance")
        
        # Analyze patterns
        pattern_scores = self._analyze_patterns(text)
        
        # Combine scores
        valence = 0.5 + valence_score * 0.5  # Scale to 0-1
        arousal = 0.5 + arousal_score * 0.5  # Scale to 0-1
        dominance = 0.5 + dominance_score * 0.5  # Scale to 0-1
        
        # Adjust based on patterns
        valence += pattern_scores.get("valence", 0)
        arousal += pattern_scores.get("arousal", 0)
        dominance += pattern_scores.get("dominance", 0)
        
        # Ensure values are within 0-1 range
        valence = max(0, min(1, valence))
        arousal = max(0, min(1, arousal))
        dominance = max(0, min(1, dominance))
        
        # Determine primary emotion based on VAD values
        primary_emotion = self._determine_primary_emotion(valence, arousal, dominance)
        
        logger.debug(f"Emotion analysis: valence={valence:.2f}, arousal={arousal:.2f}, "
                    f"dominance={dominance:.2f}, primary_emotion='{primary_emotion}'")
        
        return EmotionState(valence, arousal, dominance, primary_emotion)
    
    def _analyze_lexical_dimension(self, text, positive_category, negative_category):
        """
        Analyze text for a specific emotional dimension.
        
        Args:
            text: Text to analyze
            positive_category: Lexicon category for positive end of dimension
            negative_category: Lexicon category for negative end of dimension
            
        Returns:
            float: Score between -1 and 1
        """
        positive_count = 0
        negative_count = 0
        
        # Count positive terms
        for term in self.emotion_lexicon[positive_category]:
            positive_count += len(re.findall(term, text))
        
        # Count negative terms
        for term in self.emotion_lexicon[negative_category]:
            negative_count += len(re.findall(term, text))
        
        # Calculate score
        total_count = positive_count + negative_count
        if total_count == 0:
            return 0
        
        return (positive_count - negative_count) / total_count
    
    def _analyze_patterns(self, text):
        """
        Analyze text for emotional patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict: Adjustments for valence, arousal, and dominance
        """
        adjustments = {"valence": 0, "arousal": 0, "dominance": 0}
        
        # Check for question patterns
        if re.search(self.emotion_patterns["question"], text):
            adjustments["dominance"] -= 0.1
        
        # Check for exclamation patterns
        if re.search(self.emotion_patterns["exclamation"], text):
            adjustments["arousal"] += 0.2
        
        # Check for gratitude patterns
        if re.search(self.emotion_patterns["gratitude"], text):
            adjustments["valence"] += 0.2
        
        # Check for apology patterns
        if re.search(self.emotion_patterns["apology"], text):
            adjustments["dominance"] -= 0.2
            adjustments["valence"] -= 0.1
        
        # Check for frustration patterns
        if re.search(self.emotion_patterns["frustration"], text):
            adjustments["valence"] -= 0.2
            adjustments["arousal"] += 0.1
        
        # Check for satisfaction patterns
        if re.search(self.emotion_patterns["satisfaction"], text):
            adjustments["valence"] += 0.2
        
        # Check for confusion patterns
        if re.search(self.emotion_patterns["confusion"], text):
            adjustments["dominance"] -= 0.1
            adjustments["valence"] -= 0.1
        
        # Check for urgency patterns
        if re.search(self.emotion_patterns["urgency"], text):
            adjustments["arousal"] += 0.2
        
        return adjustments
    
    def _determine_primary_emotion(self, valence, arousal, dominance):
        """
        Determine primary emotion based on VAD values.
        
        Args:
            valence: Valence value (0-1)
            arousal: Arousal value (0-1)
            dominance: Dominance value (0-1)
            
        Returns:
            str: Primary emotion
        """
        # This is a simplified mapping for demonstration
        # In a full implementation, this would be more sophisticated
        
        # High valence
        if valence > 0.7:
            if arousal > 0.7:
                return "joy" if dominance > 0.5 else "excitement"
            else:
                return "contentment" if dominance > 0.5 else "relaxation"
        
        # Medium valence
        elif valence > 0.4:
            if arousal > 0.7:
                return "surprise" if dominance > 0.5 else "confusion"
            else:
                return "neutral"
        
        # Low valence
        else:
            if arousal > 0.7:
                return "anger" if dominance > 0.5 else "fear"
            else:
                return "sadness" if dominance > 0.5 else "disappointment"
