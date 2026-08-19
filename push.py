#!/usr/bin/env python3
"""
push.py
A helper script to push the accessibility agent code to GitHub,
avoiding shell globbing errors like "no matches found".
"""
import os
import subprocess
import sys

def main():
    # Ensure working directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 Pushing fixed accessibility agent to GitHub main branch...")
    try:
        # Run git push, connecting stdout/stderr/stdin to the terminal
        result = subprocess.run(
            ["git", "push", "origin", "agents/accessibility-configurator-integration:main"],
            check=True
        )
        print("\n✅ Successfully published updates to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Git push failed (exit code {e.returncode}).")
        print("Please check that you have write access to the repository and are logged in.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
