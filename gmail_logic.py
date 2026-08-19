import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://mail.google.com/"]

def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                return None, "Error: credentials.json not found. Please download OAuth 2.0 Client credentials from Google Cloud Console and save it as credentials.json in the project root."
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        return service, None
    except HttpError as error:
        return None, f"An error occurred: {error}"

def create_gmail_draft(to_address, subject, body):
    service, error_msg = get_gmail_service()
    if error_msg:
        return error_msg

    try:
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to_address
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
        return f"Successfully created DRAFT in your Gmail account. Draft ID: {draft['id']}"
    except HttpError as error:
        return f"An error occurred drafting email: {error}"

def send_gmail_message(to_address, subject, body):
    service, error_msg = get_gmail_service()
    if error_msg:
        return error_msg

    try:
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to_address
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return f"Successfully sent REAL email via Gmail API! Message Id: {send_message['id']}"
    except HttpError as error:
        return f"An error occurred sending email: {error}"
