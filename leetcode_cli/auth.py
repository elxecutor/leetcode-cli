"""Authentication management for LeetCode CLI."""

import getpass
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from rich.prompt import Prompt


class AuthManager:
    """Manages LeetCode authentication and session handling."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "leetcode-cli"
        self.config_file = self.config_dir / "auth.json"
        self.session = requests.Session()
        self._setup_config_dir()
        self._load_session()
    
    def _setup_config_dir(self):
        """Create config directory if it does not exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions
        os.chmod(self.config_dir, 0o700)
    
    def _load_session(self):
        """Load stored authentication data."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    auth_data = json.load(f)
                    
                # Set session cookies
                cookies = auth_data.get('cookies', {})
                for name, value in cookies.items():
                    self.session.cookies.set(name, value, domain='.leetcode.com')
                    
                # Set headers
                headers = auth_data.get('headers', {})
                self.session.headers.update(headers)
                
            except (json.JSONDecodeError, IOError):
                pass  # Ignore corrupted config files
    
    def _save_session(self, cookies: Dict[str, str], headers: Dict[str, str] = None):
        """Save authentication data to config file."""
        auth_data = {
            'cookies': cookies,
            'headers': headers or {}
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.config_file, 0o600)
    
    def interactive_login(self) -> bool:
        """Interactive login process."""
        print("LeetCode CLI Login")
        print("================")
        print("You can login using either:")
        print("1. Session cookies (recommended)")
        print("2. Username and password")
        
        choice = Prompt.ask(
            "Choose login method",
            choices=["1", "2"],
            default="1"
        )
        
        if choice == "1":
            return self._cookie_login()
        else:
            return self._credential_login()
    
    def _cookie_login(self) -> bool:
        """Login using session cookies."""
        print("\nCookie Login")
        print("============")
        print("To get your session cookies:")
        print("1. Login to LeetCode in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage > Cookies > https://leetcode.com")
        print("4. Copy the values for 'LEETCODE_SESSION' and 'csrftoken'")
        print()
        
        leetcode_session = Prompt.ask("LEETCODE_SESSION cookie value", password=True)
        csrf_token = Prompt.ask("csrftoken cookie value", password=True)
        
        if not leetcode_session or not csrf_token:
            print("Both cookie values are required!")
            return False
        
        # Test the cookies
        cookies = {
            'LEETCODE_SESSION': leetcode_session,
            'csrftoken': csrf_token
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Referer': 'https://leetcode.com'
        }
        
        if self._test_authentication(cookies, headers):
            self._save_session(cookies, headers)
            return True
        else:
            print("Invalid cookies or authentication failed!")
            return False
    
    def _credential_login(self) -> bool:
        """Login using username and password."""
        print("\nCredential Login")
        print("===============")
        print("Note: This method may be less reliable due to LeetCode's anti-bot measures.")
        
        username = Prompt.ask("Username or email")
        password = getpass.getpass("Password: ")
        
        if not username or not password:
            print("Both username and password are required!")
            return False
        
        # This is a simplified implementation
        # In practice, you'd need to handle CSRF tokens, captcha, etc.
        print("Credential login not fully implemented yet. Please use cookie login.")
        return False
    
    def _test_authentication(self, cookies: Dict[str, str], headers: Dict[str, str] = None) -> bool:
        """Test if authentication is valid."""
        test_session = requests.Session()
        
        # Set cookies
        for name, value in cookies.items():
            test_session.cookies.set(name, value, domain='.leetcode.com')
        
        # Set headers
        if headers:
            test_session.headers.update(headers)
        
        try:
            # Try to access a protected endpoint
            response = test_session.get('https://leetcode.com/api/problems/all/')
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        try:
            response = self.session.get('https://leetcode.com/api/problems/all/')
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def logout(self):
        """Clear stored authentication data."""
        if self.config_file.exists():
            self.config_file.unlink()
        
        # Clear session
        self.session.cookies.clear()
        self.session.headers.clear()
    
    def get_session(self) -> requests.Session:
        """Get the authenticated session."""
        return self.session
