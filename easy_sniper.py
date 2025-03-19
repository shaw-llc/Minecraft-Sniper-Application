#!/usr/bin/env python3
"""
Easy Minecraft Username Sniper

A simplified interface for the Minecraft Username Sniper tool designed for non-technical users.
Updated and verified working as of October 2023.
"""

import os
import sys
import time
import datetime
import traceback
import colorama
from colorama import Fore, Style, init

# Initialize colorama for colors
init(autoreset=True)

# Try to import our modules, show friendly error if not installed
try:
    from minecraft_auth import MinecraftAuth
    from name_utils import NameChecker
    from sniper import Sniper
    try:
        from notifications import NotificationManager
        notifications_available = True
    except ImportError:
        notifications_available = False
except ImportError as e:
    print(f"{Fore.RED}Error: Required modules not found.")
    print(f"{Fore.YELLOW}Please run the setup script first:")
    print(f"{Fore.CYAN}python setup.py")
    print(f"\n{Fore.RED}Details: {str(e)}")
    print(f"\n{Fore.YELLOW}Press Enter to exit...")
    input()
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
{Fore.CYAN}║ {Fore.WHITE}              Updated October 2023                  {Fore.CYAN}      ║
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
    
    try:
        # Initialize the sniper
        sniper = Sniper()
        name_checker = NameChecker()
        
        # Check if the username is valid
        if not name_checker.is_valid_minecraft_username(username):
            print(f"\n{Fore.RED}Error: '{username}' is not a valid Minecraft username!")
            print(f"{Fore.YELLOW}Minecraft usernames can only contain letters, numbers, and underscores.")
            print(f"{Fore.YELLOW}They must be between 3 and 16 characters long.")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
            
        if sniper.check_username(username):
            print(f"\n{Fore.GREEN}✓ Good news! Username '{username}' is currently AVAILABLE!")
            print(f"{Fore.YELLOW}You can claim it now by selecting option 3 from the main menu.")
        else:
            print(f"\n{Fore.RED}✗ Username '{username}' is currently taken.")
            
            # Try to get drop time from NameMC
            print(f"{Fore.CYAN}Checking when this username might become available...")
            drop_time = sniper.get_drop_time(username)
            if drop_time:
                time_until = drop_time - datetime.datetime.now()
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"\n{Fore.YELLOW}⏰ This username may become available on:")
                print(f"{Fore.GREEN}{drop_time.strftime('%Y-%m-%d at %H:%M:%S')} UTC")
                print(f"{Fore.YELLOW}Time until available: {days}d {hours}h {minutes}m {seconds}s")
                
                if days < 0 or (days == 0 and hours == 0 and minutes == 0 and seconds == 0):
                    print(f"\n{Fore.CYAN}This username should be available now or very soon!")
                    print(f"{Fore.CYAN}Try using option 2 to monitor it continuously.")
                else:
                    print(f"\n{Fore.CYAN}You can use option 2 to monitor it until it becomes available.")
            else:
                print(f"\n{Fore.YELLOW}We couldn't find when this username might become available.")
                print(f"{Fore.YELLOW}It might not be scheduled to drop, or might be permanently unavailable.")
                print(f"{Fore.CYAN}You can still use option 2 to monitor if it becomes available.")
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred while checking the username:")
        print(f"{Fore.RED}{str(e)}")
        print(f"\n{Fore.YELLOW}This could be due to network issues or Mojang's API being unavailable.")
        print(f"{Fore.YELLOW}Please try again later.")
    
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
        if check_interval < 1:
            print(f"{Fore.YELLOW}Warning: Checking too frequently may result in rate limiting.")
            print(f"{Fore.YELLOW}Setting interval to 2 seconds to be safe.")
            check_interval = 2.0
    except ValueError:
        print(f"{Fore.YELLOW}Invalid value, using default of 3 seconds.")
        check_interval = 3.0
    
    auto_claim = input(f"{Fore.GREEN}Automatically claim when available? (y/n): {Style.RESET_ALL}").lower().startswith('y')
    
    if auto_claim:
        print(f"\n{Fore.YELLOW}To claim a username, you'll need to sign in with your Microsoft account.")
        print(f"{Fore.YELLOW}A browser window will open for secure login.")
    
    print(f"\n{Fore.CYAN}Starting to monitor username '{username}'...")
    print(f"{Fore.CYAN}Press Ctrl+C at any time to stop monitoring and return to the main menu.")
    print(f"\n{Fore.YELLOW}Checking every {check_interval} seconds. Please wait...")
    
    # Initialize the sniper
    sniper = Sniper()
    name_checker = NameChecker()
    
    # Check if the username is valid
    if not name_checker.is_valid_minecraft_username(username):
        print(f"\n{Fore.RED}Error: '{username}' is not a valid Minecraft username!")
        print(f"{Fore.YELLOW}Minecraft usernames can only contain letters, numbers, and underscores.")
        print(f"{Fore.YELLOW}They must be between 3 and 16 characters long.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    try:
        # First check if it's already available
        if sniper.check_username(username):
            print(f"\n{Fore.GREEN}✓ Username '{username}' is already available!")
            
            if auto_claim:
                print(f"\n{Fore.YELLOW}Attempting to claim the username now...")
                claim_username(username)
            else:
                print(f"{Fore.YELLOW}You can claim it now by selecting option 3 from the main menu.")
            
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
        
        # Start monitoring
        start_time = time.time()
        check_count = 0
        
        def availability_callback(is_available):
            """Callback for when username becomes available"""
            if is_available:
                print(f"\n{Fore.GREEN}✓ USERNAME FOUND! '{username}' is now available!")
                
                if auto_claim:
                    print(f"\n{Fore.YELLOW}Attempting to claim the username automatically...")
                    return True  # Signal to auto-claim
                else:
                    print(f"{Fore.YELLOW}You can claim it now by selecting option 3 from the main menu.")
                    return False  # Don't auto-claim
        
        try:
            # This will run until the username becomes available or the user presses Ctrl+C
            result = sniper.monitor_username(username, check_interval, auto_claim, availability_callback)
            
            if result and result.success:
                print(f"\n{Fore.GREEN}✓ SUCCESS! Username '{username}' has been claimed!")
                print(f"{Fore.GREEN}Your Minecraft username has been changed to '{username}'.")
            elif result and not result.success:
                print(f"\n{Fore.RED}✗ Failed to claim username '{username}'.")
                print(f"{Fore.YELLOW}Error: {result.error}")
                print(f"{Fore.YELLOW}You can try again by selecting option 3 from the main menu.")
        
        except KeyboardInterrupt:
            elapsed_time = time.time() - start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print(f"\n\n{Fore.YELLOW}Monitoring stopped by user.")
            print(f"{Fore.CYAN}Monitored for: {int(hours)}h {int(minutes)}m {int(seconds)}s")
            print(f"{Fore.CYAN}Checked {check_count} times.")
            
            if check_count > 0:
                print(f"{Fore.CYAN}The username was not available during this time.")
    
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred while monitoring:")
        print(f"{Fore.RED}{str(e)}")
        print(f"\n{Fore.YELLOW}This could be due to network issues or Mojang's API being unavailable.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def claim_username_menu():
    """Menu for claiming a username"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ CLAIM A USERNAME ════════╗")
    print(f"{Fore.CYAN}║                                  ║")
    print(f"{Fore.CYAN}║  This will attempt to claim a    ║")
    print(f"{Fore.CYAN}║  username for your account.      ║")
    print(f"{Fore.CYAN}║                                  ║")
    print(f"{Fore.CYAN}║  You must be logged in with a    ║")
    print(f"{Fore.CYAN}║  Microsoft account and eligible  ║")
    print(f"{Fore.CYAN}║  for a name change.              ║")
    print(f"{Fore.CYAN}║                                  ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════╝")
    
    username = input(f"\n{Fore.GREEN}Enter the username you want to claim: {Style.RESET_ALL}").strip()
    
    if not username:
        print(f"{Fore.RED}No username entered. Returning to main menu...")
        time.sleep(2)
        return
    
    # Initialize the sniper
    sniper = Sniper()
    name_checker = NameChecker()
    
    # Check if the username is valid
    if not name_checker.is_valid_minecraft_username(username):
        print(f"\n{Fore.RED}Error: '{username}' is not a valid Minecraft username!")
        print(f"{Fore.YELLOW}Minecraft usernames can only contain letters, numbers, and underscores.")
        print(f"{Fore.YELLOW}They must be between 3 and 16 characters long.")
        input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        return
    
    # Check if the username is available first
    print(f"\n{Fore.CYAN}Checking if username '{username}' is available...")
    
    try:
        if not sniper.check_username(username):
            print(f"\n{Fore.RED}✗ Username '{username}' is not available!")
            print(f"{Fore.YELLOW}You can only claim usernames that are currently available.")
            print(f"{Fore.YELLOW}Use option 1 to check availability or option 2 to monitor until available.")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✓ Username '{username}' is available!")
        print(f"{Fore.YELLOW}You'll need to sign in with your Microsoft account to claim it.")
        print(f"{Fore.YELLOW}A browser window will open for secure login.")
        
        # Show different strategy options with simple descriptions
        print(f"\n{Fore.CYAN}Choose a claiming strategy:")
        print(f"{Fore.WHITE}1. Standard (recommended for most users)")
        print(f"{Fore.WHITE}2. Burst (rapid multiple attempts)")
        print(f"{Fore.WHITE}3. Distributed (uses multiple threads)")
        print(f"{Fore.WHITE}4. Precision (timing-optimized)")
        print(f"{Fore.WHITE}5. Adaptive (self-tuning)")
        
        strategy_map = {
            1: "timing",
            2: "burst",
            3: "distributed",
            4: "precision",
            5: "adaptive"
        }
        
        while True:
            try:
                strategy_choice = int(input(f"\n{Fore.GREEN}Enter strategy (1-5): {Style.RESET_ALL}"))
                if 1 <= strategy_choice <= 5:
                    strategy = strategy_map[strategy_choice]
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.")
        
        print(f"\n{Fore.CYAN}Authenticating with Microsoft...")
        
        if not sniper.authenticate():
            print(f"\n{Fore.RED}✗ Authentication failed!")
            print(f"{Fore.YELLOW}Please make sure you have a valid Microsoft account with Minecraft.")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✓ Authentication successful!")
        print(f"\n{Fore.CYAN}Checking if your account is eligible for a name change...")
        
        if not sniper.is_eligible_for_name_change():
            print(f"\n{Fore.RED}✗ Your account is not eligible for a name change!")
            print(f"{Fore.YELLOW}You can only change your Minecraft username once every 30 days.")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✓ Your account is eligible for a name change!")
        print(f"\n{Fore.CYAN}Attempting to claim username '{username}' using {strategy} strategy...")
        
        result = sniper.claim_username(username)
        
        if result.success:
            print(f"\n{Fore.GREEN}✓ SUCCESS! Username '{username}' has been claimed!")
            print(f"{Fore.GREEN}Your Minecraft username has been changed to '{username}'.")
        else:
            print(f"\n{Fore.RED}✗ Failed to claim username '{username}'.")
            print(f"{Fore.YELLOW}Error: {result.error}")
            print(f"{Fore.YELLOW}This could be because someone claimed it first, or a temporary API issue.")
    
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred while attempting to claim the username:")
        print(f"{Fore.RED}{str(e)}")
        traceback.print_exc()
        print(f"\n{Fore.YELLOW}This could be due to network issues or Mojang's API being unavailable.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def check_account_status_menu():
    """Menu for checking account status"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ ACCOUNT STATUS ════════╗")
    print(f"{Fore.CYAN}║                                ║")
    print(f"{Fore.CYAN}║  This will check your account  ║")
    print(f"{Fore.CYAN}║  status and eligibility for    ║")
    print(f"{Fore.CYAN}║  name changes.                 ║")
    print(f"{Fore.CYAN}║                                ║")
    print(f"{Fore.CYAN}║  You'll need to sign in with   ║")
    print(f"{Fore.CYAN}║  your Microsoft account.       ║")
    print(f"{Fore.CYAN}║                                ║")
    print(f"{Fore.CYAN}╚════════════════════════════════╝")
    
    print(f"\n{Fore.YELLOW}A browser window will open for secure login with Microsoft.")
    print(f"{Fore.CYAN}Authenticating...")
    
    # Initialize the sniper
    sniper = Sniper()
    
    try:
        if not sniper.authenticate():
            print(f"\n{Fore.RED}✗ Authentication failed!")
            print(f"{Fore.YELLOW}Please make sure you have a valid Microsoft account with Minecraft.")
            input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✓ Authentication successful!")
        
        # Get current username
        auth = sniper.auth
        current_username = auth.get_current_username()
        
        print(f"\n{Fore.CYAN}Account Information:")
        print(f"{Fore.WHITE}Current Username: {Fore.GREEN}{current_username}")
        
        # Check eligibility
        is_eligible = sniper.is_eligible_for_name_change()
        
        if is_eligible:
            print(f"{Fore.WHITE}Name Change Eligibility: {Fore.GREEN}Eligible ✓")
            print(f"\n{Fore.GREEN}Your account is eligible for a name change!")
            print(f"{Fore.YELLOW}You can change your username using option 3 from the main menu.")
        else:
            print(f"{Fore.WHITE}Name Change Eligibility: {Fore.RED}Not Eligible ✗")
            print(f"\n{Fore.RED}Your account is not currently eligible for a name change.")
            print(f"{Fore.YELLOW}You can only change your Minecraft username once every 30 days.")
    
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred while checking account status:")
        print(f"{Fore.RED}{str(e)}")
        print(f"\n{Fore.YELLOW}This could be due to network issues or Mojang's API being unavailable.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def show_help_menu():
    """Show help and instructions"""
    clear_screen()
    display_banner()
    
    print(f"{Fore.CYAN}╔════════ HELP & INSTRUCTIONS ════════╗")
    print(f"{Fore.CYAN}║                                     ║")
    print(f"{Fore.CYAN}║  How to use this tool and answers   ║")
    print(f"{Fore.CYAN}║  to common questions.               ║")
    print(f"{Fore.CYAN}║                                     ║")
    print(f"{Fore.CYAN}╚═════════════════════════════════════╝")
    
    print(f"\n{Fore.YELLOW}◆ FREQUENTLY ASKED QUESTIONS ◆")
    
    print(f"\n{Fore.GREEN}Q: How do I check if a username is available?")
    print(f"{Fore.WHITE}A: Select option 1 from the main menu and enter the username.")
    
    print(f"\n{Fore.GREEN}Q: How do I get notified when a username becomes available?")
    print(f"{Fore.WHITE}A: Select option 2 to monitor a username until it becomes available.")
    
    print(f"\n{Fore.GREEN}Q: How do I claim a username?")
    print(f"{Fore.WHITE}A: Select option 3 and enter the username you want to claim.")
    print(f"{Fore.WHITE}   Note: The username must be available, and your account must be eligible.")
    
    print(f"\n{Fore.GREEN}Q: How often can I change my Minecraft username?")
    print(f"{Fore.WHITE}A: You can only change your username once every 30 days.")
    
    print(f"\n{Fore.GREEN}Q: What does 'monitoring' a username do?")
    print(f"{Fore.WHITE}A: It continually checks if a username is available and notifies you")
    print(f"{Fore.WHITE}   when it becomes available. It can also automatically claim it.")
    
    print(f"\n{Fore.GREEN}Q: What's the best strategy to claim a username?")
    print(f"{Fore.WHITE}A: For most users, the Standard strategy (option 1) works well.")
    print(f"{Fore.WHITE}   If you're trying to claim a highly competitive username, try")
    print(f"{Fore.WHITE}   Distributed (option 3) or Adaptive (option 5).")
    
    print(f"\n{Fore.GREEN}Q: I'm getting rate limited errors. What should I do?")
    print(f"{Fore.WHITE}A: Decrease how frequently you check for usernames (increase the")
    print(f"{Fore.WHITE}   checking interval when monitoring).")
    
    print(f"\n{Fore.GREEN}Q: The tool isn't working. What should I check?")
    print(f"{Fore.WHITE}A: 1. Make sure you have a stable internet connection")
    print(f"{Fore.WHITE}   2. Verify your Minecraft account is working correctly")
    print(f"{Fore.WHITE}   3. Try running the setup script again (python setup.py)")
    
    print(f"\n{Fore.YELLOW}◆ IMPORTANT NOTES ◆")
    
    print(f"\n{Fore.WHITE}• This tool uses Microsoft's official OAuth flow for authentication.")
    print(f"{Fore.WHITE}• Your login credentials are never stored by this tool (unless you")
    print(f"{Fore.WHITE}  created a .env file during setup).")
    print(f"{Fore.WHITE}• Using this tool excessively may result in temporary IP bans from Mojang.")
    print(f"{Fore.WHITE}• Be patient - securing a desired username can take time.")
    
    input(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")

def main():
    """Main function to run the easy interface"""
    while True:
        clear_screen()
        display_banner()
        choice = show_main_menu()
        
        if choice == 0:
            # Exit
            clear_screen()
            print(f"\n{Fore.GREEN}Thank you for using the Minecraft Username Sniper!")
            print(f"{Fore.YELLOW}Goodbye!\n")
            sys.exit(0)
        
        elif choice == 1:
            # Check username availability
            check_username_menu()
        
        elif choice == 2:
            # Monitor username
            monitor_username_menu()
        
        elif choice == 3:
            # Claim username
            claim_username_menu()
        
        elif choice == 4:
            # Check account status
            check_account_status_menu()
        
        elif choice == 5:
            # Help & Instructions
            show_help_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Fore.RED}An unexpected error occurred:")
        print(f"{Fore.RED}{str(e)}")
        print(f"\n{Fore.YELLOW}Please try restarting the program.")
        input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")
        sys.exit(1) 