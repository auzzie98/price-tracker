#!/usr/bin/env python
import sys
import re

if len(sys.argv) < 4:
    print("Usage: replace_in_file.py <filename> <old_text> <new_text>")
    sys.exit(1)

filename = sys.argv[1]
old_text = sys.argv[2]
new_text = sys.argv[3]

with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

if old_text in content:
    new_content = content.replace(old_text, new_text)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Replaced '{old_text}' with '{new_text}' in {filename}")
else:
    print(f"ERROR: '{old_text}' not found in {filename}")
    print("Searching for similar patterns...")
    # Try to find the pattern
    if 'approve-button' in content:
        print("Found 'approve-button' in file")
    if 'reject-button' in content:
        print("Found 'reject-button' in file")
    if 'primary-button' in content:
        print("Found 'primary-button' in file")
    if 'submit-button' in content:
        print("Found 'submit-button' in file")