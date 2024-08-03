import os
import base64
import requests
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def save_token(creds):
    """Save the credentials to a token.json file and update the environment variable."""
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    # Update the base64 encoded token in Heroku environment variables
    with open('token.json', 'rb') as token:
        token_base64 = base64.b64encode(token.read()).decode('utf-8')
        os.system(f'heroku config:set TOKEN_JSON={token_base64} --app cryptic-depths-88362')

def load_credentials():
    """Load credentials from the environment and file."""
    if 'GOOGLE_CREDENTIALS' in os.environ:
        credentials_base64 = os.environ['GOOGLE_CREDENTIALS']
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        with open('credentials.json', 'w') as f:
            f.write(credentials_json)
    
    creds = None
    if 'TOKEN_JSON' in os.environ:
        token_base64 = os.environ['TOKEN_JSON']
        token_json = base64.b64decode(token_base64).decode('utf-8')
        with open('token.json', 'w') as f:
            f.write(token_json)

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    return creds

def main():
    creds = load_credentials()
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                save_token(creds)
            except Exception as e:
                print(f"Error refreshing token: {e}")
                os.remove('token.json')
                creds = None
        else:
            print("No valid credentials available.")
            return  # Exit if no valid credentials

    service = build('gmail', 'v1', credentials=creds)

    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    ten_minutes_ago_str = ten_minutes_ago.isoformat() + 'Z'

    query = f'from:loopsbot@mail.loops.so after:{ten_minutes_ago_str}'
    print(f"Query: {query}")
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    print(f"Messages found: {len(messages)}")

    if not messages:
        print('No new messages.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            try:
                timestamp = next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Date')
                timestamp_dt = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')
                formatted_timestamp = timestamp_dt.strftime('%a, %d %b %Y %H:%M:%S %z')
            except StopIteration:
                formatted_timestamp = "This is a test."

            webhook_url = os.environ['DISCORD_WEBHOOK_URL']
            data = {
                'content': f'Someone just signed up for CodeClimbers via the website!\n\nTimestamp: {formatted_timestamp}\n\n[[[ Keep Climbing ]]]'
            }
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                print('Message sent successfully.')
            else:
                print(f'Failed to send message. Response code: {response.status_code}')

if __name__ == '__main__':
    main()