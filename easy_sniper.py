#!/usr/bin/env python3
"""
Easy Minecraft Username Sniper

A simplified interface for the Minecraft Username Sniper tool designed for non-technical users.
"""

import os
import sys
import time
import datetime
import colorama
from colorama import Fore, Style, init

# Initialize colorama for colors
init(autoreset=True)

# Try to import our modules, show friendly error if not installed
try:
    from minecraft_auth import MinecraftAuth
    from name_utils import NameChecker
    from sniper import Sniper
except ImportError:
    print(f"{Fore.RED}Error: Required modules not found.")
    print(f"{Fore.YELLOW}Please run the setup script first:")
    print(f"{Fore.CYAN}python setup.py")
    sys.exit(1)

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """Display a friendly banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.GREEN}  __  __ _                            __ _   {Fore.CYAN}              ║
{Fore.CYAN}║ {Fore.GREEN}  |  \/  (_)_ __   ___  ___ _ __ __ _/ _| |_ {Fore.CYAN}              ║
{Fore.CYAN}║ {Fore.GREEN}  | |\/| | | '_ \ / _ \/ __| '__/ _` | |_| __|{Fore.CYAN}             ║
{Fore.CYAN}║ {Fore.GREEN}  | |  | | | | | |  __/ (__| | | (_| |  _| |_ {Fore.CYAN}             ║
{Fore.CYAN}║ {Fore.GREEN}  |_|  |_|_|_| |_|\___|\___|_|  \__,_|_|  \__|{Fore.CYAN}             ║
{Fore.CYAN}║                                                           ║
{Fore.CYAN}║ {Fore.YELLOW}  EASY USERNAME SNIPER - BEGINNER FRIENDLY EDITION  {Fore.CYAN}      ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"{Fore.YELLOW}This tool helps you check, monitor, and claim Minecraft usernames.")
    print()

def show_main_menu():
    """Display the main menu options"""
    print(f"{Fore.CYAN}╔════════════════ MAIN MENU ════════════════╗")
    print(f"{Fore.CYAN}║                                           ║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}1. Check if a username is available     {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}2. Monitor a username until available   {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}3. Try to claim a username              {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}4. Check your account status            {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}5. Help & Instructions                  {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}0. Exit                                 {Fore.CYAN}║")
    print(f"{Fore.CYAN}║                                           ║")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝")
    
    while True:
        try:
            choice = input(f"\n{Fore.GREEN}Enter your choice (0-5): {Style.RESET_ALL}")
            choice = int(choice)
            if 0 <= choice <= 5:
                return choice
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a number between 0 and 5.")
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number.")

def check_username_menu():
    """Menu for checking username availability"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ CHECK USERNAME AVAILABILITY ════════╗")
    print(f"{Fore.CYAN}║                                             ║")
    print(f"{Fore.CYAN}║  Enter the username you want to check.      ║")
    print(f"{Fore.CYAN}║  The tool will tell you if it's available   ║")
    print(f"{Fore.CYAN}║  or when it might become available.         ║")
    print(f"{Fore.CYAN}║                                             ║")
    print(f"{Fore.CYAN}╚═════════════════════════════════════════════╝")
    
    username = input(f"\n{Fore.GREEN}Enter a username to check: {Style.RESET_ALL}").strip()
    
    if not username:
        print(f"{Fore.RED}No username entered. Returning to main menu...")
        time.sleep(2)
        return
    
    print(f"\n{Fore.CYAN}Checking if username '{username}' is available...")
    
    # Initialize the sniper
    sniper = Sniper()
    
    if sniper.check_username(username):
        print(f"\n{Fore.GREEN}Good news! Username '{username}' is currently AVAILABLE!")
        print(f"{Fore.YELLOW}You can claim it now by selecting option 3 from the main menu.")
    else:
        print(f"\n{Fore.RED}Username '{username}' is currently taken.")
        
        # Try to get drop time from NameMC
        drop_time = sniper.get_drop_time(username)
        if drop_time:
            time_until = drop_time - datetime.datetime.now()
            days = time_until.days
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print(f"{Fore.YELLOW}This username may become available at: {drop_time}")
            print(f"{Fore.YELLOW}Time until available: {days}d {hours}h {minutes}m {seconds}s")
            print(f"{Fore.YELLOW}You can use the monitor option to keep checking until it's available.")
        else:
            print(f"{Fore.YELLOW}We couldn't find when this username might become available.")
            print(f"{Fore.YELLOW}You can still use the monitor option to periodically check if it becomes available.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def monitor_username_menu():
    """Menu for monitoring a username until it becomes available"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ MONITOR USERNAME AVAILABILITY ════════╗")
    print(f"{Fore.CYAN}║                                               ║")
    print(f"{Fore.CYAN}║  This will continuously check a username      ║")
    print(f"{Fore.CYAN}║  until it becomes available.                  ║")
    print(f"{Fore.CYAN}║                                               ║")
    print(f"{Fore.CYAN}║  The tool will notify you when the username   ║")
    print(f"{Fore.CYAN}║  becomes available. You can stop at any time  ║")
    print(f"{Fore.CYAN}║  by pressing Ctrl+C.                          ║")
    print(f"{Fore.CYAN}║                                               ║")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════════╝")
    
    username = input(f"\n{Fore.GREEN}Enter a username to monitor: {Style.RESET_ALL}").strip()
    
    if not username:
        print(f"{Fore.RED}No username entered. Returning to main menu...")
        time.sleep(2)
        return
    
    try:
        check_interval = float(input(f"{Fore.GREEN}How often to check (in seconds, recommended 2-5): {Style.RESET_ALL}"))
    except ValueError:
        print(f"{Fore.YELLOW}Invalid value, using default of 3 seconds.")
        check_interval = 3.0
    
    auto_claim = input(f"{Fore.GREEN}Automatically claim when available? (y/n): {Style.RESET_ALL}").lower().startswith('y')
    
    # Initialize the sniper
    sniper = Sniper()
    
    if auto_claim:
        print(f"{Fore.CYAN}You'll need to log in to your Microsoft account to claim the username.")
        if not sniper.authenticate():
            print(f"{Fore.RED}Authentication failed. Cannot auto-claim without logging in.")
            auto_claim = False
    
    print(f"\n{Fore.CYAN}Starting to monitor username '{username}'...")
    print(f"{Fore.CYAN}Checking every {check_interval} seconds. Press Ctrl+C to stop.")
    print(f"{Fore.CYAN}This window will notify you when the username becomes available.")
    
    try:
        result = sniper.monitor_username(username, check_interval, auto_claim)
        if result:
            print(f"\n{Fore.GREEN}Username '{username}' is now available!")
            
            if auto_claim:
                if sniper.claim_username(username):
                    print(f"{Fore.GREEN}Successfully claimed username '{username}'!")
                else:
                    print(f"{Fore.RED}Failed to claim username '{username}'")
                    print(f"{Fore.YELLOW}You can try to claim it manually using option 3 from the main menu.")
            else:
                print(f"{Fore.YELLOW}You can now claim this username using option 3 from the main menu.")
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring stopped by user")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def claim_username_menu():
    """Menu for claiming a username"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ CLAIM A MINECRAFT USERNAME ════════╗")
    print(f"{Fore.CYAN}║                                           ║")
    print(f"{Fore.CYAN}║  This will attempt to claim a username    ║")
    print(f"{Fore.CYAN}║  for your Minecraft account.              ║")
    print(f"{Fore.CYAN}║                                           ║")
    print(f"{Fore.CYAN}║  You will need to log in to your          ║")
    print(f"{Fore.CYAN}║  Microsoft account.                       ║")
    print(f"{Fore.CYAN}║                                           ║")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════╝")
    
    username = input(f"\n{Fore.GREEN}Enter the username you want to claim: {Style.RESET_ALL}").strip()
    
    if not username:
        print(f"{Fore.RED}No username entered. Returning to main menu...")
        time.sleep(2)
        return
    
    sniper = Sniper()
    
    # Check if the username is available first
    print(f"{Fore.CYAN}Checking if username '{username}' is available...")
    if not sniper.check_username(username):
        print(f"\n{Fore.RED}Username '{username}' is currently not available.")
        print(f"{Fore.YELLOW}You can only claim available usernames.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.GREEN}Username '{username}' is available!")
    print(f"{Fore.CYAN}You need to log in to your Microsoft account to claim it.")
    
    # Handle authentication
    if not sniper.authenticate():
        print(f"\n{Fore.RED}Authentication failed. Cannot claim username without logging in.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    # Check eligibility for name change
    if not sniper.is_eligible_for_name_change():
        print(f"\n{Fore.RED}Your account is not eligible for a name change at this time.")
        print(f"{Fore.YELLOW}You might need to wait 30 days after your last name change.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    # Confirm the claim
    confirm = input(f"\n{Fore.YELLOW}Are you sure you want to claim the username '{username}'? (y/n): {Style.RESET_ALL}")
    if not confirm.lower().startswith('y'):
        print(f"{Fore.YELLOW}Claim cancelled. Returning to main menu...")
        time.sleep(2)
        return
    
    # Attempt to claim the username
    print(f"\n{Fore.CYAN}Attempting to claim username '{username}'...")
    
    if sniper.claim_username(username):
        print(f"\n{Fore.GREEN}Success! You have claimed the username '{username}'!")
        print(f"{Fore.GREEN}The change should be reflected in your Minecraft account shortly.")
    else:
        print(f"\n{Fore.RED}Failed to claim username '{username}'.")
        print(f"{Fore.YELLOW}This could be because someone else claimed it first")
        print(f"{Fore.YELLOW}or there was an issue with the Minecraft API.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def check_account_status_menu():
    """Menu for checking account status"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ CHECK ACCOUNT STATUS ════════╗")
    print(f"{Fore.CYAN}║                                     ║")
    print(f"{Fore.CYAN}║  This will check your account's     ║")
    print(f"{Fore.CYAN}║  current status and whether you're  ║")
    print(f"{Fore.CYAN}║  eligible for a name change.        ║")
    print(f"{Fore.CYAN}║                                     ║")
    print(f"{Fore.CYAN}╚═════════════════════════════════════╝")
    
    print(f"\n{Fore.CYAN}You need to log in to your Microsoft account to check your status.")
    
    # Initialize the sniper
    sniper = Sniper()
    
    if not sniper.authenticate():
        print(f"\n{Fore.RED}Authentication failed. Cannot check account status without logging in.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    # Get account status
    current_username = sniper.auth.get_current_username()
    eligible = sniper.is_eligible_for_name_change()
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Account Status")
    print(f"{Fore.CYAN}{'='*50}")
    print(f"Current Username: {Fore.GREEN}{current_username}")
    print(f"Eligible for name change: {Fore.GREEN if eligible else Fore.RED}{eligible}")
    
    if not eligible:
        print(f"{Fore.YELLOW}You can usually change your name once every 30 days.")
    
    print(f"{Fore.CYAN}{'='*50}")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def show_help_menu():
    """Display help and instructions"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ HELP & INSTRUCTIONS ════════╗")
    print(f"{Fore.CYAN}║                                    ║")
    print(f"{Fore.CYAN}╚════════════════════════════════════╝")
    
    print(f"\n{Fore.YELLOW}How to Use This Tool:")
    
    print(f"\n{Fore.GREEN}Check if a username is available:")
    print(f"{Fore.WHITE}Select option 1 from the main menu.")
    print(f"{Fore.WHITE}Enter the username you're interested in.")
    print(f"{Fore.WHITE}The tool will tell you if it's available or when it might become available.")
    
    print(f"\n{Fore.GREEN}Monitor a username until it becomes available:")
    print(f"{Fore.WHITE}Select option 2 from the main menu.")
    print(f"{Fore.WHITE}Enter the username you want to monitor.")
    print(f"{Fore.WHITE}The tool will continuously check the username and notify you when it's available.")
    print(f"{Fore.WHITE}You can choose to automatically claim it when it becomes available.")
    
    print(f"\n{Fore.GREEN}Claim a username:")
    print(f"{Fore.WHITE}Select option 3 from the main menu.")
    print(f"{Fore.WHITE}Enter the username you want to claim.")
    print(f"{Fore.WHITE}You'll need to log in to your Microsoft account.")
    print(f"{Fore.WHITE}The tool will check if the username is available and if your account is eligible.")
    print(f"{Fore.WHITE}If everything checks out, it will claim the username for you.")
    
    print(f"\n{Fore.GREEN}Check your account status:")
    print(f"{Fore.WHITE}Select option 4 from the main menu.")
    print(f"{Fore.WHITE}You'll need to log in to your Microsoft account.")
    print(f"{Fore.WHITE}The tool will show your current username and whether you're eligible for a name change.")
    
    print(f"\n{Fore.YELLOW}Important Tips:")
    print(f"{Fore.WHITE}1. You can only change your Minecraft username once every 30 days.")
    print(f"{Fore.WHITE}2. When a user changes their name, the old name becomes available after some time.")
    print(f"{Fore.WHITE}3. Some premium names may never become available.")
    print(f"{Fore.WHITE}4. Use this tool responsibly and be aware of Minecraft's terms of service.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def main():
    """Main function to run the easy sniper interface"""
    while True:
        clear_screen()
        display_banner()
        choice = show_main_menu()
        
        if choice == 0:
            clear_screen()
            print(f"{Fore.CYAN}Thank you for using Easy Minecraft Username Sniper!")
            break
        elif choice == 1:
            check_username_menu()
        elif choice == 2:
            monitor_username_menu()
        elif choice == 3:
            claim_username_menu()
        elif choice == 4:
            check_account_status_menu()
        elif choice == 5:
            show_help_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {str(e)}")
        print(f"{Fore.RED}If this problem persists, please report it on GitHub.")
        input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}") 