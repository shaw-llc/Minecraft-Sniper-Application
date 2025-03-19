#!/usr/bin/env python3
"""
Minecraft Username Sniper Notifications

This module handles notifications for various events through different channels.
Supports Discord webhooks, email, and desktop notifications.
"""

import os
import json
import smtplib
import logging
import requests
import platform
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore
from datetime import datetime

# Constants
CONFIG_FILE = "notification_config.json"

class NotificationManager:
    """Handles various notification methods"""
    
    def __init__(self, config_file=CONFIG_FILE):
        """Initialize the notification manager with configuration"""
        self.config_file = config_file
        self.config = self._load_config()
        self.notification_threads = []
    
    def _load_config(self):
        """Load notification configuration from file"""
        default_config = {
            "discord": {
                "enabled": False,
                "webhook_url": "",
                "username": "Minecraft Sniper",
                "avatar_url": "https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/img/minecraft-logo.png"
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "from_email": "",
                "to_email": ""
            },
            "desktop": {
                "enabled": True
            },
            "events": {
                "username_available": True,
                "username_claimed": True,
                "drop_time_found": True,
                "authentication_success": True,
                "error": True
            }
        }
        
        # Create default config file if it doesn't exist
        if not os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                logging.info(f"{Fore.GREEN}Created default notification configuration at {self.config_file}")
            except Exception as e:
                logging.error(f"{Fore.RED}Failed to create default notification config: {str(e)}")
            
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Update with any missing default values
            for category, settings in default_config.items():
                if category not in config:
                    config[category] = settings
                elif isinstance(settings, dict):
                    for key, value in settings.items():
                        if key not in config[category]:
                            config[category][key] = value
            
            return config
        except Exception as e:
            logging.error(f"{Fore.RED}Error loading notification config: {str(e)}")
            return default_config
    
    def save_config(self):
        """Save the current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"{Fore.RED}Error saving notification config: {str(e)}")
            return False
    
    def _should_notify(self, event_type):
        """Check if notifications are enabled for this event type"""
        return self.config["events"].get(event_type, False)
    
    def _format_message(self, event_type, username=None, details=None):
        """Format a message based on the event type"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if event_type == "username_available":
            return f"🎯 USERNAME AVAILABLE! '{username}' is now available for claiming! ({timestamp})"
        
        elif event_type == "username_claimed":
            return f"✅ USERNAME CLAIMED! Successfully claimed '{username}'! ({timestamp})"
        
        elif event_type == "drop_time_found":
            drop_time = details.get("drop_time", "Unknown")
            time_until = details.get("time_until", "Unknown")
            return f"⏰ DROP TIME FOUND! '{username}' will be available at {drop_time} (in {time_until}) ({timestamp})"
        
        elif event_type == "authentication_success":
            current_user = details.get("current_user", "Unknown")
            return f"🔐 AUTHENTICATION SUCCESSFUL! Logged in as '{current_user}' ({timestamp})"
        
        elif event_type == "error":
            error_msg = details.get("error", "Unknown error")
            return f"❌ ERROR: {error_msg} ({timestamp})"
        
        else:
            return f"📢 NOTIFICATION: {details} ({timestamp})"
    
    def notify(self, event_type, username=None, details=None, immediate=False):
        """
        Send a notification for an event
        
        Args:
            event_type: Type of event (username_available, username_claimed, etc.)
            username: Related username (if applicable)
            details: Additional details as a dictionary
            immediate: If True, send notification immediately; otherwise, use a background thread
        """
        if not self._should_notify(event_type):
            return False
        
        message = self._format_message(event_type, username, details)
        
        if immediate:
            return self._send_notifications(event_type, message, username, details)
        else:
            # Send notifications in a background thread
            thread = threading.Thread(
                target=self._send_notifications,
                args=(event_type, message, username, details)
            )
            thread.daemon = True
            thread.start()
            self.notification_threads.append(thread)
            return True
    
    def _send_notifications(self, event_type, message, username=None, details=None):
        """Send notifications through all enabled channels"""
        success = False
        
        # Desktop notification
        if self.config["desktop"]["enabled"]:
            self._send_desktop_notification(event_type, message)
            success = True
        
        # Discord notification
        if self.config["discord"]["enabled"]:
            self._send_discord_notification(event_type, message, username, details)
            success = True
        
        # Email notification
        if self.config["email"]["enabled"]:
            self._send_email_notification(event_type, message, username, details)
            success = True
        
        return success
    
    def _send_desktop_notification(self, event_type, message):
        """Send a desktop notification"""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows notification using PowerShell
                from subprocess import call
                ps_cmd = f'powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; ' \
                        f'[System.Windows.Forms.MessageBox]::Show(\'{message}\', \'Minecraft Sniper\');"'
                call(ps_cmd, shell=True)
                return True
                
            elif system == "Darwin":  # macOS
                # macOS notification using osascript
                from subprocess import call
                title = "Minecraft Sniper"
                script = f'display notification "{message}" with title "{title}"'
                call(["osascript", "-e", script])
                return True
                
            elif system == "Linux":
                # Linux notification using notify-send
                from subprocess import call
                call(["notify-send", "Minecraft Sniper", message])
                return True
                
            else:
                logging.warning(f"{Fore.YELLOW}Desktop notifications not supported on {system}")
                return False
                
        except Exception as e:
            logging.error(f"{Fore.RED}Error sending desktop notification: {str(e)}")
            return False
    
    def _send_discord_notification(self, event_type, message, username=None, details=None):
        """Send a notification to a Discord webhook"""
        if not self.config["discord"]["webhook_url"]:
            return False
        
        webhook_url = self.config["discord"]["webhook_url"]
        webhook_username = self.config["discord"]["username"]
        avatar_url = self.config["discord"]["avatar_url"]
        
        # Create embed based on event type
        color = 0x55FF55  # Green by default
        title = "Minecraft Username Update"
        
        if event_type == "username_available":
            color = 0x55FF55  # Green
            title = "Username Available!"
        elif event_type == "username_claimed":
            color = 0x5555FF  # Blue
            title = "Username Claimed!"
        elif event_type == "drop_time_found":
            color = 0xFFAA00  # Orange
            title = "Drop Time Found!"
        elif event_type == "authentication_success":
            color = 0x00AAFF  # Light Blue
            title = "Authentication Successful"
        elif event_type == "error":
            color = 0xFF5555  # Red
            title = "Error"
        
        try:
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            
            if username:
                embed["fields"] = [{"name": "Username", "value": username, "inline": True}]
            
            if details:
                # Add details as fields
                if "fields" not in embed:
                    embed["fields"] = []
                
                for key, value in details.items():
                    if key != "error" and value is not None:
                        embed["fields"].append({
                            "name": key.replace("_", " ").title(),
                            "value": str(value),
                            "inline": True
                        })
            
            data = {
                "username": webhook_username,
                "avatar_url": avatar_url,
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=data)
            
            if response.status_code == 204:
                logging.debug(f"Discord notification sent successfully for {event_type}")
                return True
            else:
                logging.error(f"{Fore.RED}Failed to send Discord notification: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"{Fore.RED}Error sending Discord notification: {str(e)}")
            return False
    
    def _send_email_notification(self, event_type, message, username=None, details=None):
        """Send an email notification"""
        config = self.config["email"]
        
        if not all([config["smtp_server"], config["smtp_username"], 
                   config["smtp_password"], config["from_email"], config["to_email"]]):
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = config["to_email"]
            
            # Set subject based on event type
            if event_type == "username_available":
                msg['Subject'] = f"🎯 Minecraft Username Available: {username}"
            elif event_type == "username_claimed":
                msg['Subject'] = f"✅ Minecraft Username Claimed: {username}"
            elif event_type == "drop_time_found":
                msg['Subject'] = f"⏰ Minecraft Username Drop Time: {username}"
            elif event_type == "authentication_success":
                msg['Subject'] = f"🔐 Minecraft Authentication Successful"
            elif event_type == "error":
                msg['Subject'] = f"❌ Minecraft Sniper Error"
            else:
                msg['Subject'] = f"📢 Minecraft Sniper Notification"
            
            # Email body
            body = f"<html><body><h2>{msg['Subject']}</h2><p>{message}</p>"
            
            # Add details if present
            if details:
                body += "<h3>Details:</h3><ul>"
                for key, value in details.items():
                    if value is not None:
                        body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
                body += "</ul>"
            
            body += "</body></html>"
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["smtp_username"], config["smtp_password"])
            text = msg.as_string()
            server.sendmail(config["from_email"], config["to_email"], text)
            server.quit()
            
            logging.debug(f"Email notification sent successfully for {event_type}")
            return True
            
        except Exception as e:
            logging.error(f"{Fore.RED}Error sending email notification: {str(e)}")
            return False
    
    def configure_discord(self, webhook_url, username="Minecraft Sniper", avatar_url=None):
        """Configure Discord notifications"""
        self.config["discord"]["enabled"] = bool(webhook_url)
        self.config["discord"]["webhook_url"] = webhook_url
        self.config["discord"]["username"] = username
        
        if avatar_url:
            self.config["discord"]["avatar_url"] = avatar_url
        
        return self.save_config()
    
    def configure_email(self, smtp_server, smtp_port, username, password, from_email, to_email):
        """Configure email notifications"""
        self.config["email"]["enabled"] = all([smtp_server, username, password, from_email, to_email])
        self.config["email"]["smtp_server"] = smtp_server
        self.config["email"]["smtp_port"] = int(smtp_port)
        self.config["email"]["smtp_username"] = username
        self.config["email"]["smtp_password"] = password
        self.config["email"]["from_email"] = from_email
        self.config["email"]["to_email"] = to_email
        
        return self.save_config()
    
    def configure_events(self, username_available=True, username_claimed=True, 
                       drop_time_found=True, authentication_success=True, error=True):
        """Configure which events trigger notifications"""
        self.config["events"]["username_available"] = username_available
        self.config["events"]["username_claimed"] = username_claimed
        self.config["events"]["drop_time_found"] = drop_time_found
        self.config["events"]["authentication_success"] = authentication_success
        self.config["events"]["error"] = error
        
        return self.save_config()
    
    def toggle_discord(self, enabled=None):
        """Toggle Discord notifications"""
        if enabled is None:
            enabled = not self.config["discord"]["enabled"]
        
        self.config["discord"]["enabled"] = enabled
        return self.save_config()
    
    def toggle_email(self, enabled=None):
        """Toggle email notifications"""
        if enabled is None:
            enabled = not self.config["email"]["enabled"]
        
        self.config["email"]["enabled"] = enabled
        return self.save_config()
    
    def toggle_desktop(self, enabled=None):
        """Toggle desktop notifications"""
        if enabled is None:
            enabled = not self.config["desktop"]["enabled"]
        
        self.config["desktop"]["enabled"] = enabled
        return self.save_config()
    
    def test_all_notifications(self):
        """Send a test notification through all configured channels"""
        return self.notify(
            "test", 
            username="testuser", 
            details={"message": "This is a test notification"},
            immediate=True
        )


if __name__ == "__main__":
    # Simple test of the notification manager
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    manager = NotificationManager()
    
    # Test desktop notification
    print("Sending test desktop notification...")
    manager.notify("username_available", username="coolname", immediate=True)
    
    # To configure Discord
    # manager.configure_discord("your_webhook_url_here")
    
    # To configure email
    # manager.configure_email("smtp.gmail.com", 587, "your_email@gmail.com", 
    #                      "your_password", "your_email@gmail.com", "recipient@example.com")
    
    # Test all notifications
    # manager.test_all_notifications() 