#!/usr/bin/env python3
"""
Clean null bytes from Python files
"""
import os

files_to_clean = [
    'core/twisterlang_encoder.py',
    'core/twisterlang_decoder.py',
    'core/twisterlang_sync.py',
    'tests/test_twisterlang.py',
    'tests/test_twisterlang_sync.py'
]

for file_path in files_to_clean:
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            content = f.read()
        if b'\x00' in content:
            print(f"Cleaning null bytes from {file_path}")
            cleaned = content.replace(b'\x00', b'')
            with open(file_path, 'wb') as f:
                f.write(cleaned)
        else:
            print(f"No null bytes in {file_path}")
    else:
        print(f"File not found: {file_path}")