#!/usr/bin/env python3
"""
Claim Username Adapter

This script serves as a bridge between the Electron app and the existing Python codebase.
It attempts to claim a Minecraft username using the specified strategy.
"""

import os
import sys
import json
import time
import traceback
import datetime

# Add the parent directory to the path so we can import the original modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from minecraft_auth import MinecraftAuth
    from name_utils import NameChecker
    from sniper import Sniper
except ImportError as e:
    result = {
        "success": False,
        "error": f"Failed to import required modules: {str(e)}"
    }
    print(json.dumps(result))
    sys.exit(1)

def claim_username(username, strategy, auth_token=None, email=None, password=None):
    """Attempt to claim a username with the specified strategy"""
    try:
        # Initialize required objects
        name_checker = NameChecker()
        sniper = Sniper()
        
        # First, check if the username is valid
        if not name_checker.is_valid_minecraft_username(username):
            return {
                "success": False,
                "error": "Invalid username format",
                "details": "Minecraft usernames can only contain letters, numbers, and underscores, and must be between 3 and 16 characters long."
            }
        
        # Next, check if the username is available before attempting to claim
        print(json.dumps({
            "status": "checking",
            "message": f"Checking if username '{username}' is available"
        }))
        
        is_available = sniper.check_username(username)
        if not is_available:
            return {
                "success": False,
                "error": "Username is not available",
                "details": f"The username '{username}' is currently not available for claiming."
            }
        
        # Authenticate with Minecraft
        print(json.dumps({
            "status": "authenticating",
            "message": "Authenticating with Microsoft account"
        }))
        
        auth = MinecraftAuth()
        
        # Use auth token if provided, otherwise use email/password
        if auth_token:
            auth_success = auth.authenticate_with_token(auth_token)
        elif email and password:
            auth_success = auth.authenticate(email, password)
        else:
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
        
        # Check if account is eligible for name change
        print(json.dumps({
            "status": "checking_eligibility",
            "message": "Checking if account is eligible for name change"
        }))
        
        if not sniper.check_name_change_eligibility():
            return {
                "success": False,
                "error": "Account not eligible",
                "details": "Your account is not eligible for a name change at this time."
            }
        
        # Set up the sniper with the selected strategy
        print(json.dumps({
            "status": "preparing",
            "message": f"Preparing to claim username with {strategy} strategy"
        }))
        
        # Claim the username with the selected strategy
        result = None
        
        if strategy == "timing":
            print(json.dumps({
                "status": "claiming",
                "message": "Claiming username with timing strategy"
            }))
            result = sniper.claim_username_timing(username)
        elif strategy == "burst":
            print(json.dumps({
                "status": "claiming",
                "message": "Claiming username with burst strategy"
            }))
            result = sniper.claim_username_burst(username)
        elif strategy == "distributed":
            print(json.dumps({
                "status": "claiming",
                "message": "Claiming username with distributed strategy"
            }))
            result = sniper.claim_username_distributed(username)
        elif strategy == "precision":
            print(json.dumps({
                "status": "claiming",
                "message": "Claiming username with precision strategy"
            }))
            result = sniper.claim_username_precision(username)
        elif strategy == "adaptive":
            print(json.dumps({
                "status": "claiming",
                "message": "Claiming username with adaptive strategy"
            }))
            result = sniper.claim_username_adaptive(username)
        else:
            # Default to timing strategy if invalid strategy provided
            print(json.dumps({
                "status": "claiming",
                "message": f"Invalid strategy '{strategy}', using timing strategy instead"
            }))
            result = sniper.claim_username_timing(username)
        
        # Process the result
        if result and result.success:
            return {
                "success": True,
                "username": username,
                "message": f"Successfully claimed username '{username}'!",
                "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "strategy": strategy
            }
        else:
            return {
                "success": False,
                "error": "Failed to claim username",
                "details": result.error if result else "Unknown error during claiming process",
                "strategy": strategy
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
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Insufficient arguments",
            "details": "Usage: python claim_username.py <username> <strategy> [auth_token]"
        }))
        sys.exit(1)
    
    username = sys.argv[1]
    strategy = sys.argv[2]
    
    # Optional auth token
    auth_token = None
    if len(sys.argv) >= 4:
        auth_token = sys.argv[3]
    
    # Run the claiming process
    result = claim_username(username, strategy, auth_token)
    
    # Return the result as JSON
    print(json.dumps(result)) 