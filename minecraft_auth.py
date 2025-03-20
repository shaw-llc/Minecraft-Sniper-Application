#!/usr/bin/env python3
"""
Minecraft Authentication Module

This module handles authentication with Microsoft for Minecraft accounts.
It implements the Microsoft OAuth flow for Minecraft/Xbox authentication.
Updated with the latest OAuth flow as of 2023.
"""

import os
import json
import time
import urllib.parse
import webbrowser
import requests
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from colorama import Fore, Style
import socket

# Constants for Microsoft OAuth
CLIENT_ID = "1e0a5a15-02ea-472a-b765-7b3a5c5c9d09"  # Official Minecraft Launcher client ID
REDIRECT_URI = "http://localhost:8000/auth"
SCOPE = "XboxLive.signin offline_access"
MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
MICROSOFT_DEVICE_AUTH_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
XBOX_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
MINECRAFT_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MINECRAFT_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"
MINECRAFT_NAME_CHANGE_URL = "https://api.minecraftservices.com/minecraft/profile/name/{username}"

# Auth token cache file
AUTH_CACHE_FILE = "auth_cache.json"

# OAuth server for callback handling
class AuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from Microsoft"""
    
    def do_GET(self):
        """Process the callback GET request"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        try:
            # Extract the authorization code from the URL query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            
            # Debug the path we received
            logging.debug(f"Received callback on path: {self.path}")
            
            # Handle any path to be more flexible with OAuth redirects
            # Microsoft might redirect to root path instead of /auth in some cases
            query_components = urllib.parse.parse_qs(parsed_path.query)
            
            if 'code' in query_components:
                self.server.auth_code = query_components['code'][0]
                response_content = """
                <html>
                <head><title>Authentication Successful</title></head>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can now close this window and return to the application.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
                logging.info(f"{Fore.GREEN}Received valid authentication code")
            elif 'error' in query_components:
                error = query_components['error'][0]
                error_description = query_components.get('error_description', ['Unknown error'])[0]
                logging.error(f"{Fore.RED}Authentication error: {error} - {error_description}")
                self.server.auth_code = None
                response_content = f"""
                <html>
                <head><title>Authentication Failed</title></head>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {error}</p>
                    <p>Description: {error_description}</p>
                    <p>Please try again.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
            else:
                self.server.auth_code = None
                response_content = """
                <html>
                <head><title>Authentication Failed</title></head>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>No authorization code received.</p>
                    <p>Please try again.</p>
                    <script>window.close();</script>
                </body>
                </html>
                """
        except Exception as e:
            logging.error(f"{Fore.RED}Error processing OAuth callback: {str(e)}")
            self.server.auth_code = None
            response_content = f"""
            <html>
            <head><title>Authentication Error</title></head>
            <body>
                <h1>Authentication Error</h1>
                <p>An error occurred while processing the authentication.</p>
                <p>Error: {str(e)}</p>
                <p>Please try again.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
        
        self.wfile.write(response_content.encode())
    
    def log_message(self, format, *args):
        """Silence the HTTP server logs"""
        return


class MinecraftAuth:
    """Handle Minecraft authentication via Microsoft OAuth"""
    
    def __init__(self, cache_file=AUTH_CACHE_FILE):
        """Initialize the authentication handler"""
        self.access_token = None
        self.refresh_token = None
        self.minecraft_token = None
        self.minecraft_profile = None
        self.token_expires_at = 0
        self.cache_file = cache_file
        
        # Try to load cached credentials
        self._load_cached_credentials()
    
    def _load_cached_credentials(self):
        """Load cached credentials from file if available"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.minecraft_token = data.get("minecraft_token")
                    self.token_expires_at = data.get("expires_at", 0)
                    
                    # Check if the token is still valid
                    if self.token_expires_at > time.time():
                        # Validate the Minecraft token
                        if self.minecraft_token and self.validate_minecraft_token():
                            logging.info(f"{Fore.GREEN}Loaded valid cached credentials")
                            return True
        except Exception as e:
            logging.error(f"{Fore.RED}Error loading cached credentials: {str(e)}")
        
        # Reset credentials if loading failed or they're invalid
        self.access_token = None
        self.refresh_token = None
        self.minecraft_token = None
        self.token_expires_at = 0
        return False
    
    def _save_cached_credentials(self):
        """Save credentials to cache file"""
        try:
            with open(self.cache_file, "w") as f:
                json.dump({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "minecraft_token": self.minecraft_token,
                    "expires_at": self.token_expires_at
                }, f)
            logging.debug("Credentials cached successfully")
        except Exception as e:
            logging.error(f"{Fore.RED}Error caching credentials: {str(e)}")
    
    def authenticate(self):
        """Authenticate with Microsoft services"""
        # First try to use cached credentials if available
        if self.access_token and time.time() < self.token_expires_at:
            # Validate the token
            if self.validate_minecraft_token():
                current_username = self.get_current_username()
                logging.info(f"{Fore.GREEN}Authenticated as {current_username} (using cached credentials)")
                return True
        
        # Try to refresh token if we have one
        if self.refresh_token:
            if self.refresh_access_token():
                return True
        
        # Begin the OAuth flow
        logging.info(f"{Fore.YELLOW}Most users experience issues with browser authentication. Using device code flow instead.")
        
        # Try device code flow first since it's more reliable
        if self._try_device_code_flow():
            return True
            
        # Fall back to browser flow if device code fails
        logging.info(f"{Fore.YELLOW}Device code flow failed. Trying browser authentication as a fallback...")
        return self._try_oauth_browser_flow()
    
    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        try:
            payload = {
                "client_id": CLIENT_ID,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(MICROSOFT_TOKEN_URL, data=payload)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                # Update refresh token if provided
                if "refresh_token" in token_data:
                    self.refresh_token = token_data.get("refresh_token")
                
                self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
                
                # Now authenticate with Xbox Live and get Minecraft token
                return self.authenticate_with_minecraft()
            else:
                logging.error(f"{Fore.RED}Failed to refresh token: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"{Fore.RED}Error refreshing token: {str(e)}")
            return False
    
    def _try_oauth_browser_flow(self):
        """Attempt the standard OAuth browser flow"""
        # Generate the authorization URL
        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPE,
            "response_mode": "query"
        }
        
        auth_url = f"{MICROSOFT_AUTH_URL}?{urllib.parse.urlencode(params)}"
        
        # Start a local server to handle the callback
        server = None
        try:
            # Bind to all interfaces (0.0.0.0) instead of just localhost
            # This helps with certain networking setups
            server = HTTPServer(("0.0.0.0", 8000), AuthCallbackHandler)
            server.auth_code = None
            
            # Configure socket to allow address reuse
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Open the browser for the user to authenticate
            logging.info(f"{Fore.CYAN}Opening browser for Microsoft authentication...")
            webbrowser.open(auth_url)
            
            # Wait for the callback
            logging.info(f"{Fore.YELLOW}Waiting for authentication. Browser window should open automatically...")
            logging.info(f"{Fore.YELLOW}If no browser opens, please manually visit: {auth_url}")
            server.timeout = 300  # 5 minutes timeout
            server.handle_request()
            
            # Check if we got an auth code
            if not server.auth_code:
                logging.error(f"{Fore.RED}Authentication failed or timed out")
                return False
        except Exception as e:
            logging.error(f"{Fore.RED}Error with authentication server: {str(e)}")
            logging.info(f"{Fore.YELLOW}Please make sure port 8000 is available and not blocked by firewall.")
            
            # Provide fallback instructions
            logging.info(f"{Fore.YELLOW}Alternative authentication method:")
            logging.info(f"{Fore.YELLOW}1. Open this URL in your browser: {auth_url}")
            logging.info(f"{Fore.YELLOW}2. Complete the authentication")
            logging.info(f"{Fore.YELLOW}3. You will be redirected to a URL starting with 'http://localhost:8000/auth?code='")
            logging.info(f"{Fore.YELLOW}4. Copy the entire URL from your browser address bar")
            
            manual_url = input(f"{Fore.CYAN}Paste the redirect URL here (or press Enter to cancel): {Style.RESET_ALL}")
            if manual_url:
                # Extract code from manually entered URL
                try:
                    parsed_url = urllib.parse.urlparse(manual_url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    if 'code' in query_params:
                        server = type('obj', (object,), {'auth_code': query_params['code'][0]})
                        logging.info(f"{Fore.GREEN}Manual authentication code accepted")
                    else:
                        logging.error(f"{Fore.RED}No authentication code found in the URL")
                        return False
                except Exception as e:
                    logging.error(f"{Fore.RED}Error parsing manual URL: {str(e)}")
                    return False
            else:
                return False
        finally:
            # Clean up server if it was created
            if server and hasattr(server, 'server_close'):
                server.server_close()
        
        # Exchange the auth code for tokens
        payload = {
            "client_id": CLIENT_ID,
            "code": server.auth_code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(MICROSOFT_TOKEN_URL, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
            
            # Now authenticate with Xbox Live and get Minecraft token
            return self.authenticate_with_minecraft()
        else:
            logging.error(f"{Fore.RED}Failed to get access token: {response.status_code}")
            try:
                error_data = response.json()
                logging.error(f"{Fore.RED}Error: {error_data.get('error')}")
                logging.error(f"{Fore.RED}Description: {error_data.get('error_description')}")
            except:
                logging.error(f"{Fore.RED}Response: {response.text}")
            return False
    
    def _try_device_code_flow(self):
        """Authenticate using the device code flow (no browser required)"""
        try:
            # Step 1: Request device code
            payload = {
                "client_id": CLIENT_ID,
                "scope": SCOPE
            }
            
            response = requests.post(MICROSOFT_DEVICE_AUTH_URL, data=payload)
            
            if response.status_code != 200:
                logging.error(f"{Fore.RED}Failed to start device code flow: {response.status_code}")
                return False
            
            data = response.json()
            user_code = data.get("user_code")
            device_code = data.get("device_code")
            verification_uri = data.get("verification_uri")
            expires_in = int(data.get("expires_in", 900))
            interval = int(data.get("interval", 5))
            
            # Step 2: Display clear instructions for the user
            print("\n" + "="*60)
            print(f"{Fore.GREEN}MICROSOFT AUTHENTICATION INSTRUCTIONS")
            print("="*60)
            print(f"{Fore.CYAN}1. Open {Fore.YELLOW}{verification_uri}{Fore.CYAN} in your web browser")
            print(f"   (or go to 'device.microsoft.com')")
            print(f"{Fore.CYAN}2. Enter this code when prompted: {Fore.YELLOW}{user_code}")
            print(f"{Fore.CYAN}3. Sign in with your Microsoft account")
            print(f"{Fore.CYAN}4. Approve the authentication request")
            print(f"{Fore.CYAN}5. Return here and wait for the process to complete")
            print("="*60 + "\n")
            
            logging.info(f"{Fore.CYAN}Waiting for you to complete the authentication...")
            
            # Step 3: Poll for token
            start_time = time.time()
            # Show a simple progress indicator
            print(f"{Fore.CYAN}Waiting for authentication: ", end="", flush=True)
            dots = 0
            
            while time.time() - start_time < expires_in:
                # Wait before polling
                for _ in range(interval):
                    time.sleep(1)
                    dots = (dots + 1) % 4
                    print(f"\r{Fore.CYAN}Waiting for authentication: {'.' * dots}{' ' * (3 - dots)}", end="", flush=True)
                
                # Check if the user has completed the flow
                token_payload = {
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                }
                
                token_response = requests.post(MICROSOFT_TOKEN_URL, data=token_payload)
                
                if token_response.status_code == 200:
                    # Success
                    print(f"\r{Fore.GREEN}Authentication successful! ✓                  ")
                    token_data = token_response.json()
                    self.access_token = token_data.get("access_token")
                    self.refresh_token = token_data.get("refresh_token")
                    self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
                    
                    # Authenticate with Xbox and Minecraft
                    return self.authenticate_with_minecraft()
                elif token_response.status_code == 400:
                    # Check the error
                    error_data = token_response.json()
                    error = error_data.get("error")
                    
                    if error == "authorization_pending":
                        # Still waiting for the user
                        continue
                    elif error == "expired_token":
                        print(f"\r{Fore.RED}The device code has expired. Please try again. ✗               ")
                        logging.error(f"{Fore.RED}The device code has expired. Please try again.")
                        return False
                    else:
                        print(f"\r{Fore.RED}Error during authentication: {error} ✗               ")
                        logging.error(f"{Fore.RED}Error during polling: {error}")
                        return False
                else:
                    print(f"\r{Fore.RED}Unexpected response during authentication: {token_response.status_code} ✗               ")
                    logging.error(f"{Fore.RED}Unexpected response during polling: {token_response.status_code}")
                    return False
            
            print(f"\r{Fore.RED}Authentication timed out. Please try again. ✗               ")
            logging.error(f"{Fore.RED}Timeout waiting for device code authentication")
            return False
            
        except Exception as e:
            print(f"\r{Fore.RED}Error during authentication: {str(e)} ✗               ")
            logging.error(f"{Fore.RED}Error in device code flow: {str(e)}")
            return False
    
    def authenticate_with_minecraft(self):
        """Authenticate with Xbox Live and Minecraft services"""
        try:
            # Step 1: Authenticate with Xbox Live
            logging.info(f"{Fore.CYAN}Authenticating with Xbox Live...")
            xbox_response = requests.post(
                XBOX_AUTH_URL,
                json={
                    "Properties": {
                        "AuthMethod": "RPS",
                        "SiteName": "user.auth.xboxlive.com",
                        "RpsTicket": f"d={self.access_token}"
                    },
                    "RelyingParty": "http://auth.xboxlive.com",
                    "TokenType": "JWT"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if xbox_response.status_code != 200:
                logging.error(f"{Fore.RED}Xbox Live authentication failed: {xbox_response.status_code}")
                return False
            
            xbox_data = xbox_response.json()
            xbox_token = xbox_data.get("Token")
            user_hash = xbox_data.get("DisplayClaims", {}).get("xui", [{}])[0].get("uhs")
            
            # Step 2: Get XSTS token
            logging.info(f"{Fore.CYAN}Getting XSTS token...")
            xsts_response = requests.post(
                XSTS_AUTH_URL,
                json={
                    "Properties": {
                        "SandboxId": "RETAIL",
                        "UserTokens": [xbox_token]
                    },
                    "RelyingParty": "rp://api.minecraftservices.com/",
                    "TokenType": "JWT"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if xsts_response.status_code != 200:
                logging.error(f"{Fore.RED}XSTS authentication failed: {xsts_response.status_code}")
                return False
            
            xsts_data = xsts_response.json()
            xsts_token = xsts_data.get("Token")
            
            # Step 3: Authenticate with Minecraft
            logging.info(f"{Fore.CYAN}Authenticating with Minecraft services...")
            minecraft_response = requests.post(
                MINECRAFT_AUTH_URL,
                json={
                    "identityToken": f"XBL3.0 x={user_hash};{xsts_token}"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if minecraft_response.status_code != 200:
                logging.error(f"{Fore.RED}Minecraft authentication failed: {minecraft_response.status_code}")
                return False
            
            minecraft_data = minecraft_response.json()
            self.minecraft_token = minecraft_data.get("access_token")
            
            # Save the credentials
            self._save_cached_credentials()
            
            # Get and store profile info
            profile = self.get_profile()
            
            # Display success messages with profile information
            print("\n" + "="*60)
            print(f"{Fore.GREEN}AUTHENTICATION SUCCESSFUL!")
            print("="*60)
            
            if profile and profile.get("name"):
                print(f"{Fore.CYAN}Logged in as: {Fore.YELLOW}{profile.get('name')}")
                
                if profile.get("id"):
                    print(f"{Fore.CYAN}UUID: {Fore.WHITE}{profile.get('id')}")
                
                # Check if name change is eligible
                eligible = self.is_eligible_for_name_change()
                eligibility_status = f"{Fore.GREEN}Available" if eligible else f"{Fore.RED}Not Available"
                print(f"{Fore.CYAN}Name Change Status: {eligibility_status}")
            
            print("="*60 + "\n")
            
            logging.info(f"{Fore.GREEN}Authentication successful!")
            return True
        
        except Exception as e:
            logging.error(f"{Fore.RED}Error during authentication: {str(e)}")
            return False
    
    def validate_minecraft_token(self):
        """Verify that the current Minecraft token is valid"""
        try:
            if not self.minecraft_token:
                return False
                
            headers = {
                "Authorization": f"Bearer {self.minecraft_token}"
            }
            
            response = requests.get(MINECRAFT_PROFILE_URL, headers=headers)
            
            if response.status_code == 200:
                # Store profile data for later use
                self.minecraft_profile = response.json()
                return True
                
            return False
        except Exception as e:
            logging.error(f"{Fore.RED}Error validating Minecraft token: {str(e)}")
            return False
    
    def get_profile(self):
        """Get the Minecraft profile information"""
        if not self.minecraft_token:
            logging.error(f"{Fore.RED}No Minecraft token available")
            return False
        
        try:
            response = requests.get(
                MINECRAFT_PROFILE_URL,
                headers={
                    "Authorization": f"Bearer {self.minecraft_token}"
                }
            )
            
            if response.status_code == 200:
                self.minecraft_profile = response.json()
                return True
            elif response.status_code == 401:
                # Token expired
                logging.error(f"{Fore.RED}Minecraft token expired")
                self.minecraft_token = None
                return False
            else:
                logging.error(f"{Fore.RED}Failed to get profile: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"{Fore.RED}Error getting profile: {str(e)}")
            return False
    
    def change_username(self, new_username):
        """Change the Minecraft username using the authenticated account
        
        Args:
            new_username: The new username to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.minecraft_token:
                logging.error(f"{Fore.RED}Not authenticated. Call authenticate() first")
                return False
            
            # Validate the token before attempting to change the name
            if not self.validate_minecraft_token():
                logging.error(f"{Fore.RED}Invalid or expired Minecraft token")
                return False
            
            # Updated URL construction to avoid 404 errors
            url = f"https://api.minecraftservices.com/minecraft/profile/name/{new_username}"
            headers = {
                "Authorization": f"Bearer {self.minecraft_token}",
                "Content-Type": "application/json"
            }
            
            # The API requires a PUT request with an empty body
            response = requests.put(url, headers=headers, json={})
            
            if response.status_code == 200:
                logging.info(f"{Fore.GREEN}Successfully changed username to '{new_username}'")
                # Update profile data
                self.validate_minecraft_token()
                return True
            elif response.status_code == 400:
                # Parse the error message
                error_data = response.json()
                error_message = error_data.get("errorMessage", "Unknown error")
                logging.error(f"{Fore.RED}Failed to change username: {error_message}")
                return False
            elif response.status_code == 401:
                logging.error(f"{Fore.RED}Authentication error (401)")
                return False
            elif response.status_code == 403:
                logging.error(f"{Fore.RED}Not eligible for name change (403)")
                return False
            elif response.status_code == 429:
                logging.error(f"{Fore.RED}Rate limited (429)")
                return False
            elif response.status_code == 404:
                logging.error(f"{Fore.RED}API endpoint not found (404). This could be due to API changes.")
                return False
            else:
                logging.error(f"{Fore.RED}Unexpected response: {response.status_code}")
                try:
                    logging.error(f"{Fore.RED}Response: {response.json()}")
                except:
                    logging.error(f"{Fore.RED}Response text: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"{Fore.RED}Error changing username: {str(e)}")
            return False
    
    def get_current_username(self):
        """Get the current username of the authenticated account"""
        if not self.minecraft_profile:
            if not self.validate_minecraft_token():
                return None
        
        return self.minecraft_profile.get("name")
    
    def is_eligible_for_name_change(self):
        """Check if the account is eligible for a name change
        
        Returns:
            bool: True if eligible, False otherwise
        """
        try:
            if not self.minecraft_token:
                logging.error(f"{Fore.RED}Not authenticated. Call authenticate() first")
                return False
            
            # Validate the token before checking eligibility
            if not self.validate_minecraft_token():
                logging.error(f"{Fore.RED}Invalid or expired Minecraft token")
                return False
            
            # In the current API, we can check the nameChangeAllowed field in the profile
            if self.minecraft_profile and "nameChangeAllowed" in self.minecraft_profile:
                return self.minecraft_profile["nameChangeAllowed"]
            
            # If the field is not present, use the alternative check
            url = "https://api.minecraftservices.com/minecraft/profile/namechange"
            headers = {"Authorization": f"Bearer {self.minecraft_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("nameChangeAllowed", False)
            
            return False
        except Exception as e:
            logging.error(f"{Fore.RED}Error checking name change eligibility: {str(e)}")
            return False


if __name__ == "__main__":
    # Simple test of the authentication flow
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    auth = MinecraftAuth()
    if auth.authenticate():
        print(f"Logged in as: {auth.get_current_username()}")
        print(f"Eligible for name change: {auth.is_eligible_for_name_change()}")
    else:
        print("Authentication failed") 