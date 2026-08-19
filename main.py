import re

# 1. Define our Risk Levels
BLOCKED_KEYWORDS = [
    r"rm\s+-rf\s+/",      # Absolute disk wipe
    r"chmod\s+777",        # Dangerous permissions
    r"chown",              # Ownership theft
    r"mkfs",               # Partition formatting
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
#     print(f"🛑 Security Alert: {result['reason']}")