#!/usr/bin/env python3
"""
Check Username Adapter

This script serves as a bridge between the Electron app and the existing Python codebase.
It checks if a username is available and returns the result in JSON format.
"""

import os
import sys
import json
import traceback
import datetime

# Add the parent directory to the path so we can import the original modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from name_utils import NameChecker
    from sniper import Sniper
except ImportError as e:
    result = {
        "success": False,
        "error": f"Failed to import required modules: {str(e)}"
    }
    print(json.dumps(result))
    sys.exit(1)

def check_username(username):
    """Check if a username is available and return the result in JSON format"""
    try:
        # Initialize the required objects
        name_checker = NameChecker()
        sniper = Sniper()
        
        # First, check if the username is valid
        if not name_checker.is_valid_minecraft_username(username):
            return {
                "success": False,
                "error": "Invalid username format",
                "details": "Minecraft usernames can only contain letters, numbers, and underscores, and must be between 3 and 16 characters long."
            }
        
        # Check if the username is available
        is_available = sniper.check_username(username)
        
        result = {
            "success": True,
            "username": username,
            "available": is_available
        }
        
        # If not available, try to get the drop time
        if not is_available:
            drop_time = sniper.get_drop_time(username)
            
            if drop_time:
                time_until = drop_time - datetime.datetime.now()
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                result["drop_time"] = drop_time.strftime('%Y-%m-%d %H:%M:%S')
                result["time_until"] = {
                    "days": days,
                    "hours": hours,
                    "minutes": minutes,
                    "seconds": seconds
                }
                result["soon_available"] = days < 0 or (days == 0 and hours == 0 and minutes < 5)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    # Get the username from command line arguments
    if len(sys.argv) < 2:
        result = {
            "success": False,
            "error": "No username provided"
        }
    else:
        username = sys.argv[1]
        result = check_username(username)
    
    # Return the result as JSON
    print(json.dumps(result)) 