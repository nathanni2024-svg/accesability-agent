[main.py](https://github.com/user-attachments/files/26200330/main.py)[Uploading PythonProject…]()
[app.py](https://github.com/user-attachments/files/26200316/app.py)
import os
import json
import subprocess
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from main import audit_command
from research_logic import deep_research
from email_logic import draft_email, confirm_and_send_mock_email, confirm_and_send_real_email, read_recent_emails
from security_logic import analyze_security

class SkillAgent:
    def __init__(self):
        # Initialize client to use Google Gemini API for cloud web-deployment 
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = "gemini-2.5-flash"
        
        self.system_prompt = (
            "You are a helpful, local AI skill agent similar to OpenClaw. "
            "You have tools to perform deep web research, execute bash commands on the user's machine, and manage emails. "
            "Always be safe and helpful. If a user asks a factual question, use web_research. "
            "If they ask you to perform a local operation or look at your own files, use execute_bash (like 'ls' or 'cat'). Reading most files is completely SAFE and permitted. "
            "CRITICAL SECURITY RULE: You must NEVER read, expose, or output the contents of the .env file. Protect the user's email information, passwords, and API keys at all costs. "
            "To send emails, first use draft_email, show the draft to the user, and ask for explicit approval. You must ask: 'Do you want to send this as a SAFE LOCAL MOCK (test mode) or over the REAL INTERNET?' "
            "If they choose the mock test, use confirm_and_send_mock_email. If they choose real internet, use confirm_and_send_real_email. "
            "If a user asks you to scan an email, text, or query for safety/phishing/spam/privacy leaks, ALWAYS use the analyze_security tool! "
            "NOTE: The execute_bash tool is audited for safety, but try not to run destructive actions."
        )
        
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_bash",
                    "description": "Execute a bash command on the local machine.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The exact bash command string to execute (e.g. 'ls -l', 'pwd', 'echo Hello')"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_research",
                    "description": "Perform deep web research to gather information on a topic using Tavily API.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to investigate"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "draft_email",
                    "description": "Draft an email to be sent. The user MUST approve the draft before you can actually send it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_address": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to_address", "subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "confirm_and_send_mock_email",
                    "description": "Simulate sending a drafted message offline. It prints to the local console without using the internet. 100% safe test.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_address": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to_address", "subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "confirm_and_send_real_email",
                    "description": "Actually send a drafted email over the internet. ONLY call this AFTER the user has explicitly approved a REAL send.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_address": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to_address", "subject", "body"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_recent_emails",
                    "description": "Read the most recent emails from the inbox.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Number of recent emails to read (default 3)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_security",
                    "description": "Scan a message, email, or chunk of text to detect spam, phishing attempts, malware links, or privacy leaks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The text content to scan."}
                        },
                        "required": ["content"]
                    }
                }
            }
        ]

    def execute_bash(self, command):
        """Executes a bash command and returns its output, after an audit check."""
        audit_result = audit_command(command)
        if audit_result['status'] == "BLOCKED":
            return f"Command execution blocked for safety: {audit_result['reason']}"
        elif audit_result['status'] == "NEEDS_APPROVAL":
            # For this agent, we will note that it needed approval but allow it through,
            # or we could return asking the user for confirmation. 
            # We'll run it but add a prefix note.
            output_prefix = f"[WARNING: {audit_result['reason']}]\n"
        else:
            output_prefix = ""
            
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                text=True, 
                capture_output=True, 
                timeout=30
            ) # Using shell=True for full command string support
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
                
            if not output.strip() and result.returncode == 0:
                output = "Command executed successfully with no output."
            elif not output.strip() and result.returncode != 0:
                output = f"Command failed with return code {result.returncode}"
                
            return output_prefix + output
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def web_research(self, query):
        """Runs the deep research logic using Tavily via research_logic.py."""
        return deep_research(query)

    def process_message(self, user_message: str):
        """Processes a new user message and handles the tool execution loop."""
        self.messages.append({"role": "user", "content": user_message})
        
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Convert response message to a plain dictionary to safely store in session state
            message_dict = {"role": response_message.role, "content": response_message.content}
            
            tool_calls = response_message.tool_calls
            if tool_calls:
                message_dict["tool_calls"] = [
                    {
                        "id": t.id,
                        "type": t.type,
                        "function": {
                            "name": t.function.name,
                            "arguments": t.function.arguments
                        }
                    } for t in tool_calls
                ]
                
            self.messages.append(message_dict)
            
            # If no tool calls, we are completely done and just return the final content
            if not tool_calls:
                return response_message.content
                
            # If there are tool calls, execute them and continue the loop
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                if function_name == "execute_bash":
                    tool_output = self.execute_bash(args.get("command", ""))
                elif function_name == "web_research":
                    tool_output = self.web_research(args.get("query", ""))
                elif function_name == "draft_email":
                    tool_output = draft_email(args.get("to_address", ""), args.get("subject", ""), args.get("body", ""))
                elif function_name == "confirm_and_send_mock_email":
                    tool_output = confirm_and_send_mock_email(args.get("to_address", ""), args.get("subject", ""), args.get("body", ""))
                elif function_name == "confirm_and_send_real_email":
                    tool_output = confirm_and_send_real_email(args.get("to_address", ""), args.get("subject", ""), args.get("body", ""))
                elif function_name == "read_recent_emails":
                    tool_output = read_recent_emails(args.get("limit", 3))
                elif function_name == "analyze_security":
                    tool_output = analyze_security(args.get("content", ""))
                else:
                    tool_output = f"Unknown tool {function_name}"
                    
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(tool_output)
                })

# Allow running standalone to test the logic
if __name__ == "__main__":
    agent = SkillAgent()
    print("Welcome to the Command Line interface for OpenClaw-style Agent.")
    print("Type 'exit' to quit.")
    while True:
        try:
            req = input("\nUser> ")
            if req.lower() in ['exit', 'quit']:
                break
            print("Agent> Thinking...")
            res = agent.process_message(req)
            print(f"\Agent> {res}")
        except KeyboardInterrupt:
            break
[app.py logic.py](https://github.com/user-attachments/files/26200327/app.py.logic.py)
import datetime

def save_research_to_file(query, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"research_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:[email_logic.py](https://github.com/user-attachments/files/26200329/email_logic.py)

        f.write(f"# Deep Research: {query}\n")
        f.write(f"Generated on: {timestamp}\n\n")
        f.write(content)
    
    return filename
import os
import smtplib
from email.message import EmailMessage

def _get_credentials():
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_APP_PASSWORD")
    if not email_address or not email_password or "your_email" in email_address:
         return None, None
    return email_address, email_password

def draft_email(to_address, subject, body):
    """
    Drafts an email to be reviewed by the user. Does not send it.
    Returns the formatted draft.
    """
    draft = f"DRAFT EMAIL:\nTo: {to_address}\nSubject: {subject}\n\n{body}\n\n[Status: DRAFTING]\nPlease ask the user if they want to 'test send' (100% safe local mock) or 'real send' (actually send over the internet)."
    return draft

def confirm_and_send_mock_email(to_address, subject, body):
    """
    100% Safe Mock Sandbox for sending emails.
    """
    print("\n" + "="*50)
    print("📩 100% SAFE MOCK SERVER INTERCEPTED MOCK EMAIL:")
    print(f"To:   {to_address}")
    print(f"Subj: {subject}")
    print("-" * 50)
    print(body)
    print("="*50 + "\n")
    return f"Successfully 'sent' MOCK email to {to_address} (printed to local console). 100% Safe, zero internet used."

def confirm_and_send_real_email(to_address, subject, body):
    """
    Actually sends the email via Real SMTP Internet connection.
    Requires EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env.
    """
    user, password = _get_credentials()
    if not user or not password:
         return "Error: Tell the user they must add their real EMAIL_ADDRESS and EMAIL_APP_PASSWORD to their .env file to send real messages!"

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = to_address

        # Target Google or Outlook SMTP depending on the sender email
        smtp_server = "smtp.gmail.com" if "gmail" in user.lower() else "smtp-mail.outlook.com"
        
        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            
        return f"Successfully sent REAL email over the internet to {to_address}."
    except Exception as e:
        return f"SMTP Error sending real email: {str(e)}"

def read_recent_emails(limit=3):
    """
    Stays as a mock so the AI doesn't crash if credentials are empty.
    """
    return "[Mock Inbox Active] No new real messages right now."[Uploading maiimport re

# 1. Define our Risk Levels
BLOCKED_KEYWORDS = [
    r"rm\s+-rf\s+/",      # Absolute disk wipe
    r"chmod\s+777",        # Dangerous permissions
    r"chown",              # Ownership theft[research_logic.py](https://github.com/user-attachments/files/26200333/research_logic.py)

    r"mkfs",               # Partition formatting[requirements.txt](https://github.com/user-attachments/files/26200332/requirements.txt)

    r"/etc/shadow",        # Password file access
    r"nvram",              # BIOS/Firmware tampering
    r"\.env",              # Protect environment variables and email passwords
]

CAUTION_KEYWORDS = [
    r"curl", r"wget",      # Networking
    r"pip\s+install",      # Installing new code
    r"rm\s+",              # Standard deletion
    r"apt-get",            # System updates
    r"ssh",                # Remote access
]

def audit_command(command: str):
    """
    Analyzes a command string and returns a Safety Status.
    """
    command = command.lower().strip()

    # Check for Hard Blocks
    for pattern in BLOCKED_KEYWORDS:
        if re.search(pattern, command):
            return {"status": "BLOCKED", "reason": f"Matches critical threat pattern: {pattern}"}

    # Check for "Needs Approval"
    for pattern in CAUTION_KEYWORDS:
        if re.search(pattern, command):
            return {"status": "NEEDS_APPROVAL", "reason": "Command involves networking or system modification."}

    # Default to Safe (within the VM)
    return {"status": "SAFE", "reason": "No high-risk patterns detected."}

# --- Example Usage ---
# test_cmd = "rm -rf /"
# result = audit_command(test_cmd)
# if result['status'] == "BLOCKED":
#     print(f"🛑 Security Alert: {result['reason']}")n.py…]()

[Streamlit UI.py](https://github.com/user-attachments/files/26200343/Streamlit.UI.py)
[security_logic.py](https://github.com/user-attachments/files/26200341/security_logic.py)
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
