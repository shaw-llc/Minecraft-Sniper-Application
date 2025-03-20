#!/usr/bin/env python3
import json
import sys
import requests
import time
from datetime import datetime, timedelta

def get_drop_time(username):
    """
    Check when a username will become available.
    
    Args:
        username (str): The Minecraft username to check
        
    Returns:
        dict: Result containing success status and drop time if available
    """
    try:
        # Validate username
        if not username or not isinstance(username, str):
            return {
                "success": False,
                "message": "Invalid username provided"
            }
            
        # Strip any spaces and convert to lowercase
        username = username.strip().lower()
        
        # Check if username meets Minecraft requirements
        if not (3 <= len(username) <= 16):
            return {
                "success": False, 
                "message": "Username must be between 3 and 16 characters"
            }
            
        if not all(c.isalnum() or c == '_' for c in username):
            return {
                "success": False,
                "message": "Username can only contain letters, numbers, and underscores"
            }
        
        # Make request to Mojang API to check name availability
        api_url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            # Username is taken, check if it will be available soon
            profile_data = response.json()
            
            # Now check when the name will become available
            names_api_url = f"https://api.mojang.com/user/profiles/{profile_data['id']}/names"
            names_response = requests.get(names_api_url)
            
            if names_response.status_code == 200:
                names_data = names_response.json()
                
                # Find the current name record
                current_name = None
                for name_record in names_data:
                    if 'name' in name_record and name_record['name'].lower() == username:
                        current_name = name_record
                        break
                
                if current_name and 'changedToAt' in current_name:
                    # Calculate when the name will become available
                    # Names become available 37 days after being changed
                    changed_at = datetime.fromtimestamp(current_name['changedToAt'] / 1000)
                    available_at = changed_at + timedelta(days=37)
                    
                    # If the available time is in the past, it's already available for name change
                    now = datetime.now()
                    if available_at < now:
                        return {
                            "success": True,
                            "dropTime": None,
                            "message": "Username is currently taken but available for name change",
                            "username": username
                        }
                    
                    return {
                        "success": True,
                        "dropTime": available_at.isoformat(),
                        "message": f"Username will be available on {available_at.strftime('%Y-%m-%d %H:%M:%S')}",
                        "username": username
                    }
                
                return {
                    "success": True,
                    "dropTime": None,
                    "message": "Username is taken and no drop time could be determined",
                    "username": username
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to retrieve name history: {names_response.status_code}"
                }
        elif response.status_code == 404:
            # Username is not taken, it's already available
            return {
                "success": True,
                "dropTime": None,
                "available": True,
                "message": "Username is already available",
                "username": username
            }
        else:
            return {
                "success": False,
                "message": f"Error checking username availability: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking drop time: {str(e)}"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        result = {
            "success": False,
            "message": "Username argument is required"
        }
    else:
        username = sys.argv[1]
        result = get_drop_time(username)
    
    # Print the result as JSON
    print(json.dumps(result)) 