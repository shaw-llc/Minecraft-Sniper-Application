#!/usr/bin/env python3
"""
Authentication Adapter

This script serves as a bridge between the Electron app and the existing Python codebase.
It handles Microsoft account authentication and returns account details.
"""

import os
import sys
import json
import traceback
import datetime

# Add the parent directory to the path so we can import the original modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from minecraft_auth import MinecraftAuth
except ImportError as e:
    result = {
        "success": False,
        "error": f"Failed to import required modules: {str(e)}"
    }
    print(json.dumps(result))
    sys.exit(1)

def authenticate(use_stored_token=False, email=None, password=None):
    """Authenticate with Microsoft account and return account details"""
    try:
        print(json.dumps({
            "status": "starting",
            "message": "Starting authentication process"
        }))
        
        auth = MinecraftAuth()
        
        # Try to authenticate based on the provided options
        if use_stored_token:
            print(json.dumps({
                "status": "authenticating",
                "message": "Authenticating with stored token"
            }))
            auth_success = auth.authenticate_with_stored_token()
        elif email and password:
            print(json.dumps({
                "status": "authenticating",
                "message": "Authenticating with provided credentials"
            }))
            auth_success = auth.authenticate(email, password)
        else:
            print(json.dumps({
                "status": "authenticating",
                "message": "Opening browser for interactive authentication"
            }))
            auth_success = auth.authenticate_interactive()
        
        if not auth_success:
            return {
                "success": False,
                "error": "Authentication failed",
                "details": "Failed to authenticate with Microsoft account."
            }
        
        print(json.dumps({
            "status": "authenticated",
            "message": f"Successfully authenticated as {auth.username}"
        }))
        
        # Get account details
        print(json.dumps({
            "status": "fetching_details",
            "message": "Fetching account details"
        }))
        
        # Check if account is eligible for name change
        eligibility = auth.check_name_change_eligibility()
        
        # Get profile details
        profile = {
            "username": auth.username,
            "uuid": auth.uuid,
            "token": auth.token,
            "name_change_eligible": eligibility,
            "authenticated_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return {
            "success": True,
            "profile": profile,
            "message": f"Successfully authenticated as {auth.username}"
        }
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        }))
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    # Get command line arguments
    use_stored_token = False
    email = None
    password = None
    
    # Parse arguments if provided
    if len(sys.argv) > 1:
        use_stored_token = sys.argv[1].lower() == 'true'
    
    if len(sys.argv) > 3:
        email = sys.argv[2]
        password = sys.argv[3]
    
    # Run the authentication process
    result = authenticate(use_stored_token, email, password)
    
    # Return the result as JSON
    print(json.dumps(result)) 