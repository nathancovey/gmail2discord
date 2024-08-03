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
    
    # Save to Heroku config
    os.system(f"heroku config:set TOKEN_JSON={token_base64} --app cryptic-depths-88362")
    logger.info("Token saved to Heroku config")

def load_credentials():
    """Load credentials from the environment."""
    creds = None
    if 'TOKEN_JSON' in os.environ:
        token_base64 = os.environ['TOKEN_JSON']
        token_json = base64.b64decode(token_base64).decode('utf-8')
        creds = Credentials.from_authorized_user_info(eval(token_json), SCOPES)
        logger.info("Token loaded from environment variable")
    return creds

def authenticate():
    """Perform the authentication process."""
    if 'GOOGLE_CREDENTIALS' not in os.environ:
        logger.error("GOOGLE_CREDENTIALS environment variable is not set")
        return None

    credentials_base64 = os.environ['GOOGLE_CREDENTIALS']
    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
    
    flow = Flow.from_client_config(eval(credentials_json), SCOPES)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\nTo authenticate, please follow these steps:")
    print(f"1. Visit this URL in a web browser: {auth_url}")
    print("2. Complete the authorization process.")
    print("3. Copy the authorization code you receive.")
    print("4. Paste the authorization code here and press Enter.")
    
    auth_code = input("Enter the authorization code: ").strip()
    
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        save_token(creds)
        print("Authentication successful. Token saved.")
        return creds
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return None

def ensure_valid_credentials():
    """Ensure we have valid credentials, refreshing or getting new ones if necessary."""
    creds = load_credentials()
    
    if not creds:
        logger.info("No existing credentials found. Starting new authentication.")
        return authenticate()
    
    if creds.valid:
        logger.info("Existing credentials are valid.")
        return creds
    
    if creds.expired and creds.refresh_token:
        try:
            logger.info("Refreshing expired credentials.")
            creds.refresh(Request())
            save_token(creds)
            logger.info("Token refreshed successfully")
            return creds
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            logger.info("Starting new authentication.")
            return authenticate()
    
    logger.info("Credentials invalid. Starting new authentication.")
    return authenticate()

# ... (rest of the functions remain the same)

def main():
    try:
        creds = ensure_valid_credentials()
        if not creds:
            logger.error("Failed to obtain valid credentials")
            return

        service = build('gmail', 'v1', credentials=creds)
        check_emails(service)

    except HttpError as error:
        logger.error(f'An error occurred: {error}')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()