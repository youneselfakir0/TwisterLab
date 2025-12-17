"""
SentimentAnalyzerAgent - Analyzes text sentiment (positive/negative/neutral).

Part of TwisterLab autonomous agent system.
"""

from typing import Any, Dict, List, Optional
from twisterlab.agents.base import TwisterAgent


class SentimentAnalyzerAgent(TwisterAgent):
    """
    Agent specialized in sentiment analysis of text content.
    
    Capabilities:
    - Detects positive, negative, or neutral sentiment
    - Provides confidence scores
    - Supports multi-language text (English, French, etc.)
    - Can analyze individual texts or batches
    """

    def __init__(self):
        super().__init__(
            name="sentiment-analyzer",
            display_name="Sentiment Analyzer",
            description="Analyzes text sentiment and returns positive/negative/neutral classification with confidence scores",
            role="analyst",
            instructions="""You are a sentiment analysis expert. Analyze the given text and classify it as:
- POSITIVE: Expresses happiness, satisfaction, approval, or optimism
- NEGATIVE: Expresses sadness, dissatisfaction, criticism, or pessimism
- NEUTRAL: Factual statements without emotional tone

Provide a confidence score (0.0-1.0) for your classification.""",
            model="llama-3.2",
            temperature=0.3,  # Lower temperature for consistent analysis
            metadata={
                "version": "1.0.0",
                "supported_languages": ["en", "fr", "es", "de"],
                "categories": ["positive", "negative", "neutral"]
            }
        )
        
        # Sentiment keywords for simple rule-based fallback
        self.positive_keywords = {
            "excellent", "great", "amazing", "wonderful", "fantastic",
            "love", "happy", "good", "best", "awesome", "perfect",
            "g├⌐nial", "super", "excellent", "formidable", "merveilleux"
        }
        
        self.negative_keywords = {
            "terrible", "awful", "bad", "worst", "hate", "horrible",
            "poor", "disappointing", "frustrating", "angry", "sad",
            "mauvais", "horrible", "nul", "catastrophique", "d├⌐├ºu"
        }

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute sentiment analysis on the given text.

        Args:
            task: Text to analyze
            context: Optional context with:
                - language: Target language (default: auto-detect)
                - threshold: Confidence threshold (default: 0.6)
                - detailed: Return detailed scores (default: False)

        Returns:
            Dict containing:
                - sentiment: "positive", "negative", or "neutral"
                - confidence: float (0.0-1.0)
                - details: optional detailed analysis
                - analyzed_text: original text
        """
        context = context or {}
        
        try:
            # Extract parameters
            text = task.strip()
            threshold = context.get("threshold", 0.6)
            detailed = context.get("detailed", False)
            
            if not text:
                return {
                    "error": "No text provided for analysis",
                    "sentiment": "neutral",
                    "confidence": 0.0
                }
            
            # Perform simple rule-based analysis
            # In production, this would call an LLM or ML model
            sentiment, confidence, scores = self._analyze_simple(text)
            
            result = {
                "sentiment": sentiment,
                "confidence": round(confidence, 3),
                "analyzed_text": text[:100] + "..." if len(text) > 100 else text,
                "method": "rule-based",  # Would be "llm" in production
                "timestamp": self._get_timestamp()
            }
            
            if detailed:
                result["details"] = {
                    "positive_score": round(scores["positive"], 3),
                    "negative_score": round(scores["negative"], 3),
                    "neutral_score": round(scores["neutral"], 3),
                    "word_count": len(text.split()),
                    "detected_keywords": self._get_detected_keywords(text)
                }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Sentiment analysis failed: {str(e)}",
                "sentiment": "neutral",
                "confidence": 0.0
            }

    def _analyze_simple(self, text: str) -> tuple:
        """
        Simple rule-based sentiment analysis.
        
        Returns:
            (sentiment, confidence, scores_dict)
        """
        text_lower = text.lower()
        words = set(text_lower.split())
        
        # Count positive/negative matches
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Calculate scores
        total_words = len(words)
        if total_words == 0:
            return ("neutral", 0.5, {"positive": 0.33, "negative": 0.33, "neutral": 0.34})
        
        positive_score = min(positive_count / max(total_words / 10, 1), 1.0)
        negative_score = min(negative_count / max(total_words / 10, 1), 1.0)
        neutral_score = 1.0 - max(positive_score, negative_score)
        
        # Normalize scores
        total_score = positive_score + negative_score + neutral_score
        if total_score > 0:
            positive_score /= total_score
            negative_score /= total_score
            neutral_score /= total_score
        
        # Determine sentiment
        if positive_score > negative_score and positive_score > neutral_score:
            sentiment = "positive"
            confidence = positive_score
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment = "negative"
            confidence = negative_score
        else:
            sentiment = "neutral"
            confidence = neutral_score
        
        return (
            sentiment,
            confidence,
            {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score
            }
        )

    def _get_detected_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract detected positive/negative keywords."""
        text_lower = text.lower()
        
        detected_positive = [kw for kw in self.positive_keywords if kw in text_lower]
        detected_negative = [kw for kw in self.negative_keywords if kw in text_lower]
        
        return {
            "positive": detected_positive[:5],  # Top 5
            "negative": detected_negative[:5]
        }

    def _get_timestamp(self) -> str:
        """Get ISO format timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        return [
            "sentiment_analysis",
            "text_classification",
            "emotion_detection",
            "confidence_scoring",
            "multilingual_support"
        ]

    def to_schema(self, format: str = "microsoft") -> Dict[str, Any]:
        """
        Export agent schema in specified format.
        
        Supports: microsoft, langchain, semantic_kernel, openai
        """
        base_schema = {
            "name": self.name,
            "description": "Text sentiment analysis with multilingual support",
            "version": self.version,
            "model": self.model,
            "temperature": self.temperature,
            "capabilities": self.get_capabilities(),
            "supported_languages": ["en", "fr", "es", "de"],
        }
        
        if format == "microsoft":
            return {
                "agent_type": "SentimentAnalyzer",
                "metadata": base_schema,
                "input_schema": {
                    "text": "string (required)",
                    "detailed": "boolean (optional)"
                },
                "output_schema": {
                    "sentiment": "string (positive/negative/neutral)",
                    "confidence": "float (0.0-1.0)",
                    "keywords": "list[string] (if detailed=true)"
                }
            }
        elif format == "langchain":
            return {
                "name": self.name,
                "description": base_schema["description"],
                "parameters": {
                    "text": {"type": "string", "required": True},
                    "detailed": {"type": "boolean", "default": False}
                }
            }
        elif format == "semantic_kernel":
            return {
                "name": self.name.replace("-", "_"),
                "description": base_schema["description"],
                "input_variables": ["text", "detailed"],
                "output_variable": "sentiment_result"
            }
        elif format == "openai":
            return {
                "type": "function",
                "function": {
                    "name": self.name.replace("-", "_"),
                    "description": base_schema["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to analyze"},
                            "detailed": {"type": "boolean", "description": "Return detailed analysis"}
                        },
                        "required": ["text"]
                    }
                }
            }
        else:
            return base_schema

