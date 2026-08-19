import os
import smtplib
from email.message import EmailMessage
from gmail_logic import create_gmail_draft, send_gmail_message

def _get_credentials():
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_APP_PASSWORD")
    if not email_address or not email_password or "your_email" in email_address:
         return None, None
    return email_address, email_password

def draft_email(to_address, subject, body):
    """
    Drafts an email to be reviewed by the user. Creates a real draft via Gmail API.
    """
    res = create_gmail_draft(to_address, subject, body)
    if res.startswith("Error"):
        # Fallback to local mock
        return f"Fallback Draft (Local String Only):\nTo: {to_address}\nSubject: {subject}\n\n{body}\n\n[Status: DRAFTING]\nPlease ask the user if they want to 'test send' (mock) or 'real send' (actual). Note: Gmail API not configured properly: {res}"
    
    return f"CREATED REAL GMAIL DRAFT:\nTo: {to_address}\nSubject: {subject}\n\n{body}\n\n[Status: DRAFT CREATED]\nGmail API response: {res}\nPlease ask the user if they want to 'test send' (100% safe local mock) or 'real send' (actually send a new email over the internet)."

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
    Actually sends the email via Real Gmail API (or falls back to SMTP).
    """
    res = send_gmail_message(to_address, subject, body)
    if not res.startswith("Error"):
        return res
        
    # Fallback to SMTP
    user, password = _get_credentials()
    if not user or not password:
         return f"Error: Tell the user they must add `credentials.json` for Gmail API, OR EMAIL_ADDRESS and EMAIL_APP_PASSWORD to their .env file to send real messages! Gmail API Error was: {res}"

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
    return "[Mock Inbox Active] No new real messages right now."
