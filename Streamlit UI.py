import os
from dotenv import load_dotenv
load_dotenv(override=True)

import streamlit as st
from app import SkillAgent

# Configure basic settings
st.set_page_config(page_title="OpenClaw-style Agent", page_icon="🐾")
st.title("🐾 OpenClaw Skill Agent")

with st.sidebar:
    api_status = os.getenv('GEMINI_API_KEY')
    if api_status and str(api_status).startswith("AIza"):
        st.success("✅ Secret Key Loaded")
    else:
        st.error("❌ Key Not Found in .env")
        
    if st.button("🔄 Hard Reset Agent Memory"):
        st.session_state.clear()
        st.rerun()

st.markdown("A local LLM agent with Bash Execution and Web Research skills.")

# Initialize or Re-initialize the stateful skill agent if the environment key was updated
current_api_key = os.getenv('GEMINI_API_KEY')
if "agent" not in st.session_state or st.session_state.agent.client.api_key != current_api_key:
    # Build a strictly new agent with the freshest environment vars
    st.session_state.agent = SkillAgent()

# Render existing conversation history
for msg in st.session_state.agent.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant" and msg.get("content"):
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
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
                st.markdown(response)
                # Note: Tool outputs generated in this loop iteration won't visibly instantly append code blocks above
                # the st.markdown(response) unless we re-render, so Streamlit will naturally re-render them correctly 
                # on the *next* rerun. But to fix the current rerun state, we rerun immediately.
                st.rerun()
            except Exception as e:
                st.error(f"Error communicating with Agent: {str(e)}")
