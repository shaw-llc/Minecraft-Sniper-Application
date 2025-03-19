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
  Just follow the instructions on screen.
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
        return False
    
    print_color(f"Python version {major}.{minor} is compatible. Continuing setup...", Colors.GREEN)
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
        
        choice = input("\nDo you want to install these packages? (y/n): ").lower()
        if choice != 'y' and choice != 'yes':
            print_color("Setup aborted by user.", Colors.YELLOW)
            return False
        
        # Install packages using pip
        print_color("\nInstalling packages with pip...", Colors.BLUE)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        for package in packages:
            print_color(f"Installing {package}...", Colors.YELLOW)
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print_color("\nAll packages installed successfully!", Colors.GREEN)
        return True
    
    except Exception as e:
        print_color(f"\nError installing packages: {str(e)}", Colors.RED)
        print_color("You can try to install them manually using the following command:", Colors.YELLOW)
        print("pip install requests colorama python-dotenv urllib3 beautifulsoup4")
        return False

def create_env_file():
    """Create a .env file if the user wants to use credentials"""
    print_color("\nSetting up the configuration file...", Colors.BLUE)
    
    if os.path.exists(".env"):
        print_color("A configuration file (.env) already exists.", Colors.YELLOW)
        choice = input("Do you want to create a new one? (y/n): ").lower()
        if choice != 'y' and choice != 'yes':
            print_color("Keeping the existing .env file.", Colors.GREEN)
            return True
    
    print_color("\nThe sniper tool can use your Microsoft account credentials.", Colors.YELLOW)
    print_color("NOTE: It's recommended to use the browser authentication instead of storing credentials.", Colors.YELLOW)
    print_color("      The tool will open a browser where you can log in securely.", Colors.YELLOW)
    print_color("      Only create a .env file if you know what you're doing.", Colors.YELLOW)
    
    choice = input("\nDo you want to create a .env file with your credentials? (y/n): ").lower()
    if choice != 'y' and choice != 'yes':
        print_color("Skipping .env file creation. The tool will use browser authentication.", Colors.GREEN)
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
        
        print_color("\n.env file created successfully!", Colors.GREEN)
        print_color("Your credentials are stored in the .env file.", Colors.YELLOW)
        print_color("You can delete this file at any time to use browser authentication instead.", Colors.YELLOW)
        return True
    
    except Exception as e:
        print_color(f"\nError creating .env file: {str(e)}", Colors.RED)
        print_color("You can manually create a .env file based on the .env.example file.", Colors.YELLOW)
        return False

def create_shortcuts():
    """Create desktop shortcuts for Windows users"""
    if os.name != "nt":  # Only for Windows
        return True
    
    print_color("\nCreating shortcuts for Windows...", Colors.BLUE)
    
    choice = input("Create a desktop shortcut to the easy sniper tool? (y/n): ").lower()
    if choice != 'y' and choice != 'yes':
        print_color("Skipping shortcut creation.", Colors.YELLOW)
        return True
    
    try:
        import win32com.client
        desktop = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
        
        # Create shortcut for the easy_sniper.py
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(desktop / "Minecraft Username Sniper.lnk"))
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = str(Path(os.getcwd()) / "easy_sniper.py")
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print_color("\nShortcut created on your desktop!", Colors.GREEN)
        print_color("You can now start the tool by double-clicking the shortcut.", Colors.GREEN)
        return True
    
    except ImportError:
        print_color("\nCouldn't create shortcut: pywin32 package not installed.", Colors.YELLOW)
        print_color("You can start the tool by running 'python easy_sniper.py'", Colors.YELLOW)
        return True
    
    except Exception as e:
        print_color(f"\nError creating shortcut: {str(e)}", Colors.RED)
        print_color("You can start the tool by running 'python easy_sniper.py'", Colors.YELLOW)
        return True

def final_instructions():
    """Show final instructions to the user"""
    print_color("\n================================================================================", Colors.CYAN)
    print_color("                          SETUP COMPLETED SUCCESSFULLY", Colors.GREEN)
    print_color("================================================================================", Colors.CYAN)
    print_color("\nTo start the Minecraft Username Sniper, run:", Colors.YELLOW)
    print_color("   python easy_sniper.py", Colors.GREEN)
    
    if os.name == "nt":  # Windows
        print_color("\nOr double-click the shortcut on your desktop (if you created one).", Colors.YELLOW)
    
    print_color("\nImportant Notes:", Colors.YELLOW)
    print_color("1. The tool will guide you through the process with simple menus.", Colors.YELLOW)
    print_color("2. For authentication, a browser window will open where you can log in to your", Colors.YELLOW)
    print_color("   Microsoft account securely.", Colors.YELLOW)
    print_color("3. You can only change your Minecraft username once every 30 days.", Colors.YELLOW)
    print_color("\nIf you encounter any issues, please check the GitHub repository for help.", Colors.YELLOW)
    print_color("================================================================================", Colors.CYAN)

def main():
    """Run the setup assistant"""
    print_banner()
    
    # Check if Python version is compatible
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Install required dependencies
    if not install_dependencies():
        input("Press Enter to continue anyway, or Ctrl+C to abort...")
    
    # Create .env file if needed
    create_env_file()
    
    # Create shortcuts for Windows users
    if os.name == "nt":
        create_shortcuts()
    
    # Show final instructions
    final_instructions()
    
    input("\nPress Enter to exit the setup assistant...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\nSetup aborted by user.", Colors.YELLOW)
    except Exception as e:
        print_color(f"\nAn unexpected error occurred: {str(e)}", Colors.RED)
        input("Press Enter to exit...") 