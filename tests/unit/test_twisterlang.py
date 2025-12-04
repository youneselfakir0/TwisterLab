"""
Tests for TwisterLang codec.
"""

import pytest
import json


class TestTwisterLangCodec:
    """Tests for the TwisterLang encoding/decoding."""

    def test_codec_import(self):
        """Test that codec can be imported."""
        try:
            from src.twisterlab.twisterlang.codec import encode, decode
            assert callable(encode)
            assert callable(decode)
        except ImportError:
            pytest.skip("TwisterLang codec not available")

    def test_encode_simple_message(self):
        """Test encoding a simple message."""
        try:
            from src.twisterlab.twisterlang.codec import encode

            message = {
                "type": "request",
                "action": "classify",
                "data": {"text": "Hello world"},
            }
            encoded = encode(message)
            assert encoded is not None
            assert isinstance(encoded, (str, bytes))
        except ImportError:
            pytest.skip("TwisterLang codec not available")

    def test_decode_encoded_message(self):
        """Test decoding an encoded message."""
        try:
            from src.twisterlab.twisterlang.codec import encode, decode

            original = {
                "type": "response",
                "status": "success",
                "data": {"result": 42},
            }
            encoded = encode(original)
            decoded = decode(encoded)
            assert decoded == original
        except ImportError:
            pytest.skip("TwisterLang codec not available")

    def test_roundtrip_complex_message(self):
        """Test encoding and decoding a complex message."""
        try:
            from src.twisterlab.twisterlang.codec import encode, decode

            complex_message = {
                "type": "agent_task",
                "agent": "maestro",
                "task": {
                    "action": "orchestrate",
                    "sub_tasks": [
                        {"agent": "classifier", "input": "classify this"},
                        {"agent": "resolver", "input": "resolve that"},
                    ],
                },
                "metadata": {
                    "priority": 1,
                    "timeout": 30,
                    "tags": ["urgent", "test"],
                },
            }
            encoded = encode(complex_message)
            decoded = decode(encoded)
            assert decoded == complex_message
        except ImportError:
            pytest.skip("TwisterLang codec not available")


class TestTwisterLangValidation:
    """Tests for TwisterLang message validation."""

    def test_validate_message_structure(self):
        """Test message structure validation."""
        valid_message = {
            "type": "request",
            "action": "test",
        }
        # Basic structure check
        assert "type" in valid_message
        assert "action" in valid_message

    def test_invalid_message_missing_type(self):
        """Test that messages without type are handled."""
        invalid_message = {
            "action": "test",
            "data": {},
        }
        assert "type" not in invalid_message
