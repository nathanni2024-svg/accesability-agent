import os
import streamlit as st
from app import SkillAgent

# Configure the visual website
st.set_page_config(page_title="OpenClaw Agent", page_icon="🐾")
st.title("🐾 OpenClaw Skill Agent")

# Memory Management Tracker
if "agent" not in st.session_state:
    st.session_state.agent = SkillAgent()

# Draw the chat history on the screen
for msg in st.session_state.agent.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant" and msg.get("content"):
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    elif msg["role"] == "tool":
        with st.expander(f"⚙️ Tool Output: {msg.get('name', 'tool')}", expanded=False):
            st.code(msg.get("content", ""))

# The Main Text Box Input
if prompt := st.chat_input("Ask the agent to do something..."):
    # Immediately render what the user typed on the screen
    with st.chat_message("user"):
        st.markdown(prompt)

    # Output area for the agent's robot response
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                response = st.session_state.agent.process_message(prompt)
                if response:
                    st.markdown(response)
                st.rerun()
            except Exception as e:
                st.error(f"Error communicating with Agent: {str(e)}")

                response = st.session_state.agent.process_message(prompt)
                if response:
                    st.markdown(response)
                st.rerun()
            except Exception as e:
                st.error(f"Error communicating with Agent: {str(e)}")
