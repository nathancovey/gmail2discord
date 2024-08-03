import os
import base64
import requests
import logging
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MONITORED_EMAIL = os.getenv('MONITORED_EMAIL', 'loopsbot@mail.loops.so')
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', 10))
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def save_token(creds):
    """Save the credentials to the environment variable."""
    token_json = creds.to_json()
    token_base64 = base64.b64encode(token_json.encode()).decode()
    os.environ['TOKEN_JSON'] = token_base64
    logger.info("Token saved to environment variable")

def load_credentials():
    """Load credentials from the environment."""
    creds = None
    if 'TOKEN_JSON' in os.environ:
        token_base64 = os.environ['TOKEN_JSON']
        token_json = base64.b64decode(token_base64).decode('utf-8')
        creds = Credentials.from_authorized_user_info(eval(token_json), SCOPES)
        logger.info("Token loaded from environment variable")
    return creds

def get_new_token():
    """Get a new token using manual authorization."""
    if 'GOOGLE_CREDENTIALS' not in os.environ:
        logger.error("GOOGLE_CREDENTIALS environment variable is not set")
        return None

    credentials_base64 = os.environ['GOOGLE_CREDENTIALS']
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    
    flow = Flow.from_client_config(eval(credentials_json), SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

    auth_url, _ = flow.authorization_url(prompt='consent')
    
    logger.info("To authorize this application, please follow these steps:")
    logger.info(f"1. Visit this URL in a web browser: {auth_url}")
    logger.info("2. Complete the authorization process.")
    logger.info("3. Copy the authorization code you receive.")
    logger.info("4. Set the authorization code as an environment variable named 'GOOGLE_AUTH_CODE' using the following command:")
    logger.info("   heroku config:set GOOGLE_AUTH_CODE=<your_auth_code> --app cryptic-depths-88362")
    logger.info("5. Then, run this script again.")
    
    return None

def ensure_valid_credentials():
    """Ensure we have valid credentials, refreshing or getting new ones if necessary."""
    creds = load_credentials()
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                save_token(creds)
                logger.info("Token refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                return get_new_token()
        else:
            return get_new_token()
    
    return creds

def process_auth_code():
    """Process the authorization code if it's set in the environment."""
    if 'GOOGLE_AUTH_CODE' in os.environ:
        auth_code = os.environ['GOOGLE_AUTH_CODE']
        credentials_base64 = os.environ['GOOGLE_CREDENTIALS']
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        
        flow = Flow.from_client_config(eval(credentials_json), SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        try:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            save_token(creds)
            logger.info("New token generated and saved successfully")
            
            # Remove the auth code from the environment
            os.environ.pop('GOOGLE_AUTH_CODE')
            logger.info("Removed GOOGLE_AUTH_CODE from environment")
            
            return creds
        except Exception as e:
            logger.error(f"Error processing authorization code: {e}")
    
    return None

def send_discord_notification(timestamp):
    """Send a notification to Discord."""
    if not DISCORD_WEBHOOK_URL:
        logger.error("Discord webhook URL is not set")
        return

    data = {
        'content': f'Someone just signed up for CodeClimbers via the website! 🚀\n\nTimestamp: {timestamp}\n\n[[[ Keep Climbing ]]]'
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        logger.info('Discord notification sent successfully')
    except requests.exceptions.RequestException as e:
        logger.error(f'Failed to send Discord notification: {e}')

def main():
    try:
        creds = process_auth_code() or ensure_valid_credentials()
        if not creds:
            logger.error("Failed to obtain valid credentials")
            return

        service = build('gmail', 'v1', credentials=creds)

        check_time = datetime.utcnow() - timedelta(minutes=CHECK_INTERVAL_MINUTES)
        check_time_str = check_time.isoformat() + 'Z'
        query = f'from:{MONITORED_EMAIL} after:{check_time_str}'
        logger.info(f"Checking for emails with query: {query}")

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} new messages")

        for message in messages:
            try:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                timestamp = next((header['value'] for header in headers if header['name'] == 'Date'), None)
                
                if timestamp:
                    timestamp_dt = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_timestamp = timestamp_dt.strftime('%a, %d %b %Y %H:%M:%S %z')
                else:
                    formatted_timestamp = "Timestamp not available"

                send_discord_notification(formatted_timestamp)
            except StopIteration:
                logger.warning(f"Could not find Date header for message {message['id']}")
            except HttpError as error:
                logger.error(f'An error occurred while retrieving message {message["id"]}: {error}')
            except Exception as e:
                logger.error(f"Error processing message {message['id']}: {e}")

    except HttpError as error:
        logger.error(f'An error occurred: {error}')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()