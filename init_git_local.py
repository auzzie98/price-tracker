#!/usr/bin/env python
import os
import sys

repo_dir = r"c:\Users\auzzi\OneDrive\Desktop\price-tracker"
os.chdir(repo_dir)

# Read all files to commit, excluding data, venv, etc.
exclude_dirs = {'venv', '.venv', 'data'}
exclude_exts = {'.db', '.sqlite', '.sqlite3', '.csv'}

files_to_commit = []
for root, dirs, files in os.walk(repo_dir):
    # Skip excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
    
    for f in files:
        filepath = os.path.join(root, f)
        
        # Skip excluded extensions
        if any(f.endswith(ext) for ext in exclude_exts):
            continue
        
        # Skip .git directory
        if '.git' in filepath:
            continue
        
        # Skip the init_git.py script we just created
        if 'init_git.py' in filepath:
            continue
        
        files_to_commit.append(filepath)

print(f"Found {len(files_to_commit)} files to commit")

# Initialize git repo
os.system("git init")
os.system("git add .")
os.system('git commit -m "Initial price-tracker repository"')

# Print git status
os.system("git status")