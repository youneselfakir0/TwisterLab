#!/usr/bin/env python3
"""
Diagnose file corruption
"""


def diagnose_file(filename):
    try:
        with open(filename, "rb") as f:
            content = f.read()
        print(f"File {filename}: {len(content)} bytes")
        # Check for null bytes
        null_pos = content.find(b"\x00")
        if null_pos >= 0:
            print(f"First null byte at position {null_pos}")
            print(f"Context: {content[max(0, null_pos-10):null_pos+10]}")
        else:
            print("No null bytes found")

        # Try to decode as UTF-8
        try:
            text = content.decode("utf-8")
            print("UTF-8 decode successful")
        except UnicodeDecodeError as e:
            print(f"UTF-8 decode failed: {e}")

    except Exception as e:
        print(f"Error reading {filename}: {e}")


diagnose_file("core/twisterlang_encoder.py")
diagnose_file("core/__init__.py")
