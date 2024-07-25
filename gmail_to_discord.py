import os
import base64
import requests
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Decode the base64 encoded credentials and write to a file
    if 'GOOGLE_CREDENTIALS' in os.environ:
        credentials_base64 = os.environ['GOOGLE_CREDENTIALS']
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        with open('credentials.json', 'w') as f:
            f.write(credentials_json)
    
    creds = None
    # Decode the base64 encoded token.json and write to a file
    if 'TOKEN_JSON' in os.environ:
        token_base64 = os.environ['TOKEN_JSON']
        token_json = base64.b64decode(token_base64).decode('utf-8')
        with open('token.json', 'w') as f:
            f.write(token_json)

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Calculate the timestamp for 10 minutes ago
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.strftime('%Y/%m/%d %H:%M:%S')

    # Call the Gmail API with a query to find messages from the last 10 minutes
    query = f'from:loopsbot@mail.loops.so after:{ten_minutes_ago_str}'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No new messages.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Try to get the timestamp from the email metadata
            try:
                timestamp = next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Date')
                # Format the timestamp to a readable format
                timestamp_dt = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')
                formatted_timestamp = timestamp_dt.strftime('%a, %d %b %Y %H:%M:%S %z')
            except StopIteration:
                formatted_timestamp = "This is a test."

            # Send message to Discord
            webhook_url = 'https://discord.com/api/webhooks/1266081211978219666/h3fWkbdcmlNakJww9S-QWibCHSvss0U2MdtAjbcrypiLZfEmUpRcPCnAu3vObYMEBLVP'
            data = {
                'content': f'Someone just signed up for CodeClimbers via the website! 🚀\n\nTimestamp: {formatted_timestamp}\n\n[[[ Keep Climbing ]]]'
            }
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                print('Message sent successfully.')
            else:
                print(f'Failed to send message. Response code: {response.status_code}')

if __name__ == '__main__':
    main()