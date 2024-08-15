import os
import base64
import requests
from datetime import datetime, timedelta, timezone
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

    current_time = datetime.now(timezone.utc)
    ten_minutes_ago = current_time - timedelta(minutes=10)

    print(f"Current time: {current_time.isoformat()}")
    print(f"Ten minutes ago: {ten_minutes_ago.isoformat()}")

    # Improved query: Only get messages between the last 10 minutes.
    query = f'after:{int(ten_minutes_ago.timestamp())} before:{int(current_time.timestamp())}'
    print(f"Query: {query}")

    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        print("API response:", results)
        messages = results.get('messages', [])
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return

    print(f"Messages found: {len(messages)}")

    if not messages:
        print('No new messages.')
    else:
        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                timestamp = next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Date')

                # Fix the timestamp parsing issue with proper handling of (UTC)
                timestamp = timestamp.replace('(UTC)', '').strip()
                timestamp_dt = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')
                
                formatted_timestamp = timestamp_dt.strftime('%a, %d %b %Y %H:%M:%S %z')
                print(f"Message timestamp: {formatted_timestamp}")
                print(f"Timestamp as datetime: {timestamp_dt}")
                print(f"Comparison datetime: {ten_minutes_ago}")

                # Check if the message was received in the last 10 minutes
                if ten_minutes_ago <= timestamp_dt <= current_time:
                    webhook_url = os.environ['DISCORD_WEBHOOK_URL']
                    data = {
                        'content': f'Someone just signed up for CodeClimbers via the website!\n\nTimestamp: {formatted_timestamp}\n\n[[[ Keep Climbing ]]]'
                    }
                    response = requests.post(webhook_url, json=data)
                    if response.status_code == 204:
                        print('Message sent successfully.')
                    else:
                        print(f'Failed to send message. Response code: {response.status_code}')
                else:
                    print('Message received outside the 10-minute window.')

            except Exception as e:
                print(f"Error processing message: {e}")

if __name__ == '__main__':
    main()