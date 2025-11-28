import argparse
import json

from twisterlang.codec import build_message, validate_message


def main():
    parser = argparse.ArgumentParser(
        description="TwisterLang CLI for message operations."
    )
    parser.add_argument(
        "operation",
        choices=["build", "validate"],
        help="Operation to perform on TwisterLang messages.",
    )
    parser.add_argument(
        "--message", type=str, help="JSON string of the message to build or validate."
    )
    parser.add_argument(
        "--schema", type=str, help="Path to the schema file for validation."
    )

    args = parser.parse_args()

    if args.operation == "build":
        if not args.message:
            print("Error: --message is required for build operation.")
            return
        try:
            message_dict = json.loads(args.message)
            encoded_message = build_message(message_dict)
            print(f"Encoded Message: {encoded_message}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON string provided for --message.")

    elif args.operation == "validate":
        if not args.message or not args.schema:
            print("Error: --message and --schema are required for validate operation.")
            return
        try:
            message_dict = json.loads(args.message)
            with open(args.schema, "r") as schema_file:
                schema = json.load(schema_file)
            is_valid = validate_message(message_dict, schema)
            print(f"Message is valid: {is_valid}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON string provided for --message.")
        except FileNotFoundError:
            print(f"Error: Schema file not found at {args.schema}.")
        except Exception as e:
            print(f"Error during validation: {e}")


if __name__ == "__main__":
    main()
