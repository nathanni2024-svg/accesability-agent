import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app import SkillAgent
from main import audit_command

def test_hitl_logic():
    agent = SkillAgent()
    
    print("--- Testing 'BLOCKED' command (rm -rf /) ---")
    res1 = agent.process_message("run the command rm -rf /")
    print(f"Status: {res1.get('status')}")
    print(f"Response: {res1.get('response', res1.get('error'))}\n")
    
    print("--- Testing 'PENDING_APPROVAL' command (curl) ---")
    res2 = agent.process_message("fetch the status of google.com using curl")
    print(f"Status: {res2.get('status')}")
    if res2.get('status') == 'PENDING_APPROVAL':
        print(f"Command: {res2.get('command')}")
        print(f"Reason: {res2.get('reason')}\n")
        
        print("--- Testing 'APPROVE' flow ---")
        approved_call = {
            "id": res2['tool_call_id'],
            "name": "execute_bash",
            "command": res2['command']
        }
        res3 = agent.process_message(None, approved_tool_call=approved_call)
        print(f"Status: {res3.get('status')}")
        print(f"Response (Fragment): {res3.get('response', res3.get('error'))[:50]}...\n")
    else:
        print(f"Response: {res2.get('response', res2.get('error'))}")

if __name__ == "__main__":
    test_hitl_logic()
