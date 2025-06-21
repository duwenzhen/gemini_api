import datetime
import os

import os.path
import base64
import mimetypes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase # For more general binary attachments

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send',]
TOKEN_FILE = './src/mcp-gmail-fetcher/token.json'
CREDENTIALS_FILE = './src/mcp-gmail-fetcher/credentials.json'

def authenticate_gmail_api():
    """Authenticates with the Gmail API and returns the service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_emails_between_dates(service, start_date: datetime.date, end_date: datetime.date):
    """
    Fetches emails received between start_date and end_date (inclusive of start_date, exclusive of end_date's next day).
    Args:
        service: The authenticated Gmail API service object.
        start_date (datetime.date): The start date for the email search.
        end_date (datetime.date): The end date for the email search.
    Returns:
        list: A list of dictionaries containing email details.
    """
    # Gmail API query format: 'after:YYYY/MM/DD before:YYYY/MM/DD'
    # 'before' is exclusive, so to include emails on end_date, we need to query up to the next day.
    query_start_str = start_date.strftime("%Y/%m/%d")
    query_end_exclusive_str = (end_date + datetime.timedelta(days=1)).strftime("%Y/%m/%d")

    query = f"after:{query_start_str} before:{query_end_exclusive_str}"

    print(f"Searching for emails received between {query_start_str} and {end_date.strftime('%Y/%m/%d')}...")
    print(f"Gmail API query string: '{query}'")

    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No emails found in the specified date range.")
            return {}
        else:
            print(f"Found {len(messages)} email IDs. Fetching details...")
            email_details = {}
            for msg in messages:
                msg_id = msg['id']
                msg_full = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

                headers = msg_full['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No Sender')
                received_date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No Date')

                # Decode email body (example for plain text, might need more robust handling for HTML)
                message_body = "No body found."
                msg_payload = msg_full['payload']
                if 'parts' in msg_payload:
                    for part in msg_payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                message_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                break
                        elif part['mimeType'] == 'text/html':
                            pass # HTML content, you can parse this if needed
                elif 'body' in msg_payload and 'data' in msg_payload['body']:
                     message_body = base64.urlsafe_b64decode(msg_payload['body']['data']).decode('utf-8')


                email_details[msg_id] = {
                    'subject': subject,
                    'sender': sender,
                    'date': received_date,
                    'body': message_body
                }
            return email_details

    except HttpError as error:
        print(f"An API error occurred: {error}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

async def get_email(starttime_str : str, endtime_str : str):
    starttime_time = datetime.datetime.strptime(starttime_str, "%Y-%m-%d")
    endtime_time = datetime.datetime.strptime(endtime_str, "%Y-%m-%d")

    print("--- Starting Gmail Email Fetcher ---")
    service = authenticate_gmail_api()
    if service:
        # Define your desired date range
        # Current time is Sunday, June 15, 2025 at 9:49:27 PM +04.
        # Let's search for emails from June 12, 2025 to June 15, 2025 (inclusive)
        # start_date = datetime.date(2025, 6, 12)
        # end_date = datetime.date(2025, 6, 15)

        emails_in_range = get_emails_between_dates(service, starttime_time, endtime_time)
        return emails_in_range
    return {}


def create_message_with_attachment(sender, to, subject, html_content, file_path):
    """Create a MIME message with an attachment."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg_text = MIMEText(html_content, "html")
    message.attach(msg_text)

    # Attach the WAV file
    content_type, encoding = mimetypes.guess_type(file_path)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream' # Fallback if MIME type can't be guessed

    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'audio':
        with open(file_path, 'rb') as fp:
            msg_attachment = MIMEAudio(fp.read(), _subtype=sub_type)
    else:
        # Handle other types if necessary, though for .wav, audio is expected
        with open(file_path, 'rb') as fp:
            msg_attachment = MIMEBase(main_type, sub_type)
            msg_attachment.set_payload(fp.read())
            # For general binary data, you might need to encode it
            from email import encoders
            encoders.encode_base64(msg_attachment)


    filename = os.path.basename(file_path)
    msg_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg_attachment)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email_with_attachment(sender_email, recipient_email, email_subject, email_body, attachment_path):
    """Sends an email with a specified subject, body, and attachment."""
    service = authenticate_gmail_api()
    if not service:
        print("Failed to authenticate with Gmail API.")
        return

    message_content = create_message_with_attachment(
        sender=sender_email,
        to=recipient_email,
        subject=email_subject,
        html_content=email_body,
        file_path=attachment_path
    )

    sent_message = send_email(service, "me", message_content)
    if sent_message:
        print(f"Email sent successfully with ID: {sent_message['id']}")
    else:
        print("Failed to send email.")

def send_email(service, user_id, message_body):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
        message_body: The email message as a dictionary with a 'raw' key containing the base64url encoded message.

    Returns:
        Sent Message.
    """
    try:
        message = service.users().messages().send(userId=user_id, body=message_body).execute()
        print(f'Message Id: {message["id"]}')
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None



if __name__ == '__main__':
    print("--- Starting Gmail Email Fetcher ---")
    service = authenticate_gmail_api()
    if service:
        # Define your desired date range
        # Current time is Sunday, June 15, 2025 at 9:49:27 PM +04.
        # Let's search for emails from June 12, 2025 to June 15, 2025 (inclusive)
        start_date = datetime.date(2025, 6, 12)
        end_date = datetime.date(2025, 6, 15)

        emails_in_range = get_emails_between_dates(service, start_date, end_date)

        if emails_in_range:
            print(f"\n--- Emails Received Between {start_date} and {end_date} ---")
            for email in emails_in_range:
                print(f"  Subject: {email['subject']}")
                print(f"  From: {email['sender']}")
                print(f"  Date: {email['date']}")
                print(f"  Snippet: {email['body_snippet']}\n")
        else:
            print(f"\nNo emails to display for the range {start_date} to {end_date}.")
    else:
        print("Failed to authenticate with Gmail API.")
    print("--- Gmail Email Fetcher Finished ---")