#!/usr/bin/env python3
"""
run.py
An interactive launcher script that checks dependencies, configures API keys,
starts the Flask server, and opens the application in your web browser.
"""
import os
import sys
import subprocess
import webbrowser
import time

def check_and_install_dependencies():
    print("🔍 Checking dependencies...")
    try:
        import flask
        import openai
        import dotenv
        print("✅ Core dependencies already installed.")
    except ImportError:
        print("📥 Installing missing dependencies from requirements.txt...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed successfully!")
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("Please run: pip install -r requirements.txt manually.")
            sys.exit(1)

def configure_env_file():
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating a new .env configuration file...")
        with open(env_file, "w") as f:
            f.write("# Environment Configuration\nFLASK_SECRET_KEY=dev-insecure-key-change-me\n")
    
    # Check for GEMINI_API_KEY
    has_gemini = False
    with open(env_file, "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=" in content:
            has_gemini = True

    if not has_gemini:
        print("\n🔑 The agent requires a Gemini API Key to communicate with the AI model.")
        print("You can get a free key from: https://aistudio.google.com/")
        try:
            key = input("Enter your GEMINI_API_KEY: ").strip()
            if key:
                with open(env_file, "a") as f:
                    f.write(f"\nGEMINI_API_KEY={key}\n")
                print("✅ Key saved to .env file.")
            else:
                print("⚠️ Warning: No key entered. The AI engine might not function correctly.")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ Environment configuration skipped.")

def launch_server():
    print("\n🚀 Starting the OpenClaw Accessibility Skill Agent Hub...")
    
    # We will launch server.py as a subprocess
    server_process = None
    try:
        # Start server
        server_process = subprocess.Popen([sys.executable, "server.py"])
        
        # Give the server 2 seconds to start up
        time.sleep(2)
        
        # Open web browser
        url = "http://127.0.0.1:5000"
        print(f"🌐 Opening {url} in your default browser...")
        webbrowser.open(url)
        
        # Keep launcher running until server exits
        server_process.wait()
    except KeyboardInterrupt:
        print("\n👋 Stopping the server...")
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server_process.kill()
        print("😴 Server stopped.")
    except Exception as e:
        print(f"❌ Error launching server: {e}")
        if server_process:
            server_process.kill()

if __name__ == "__main__":
    # Ensure working directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    check_and_install_dependencies()
    configure_env_file()
    launch_server()
