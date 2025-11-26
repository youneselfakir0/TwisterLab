from twisterlab.twisterlang.codec import (
    build_message,
    decode_message_from_base64,
    encode_message_to_base64,
    validate_message,
)


def test_twisterlang_roundtrip():
    # Sample payload for testing
    payload = {
        "twisterlang_version": "1.0",
        "correlation_id": "test-correlation-id",
        "data": {"example_key": "example_value"},
    }

    # Build and validate the message
    message = build_message(payload)
    assert validate_message(message) is True

    # Encode the message to base64
    encoded_message = encode_message_to_base64(message)
    assert isinstance(encoded_message, str)

    # Decode the message from base64
    decoded_message = decode_message_from_base64(encoded_message)
    assert decoded_message == message

    # Validate the decoded message
    assert validate_message(decoded_message) is True


def test_twisterlang_invalid_message():
    # Test with an invalid message
    invalid_message = {
        "twisterlang_version": "1.0",
        "correlation_id": "test-correlation-id",
        # Missing 'data' key
    }

    assert validate_message(invalid_message) is False


def test_twisterlang_empty_message():
    # Test with an empty message
    empty_message = {}
    assert validate_message(empty_message) is False


def test_twisterlang_roundtrip_with_different_data():
    # Test roundtrip with different data
    payload = {
        "twisterlang_version": "1.0",
        "correlation_id": "test-correlation-id-2",
        "data": {"another_key": "another_value"},
    }

    message = build_message(payload)
    assert validate_message(message) is True

    encoded_message = encode_message_to_base64(message)
    decoded_message = decode_message_from_base64(encoded_message)
    assert decoded_message == message
    assert validate_message(decoded_message) is True
