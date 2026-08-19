# 🐾 OpenClaw Accessibility Agent Hub

A unified, modern web portal integrating the **AccessPath Student Hub** and the **Accessibility Configurator** with a secure local/cloud Python AI agent backend.

## 🚀 Easy Start (Run Instantly)

We have provided an interactive launcher script that does all the setup and startup for you automatically:

```bash
python run.py
```

### What `run.py` does:
1. Checks for and installs any missing Python dependencies (`requirements.txt`).
2. Configures a local `.env` file and prompts you to enter your `GEMINI_API_KEY` if it isn't configured.
3. Automatically launches the Flask server.
4. Opens the beautiful web UI in your default web browser (`http://127.0.0.1:5000`).

---

## 🛠️ Manual Installation & Startup

If you prefer to start the server manually, follow these steps:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your API credentials:
   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   FLASK_SECRET_KEY=change-me-to-something-secure
   ```
3. **Start the Flask Server**:
   ```bash
   python server.py
   ```
4. **Access the App**:
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 🔒 Security & Bug Fixes Over the Old GitHub Version

This version resolves the key failures of the previous GitHub code:

1. **Obsolete Model 404 Fix**: 
   The old code hardcoded the decommissioned `gemini-2.0-flash` model, resulting in a startup/interaction crash (404 Not Found error). This has been upgraded to utilize the stable `gemini-2.5-flash` model by default.
   
2. **True Human-in-the-Loop (HITL) Execution**: 
   In the old code, commands that required approval (`NEEDS_APPROVAL`) were automatically run anyway with just a printed warning. In this unified version, the Flask server suspends caution-level commands in a pending state, rendering a **Security Halt** overlay on the UI. The command will **never** run unless you explicitly click **Approve**.

3. **Unified Server Structure**: 
   Integrates static frontend dashboards (like Speech Accessibility, Overlay Generator, and Finders) directly into the Flask asset pipeline, removing configuration hurdles when opening separate frontend instances.
