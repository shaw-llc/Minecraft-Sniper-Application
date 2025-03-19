#!/usr/bin/env python3
"""
Minecraft Username Sniper Setup Script

This script helps set up the Minecraft Username Sniper for users who are
not familiar with coding or command-line interfaces.
"""

import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

# Colors for terminal output (simplified for non-technical users)
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_color(text, color):
    """Print colored text if the terminal supports it"""
    if os.name == "nt":  # Windows
        try:
            import colorama
            colorama.init()
            supports_color = True
        except ImportError:
            supports_color = False
    else:
        supports_color = True
    
    if supports_color:
        print(f"{color}{text}{Colors.RESET}")
    else:
        print(text)

def print_banner():
    """Print a welcome banner"""
    banner = """
================================================================================
                  MINECRAFT USERNAME SNIPER - SETUP ASSISTANT
================================================================================
  This assistant will help you install everything needed to run the sniper tool.
  Just follow the instructions on screen. Updated and working as of October 2023.
================================================================================
"""
    print_color(banner, Colors.CYAN)

def check_python_version():
    """Check if Python version is compatible"""
    print_color("Checking Python version...", Colors.BLUE)
    major, minor, _ = platform.python_version_tuple()
    major, minor = int(major), int(minor)
    
    if major < 3 or (major == 3 and minor < 6):
        print_color(f"Error: Python 3.6 or higher is required, but you have {major}.{minor}", Colors.RED)
        print_color("Please install a newer version of Python from https://python.org", Colors.YELLOW)
        print_color("Be sure to check 'Add Python to PATH' during installation!", Colors.YELLOW)
        return False
    
    print_color(f"Python version {major}.{minor} is compatible! ✓", Colors.GREEN)
    return True

def install_dependencies():
    """Install required Python packages"""
    print_color("\nInstalling required dependencies...", Colors.BLUE)
    
    try:
        packages = ["requests", "colorama", "python-dotenv", "urllib3", "beautifulsoup4"]
        
        # Ask the user for permission
        print_color("The following packages will be installed:", Colors.YELLOW)
        for pkg in packages:
            print(f"  - {pkg}")
        
        choice = input("\nDo you want to install these packages? (y/n, default: y): ").lower()
        if choice and choice not in ['y', 'yes']:
            print_color("Setup aborted by user.", Colors.YELLOW)
            return False
        
        # Install packages using pip
        print_color("\nInstalling packages with pip...", Colors.BLUE)
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        except subprocess.CalledProcessError:
            print_color("Warning: Failed to upgrade pip, but we'll continue anyway.", Colors.YELLOW)
        
        success = True
        for package in packages:
            print_color(f"Installing {package}...", Colors.YELLOW)
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print_color(f"  ✓ {package} installed successfully", Colors.GREEN)
            except subprocess.CalledProcessError as e:
                print_color(f"  ✗ Error installing {package}: {str(e)}", Colors.RED)
                success = False
        
        if success:
            print_color("\nAll packages installed successfully! ✓", Colors.GREEN)
        else:
            print_color("\nSome packages failed to install. You may need to install them manually:", Colors.RED)
            print_color(f"pip install {' '.join(packages)}", Colors.YELLOW)
            print_color("\nDo you want to continue anyway? (y/n, default: y): ", Colors.YELLOW)
            choice = input().lower()
            if choice and choice not in ['y', 'yes']:
                return False
        
        return True
    
    except Exception as e:
        print_color(f"\nError installing packages: {str(e)}", Colors.RED)
        print_color("You can try to install them manually using the following command:", Colors.YELLOW)
        print_color(f"pip install {' '.join(packages)}", Colors.YELLOW)
        
        print_color("\nDo you want to continue anyway? (y/n, default: y): ", Colors.YELLOW)
        choice = input().lower()
        if choice and choice not in ['y', 'yes']:
            return False
        return True

def create_env_file():
    """Create a .env file if the user wants to use credentials"""
    print_color("\nSetting up the configuration file...", Colors.BLUE)
    
    if os.path.exists(".env"):
        print_color("A configuration file (.env) already exists.", Colors.YELLOW)
        choice = input("Do you want to create a new one? (y/n, default: n): ").lower()
        if not choice or choice not in ['y', 'yes']:
            print_color("Keeping the existing .env file. ✓", Colors.GREEN)
            return True
    
    print_color("\nThe sniper tool can use your Microsoft account credentials.", Colors.YELLOW)
    print_color("IMPORTANT SECURITY NOTE:", Colors.RED)
    print_color("  - It's recommended to use the browser authentication instead of storing credentials", Colors.YELLOW)
    print_color("  - The tool will open a browser where you can log in securely", Colors.YELLOW)
    print_color("  - Only create a .env file if you know what you're doing", Colors.YELLOW)
    print_color("  - Your password will be stored in plain text if you choose this option", Colors.RED)
    
    choice = input("\nDo you want to create a .env file with your credentials? (y/n, default: n): ").lower()
    if not choice or choice not in ['y', 'yes']:
        print_color("Skipping .env file creation. The tool will use browser authentication instead. ✓", Colors.GREEN)
        return True
    
    # Create .env file
    print_color("\nCreating .env file...", Colors.BLUE)
    
    email = input("Enter your Microsoft account email: ")
    password = input("Enter your Microsoft account password: ")
    
    try:
        with open(".env", "w") as f:
            f.write("# Minecraft Username Sniper - Environment Variables\n")
            f.write("# This file contains sensitive information. Do not share it with anyone.\n\n")
            f.write(f"EMAIL={email}\n")
            f.write(f"PASSWORD={password}\n")
            f.write("\n# API settings (optional)\n")
            f.write("BASE_DELAY=1.5\n")
            f.write("MAX_THREADS=5\n")
        
        print_color("\n.env file created successfully! ✓", Colors.GREEN)
        print_color("Your credentials are stored in the .env file.", Colors.YELLOW)
        print_color("You can delete this file at any time to use browser authentication instead.", Colors.YELLOW)
        return True
    
    except Exception as e:
        print_color(f"\nError creating .env file: {str(e)}", Colors.RED)
        print_color("You can manually create a .env file based on the .env.example file.", Colors.YELLOW)
        return False

def create_shortcuts():
    """Create desktop shortcuts for Windows users"""
    if os.name != "nt":
        # Not Windows, so skip shortcut creation
        return True
    
    print_color("\nCreating desktop shortcut (Windows only)...", Colors.BLUE)
    
    try:
        # Get current directory and desktop path
        current_dir = os.path.abspath(os.path.dirname(__file__))
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Check if desktop directory exists
        if not os.path.exists(desktop_dir):
            print_color(f"Could not find Desktop directory at {desktop_dir}", Colors.YELLOW)
            print_color("Skipping shortcut creation. You can still run the tool using easy_sniper.py", Colors.YELLOW)
            return True
        
        # Create shortcut using PowerShell (more reliable than vbs)
        shortcut_path = os.path.join(desktop_dir, "Minecraft Username Sniper.lnk")
        target_path = os.path.join(current_dir, "easy_sniper.py")
        
        # Create PowerShell command to create shortcut
        ps_command = f'''
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{sys.executable}"
        $Shortcut.Arguments = "{target_path}"
        $Shortcut.WorkingDirectory = "{current_dir}"
        $Shortcut.IconLocation = "{sys.executable}, 0"
        $Shortcut.Description = "Minecraft Username Sniper"
        $Shortcut.Save()
        '''
        
        # Execute PowerShell command
        subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
        
        if os.path.exists(shortcut_path):
            print_color(f"Desktop shortcut created successfully! ✓", Colors.GREEN)
            print_color(f"You can now launch the tool by double-clicking the shortcut on your desktop.", Colors.GREEN)
        else:
            print_color(f"Failed to create shortcut, but setup will continue.", Colors.YELLOW)
            print_color(f"You can still run the tool by double-clicking easy_sniper.py", Colors.YELLOW)
        
        return True
    
    except Exception as e:
        print_color(f"Error creating shortcut: {str(e)}", Colors.RED)
        print_color(f"You can still run the tool by double-clicking easy_sniper.py", Colors.YELLOW)
        return True

def final_instructions():
    """Show final instructions to the user"""
    print_color("\n================================================================================", Colors.CYAN)
    print_color("                   SETUP COMPLETE! YOU'RE READY TO GO!", Colors.GREEN)
    print_color("================================================================================", Colors.CYAN)
    print_color("\nHow to use the Minecraft Username Sniper:", Colors.YELLOW)
    
    if os.name == "nt":  # Windows
        print_color("\n1. Double-click the 'Minecraft Username Sniper' shortcut on your desktop", Colors.WHITE)
        print_color("   OR", Colors.WHITE)
        print_color("   Double-click easy_sniper.py in this folder", Colors.WHITE)
    else:  # macOS or Linux
        print_color("\n1. Open Terminal", Colors.WHITE)
        print_color("2. Navigate to this directory:", Colors.WHITE)
        print_color(f"   cd {os.path.abspath(os.path.dirname(__file__))}", Colors.WHITE)
        print_color("3. Run the easy interface:", Colors.WHITE)
        print_color("   python3 easy_sniper.py", Colors.WHITE)
    
    print_color("\nThe first time you use the tool, you'll need to log in with your Microsoft account.", Colors.YELLOW)
    print_color("A browser window will open for secure login.", Colors.YELLOW)
    
    print_color("\nNeed help? See the README.md file for detailed instructions and troubleshooting.", Colors.CYAN)
    print_color("================================================================================", Colors.CYAN)

def main():
    """Main setup function"""
    # Clear the screen and show banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    print_color("Welcome to the Minecraft Username Sniper setup wizard!", Colors.GREEN)
    print_color("This will help you install everything needed to run the tool.\n", Colors.GREEN)
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return False
    
    # Install required packages
    if not install_dependencies():
        input("\nSetup failed. Press Enter to exit...")
        return False
    
    # Create .env file
    create_env_file()
    
    # Create desktop shortcut (Windows only)
    create_shortcuts()
    
    # Show final instructions
    final_instructions()
    
    input("\nPress Enter to finish setup...")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\nSetup interrupted by user.", Colors.YELLOW)
    except Exception as e:
        print_color(f"\nAn unexpected error occurred during setup: {str(e)}", Colors.RED)
        print_color("Please try running the setup again.", Colors.YELLOW)
        input("\nPress Enter to exit...") 