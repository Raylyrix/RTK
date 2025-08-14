"""
RTX Innovations - Enhanced Google Authentication
Multi-account support with beautiful UI and logout functionality
"""

import os
import json
import pickle
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GOOGLE_API_SCOPES, SECURITY_CONFIG, ACCOUNT_CONFIG

class GoogleAccount:
    """Represents a Google account with credentials and services"""
    
    def __init__(self, email: str, credentials, account_data: Dict[str, Any] = None):
        self.email = email
        self.credentials = credentials
        self.account_data = account_data or {}
        self.services = {}
        self.last_used = datetime.now()
        self.is_active = True
        
        # Initialize services
        self._init_services()
    
    def _init_services(self):
        """Initialize Google API services"""
        try:
            self.services['gmail'] = build('gmail', 'v1', credentials=self.credentials)
            self.services['sheets'] = build('sheets', 'v4', credentials=self.credentials)
            self.services['drive'] = build('drive', 'v3', credentials=self.credentials)
        except Exception as e:
            print(f"❌ Error initializing services for {self.email}: {e}")
    
    def get_service(self, service_name: str):
        """Get a specific service"""
        return self.services.get(service_name)
    
    def refresh_if_needed(self):
        """Refresh credentials if expired"""
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self.last_used = datetime.now()
                return True
            except Exception as e:
                print(f"❌ Error refreshing credentials for {self.email}: {e}")
                return False
        return True
    
    def is_valid(self) -> bool:
        """Check if account is valid and active"""
        return (
            self.is_active and 
            self.credentials and 
            self.credentials.valid and 
            self.refresh_if_needed()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary for storage"""
        return {
            'email': self.email,
            'account_data': self.account_data,
            'last_used': self.last_used.isoformat(),
            'is_active': self.is_active
        }

class GoogleAuthManager:
    """Enhanced Google authentication manager with multi-account support"""
    
    def __init__(self):
        self.accounts: Dict[str, GoogleAccount] = {}
        self.current_account: Optional[GoogleAccount] = None
        self.accounts_file = Path("accounts.json")
        self.tokens_dir = Path("tokens")
        self.tokens_dir.mkdir(exist_ok=True)
        
        # Load existing accounts
        self.load_accounts()
        
        # Authentication state
        self.is_authenticating = False
        self.auth_lock = threading.Lock()
    
    def load_accounts(self):
        """Load existing accounts from storage"""
        try:
            if self.accounts_file.exists():
                with open(self.accounts_file, 'r') as f:
                    accounts_data = json.load(f)
                
                for email, account_info in accounts_data.items():
                    token_file = self.tokens_dir / f"{email}.pickle"
                    if token_file.exists():
                        try:
                            with open(token_file, 'rb') as tf:
                                credentials = pickle.load(tf)
                            
                            account = GoogleAccount(email, credentials, account_info)
                            if account.is_valid():
                                self.accounts[email] = account
                                print(f"✅ Loaded account: {email}")
                            else:
                                print(f"⚠️ Invalid account: {email}")
                        except Exception as e:
                            print(f"❌ Error loading account {email}: {e}")
                
                print(f"✅ Loaded {len(self.accounts)} accounts")
        except Exception as e:
            print(f"❌ Error loading accounts: {e}")
    
    def save_accounts(self):
        """Save accounts to storage"""
        try:
            accounts_data = {}
            for email, account in self.accounts.items():
                accounts_data[email] = account.to_dict()
                
                # Save credentials separately
                token_file = self.tokens_dir / f"{email}.pickle"
                with open(token_file, 'wb') as tf:
                    pickle.dump(account.credentials, tf)
            
            with open(self.accounts_file, 'w') as f:
                json.dump(accounts_data, f, indent=2)
            
            print(f"✅ Saved {len(self.accounts)} accounts")
        except Exception as e:
            print(f"❌ Error saving accounts: {e}")
    
    def authenticate_account(self, credentials_file: str, email: str = None) -> Optional[GoogleAccount]:
        """Authenticate a new Google account"""
        with self.auth_lock:
            if self.is_authenticating:
                print("⚠️ Authentication already in progress")
                return None
            
            self.is_authenticating = True
        
        try:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
            
            # Create OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, 
                GOOGLE_API_SCOPES
            )
            
            # Run OAuth flow
            credentials = flow.run_local_server(port=0)
            
            # Get user email if not provided
            if not email:
                temp_service = build('gmail', 'v1', credentials=credentials)
                profile = temp_service.users().getProfile(userId='me').execute()
                email = profile['emailAddress']
            
            # Check if account already exists
            if email in self.accounts:
                print(f"⚠️ Account {email} already exists")
                # Update existing account
                self.accounts[email].credentials = credentials
                self.accounts[email].last_used = datetime.now()
                account = self.accounts[email]
            else:
                # Create new account
                account = GoogleAccount(email, credentials)
                self.accounts[email] = account
                print(f"✅ New account authenticated: {email}")
            
            # Set as current account
            self.current_account = account
            
            # Save accounts
            self.save_accounts()
            
            return account
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return None
        finally:
            self.is_authenticating = False
    
    def switch_account(self, email: str) -> bool:
        """Switch to a different account"""
        if email not in self.accounts:
            print(f"❌ Account {email} not found")
            return False
        
        account = self.accounts[email]
        if not account.is_valid():
            print(f"❌ Account {email} is not valid")
            return False
        
        self.current_account = account
        account.last_used = datetime.now()
        print(f"✅ Switched to account: {email}")
        return True
    
    def logout_account(self, email: str = None):
        """Logout a specific account or current account"""
        if email:
            # Logout specific account
            if email in self.accounts:
                account = self.accounts[email]
                account.is_active = False
                print(f"✅ Logged out account: {email}")
                
                # Remove from current if it's the current account
                if self.current_account and self.current_account.email == email:
                    self.current_account = None
        else:
            # Logout current account
            if self.current_account:
                self.current_account.is_active = False
                print(f"✅ Logged out current account: {self.current_account.email}")
                self.current_account = None
        
        # Save accounts
        self.save_accounts()
    
    def remove_account(self, email: str) -> bool:
        """Completely remove an account"""
        if email not in self.accounts:
            print(f"❌ Account {email} not found")
            return False
        
        # Remove account
        del self.accounts[email]
        
        # Remove token file
        token_file = self.tokens_dir / f"{email}.pickle"
        if token_file.exists():
            token_file.unlink()
        
        # Update current account if needed
        if self.current_account and self.current_account.email == email:
            self.current_account = None
        
        # Save accounts
        self.save_accounts()
        
        print(f"✅ Removed account: {email}")
        return True
    
    def get_current_account(self) -> Optional[GoogleAccount]:
        """Get current active account"""
        if self.current_account and self.current_account.is_valid():
            return self.current_account
        return None
    
    def get_all_accounts(self) -> List[GoogleAccount]:
        """Get all valid accounts"""
        valid_accounts = []
        for account in self.accounts.values():
            if account.is_valid():
                valid_accounts.append(account)
        return valid_accounts
    
    def get_account_info(self, email: str) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if email in self.accounts:
            account = self.accounts[email]
            return {
                'email': account.email,
                'is_active': account.is_active,
                'last_used': account.last_used,
                'is_current': account == self.current_account,
                'services': list(account.services.keys())
            }
        return None
    
    def get_service(self, service_name: str):
        """Get service from current account"""
        if not self.current_account:
            print("❌ No current account")
            return None
        
        if not self.current_account.is_valid():
            print(f"❌ Current account {self.current_account.email} is not valid")
            return None
        
        return self.current_account.get_service(service_name)
    
    def refresh_all_accounts(self):
        """Refresh all account credentials"""
        print("🔄 Refreshing all accounts...")
        refreshed_count = 0
        
        for email, account in self.accounts.items():
            if account.refresh_if_needed():
                refreshed_count += 1
        
        print(f"✅ Refreshed {refreshed_count} accounts")
        self.save_accounts()
    
    def cleanup_expired_accounts(self):
        """Remove expired or invalid accounts"""
        print("🧹 Cleaning up expired accounts...")
        expired_accounts = []
        
        for email, account in list(self.accounts.items()):
            if not account.is_valid():
                expired_accounts.append(email)
        
        for email in expired_accounts:
            self.remove_account(email)
        
        print(f"✅ Cleaned up {len(expired_accounts)} expired accounts")
    
    def export_accounts(self, file_path: str):
        """Export accounts to file (without sensitive data)"""
        try:
            export_data = {}
            for email, account in self.accounts.items():
                export_data[email] = {
                    'email': account.email,
                    'last_used': account.last_used.isoformat(),
                    'is_active': account.is_active,
                    'services': list(account.services.keys())
                }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Exported accounts to: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error exporting accounts: {e}")
            return False
    
    def import_accounts(self, file_path: str):
        """Import accounts from file"""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for email, account_info in import_data.items():
                # Note: This only imports account info, not credentials
                # Credentials need to be re-authenticated
                if email not in self.accounts:
                    print(f"⚠️ Account {email} needs re-authentication")
                    imported_count += 1
            
            print(f"✅ Imported {imported_count} account info records")
            return True
        except Exception as e:
            print(f"❌ Error importing accounts: {e}")
            return False
    
    def get_authentication_status(self) -> Dict[str, Any]:
        """Get comprehensive authentication status"""
        status = {
            'total_accounts': len(self.accounts),
            'active_accounts': len([a for a in self.accounts.values() if a.is_active]),
            'valid_accounts': len([a for a in self.accounts.values() if a.is_valid()]),
            'current_account': self.current_account.email if self.current_account else None,
            'is_authenticating': self.is_authenticating,
            'last_cleanup': getattr(self, '_last_cleanup', None)
        }
        return status

# Global authentication manager instance
auth_manager = GoogleAuthManager()

# Convenience functions for backward compatibility
def authenticate(credentials_file: str) -> bool:
    """Authenticate with Google APIs (backward compatibility)"""
    account = auth_manager.authenticate_account(credentials_file)
    return account is not None

def get_user_email() -> Optional[str]:
    """Get current user's email (backward compatibility)"""
    account = auth_manager.get_current_account()
    return account.email if account else None

def get_gmail_service():
    """Get Gmail service (backward compatibility)"""
    return auth_manager.get_service('gmail')

def get_sheets_service():
    """Get Sheets service (backward compatibility)"""
    return auth_manager.get_service('sheets') 