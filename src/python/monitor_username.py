#!/usr/bin/env python3
"""
Monitor Username Adapter

This script serves as a bridge between the Electron app and the existing Python codebase.
It monitors a username continuously and reports status updates to the Electron app.
"""

import os
import sys
import json
import time
import signal
import traceback
import datetime

# Add the parent directory to the path so we can import the original modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from name_utils import NameChecker
    from sniper import Sniper
except ImportError as e:
    result = {
        "type": "error",
        "error": f"Failed to import required modules: {str(e)}"
    }
    print(json.dumps(result))
    sys.exit(1)

# Flag to handle graceful shutdown
monitoring_active = True

def signal_handler(sig, frame):
    """Handle interrupt signals to exit gracefully"""
    global monitoring_active
    monitoring_active = False
    print(json.dumps({"type": "status", "status": "stopping"}))
    sys.exit(0)

# Set up signal handler for graceful exit
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def monitor_username(username, interval=3.0):
    """Monitor a username continuously and report status updates"""
    try:
        # Initialize the required objects
        name_checker = NameChecker()
        sniper = Sniper()
        
        # First, check if the username is valid
        if not name_checker.is_valid_minecraft_username(username):
            print(json.dumps({
                "type": "error",
                "error": "Invalid username format",
                "details": "Minecraft usernames can only contain letters, numbers, and underscores, and must be between 3 and 16 characters long."
            }))
            return
        
        # Initial check and status report
        print(json.dumps({
            "type": "status",
            "status": "starting",
            "username": username,
            "interval": interval
        }))
        
        # Get drop time info if available
        drop_time = None
        try:
            drop_time = sniper.get_drop_time(username)
            if drop_time:
                time_until = drop_time - datetime.datetime.now()
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(json.dumps({
                    "type": "drop_time",
                    "drop_time": drop_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "time_until": {
                        "days": days,
                        "hours": hours,
                        "minutes": minutes,
                        "seconds": seconds
                    }
                }))
        except:
            # Continue even if we can't get drop time
            pass
        
        check_count = 0
        
        # Main monitoring loop
        while monitoring_active:
            check_count += 1
            check_start_time = time.time()
            
            # Check if username is available
            is_available = sniper.check_username(username)
            
            if is_available:
                # Username found available!
                print(json.dumps({
                    "type": "available",
                    "username": username,
                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "checks": check_count
                }))
                # Exit after finding username is available
                break
            else:
                # Status update for regular check
                print(json.dumps({
                    "type": "check",
                    "available": False,
                    "check_count": check_count,
                    "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }))
                sys.stdout.flush()  # Ensure output is sent immediately
            
            # Calculate sleep time to maintain consistent interval
            check_duration = time.time() - check_start_time
            sleep_time = max(0.1, interval - check_duration)
            
            # Sleep in smaller chunks to allow for quicker interruption
            sleep_chunk = 0.1
            for _ in range(int(sleep_time / sleep_chunk)):
                if not monitoring_active:
                    break
                time.sleep(sleep_chunk)
            
            # Sleep any remaining time
            remaining_sleep = sleep_time % sleep_chunk
            if remaining_sleep > 0 and monitoring_active:
                time.sleep(remaining_sleep)
        
        # Final status update on exit
        print(json.dumps({
            "type": "status",
            "status": "stopped",
            "checks_performed": check_count
        }))
        
    except Exception as e:
        print(json.dumps({
            "type": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }))

if __name__ == "__main__":
    # Get the username and optional interval from command line arguments
    if len(sys.argv) < 2:
        print(json.dumps({
            "type": "error",
            "error": "No username provided"
        }))
        sys.exit(1)
    
    username = sys.argv[1]
    interval = 3.0  # Default interval
    
    if len(sys.argv) >= 3:
        try:
            interval = float(sys.argv[2])
            if interval < 0.5:
                print(json.dumps({
                    "type": "warning",
                    "warning": "Interval too short, using minimum value of 0.5 seconds"
                }))
                interval = 0.5
        except ValueError:
            print(json.dumps({
                "type": "warning",
                "warning": f"Invalid interval '{sys.argv[2]}', using default of 3.0 seconds"
            }))
    
    # Start monitoring
    monitor_username(username, interval) 