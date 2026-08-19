import os
import time
import json
import subprocess
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from main import audit_command
from research_logic import deep_research
from email_logic import draft_email, confirm_and_send_mock_email, confirm_and_send_real_email, read_recent_emails
from security_logic import analyze_security
from social_logic import check_twitter_dms, check_instagram_dms
from education_logic import analyze_and_graph_scores
from storage_logic import save_message_to_folder
from knowledge_logic import teach_ai, recall_memory
from image_logic import generate_image
from document_logic import read_document_content, summarize_document

class SkillAgent:
    def __init__(self, model_provider="gemini", custom_model=None):
        """
        Initialize the agent with either Gemini (Cloud) or Ollama (Local M5).
        """
        if model_provider == "ollama":
            self.base_url = "http://localhost:11434/v1/"
            self.api_key = "ollama"
            self.model = custom_model or "qwen2.5:7b"
        else:
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.model = custom_model or "gemini-2.5-flash"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.system_prompt = (
            "You are a helpful, local AI skill agent similar to OpenClaw. "
            "You are running on a high-performance Apple M5 chip. "
            "You are also an integrated multi-platform hub capable of managing notifications from Email, Twitter, and Instagram. "
            "You possess native multi-language intelligence. If a user uploads unstructured, messy, or foreign-language grading data, first extract it, translate it, format it internally into a clean CSV (Name,Score), and THEN call the `analyze_and_graph_scores` tool with that CSV. "
            "You act as a Universal Message Sorter. If asked to sort messages, read the recent Emails and DMs, analyze their content/language/context (e.g. 'Spanish Urgent', 'News Updates'), and use `save_message_to_folder` to automatically organize them onto the local disk disk. "
            "You have tools to perform deep web research, execute bash commands on the user's machine, and manage emails, social DMs, and storage. "
            "Always be safe and helpful. If a user asks a factual question, use web_research. "
            "If they ask you to perform a local operation or look at your own files, use execute_bash (like 'ls' or 'cat'). Reading most files is completely SAFE and permitted. "
            "CRITICAL SECURITY RULE: You must NEVER read, expose, or output the contents of the .env file. Protect the user's email information, passwords, and API keys at all costs. "
            "To send emails, first use draft_email. This will create a REAL DRAFT in the user's Gmail account (if configured). Show the draft to the user, and ask for explicit approval. You must ask: 'Do you want to send this as a SAFE LOCAL MOCK (test mode) or over the REAL INTERNET using Gmail API?' "
            "If they choose the mock test, use confirm_and_send_mock_email. If they choose real internet, use confirm_and_send_real_email. "
            "If a user asks you to scan an email, text, or query for safety/phishing/spam/privacy leaks, ALWAYS use the analyze_security tool! "
            "NOTE: The execute_bash tool is audited for safety, but try not to run destructive actions."
        )
        
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # ... (tools definition remains same, but I'll skip to the logic changes)
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
            },
            {
                "type": "function",
                "function": {
                    "name": "check_twitter_dms",
                    "description": "Check the user's Twitter direct messages.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_instagram_dms",
                    "description": "Check the user's Instagram direct messages.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_and_graph_scores",
                    "description": "Analyze student scores from a CSV containing Name and Score columns, and generate a graph.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "csv_content": {"type": "string", "description": "The raw CSV data content to analyze."}
                        },
                        "required": ["csv_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_message_to_folder",
                    "description": "Save an analyzed message to a specific category folder.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "The folder category (e.g., 'Spanish_Urgent', 'Work', 'General')."},
                            "filename": {"type": "string", "description": "The name of the text file to save."},
                            "content": {"type": "string", "description": "The content of the message."}
                        },
                        "required": ["category", "filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "teach_ai",
                    "description": "Save a new permanent system rule, update, or piece of knowledge into the AI's long-term local database. Always use this when the user asks you to permanently remember something, updates your behavior, or gives you a system update.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "A short, descriptive filename/topic (e.g., 'UserPreferences', 'SortingRules')."},
                            "information": {"type": "string", "description": "The detailed context or rule to remember forever."}
                        },
                        "required": ["topic", "information"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_picture",
                    "description": "Create a high-quality picture or art piece based on a text description using DALL-E 3.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "The detailed description of the image to create."}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_document",
                    "description": "Read the full text content of a local document (PDF, DOCX, TXT, MD). Use this to extract data from uploaded files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The local file path to the document."}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_document",
                    "description": "Get a high-level summary and snippet of a document's content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The local file path to the document."}
                        },
                        "required": ["path"]
                    }
                }
            }
        ]

    def execute_bash(self, command, approved=False):
        """Executes a bash command, strictly checking for safety and requesting approval for CAUTION patterns."""
        audit_result = audit_command(command)
        
        if audit_result['status'] == "BLOCKED":
            return {"status": "BLOCKED", "reason": audit_result['reason']}
            
        if audit_result['status'] == "NEEDS_APPROVAL" and not approved:
            return {
                "status": "PENDING_APPROVAL", 
                "command": command, 
                "reason": audit_result['reason']
            }
            
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                text=True, 
                capture_output=True, 
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
                
            if not output.strip() and result.returncode == 0:
                output = "Command executed successfully."
            elif not output.strip() and result.returncode != 0:
                output = f"Command failed (Return code: {result.returncode})"
                
            return {"status": "SUCCESS", "output": output}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    def web_research(self, query):
        """Runs the deep research logic using Tavily via research_logic.py."""
        return deep_research(query)

    def process_message(self, user_message: str, approved_tool_call=None):
        """Processes messages with an interruptible tool loop for security approval."""
        
        # If we just got an approval, we don't need to recall memory again, 
        # but we need to inject the approved tool output.
        if approved_tool_call:
            # resume from the approved call
            tool_call_id = approved_tool_call['id']
            function_name = approved_tool_call['name']
            command = approved_tool_call['command']
            
            # Re-execute with approved=True
            tool_output_node = self.execute_bash(command, approved=True)
            tool_output = tool_output_node.get("output", tool_output_node.get("error", "Error"))
            
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": function_name,
                "content": str(tool_output)
            })
        else:
            # Normal start of message
            semantic_brain_context = recall_memory(user_message)
            dynamic_system_prompt = self.system_prompt
            if semantic_brain_context:
                dynamic_system_prompt += f"\n\n{semantic_brain_context}"
            if len(self.messages) > 0 and self.messages[0]["role"] == "system":
                self.messages[0]["content"] = dynamic_system_prompt
            self.messages.append({"role": "user", "content": user_message})
        
        while True:
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                        tools=self.tools,
                        tool_choice="auto"
                    )
                    break 
                except Exception as e:
                    err_msg = str(e)
                    if "429" in err_msg and attempt < max_retries - 1:
                        print(f"Rate limited by AI Provider. Retrying in 20 seconds... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(20)
                        continue
                    else:
                        billing_link = ""
                        if "429" in err_msg:
                            billing_link = "\n\n💡 Google AI Free limits reached. Consider attaching a billing card at https://aistudio.google.com/ against your API key to remove these limits." 
                        return {"status": "ERROR", "error": f"Model Error: {err_msg}{billing_link}"}
            
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
                return {"status": "COMPLETED", "response": response_message.content}
                
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                if function_name == "execute_bash":
                    command = args.get("command", "")
                    tool_res = self.execute_bash(command)
                    
                    if tool_res['status'] == "BLOCKED":
                        tool_output = f"🛑 BLOCKED: {tool_res['reason']}"
                    elif tool_res['status'] == "PENDING_APPROVAL":
                        # INTERRUPT THE LOOP and return a 'Wait' state to the server
                        # Remove the last assistant message (the tool call) so we don't have dangling tool calls
                        # Actually, better to keep it and return the pending state
                        return {
                            "status": "PENDING_APPROVAL",
                            "tool_call_id": tool_call.id,
                            "command": command,
                            "reason": tool_res['reason']
                        }
                    else:
                        tool_output = tool_res.get("output", tool_res.get("error", "Error"))
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
                elif function_name == "check_twitter_dms":
                    tool_output = check_twitter_dms()
                elif function_name == "check_instagram_dms":
                    tool_output = check_instagram_dms()
                elif function_name == "analyze_and_graph_scores":
                    tool_output = analyze_and_graph_scores(args.get("csv_content", ""))
                elif function_name == "save_message_to_folder":
                    tool_output = save_message_to_folder(args.get("category", "General"), args.get("filename", "msg.txt"), args.get("content", ""))
                elif function_name == "teach_ai":
                    tool_output = teach_ai(args.get("topic", "Unknown"), args.get("information", ""))
                elif function_name == "generate_picture":
                    tool_output = generate_image(args.get("prompt", ""))
                elif function_name == "read_document":
                    tool_output = read_document_content(args.get("path", ""))
                elif function_name == "summarize_document":
                    tool_output = summarize_document(args.get("path", ""))
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
