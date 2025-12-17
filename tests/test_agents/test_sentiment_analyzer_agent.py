"""
Unit tests for SentimentAnalyzerAgent.
"""

import pytest
from twisterlab.agents.real.real_sentiment_analyzer_agent import SentimentAnalyzerAgent


@pytest.mark.unit
@pytest.mark.asyncio
class TestSentimentAnalyzerAgent:
    """Test suite for SentimentAnalyzerAgent."""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return SentimentAnalyzerAgent()

    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "sentiment-analyzer"
        assert agent.display_name == "Sentiment Analyzer"
        assert agent.model == "llama-3.2"
        assert agent.temperature == 0.3

    async def test_positive_sentiment(self, agent):
        """Test detection of positive sentiment."""
        result = await agent.execute("This is an excellent and amazing product! I love it!")
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5
        assert "analyzed_text" in result
        assert "error" not in result

    async def test_negative_sentiment(self, agent):
        """Test detection of negative sentiment."""
        result = await agent.execute("This is terrible and awful. I hate it completely.")
        
        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.5
        assert "analyzed_text" in result

    async def test_neutral_sentiment(self, agent):
        """Test detection of neutral sentiment."""
        result = await agent.execute("The product was delivered on Tuesday.")
        
        assert result["sentiment"] == "neutral"
        assert "confidence" in result
        assert "analyzed_text" in result

    async def test_empty_text(self, agent):
        """Test handling of empty text."""
        result = await agent.execute("")
        
        assert "error" in result
        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.0

    async def test_detailed_analysis(self, agent):
        """Test detailed analysis mode."""
        result = await agent.execute(
            "This product is great and wonderful!",
            context={"detailed": True}
        )
        
        assert "details" in result
        assert "positive_score" in result["details"]
        assert "negative_score" in result["details"]
        assert "neutral_score" in result["details"]
        assert "detected_keywords" in result["details"]

    async def test_french_text(self, agent):
        """Test sentiment analysis with French text."""
        result = await agent.execute("C'est g├⌐nial et super formidable!")
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0

    async def test_multilingual_keywords(self, agent):
        """Test that French keywords are detected."""
        text = "C'est mauvais et catastrophique"
        result = await agent.execute(text, context={"detailed": True})
        
        assert result["sentiment"] == "negative"
        detected = result["details"]["detected_keywords"]["negative"]
        assert any(kw in ["mauvais", "catastrophique"] for kw in detected)

    async def test_long_text_truncation(self, agent):
        """Test that long text is truncated in response."""
        long_text = "excellent " * 50  # 450 chars
        result = await agent.execute(long_text)
        
        assert len(result["analyzed_text"]) <= 103  # 100 + "..."

    async def test_capabilities(self, agent):
        """Test agent capabilities list."""
        caps = agent.get_capabilities()
        
        assert "sentiment_analysis" in caps
        assert "text_classification" in caps
        assert "confidence_scoring" in caps
        assert len(caps) >= 4

    async def test_schema_export_microsoft(self, agent):
        """Test Microsoft Agent Framework schema export."""
        schema = agent.to_schema(format="microsoft")
        
        # Check top-level structure
        assert "agent_type" in schema
        assert schema["agent_type"] == "SentimentAnalyzer"
        assert "metadata" in schema
        assert "input_schema" in schema
        assert "output_schema" in schema
        
        # Check metadata
        metadata = schema["metadata"]
        assert "name" in metadata
        assert metadata["name"] == "sentiment-analyzer"
        assert "capabilities" in metadata
        assert len(metadata["capabilities"]) >= 3

    async def test_error_handling(self, agent):
        """Test error handling for edge cases."""
        # None as task should be handled gracefully
        result = await agent.execute(None)
        assert "error" in result or result["sentiment"] == "neutral"

    async def test_mixed_sentiment(self, agent):
        """Test text with mixed positive and negative words."""
        result = await agent.execute(
            "The product is great but the service is terrible.",
            context={"detailed": True}
        )
        
        # Should detect both sentiment types
        details = result["details"]
        assert details["positive_score"] > 0
        assert details["negative_score"] > 0

    async def test_timestamp_format(self, agent):
        """Test that timestamp is in ISO format."""
        result = await agent.execute("Test text")
        
        assert "timestamp" in result
        # Verify ISO format (contains 'T' and timezone)
        assert "T" in result["timestamp"]
        assert result["timestamp"].endswith("Z") or "+" in result["timestamp"]
