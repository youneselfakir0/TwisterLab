"""
Pytest configuration and fixtures for TwisterLab tests.
"""

import sys
from pathlib import Path

import pytest

# Ensure 'src' is on sys.path for imports
ROOT = Path(__file__).resolve().parents[1]  # Go up to project root
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_agent_config():
    """Provide sample agent configuration for tests."""
    return {
        "name": "test_agent",
        "display_name": "Test Agent",
        "description": "A test agent",
        "model": "llama-3.2",
        "temperature": 0.7,
    }


@pytest.fixture
def sample_twisterlang_message():
    """Provide sample TwisterLang message for tests."""
    return {
        "type": "request",
        "action": "classify",
        "data": {"text": "Hello world"},
        "metadata": {"priority": 1},
    }
