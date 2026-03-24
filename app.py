import os
import json
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
        pass # Streamlit Cloud shouldn't run bash directly
        
    def web_research(self, query):
        return deep_research(query)
        
    def process_message(self, user_message: str):
        self.messages.append({"role": "user", "content": user_message})
        
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
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
            
            if not tool_calls:
                return response_message.content
                
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                if function_name == "execute_bash":
                    tool_output = "Disabled in cloud"
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


