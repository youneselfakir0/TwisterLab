# twisterlang_lint.py

import json
import os

from twisterlang.codec import validate_message
from twisterlang.message.schema import load_schema


class TwisterLangLint:
    def __init__(self, schema_path):
        self.schema = load_schema(schema_path)

    def lint_file(self, file_path):
        with open(file_path, "r") as file:
            messages = json.load(file)

        errors = []
        for message in messages:
            validation_result = validate_message(message, self.schema)
            if not validation_result["valid"]:
                errors.append(
                    {"message": validation_result["error"], "message_content": message}
                )

        return errors

    def lint_directory(self, directory_path):
        all_errors = {}
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                errors = self.lint_file(file_path)
                if errors:
                    all_errors[filename] = errors
        return all_errors


if __name__ == "__main__":
    lint = TwisterLangLint("src/twisterlab/twisterlang/twisterlang.message.schema.json")
    errors = lint.lint_directory("path/to/twisterlang/messages")
    if errors:
        for file, file_errors in errors.items():
            print(f"Errors in {file}:")
            for error in file_errors:
                print(f" - {error['message']}: {error['message_content']}")
    else:
        print("No linting errors found.")
