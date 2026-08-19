import os
from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
import qrcode
import re
from io import BytesIO
from app import SkillAgent
from security_logic import get_local_ip
from knowledge_logic import count_brain_files
from education_logic import analyze_and_graph_scores
import pandas as pd

# Configure basic settings
st.set_page_config(page_title="OpenClaw-style Agent", page_icon="🐾")
st.title("🐾 OpenClaw Skill Agent")

# Initialize or Re-initialize the stateful skill agent if the environment key was updated
if "agent_config" not in st.session_state:
    st.session_state.agent_config = {"provider": "gemini", "model": "gemini-2.5-flash"}

with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    provider = st.selectbox("Model Provider", ["Gemini Cloud", "Ollama (Local M5)"], 
                            index=0 if st.session_state.agent_config["provider"] == "gemini" else 1)
    
    selected_provider = "gemini" if provider == "Gemini Cloud" else "ollama"
    
    if selected_provider == "ollama":
        model_name = st.text_input("Ollama Model", value="qwen2.5:7b")
        st.info("🚀 Running on M5 Neural Engine")
    else:
        model_name = st.text_input("Gemini Model", value="gemini-2.5-flash")
        st.success("☁️ Running on Google Cloud")

    # Change detection for re-init
    if (selected_provider != st.session_state.agent_config["provider"] or 
        model_name != st.session_state.agent_config["model"] or 
        "agent" not in st.session_state):
        
        st.session_state.agent_config = {"provider": selected_provider, "model": model_name}
        with st.spinner("Initializing M5 AI Engine..."):
            st.session_state.agent = SkillAgent(model_provider=selected_provider, custom_model=model_name)
        st.rerun()

    st.markdown("---")
    api_status = os.getenv('GEMINI_API_KEY')
    if api_status and str(api_status).startswith("AIza"):
        st.success("✅ Gemini Key Loaded")
    else:
        if selected_provider == "gemini":
            st.error("❌ Gemini Key Not Found")
        
    if st.button("🔄 Hard Reset Agent Memory"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📱 Secure Mobile Access")
    st.markdown("Scan to connect your phone instantly (no password):")
    
    local_ip = get_local_ip()
    mobile_url = f"http://{local_ip}:8501"
    
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(mobile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1E1E1E", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption=f"Local URL: {mobile_url}")
    
    st.markdown("---")
    st.markdown("### 🧠 AI Brain")
    st.markdown(f"**Permanent Rules:** {count_brain_files()}")
    
    st.markdown("---")
    st.markdown("### 🔗 Hub Connections")
    st.markdown("✅ **Gmail** (Live)")
    st.markdown("✅ **Twitter** (Mock)")
    st.markdown("✅ **Instagram** (Mock)")

    st.markdown("---")
    st.markdown("### 🎓 Teacher Dashboard")
    uploaded_file = st.file_uploader("Upload Class Scores", type=["csv", "txt", "xls", "xlsx"])
    if uploaded_file is not None:
        if getattr(st.session_state, "last_uploaded", None) != uploaded_file.name:
            file_bytes = uploaded_file.getvalue()
            lower_name = uploaded_file.name.lower()
            try:
                if lower_name.endswith((".xls", ".xlsx")):
                    df = pd.read_excel(BytesIO(file_bytes))
                    csv_text = df.to_csv(index=False)
                else:
                    csv_text = None
                    for enc in ['utf-8', 'gbk', 'utf-8-sig', 'utf-16', 'latin-1']:
                        try:
                            csv_text = file_bytes.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    if csv_text is None:
                        raise ValueError("Unsupported text encoding for uploaded score file.")

                response = analyze_and_graph_scores(csv_text)
                st.session_state.agent.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.session_state.agent.messages.append({"role": "assistant", "content": f"Error reading uploaded score file: {str(e)}"})

            st.session_state.last_uploaded = uploaded_file.name
            st.rerun()

st.markdown("A local LLM agent with Bash Execution, Web Research, and Social Media skills.")

# Render existing conversation history
for msg in st.session_state.agent.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            if "I am uploading a data file with class grades" in msg["content"]:
                st.markdown("*(Uploaded a raw data file securely for Smart Extraction & Analysis)*")
            else:
                st.markdown(msg["content"])
    elif msg["role"] == "assistant" and msg.get("content"):
        with st.chat_message("assistant"):
            content = msg["content"]
            graph_match = re.search(r'\[GRAPH:\s*(.*?)\]', content)
            if graph_match:
                img_path = graph_match.group(1)
                clean_content = content.replace(graph_match.group(0), "").strip()
                if clean_content:
                    st.markdown(clean_content)
                if os.path.exists(img_path):
                    st.image(img_path)
            else:
                st.markdown(content)
    elif msg["role"] == "tool":
        # Show tool executions in expanding detail blocks
        with st.expander(f"⚙️ Tool Output: {msg.get('name', 'tool_execution')}", expanded=False):
            st.code(msg.get("content", ""))

# Chat input prompt
if prompt := st.chat_input("Ask the agent to do something... (e.g., 'What files are in this dir?' or 'Research quantum computing')"):
    # Render user prompt immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Output area for agent responses
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                # Blocks synchronously as the agent processes tool logic
                response = st.session_state.agent.process_message(prompt)
                
                graph_match = re.search(r'\[GRAPH:\s*(.*?)\]', response)
                if graph_match:
                    img_path = graph_match.group(1)
                    clean_content = response.replace(graph_match.group(0), "").strip()
                    if clean_content:
                        st.markdown(clean_content)
                    if os.path.exists(img_path):
                        st.image(img_path)
                else:
                    st.markdown(response)
                    
                st.rerun()
            except Exception as e:
                st.error(f"Error communicating with Agent: {str(e)}")
