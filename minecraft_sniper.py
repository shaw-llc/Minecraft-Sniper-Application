#!/usr/bin/env python3
"""
Minecraft Username Sniper

A tool for checking, monitoring, and claiming Minecraft usernames when they become available.
"""

import os
import sys
import time
import json
import logging
import argparse
import datetime
from colorama import Fore, Style, init
from dotenv import load_dotenv

from minecraft_auth import MinecraftAuth
from name_utils import NameChecker
from sniper import Sniper

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sniper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def display_banner():
    """Display a cool banner for the tool"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.GREEN}__  __ _                            __ _   {Fore.CYAN}                ║
{Fore.CYAN}║ {Fore.GREEN}|  \/  (_)_ __   ___  ___ _ __ __ _/ _| |_ {Fore.CYAN}                ║
{Fore.CYAN}║ {Fore.GREEN}| |\/| | | '_ \ / _ \/ __| '__/ _` | |_| __|{Fore.CYAN}               ║
{Fore.CYAN}║ {Fore.GREEN}| |  | | | | | |  __/ (__| | | (_| |  _| |_ {Fore.CYAN}               ║
{Fore.CYAN}║ {Fore.GREEN}|_|  |_|_|_| |_|\___|\___|_|  \__,_|_|  \__|{Fore.CYAN}               ║
{Fore.CYAN}║                                                           ║
{Fore.CYAN}║ {Fore.YELLOW}█   █ █▀▀ █▀▀ █▀█ █▀█ █▀█ █▀▄▀█ █▀▀   █▀▀ █▀█ █ █▀█ █▀▀ █▀█{Fore.CYAN} ║
{Fore.CYAN}║ {Fore.YELLOW}█   █ ▀▀█ █▀▀ █▀▄ █ █ █▀█ █ ▀ █ █▀▀   ▀▀█ █ █ █ █▀▀ █▀▀ █▀▄{Fore.CYAN} ║
{Fore.CYAN}║ {Fore.YELLOW}▀▀▀▀▀ ▀▀▀ ▀▀▀ ▀ ▀ ▀▀▀ ▀ ▀ ▀   ▀ ▀▀▀   ▀▀▀ ▀▀▀ ▀ ▀   ▀▀▀ ▀ ▀{Fore.CYAN} ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"{Fore.YELLOW}Version 1.0.0 - Use at your own risk")
    print(f"{Fore.YELLOW}See README.md for usage information and disclaimers")
    print()

def display_disclaimer():
    """Display a disclaimer about responsible use"""
    print(f"{Fore.YELLOW}{'='*80}")
    print(f"{Fore.YELLOW}DISCLAIMER:")
    print(f"{Fore.YELLOW}This tool should be used responsibly and at your own risk.")
    print(f"{Fore.YELLOW}Be aware of Mojang's Terms of Service and API rate limits.")
    print(f"{Fore.YELLOW}Excessive use could result in IP bans or account suspension.")
    print(f"{Fore.YELLOW}{'='*80}\n")

def display_results(result):
    """Display formatted results"""
    if result.success:
        status = f"{Fore.GREEN}SUCCESS"
    else:
        status = f"{Fore.RED}FAILED"
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Snipe Results for {result.username}")
    print(f"{Fore.CYAN}{'='*50}")
    print(f"Status:      {status}")
    print(f"Attempts:    {result.attempts}")
    print(f"Time Taken:  {result.time_taken:.2f} seconds")
    print(f"Timestamp:   {result.timestamp}")
    
    if result.error:
        print(f"Error:       {Fore.RED}{result.error}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*50}\n")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Minecraft Username Sniper Tool",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Check if a username is available:
    python minecraft_sniper.py check coolname
    
  Monitor a username until it becomes available:
    python minecraft_sniper.py monitor coolname -i 2
    
  Snipe a username at the specified time:
    python minecraft_sniper.py snipe coolname -t "2023-08-15 14:30:00" -s distributed
    
  Use authentication to claim a username:
    python minecraft_sniper.py snipe coolname -a
    
  Check your eligibility for a name change:
    python minecraft_sniper.py status -a
        """
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if a username is available")
    check_parser.add_argument("username", help="The Minecraft username to check")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor a username until it becomes available")
    monitor_parser.add_argument("username", help="The Minecraft username to monitor")
    monitor_parser.add_argument("-i", "--interval", type=float, default=1.5, 
                          help="Check interval in seconds (default: 1.5)")
    monitor_parser.add_argument("-c", "--claim", action="store_true", 
                          help="Attempt to claim the username if available")
    
    # Snipe command
    snipe_parser = subparsers.add_parser("snipe", help="Snipe a username at the specified time")
    snipe_parser.add_argument("username", help="The Minecraft username to snipe")
    snipe_parser.add_argument("-t", "--time", dest="target_time", 
                         help="Target time for sniping (format: 'YYYY-MM-DD HH:MM:SS')")
    snipe_parser.add_argument("-s", "--strategy", choices=["burst", "timing", "distributed"], 
                         default="timing", help="Sniping strategy to use (default: timing)")
    snipe_parser.add_argument("-l", "--latency-test", action="store_true",
                         help="Run a latency test before sniping")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check account status and eligibility")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test network latency and other functions")
    test_parser.add_argument("-i", "--iterations", type=int, default=10,
                        help="Number of iterations for latency test")
    
    # Global options
    parser.add_argument("-a", "--auth", action="store_true", 
                    help="Use authentication (requires .env file or interactive login)")
    parser.add_argument("-v", "--verbose", action="store_true", 
                    help="Enable verbose output for debugging")
    
    return parser.parse_args()

def parse_target_time(time_str):
    """Parse a time string into a datetime object"""
    if not time_str:
        return None
    
    try:
        # Try to parse the time string
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logging.error(f"{Fore.RED}Invalid time format. Use 'YYYY-MM-DD HH:MM:SS'")
        return None

def main():
    """Main function to run the username sniper"""
    # Parse command line arguments
    args = parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Display banner and disclaimer
    display_banner()
    display_disclaimer()
    
    # Initialize the sniper
    sniper = Sniper()
    
    # Handle authentication if requested
    if args.auth:
        logging.info(f"{Fore.CYAN}Authenticating with Microsoft...")
        if not sniper.authenticate():
            logging.error(f"{Fore.RED}Authentication failed")
            return
    
    # Execute the requested command
    if args.command == "check":
        username = args.username
        logging.info(f"{Fore.CYAN}Checking if username '{username}' is available...")
        
        if sniper.check_username(username):
            print(f"{Fore.GREEN}Username '{username}' is currently AVAILABLE!")
        else:
            print(f"{Fore.RED}Username '{username}' is currently taken.")
            
            # Try to get drop time from NameMC
            drop_time = sniper.get_drop_time(username)
            if drop_time:
                time_until = drop_time - datetime.datetime.now()
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"{Fore.YELLOW}This username may become available at: {drop_time}")
                print(f"{Fore.YELLOW}Time until available: {days}d {hours}h {minutes}m {seconds}s")
    
    elif args.command == "monitor":
        username = args.username
        check_interval = args.interval
        auto_claim = args.claim
        
        if auto_claim and not args.auth:
            logging.error(f"{Fore.RED}Authentication required for auto-claim")
            return
        
        logging.info(f"{Fore.CYAN}Starting to monitor username '{username}'...")
        logging.info(f"{Fore.CYAN}Press Ctrl+C to stop monitoring")
        
        try:
            result = sniper.monitor_username(username, check_interval, auto_claim)
            if result:
                print(f"{Fore.GREEN}Username '{username}' is now available!")
                
                if auto_claim:
                    if sniper.claim_username(username):
                        print(f"{Fore.GREEN}Successfully claimed username '{username}'!")
                    else:
                        print(f"{Fore.RED}Failed to claim username '{username}'")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped by user")
    
    elif args.command == "snipe":
        username = args.username
        strategy = args.strategy
        target_time_str = args.target_time
        
        # Check authentication
        if not args.auth:
            logging.error(f"{Fore.RED}Authentication required for sniping")
            return
        
        # Parse target time if provided
        target_time = parse_target_time(target_time_str)
        
        # If no target time provided, try to get it from NameMC
        if not target_time:
            logging.info(f"{Fore.CYAN}No target time provided, checking NameMC...")
            target_time = sniper.get_drop_time(username)
            
            if target_time:
                logging.info(f"{Fore.CYAN}Using drop time from NameMC: {target_time}")
            else:
                logging.warning(f"{Fore.YELLOW}No drop time found, will snipe immediately")
        
        # Run latency test if requested
        if args.latency_test:
            logging.info(f"{Fore.CYAN}Running latency test before sniping...")
            latency_results = sniper.test_network_latency(10)
            
            if latency_results:
                print(f"{Fore.CYAN}Average latency: {latency_results['average']:.2f}ms")
                print(f"{Fore.CYAN}This will be taken into account during sniping")
        
        # Check eligibility
        if not sniper.is_eligible_for_name_change():
            logging.error(f"{Fore.RED}Your account is not eligible for a name change")
            return
        
        # Start sniping
        logging.info(f"{Fore.CYAN}Starting to snipe username '{username}' using {strategy} strategy")
        if target_time:
            now = datetime.datetime.now()
            time_until = target_time - now
            
            if time_until.total_seconds() > 0:
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                print(f"{Fore.CYAN}Target time: {target_time}")
                print(f"{Fore.CYAN}Time until target: {days}d {hours}h {minutes}m {seconds}s")
        
        # Execute the snipe
        result = sniper.snipe_username(username, strategy, target_time)
        
        # Display results
        display_results(result)
    
    elif args.command == "status":
        if not args.auth:
            logging.error(f"{Fore.RED}Authentication required to check account status")
            return
        
        current_username = sniper.auth.get_current_username()
        eligible = sniper.is_eligible_for_name_change()
        
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}Account Status")
        print(f"{Fore.CYAN}{'='*50}")
        print(f"Current Username: {Fore.GREEN}{current_username}")
        print(f"Eligible for name change: {Fore.GREEN if eligible else Fore.RED}{eligible}")
        print(f"{Fore.CYAN}{'='*50}")
    
    elif args.command == "test":
        iterations = args.iterations
        
        print(f"{Fore.CYAN}Running network latency test with {iterations} iterations...")
        results = sniper.test_network_latency(iterations)
        
        if results:
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.CYAN}Latency Test Results")
            print(f"{Fore.CYAN}{'='*50}")
            print(f"Average Latency: {results['average']:.2f}ms")
            print(f"Minimum Latency: {results['minimum']:.2f}ms")
            print(f"Maximum Latency: {results['maximum']:.2f}ms")
            print(f"{Fore.CYAN}{'='*50}")
    
    else:
        print(f"{Fore.YELLOW}No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main() 