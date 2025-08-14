import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config

class GoogleAuthenticator:
    def __init__(self):
        self.creds = None
        self.service_gmail = None
        self.service_sheets = None
    
    def authenticate(self):
        """Authenticate with Google APIs"""
        # Load existing token
        if os.path.exists(config.TOKEN_FILE):
            with open(config.TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no valid credentials available, request authorization
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(config.CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Credentials file not found at {config.CREDENTIALS_FILE}\n"
                        "Please download it from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(config.TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build services
        self.service_gmail = build('gmail', 'v1', credentials=self.creds)
        self.service_sheets = build('sheets', 'v4', credentials=self.creds)
        
        return True
    
    def get_gmail_service(self):
        """Get Gmail service instance"""
        if not self.service_gmail:
            self.authenticate()
        return self.service_gmail
    
    def get_sheets_service(self):
        """Get Sheets service instance"""
        if not self.service_sheets:
            self.authenticate()
        return self.service_sheets
    
    def get_user_email(self):
        """Get authenticated user's email address"""
        try:
            profile = self.service_gmail.users().getProfile(userId='me').execute()
            return profile['emailAddress']
        except Exception as e:
            return None 