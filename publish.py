#!/usr/bin/env python3
"""
publish.py
A simple one-click script to initialize Git, commit all files in this directory,
and push/publish them to GitHub, replacing the old code.
"""
import os
import subprocess
import sys

def run_cmd(args):
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(args)}")
        sys.exit(e.returncode)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Initialize git if not already initialized
    if not os.path.exists(".git"):
        print("📁 Initializing new local Git repository...")
        run_cmd(["git", "init"])
        run_cmd(["git", "checkout", "-b", "main"])
        run_cmd(["git", "remote", "add", "origin", "https://github.com/nathanni2024-svg/accesability-agent.git"])
    else:
        print("✅ Local Git repository already initialized.")

    # 2. Stage and commit all files
    print("\n📦 Staging and committing files...")
    run_cmd(["git", "add", "."])
    # Ignore error if there's nothing new to commit
    subprocess.run(["git", "commit", "-m", "Publish merged AccessPath AI Agent Hub from Downloads"])

    # 3. Push to GitHub
    print("\n🚀 Pushing code to GitHub (this will overwrite the old, broken version)...")
    
    # Read token if present in .env
    token = None
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.strip().startswith("GITHUB_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")

    try:
        if token:
            print("🔑 Using GITHUB_TOKEN for authentication...")
            url = f"https://{token}@github.com/nathanni2024-svg/accesability-agent.git"
            subprocess.run(["git", "push", url, "main", "--force"], check=True)
        else:
            # Force-push to main branch to overwrite the old code
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
        print("\n🎉 Success! Your merged project has been published to GitHub!")
    except subprocess.CalledProcessError:
        print("\n❌ Git push failed.")
        print("Please ensure your terminal is logged into GitHub (run 'gh auth login' or enter credentials when prompted).")

if __name__ == "__main__":
    main()
