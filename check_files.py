#!/usr/bin/env python3
"""
Check for null bytes in files
"""


def check_file(filename):
    try:
        with open(filename, "rb") as f:
            content = f.read()
        null_count = content.count(b"\x00")
        if null_count > 0:
            print(f"Found {null_count} null bytes in {filename}")
            # Show first 100 bytes
            print(f"First 100 bytes: {content[:100]}")
        else:
            print(f"No null bytes in {filename}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")


check_file("core/twisterlang_encoder.py")
check_file("core/twisterlang_decoder.py")
check_file("core/twisterlang_sync.py")
