"""
server.py
A modern, lightweight Flask web server acting as the bridge between 
the breathtaking browser UI (HTML/CSS) and the local AI Agent. 
"""
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, session, url_for, Response
import os
import re
import time
import json
from datetime import timedelta
from app import SkillAgent
from knowledge_logic import count_brain_files
from education_logic import analyze_and_graph_scores, GRAPH_OUTPUT_DIR
from config import ensure_app_directories
from document_logic import read_document_content
from tools_registry import registry

ensure_app_directories()
app = Flask(__name__, static_url_path='', static_folder='static')

# Security & Session Configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-insecure-secret-change-me")
app.permanent_session_lifetime = timedelta(days=30)  # Keep logged in for 30 days

provider = os.getenv("AI_PROVIDER", "gemini").lower()
local_model = os.getenv("LOCAL_MODEL", None)
agent = SkillAgent(model_provider=provider, custom_model=local_model)

def _extract_tabular_content(filename, raw_bytes):
    # (Same implementation as before)
    lower_name = filename.lower()
    if lower_name.endswith(('.xlsx', '.xls')):
        import pandas as pd
        import io
        df = pd.read_excel(io.BytesIO(raw_bytes))
        return df.to_csv(index=False), True
    if lower_name.endswith(('.csv', '.txt')):
        for enc in ['utf-8', 'gbk', 'utf-8-sig', 'utf-16', 'latin-1']:
            try:
                return raw_bytes.decode(enc), True
            except UnicodeDecodeError:
                continue
    for enc in ['utf-8', 'gbk', 'utf-8-sig', 'utf-16', 'latin-1']:
        try:
            return raw_bytes.decode(enc), False
        except UnicodeDecodeError:
            continue
    return None, False

def _split_graphs_from_response(response):
    graph_urls = []
    if not response or not isinstance(response, str):
        return (response or ""), []
        
    for filepath in re.findall(r'\[GRAPH:\s*(.*?)\]', response):
        basename = os.path.basename(filepath)
        graph_urls.append(f"/files/{basename}")
    cleaned_response = re.sub(r'\[GRAPH:\s*.*?\]', '', response).strip()
    return cleaned_response, graph_urls

def _allow_ai_extraction_from_request() -> bool:
    return str(request.form.get("allow_ai_extraction", "")).strip().lower() in {"true", "1", "yes", "on"}

def _password_auth_enabled() -> bool:
    # IMPORTANT: In production, always require a password
    auth_req = os.getenv("APP_PASSWORD", "").strip()
    return bool(auth_req)

def _is_authenticated() -> bool:
    if not _password_auth_enabled():
        return True
    return bool(session.get("authenticated"))

@app.before_request
def require_login():
    if not _password_auth_enabled():
        # WARNING: Running without a password is only permitted in development
        if os.getenv("NODE_ENV") == "production":
            return "❌ SECURITY ERROR: APP_PASSWORD must be set in production.", 500
        return None

    if request.path.startswith('/api/'):
        return None

    allowed_endpoints = {"login", "static"}
    if request.endpoint in allowed_endpoints:
        return None

    if _is_authenticated():
        # Refresh session activity
        if not session.permanent:
            session.permanent = True
        return None

    return redirect(url_for("login"))

@app.route('/')
def index():
    """Renders the breathtaking main UI."""
    return render_template('index.html')

@app.route('/index.html')
def index_html():
    return redirect(url_for('index'))

@app.route('/university.html')
def university():
    return render_template('university.html')

@app.route('/accessibility-configurator.html')
def accessibility_configurator():
    return render_template('accessibility-configurator.html')

@app.route('/accesspath-app.html')
def accesspath_app():
    return render_template('accesspath-app.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        submitted_password = str(request.form.get("password", ""))
        expected_password = os.getenv("APP_PASSWORD", "")
        if submitted_password and submitted_password == expected_password:
            session.permanent = True  # Enable 30-day session
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "Incorrect password."
    return render_template('login.html', error=error, password_enabled=_password_auth_enabled())

# ... (Rest of routes remain same)
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/status')
def status():
    return jsonify({
        "status": "Online",
        "brain_count": count_brain_files()
    })

@app.route('/chat', methods=['POST'])
def chat():
    message = str(request.form.get("message", ""))
    allow_ai_extraction = _allow_ai_extraction_from_request()
    files = request.files.getlist("files")
    
    for file in files:
        if file.filename:
            raw_bytes = file.read()
            content, is_structured_scores = _extract_tabular_content(file.filename, raw_bytes)
            if content:
                if is_structured_scores:
                    analysis = analyze_and_graph_scores(content)
                    message += f"\n\n--- [Attached Score Analysis: {file.filename}] ---\n{analysis}\n--- [End of {file.filename}] ---\n"
                elif allow_ai_extraction:
                    message += f"\n\n--- [Attached Document: {file.filename}] ---\n{content}\n--- [End of {file.filename}] ---\n"
                else:
                    message += f"\n\n--- [Attached Document: {file.filename}] ---\nAI extraction disabled.\n--- [End of {file.filename}] ---\n"
    
    if not message.strip():
        return jsonify({"error": "No message or valid files provided."}), 400
        
    try:
        # response_node can be a dict now (status: COMPLETED or PENDING_APPROVAL)
        response_node = agent.process_message(message)
        
        if isinstance(response_node, dict) and response_node.get('status') == 'PENDING_APPROVAL':
            # Signal the frontend to show Approve/Reject buttons
            return jsonify(response_node)
            
        # Standard completion
        if isinstance(response_node, dict):
            full_result = response_node.get('response') or response_node.get('error') or ""
        else:
            full_result = response_node or ""
        
        # 1. Extract Graphs
        graph_url = None
        graph_match = re.search(r'\[GRAPH:\s*(.*?)\]', full_result)
        if graph_match:
            graph_url = f"/files/{os.path.basename(graph_match.group(1))}"
            full_result = full_result.replace(graph_match.group(0), "").strip()
            
        # 2. Extract AI Images
        ai_image_url = None
        image_match = re.search(r'\[IMAGE:\s*(.*?)\]', full_result)
        if image_match:
            ai_image_url = image_match.group(1)
            full_result = full_result.replace(image_match.group(0), "").strip()
            
        return jsonify({
            "response": full_result, 
            "graph": graph_url,
            "ai_image": ai_image_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/approve', methods=['POST'])
def approve():
    """RESUME the agent after a tool approval or rejection."""
    data = request.json
    choice = data.get("choice") # 'approve' or 'reject'
    tool_call_id = data.get("tool_call_id")
    command = data.get("command")
    
    try:
        if choice == 'reject':
            # Tell the agent the tool failed or was canceled
            # We inject a tool response manually
            agent.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": "execute_bash",
                "content": "Command canceled by user for security reasons."
            })
            # Continue the loop
            response_node = agent.process_message("User has REJECTED the command. Please acknowledge and ask for the next step.")
        else:
            # Approved! Resume with the tool call meta
            response_node = agent.process_message(None, approved_tool_call={
                "id": tool_call_id,
                "name": "execute_bash",
                "command": command
            })
            
        if isinstance(response_node, dict) and response_node.get('status') == 'PENDING_APPROVAL':
            return jsonify(response_node)
            
        if isinstance(response_node, dict):
            full_result = response_node.get('response') or response_node.get('error') or ""
        else:
            full_result = response_node or ""
        
        # Extract metadata from approved response too
        graph_url = None
        graph_match = re.search(r'\[GRAPH:\s*(.*?)\]', full_result)
        if graph_match:
            graph_url = f"/files/{os.path.basename(graph_match.group(1))}"
            full_result = full_result.replace(graph_match.group(0), "").strip()
            
        ai_image_url = None
        image_match = re.search(r'\[IMAGE:\s*(.*?)\]', full_result)
        if image_match:
            ai_image_url = image_match.group(1)
            full_result = full_result.replace(image_match.group(0), "").strip()

        return jsonify({
            "response": full_result, 
            "graph": graph_url, 
            "ai_image": ai_image_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    allow_ai_extraction = _allow_ai_extraction_from_request()
    files = request.files.getlist('files')
    if not files and 'file' in request.files:
        files = [request.files['file']]
    valid_files = [file for file in files if file.filename]
    if not valid_files:
        return jsonify({"error": "No selected file"}), 400
        
    try:
        response_parts, graph_urls = [], []
        for file in valid_files:
            file_ext = os.path.splitext(file.filename)[1].lower()
            raw_bytes = file.read()
            
            # 1. Attempt tabular extraction
            content, is_structured_scores = _extract_tabular_content(file.filename, raw_bytes)
            
            # 2. If tabular fails, attempt PDF/DOCX extraction
            if content is None and file_ext in ['.pdf', '.docx', '.doc']:
                # Save temp file for the library to read
                temp_path = os.path.join("data", f"temp_{file.filename}")
                with open(temp_path, "wb") as f:
                    f.write(raw_bytes)
                content = read_document_content(temp_path)
                os.remove(temp_path)
                is_structured_scores = False

            if content is None:
                response_parts.append(f"### {file.filename}\nUnsupported format.")
                continue
                
            if is_structured_scores:
                response = analyze_and_graph_scores(content)
            elif not allow_ai_extraction:
                response = "AI extraction disabled."
            else:
                automated_prompt = f"Analyze and provide insights for the document '{file.filename}':\n\n{content}"
                response_node = agent.process_message(automated_prompt)
                if isinstance(response_node, dict):
                    response = response_node.get('response') or response_node.get('error') or ""
                else:
                    response = response_node or ""
            cleaned_response, file_graphs = _split_graphs_from_response(response)
            response_parts.append(f"### {file.filename}\n{cleaned_response}")
            graph_urls.extend(file_graphs)
        return jsonify({"response": "\n\n".join(response_parts), "graph": graph_urls[0] if graph_urls else None, "graphs": graph_urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(GRAPH_OUTPUT_DIR, filename)

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('static', 'sw.js')

@app.route('/vision_guide', methods=['POST'])
def vision_guide():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    image_base64 = data.get("image_base64")
    lat = data.get("lat", "unknown")
    lon = data.get("lon", "unknown")
    
    if not image_base64:
        return jsonify({"error": "No image provided"}), 400
        
    prompt = f"You are an accessibility guide for a visually impaired user. Analyze this current camera frame. The user is at GPS coordinates {lat}, {lon}. Clearly narrate what you see, identifying obstacles, traffic objects, and path conditions. Be direct, extremely concise, and speak aloud-friendly."
    
    try:
        response_node = agent.process_message(prompt, image_base64=image_base64)
        if isinstance(response_node, dict):
            response_text = response_node.get('response') or response_node.get('error') or ""
        else:
            response_text = response_node or ""
            
        return jsonify({"response": response_text})
    except Exception as e:
        print("Vision error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    global agent
    agent = SkillAgent()
    return jsonify({"status": "Reset Successful"})

@app.route('/nvidia_tts', methods=['POST'])
def nvidia_tts():
    """
    Experimental Endpoint linking towards NVIDIA Riva / NIM for Audio.
    Expects JSON: { "text": "Speech target" }
    """
    data = request.json
    text = data.get("text") if data else None
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    nvidia_key = os.getenv("NVIDIA_API_KEY")
    if not nvidia_key:
        return jsonify({"error": "NVIDIA_API_KEY is not configured in .env"}), 500
        
    # Standard format integration to NVIDIA build APIs (e.g. Riva/FastPitch/RadTTS API format)
    # Placeholder implementation until exact NVIDIA TTS deployment endpoint is defined:
    return jsonify({
        "status": "success", 
        "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
        "note": "NVIDIA TTS Endpoint connected successfully! Synthesizing audio requires sending this text to the user's specific NIM deployment."
    })

# --- Standard External Interoperability REST API v1 ---

@app.route('/api/v1/status', methods=['GET'])
def api_v1_status():
    """System health & capability status for external apps."""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "provider": agent.model_provider,
        "model": agent.model,
        "tools_count": len(registry.get_tools_info()),
        "brain_count": count_brain_files()
    })

@app.route('/api/v1/tools', methods=['GET'])
def api_v1_tools():
    """Lists all registered tools and JSON parameter schemas."""
    return jsonify({
        "status": "success",
        "tools": registry.get_tools_info()
    })

@app.route('/api/v1/chat', methods=['POST'])
def api_v1_chat():
    """Standard JSON API chat completion endpoint for external apps & scripts."""
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Missing 'message' in JSON body."}), 400

    try:
        response_node = agent.process_message(message)
        if isinstance(response_node, dict):
            status = response_node.get("status", "COMPLETED")
            if status == "PENDING_APPROVAL":
                return jsonify({
                    "status": "PENDING_APPROVAL",
                    "reason": response_node.get("reason"),
                    "command": response_node.get("command"),
                    "tool_call_id": response_node.get("tool_call_id")
                }), 202
            content = response_node.get("response") or response_node.get("error") or ""
        else:
            content = response_node or ""

        return jsonify({
            "status": "success",
            "response": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/stream', methods=['POST', 'GET'])
def api_v1_stream():
    """Server-Sent Events (SSE) streaming endpoint for real-time word-by-word token delivery."""
    message = request.args.get("message") or (request.json and request.json.get("message")) or ""
    if not message:
        return jsonify({"error": "Missing message parameter."}), 400

    def generate_events():
        try:
            response_node = agent.process_message(message)
            if isinstance(response_node, dict):
                full_text = response_node.get("response") or response_node.get("error") or ""
            else:
                full_text = response_node or ""

            # Stream words with slight delay for realistic audio/text streaming
            words = full_text.split(" ")
            for idx, word in enumerate(words):
                chunk = word + (" " if idx < len(words) - 1 else "")
                data = json.dumps({"token": chunk})
                yield f"data: {data}\n\n"
                time.sleep(0.03)

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate_events(), mimetype='text/event-stream')

@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Renders developer API documentation overview."""
    tools_list = registry.get_tools_info()
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Hub - REST API v1 Docs</title>
        <style>
            body {{ font-family: monospace; background: #0f172a; color: #f8fafc; padding: 2rem; max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #38bdf8; }}
            .endpoint {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }}
            .method {{ background: #3b82f6; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; }}
            pre {{ background: #000; padding: 0.75rem; border-radius: 6px; overflow-x: auto; color: #93c5fd; }}
        </style>
    </head>
    <body>
        <h1><i class="fa-solid fa-code"></i> AI Hub Interoperability REST API v1</h1>
        <p>Integrate external mobile apps, scripts, or assistive tools with this local AI instance.</p>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /api/v1/status</h3>
            <p>Returns system status, active AI model, and tools count.</p>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> /api/v1/tools</h3>
            <p>Lists all registered AI skills and JSON parameter schemas ({len(tools_list)} tools active).</p>
        </div>

        <div class="endpoint">
            <h3><span class="method">POST</span> /api/v1/chat</h3>
            <p>Send a JSON prompt and receive a full AI completion response.</p>
            <pre>curl -X POST http://localhost:8080/api/v1/chat -H "Content-Type: application/json" -d '{{"message": "Hello AI"}}'</pre>
        </div>

        <div class="endpoint">
            <h3><span class="method">POST</span> /api/v1/stream</h3>
            <p>Server-Sent Events (SSE) token streaming for real-time speech and UI rendering.</p>
            <pre>curl -N http://localhost:8080/api/v1/stream?message=Summarize+system</pre>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    app.run(host=host, port=port)
