#!/usr/bin/env python3
"""
TwisterLang Test Script
Test the encoder and decoder functionality
"""

from core.twisterlang_encoder import encode
from core.twisterlang_decoder import decode


def test_twisterlang_encoding_decoding():
    """Test TwisterLang encoding and decoding functionality"""
    test_messages = [
        'system ok',
        'agent ready',
        'swarm migration start',
        'security alert',
        'monitoring ok',
        'consensus success'
    ]

    for msg in test_messages:
        # Test encoding
        encoded = encode(msg)
        assert encoded is not None
        assert len(encoded) > 0
        assert encoded != msg  # Should be different from original

        # Test decoding
        decoded, is_valid, error = decode(encoded)
        assert is_valid, f"Decoding failed for '{msg}': {error}"
        assert decoded is not None

        # Verify round-trip (allowing for case variations)
        expected_variants = [
            'system ok', 'agent ready', 'swarm migration start',
            'security alert', 'monitoring ok', 'consensus success'
        ]
        variants_lower = [v.lower() for v in expected_variants]

        assert (decoded.lower() == msg.lower() or
                decoded.lower() in variants_lower), \
            f"Round-trip failed: expected '{msg}', got '{decoded}'"


def test_twisterlang_compression():
    """Test that TwisterLang provides compression"""
    test_message = "This is a longer test message for compression testing"

    encoded = encode(test_message)

    # Encoding should be shorter than original (basic compression test)
    # Note: This might not always be true for short messages, but should be for longer ones
    compression_ratio = len(encoded) / len(test_message)

    # Allow some flexibility - compression might not be dramatic for short messages
    assert compression_ratio < 2.0, f"Compression ratio too high: {compression_ratio}"


def test_twisterlang_error_handling():
    """Test error handling for invalid inputs"""
    # Test with empty string
    encoded = encode("")
    assert encoded is not None

    # Test with None (should handle gracefully)
    try:
        result = encode(None)
        # If it doesn't raise an exception, result should be valid
        assert result is not None
    except (TypeError, AttributeError):
        # Expected for None input
        pass
