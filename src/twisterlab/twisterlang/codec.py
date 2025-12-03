import uuid


def build_message(*args, **kwargs):
    """Build a TwisterLang message.

    Supports two calling styles for backwards compatibility:
    - build_message(payload, twisterlang_version, correlation_id)
    - build_message(tool_name=..., args={...}) -> uses default twisterlang_version and a generated correlation_id
    """
    # If used with explicit payload and metadata
    if len(args) >= 3:
        payload, twisterlang_version, correlation_id = args[:3]
        return {
            "twisterlang_version": twisterlang_version,
            "correlation_id": correlation_id,
            "payload": payload,
        }

    # If called with named kwargs (tool_name, args)
    tool_name = kwargs.get("tool_name")
    tool_args = kwargs.get("args")
    if tool_name is not None:
        payload = {"tool_name": tool_name, "args": tool_args}
        return {
            "twisterlang_version": kwargs.get("twisterlang_version", "1.0"),
            "correlation_id": kwargs.get("correlation_id", str(uuid.uuid4())),
            "payload": payload,
        }

    # Last fallback: assume payload provided as kwarg
    payload = kwargs.get("payload")
    if payload is not None:
        return {
            "twisterlang_version": kwargs.get("twisterlang_version", "1.0"),
            "correlation_id": kwargs.get("correlation_id", str(uuid.uuid4())),
            "payload": payload,
        }

    # If provided a single dict argument which already contains twisterlang fields
    if len(args) == 1 and isinstance(args[0], dict):
        arg = args[0]
        if "twisterlang_version" in arg and "correlation_id" in arg:
            # Extract payload data from common key names
            inner_payload = (
                arg.get("payload")
                or arg.get("data")
                or {
                    k: v
                    for k, v in arg.items()
                    if k not in ("twisterlang_version", "correlation_id")
                }
            )
            return {
                "twisterlang_version": arg["twisterlang_version"],
                "correlation_id": arg["correlation_id"],
                "payload": inner_payload,
            }

    raise TypeError("Invalid parameters for build_message")


def validate_message(message: dict) -> bool:
    required_fields = ["twisterlang_version", "correlation_id", "payload"]
    for field in required_fields:
        if field not in message:
            return False
    return True


def encode_message_to_base64(message):
    import base64
    import json

    message_json = json.dumps(message)
    message_bytes = message_json.encode("utf-8")
    return base64.b64encode(message_bytes).decode("utf-8")


def decode_message_from_base64(encoded_message):
    import base64
    import json

    message_bytes = base64.b64decode(encoded_message)
    message_json = message_bytes.decode("utf-8")
    return json.loads(message_json)
