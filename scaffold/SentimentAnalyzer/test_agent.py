import pytest
from ..sentimentanalyzer import SentimentAnalyzer

def test_sentimentanalyzer():
    agent = SentimentAnalyzer()
    assert agent is not None
