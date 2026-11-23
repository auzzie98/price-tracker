#!/usr/bin/env python
import subprocess
import os
import sys

def main():
    repo_dir = r"c:\Users\auzzi\OneDrive\Desktop\price-tracker"
    os.chdir(repo_dir)
    
    # Initialize git repo
    result = subprocess.run(["git", "init"], capture_output=True, text=True)
    print(f"git init: stdout={result.stdout}, stderr={result.stderr}")
    
    # Add remote
    result = subprocess.run(["git", "remote", "add", "origin", "https://github.com/auzzie98/price-tracker.git"], 
                          capture_output=True, text=True)
    print(f"remote add: stdout={result.stdout}, stderr={result.stderr}")
    
    # Add all files
    result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
    print(f"git add: stdout={result.stdout}, stderr={result.stderr}")
    
    # Commit
    result = subprocess.run(["git", "commit", "-m", "Initial commit"], capture_output=True, text=True)
    print(f"git commit: stdout={result.stdout}, stderr={result.stderr}")
    
    # Push
    result = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
    print(f"git push: stdout={result.stdout}, stderr={result.stderr}")

if __name__ == "__main__":
    main()