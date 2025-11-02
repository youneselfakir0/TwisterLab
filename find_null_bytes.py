#!/usr/bin/env python3
"""
Find all Python files with null bytes
"""
import os
import glob

def find_null_bytes():
    python_files = glob.glob('**/*.py', recursive=True)
    for file_path in python_files:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            if b'\x00' in content:
                print(f"Null bytes found in: {file_path}")
                # Clean it
                cleaned = content.replace(b'\x00', b'')
                with open(file_path, 'wb') as f:
                    f.write(cleaned)
                print(f"Cleaned: {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    find_null_bytes()