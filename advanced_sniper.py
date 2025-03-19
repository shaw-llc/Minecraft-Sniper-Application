#!/usr/bin/env python3
"""
Advanced Minecraft Username Sniper

A robust tool for checking, monitoring, and sniping multiple Minecraft usernames when they become available.
Handles authentication, multiple strategies, and provides advanced functionality.
"""

import os
import sys
import time
import json
import logging
import argparse
import datetime
import threading
from colorama import Fore, Style, init
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from minecraft_auth import MinecraftAuth
from name_utils import NameChecker
from sniper import Sniper, SniperResult
try:
    from notifications import NotificationManager
    notifications_available = True
except ImportError:
    notifications_available = False

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("advanced_sniper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Constants
MAX_THREADS = 5
VERSION = "2.0.0"

class AdvancedSniper:
    """Advanced wrapper around the core Sniper class to handle multiple usernames and configurations"""
    
    def __init__(self, auth=None, base_delay=2.0, max_threads=MAX_THREADS):
        """Initialize the advanced sniper with optional authentication"""
        self.core_sniper = Sniper()
        self.max_threads = max_threads
        self.monitoring_threads = {}
        self.stop_event = threading.Event()
        self.results = {}
    
    def authenticate(self):
        """Authenticate with Minecraft services"""
        return self.core_sniper.authenticate()
    
    def check_username(self, username):
        """Check if a username is available"""
        return self.core_sniper.check_username(username)
    
    def check_usernames_bulk(self, usernames):
        """Check multiple usernames and return available ones"""
        return self.core_sniper.check_usernames_bulk(usernames)
    
    def monitor_username(self, username, check_interval=1.5, auto_claim=False):
        """
        Monitor a single username until it becomes available.
        This is a wrapper around the core sniper's monitor function.
        """
        return self.core_sniper.monitor_username(username, check_interval, auto_claim)
    
    def _monitor_username_thread(self, username, check_interval, auto_claim, results_dict):
        """Thread worker for monitoring a username"""
        try:
            result = self.monitor_username(username, check_interval, auto_claim)
            results_dict[username] = {
                "available": True,
                "timestamp": datetime.datetime.now(),
                "claimed": auto_claim and result is True
            }
        except Exception as e:
            results_dict[username] = {
                "available": False,
                "error": str(e),
                "timestamp": datetime.datetime.now()
            }
    
    def monitor_multiple_usernames(self, usernames, check_interval=1.5, auto_claim=False):
        """
        Monitor multiple usernames concurrently.
        
        Args:
            usernames: List of usernames to monitor
            check_interval: Base check interval in seconds
            auto_claim: Whether to automatically claim usernames when available
            
        Returns:
            Dictionary mapping usernames to their results
        """
        logging.info(f"{Fore.CYAN}Starting to monitor {len(usernames)} usernames")
        
        # Clear stop event
        self.stop_event.clear()
        
        # Clear previous results
        self.results = {}
        
        # Clear previous monitoring threads
        self.monitoring_threads = {}
        
        # Create threads for each username
        for username in usernames:
            thread = threading.Thread(
                target=self._monitor_username_thread,
                args=(username, check_interval, auto_claim, self.results)
            )
            thread.daemon = True
            self.monitoring_threads[username] = thread
            thread.start()
        
        try:
            # Wait for all threads to complete or until interrupted
            while any(thread.is_alive() for thread in self.monitoring_threads.values()):
                if self.stop_event.is_set():
                    break
                self.display_status_summary()
                time.sleep(5)
            
            return self.results
        
        except KeyboardInterrupt:
            logging.info(f"{Fore.YELLOW}Monitoring interrupted by user")
            self.stop_event.set()
            return self.results
    
    def display_status_summary(self):
        """Display a summary of monitoring status"""
        active_count = sum(1 for thread in self.monitoring_threads.values() if thread.is_alive())
        available_count = sum(1 for result in self.results.values() if result.get("available", False))
        claimed_count = sum(1 for result in self.results.values() if result.get("claimed", False))
        
        print(f"\r{Fore.CYAN}Monitoring: {active_count} active, {available_count} available, {claimed_count} claimed", end="")
        sys.stdout.flush()
    
    def snipe_username(self, username, strategy="timing", target_time=None, latency_ms=None):
        """Snipe a username with the specified strategy"""
        return self.core_sniper.snipe_username(username, strategy, target_time, latency_ms)
    
    def _snipe_username_thread(self, username, strategy, target_time, results_dict):
        """Thread worker for sniping a username"""
        try:
            result = self.snipe_username(username, strategy, target_time)
            results_dict[username] = result
        except Exception as e:
            results_dict[username] = SniperResult(
                username=username,
                success=False,
                error=str(e)
            )
    
    def snipe_multiple_usernames(self, usernames, strategy="timing", target_times=None):
        """
        Snipe multiple usernames concurrently.
        
        Args:
            usernames: List of usernames to snipe
            strategy: Strategy to use for sniping
            target_times: Optional dictionary mapping usernames to target times
            
        Returns:
            Dictionary mapping usernames to their results
        """
        if not self.core_sniper.authenticated:
            logging.error(f"{Fore.RED}Authentication required to snipe usernames")
            return {}
        
        if not target_times:
            target_times = {}
        
        # Create result dict
        results = {}
        threads = []
        
        # Cap the number of threads
        max_concurrent = min(len(usernames), self.max_threads)
        
        logging.info(f"{Fore.CYAN}Starting to snipe {len(usernames)} usernames using {max_concurrent} threads")
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit sniping tasks for each username
            futures = {}
            for username in usernames:
                target_time = target_times.get(username)
                future = executor.submit(
                    self._snipe_username_thread,
                    username, strategy, target_time, results
                )
                futures[future] = username
        
        return results
    
    def get_upcoming_available_names(self, limit=10):
        """Get upcoming available names from NameMC"""
        return self.core_sniper.name_checker.get_upcoming_available_names(limit)
    
    def load_proxies_from_file(self, filename):
        """Load proxies from a file"""
        return self.core_sniper.load_proxies_from_file(filename)
    
    def test_proxies(self, timeout=5):
        """Test all loaded proxies and remove non-working ones"""
        return self.core_sniper.test_proxies(timeout)
    
    def get_stats_report(self):
        """Get a comprehensive statistics report"""
        return self.core_sniper.get_stats_report()
    
    def test_network_latency(self, iterations=10):
        """Test network latency to Mojang API"""
        return self.core_sniper.test_network_latency(iterations)
    
    def save_to_file(self, data, filename="sniper_results.json"):
        """Save results to a JSON file"""
        try:
            # Convert datetime objects to strings
            serializable_data = {}
            for key, value in data.items():
                if isinstance(value, SniperResult):
                    serializable_data[key] = {
                        "username": value.username,
                        "success": value.success,
                        "attempts": value.attempts,
                        "time_taken": value.time_taken,
                        "error": value.error,
                        "timestamp": value.timestamp.isoformat()
                    }
                elif isinstance(value, dict) and "timestamp" in value:
                    serializable_value = value.copy()
                    serializable_value["timestamp"] = value["timestamp"].isoformat()
                    serializable_data[key] = serializable_value
                else:
                    serializable_data[key] = value
            
            with open(filename, "w") as f:
                json.dump(serializable_data, f, indent=4)
            
            logging.info(f"{Fore.GREEN}Results saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"{Fore.RED}Error saving results to file: {str(e)}")
            return False

    def configure_notifications(self, discord_webhook=None, email_config=None):
        """Configure notifications"""
        return self.core_sniper.configure_notifications(discord_webhook, email_config)

def display_banner():
    """Display a cool banner for the tool"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.GREEN}  ___      _                               _  {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.GREEN} / _ \  __| |_   ____ _ _ __   ___ ___  __| | {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.GREEN}/ /_\ \/ _` \ \ / / _` | '_ \ / __/ _ \/ _` | {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.GREEN}|  _  | (_| |\ V / (_| | | | | (_|  __/ (_| | {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.GREEN}\_| |_/\__,_| \_/ \__,_|_| |_|\___\___|\__,_| {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.YELLOW}__  __ _                            __ _      {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.YELLOW}|  \/  (_)_ __   ___  ___ _ __ __ _/ _| |_    {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.YELLOW}| |\/| | | '_ \ / _ \/ __| '__/ _` | |_| __|  {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.YELLOW}| |  | | | | | |  __/ (__| | | (_| |  _| |_   {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.YELLOW}|_|  |_|_|_| |_|\___|\___|_|  \__,_|_|  \__|  {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.RED}█▀▀ █▀█ █ █▀█ █▀▀ █▀█                        {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.RED}▀▀█ █ █ █ █▀▀ █▀▀ █▀▄                        {Fore.CYAN}            ║
{Fore.CYAN}║ {Fore.RED}▀▀▀ ▀▀▀ ▀ ▀   ▀▀▀ ▀ ▀                        {Fore.CYAN}            ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"{Fore.YELLOW}Version {VERSION} - Advanced Edition - Use at your own risk")
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

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Advanced Minecraft Username Sniper Tool",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Check multiple usernames from a file:
    python advanced_sniper.py check -f usernames.txt
    
  Monitor multiple usernames:
    python advanced_sniper.py monitor -f usernames.txt -i 2
    
  Snipe a single username with authentication:
    python advanced_sniper.py snipe -u coolname -s distributed -a
    
  Check for upcoming available names:
    python advanced_sniper.py upcoming --limit 20
    
  Test network latency for better timing:
    python advanced_sniper.py test -i 20
        """
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check username availability")
    check_group = check_parser.add_mutually_exclusive_group(required=True)
    check_group.add_argument("-u", "--username", help="Single username to check")
    check_group.add_argument("-f", "--file", help="File containing usernames to check (one per line)")
    check_parser.add_argument("--save", help="Save results to the specified JSON file")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor usernames until they become available")
    monitor_group = monitor_parser.add_mutually_exclusive_group(required=True)
    monitor_group.add_argument("-u", "--username", help="Single username to monitor")
    monitor_group.add_argument("-f", "--file", help="File containing usernames to monitor (one per line)")
    monitor_parser.add_argument("-i", "--interval", type=float, default=2.0, 
                        help="Check interval in seconds (default: 2.0)")
    monitor_parser.add_argument("-c", "--claim", action="store_true", 
                          help="Attempt to claim usernames when available")
    monitor_parser.add_argument("--save", help="Save results to the specified JSON file")
    
    # Snipe command
    snipe_parser = subparsers.add_parser("snipe", help="Snipe usernames at specific times")
    snipe_group = snipe_parser.add_mutually_exclusive_group(required=True)
    snipe_group.add_argument("-u", "--username", help="Single username to snipe")
    snipe_group.add_argument("-f", "--file", help="File containing usernames to snipe (one per line)")
    snipe_parser.add_argument("-t", "--time", dest="target_time", 
                         help="Target time for sniping (format: 'YYYY-MM-DD HH:MM:SS')")
    snipe_parser.add_argument("-s", "--strategy", choices=["burst", "timing", "distributed", "precision", "adaptive"], 
                         default="adaptive", help="Sniping strategy to use (default: adaptive)")
    snipe_parser.add_argument("--latency", type=float, help="Network latency in milliseconds for precision timing")
    snipe_parser.add_argument("--save", help="Save results to the specified JSON file")
    
    # Upcoming command
    upcoming_parser = subparsers.add_parser("upcoming", help="Check for upcoming available usernames")
    upcoming_parser.add_argument("--limit", type=int, default=10, 
                            help="Maximum number of names to show (default: 10)")
    upcoming_parser.add_argument("--save", help="Save results to the specified JSON file")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test network latency and other functions")
    test_parser.add_argument("-i", "--iterations", type=int, default=10,
                        help="Number of iterations for latency test")
    
    # Proxy command
    proxy_parser = subparsers.add_parser("proxy", help="Manage proxies")
    proxy_subparsers = proxy_parser.add_subparsers(dest="proxy_command", help="Proxy command")
    
    # Load proxies
    load_proxy_parser = proxy_subparsers.add_parser("load", help="Load proxies from a file")
    load_proxy_parser.add_argument("proxy_file", help="File containing proxies (one per line)")
    
    # Test proxies
    test_proxy_parser = proxy_subparsers.add_parser("test", help="Test loaded proxies")
    test_proxy_parser.add_argument("-t", "--timeout", type=int, default=5,
                              help="Timeout in seconds for proxy tests")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View sniper statistics")
    stats_parser.add_argument("--save", help="Save statistics to the specified JSON file")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check account status and eligibility")
    
    # Notification command
    if notifications_available:
        notif_parser = subparsers.add_parser("notify", help="Configure notifications")
        notif_subparsers = notif_parser.add_subparsers(dest="notif_command", help="Notification command")
        
        # Configure Discord
        discord_parser = notif_subparsers.add_parser("discord", help="Configure Discord webhook")
        discord_parser.add_argument("webhook_url", help="Discord webhook URL")
        
        # Configure email
        email_parser = notif_subparsers.add_parser("email", help="Configure email notifications")
        email_parser.add_argument("smtp_server", help="SMTP server address")
        email_parser.add_argument("smtp_port", type=int, help="SMTP server port")
        email_parser.add_argument("username", help="SMTP username")
        email_parser.add_argument("password", help="SMTP password")
        email_parser.add_argument("from_email", help="From email address")
        email_parser.add_argument("to_email", help="To email address")
        
        # Test notifications
        test_notif_parser = notif_subparsers.add_parser("test", help="Test notifications")
    
    # Global options
    parser.add_argument("-a", "--auth", action="store_true", 
                    help="Use authentication (required for claiming and sniping)")
    parser.add_argument("--threads", type=int, default=MAX_THREADS,
                    help=f"Maximum number of concurrent threads (default: {MAX_THREADS})")
    parser.add_argument("-v", "--verbose", action="store_true", 
                    help="Enable verbose output for debugging")
    
    return parser.parse_args()

def load_usernames_from_file(filename):
    """Load usernames from a file, one per line"""
    try:
        with open(filename, "r") as f:
            usernames = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return usernames
    except Exception as e:
        logging.error(f"{Fore.RED}Error loading usernames from file: {str(e)}")
        return []

def display_check_results(results):
    """Display username check results in a formatted table"""
    if not results:
        print(f"{Fore.YELLOW}No results to display")
        return
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Username Availability Results")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{'Username':<20} {'Status':<15} {'Drop Time':<25}")
    print(f"{'-'*20} {'-'*15} {'-'*25}")
    
    for username, data in results.items():
        if data.get("available", False):
            status = f"{Fore.GREEN}Available"
        else:
            status = f"{Fore.RED}Taken"
        
        drop_time = data.get("drop_time", "N/A")
        if drop_time != "N/A":
            drop_time = drop_time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{username:<20} {status:<35} {drop_time:<25}")
    
    print(f"{Fore.CYAN}{'='*60}\n")

def display_upcoming_names(names):
    """Display upcoming available names in a formatted table"""
    if not names:
        print(f"{Fore.YELLOW}No upcoming names found")
        return
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Upcoming Available Usernames")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{'Username':<20} {'Drop Time':<25} {'Time Until':<25}")
    print(f"{'-'*20} {'-'*25} {'-'*25}")
    
    for name in names:
        username = name["name"]
        drop_time = name["drop_time"].strftime("%Y-%m-%d %H:%M:%S")
        
        # Format time until
        time_until = name["time_until"]
        days = time_until.days
        hours, remainder = divmod(time_until.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_until_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        print(f"{username:<20} {drop_time:<25} {time_until_str:<25}")
    
    print(f"{Fore.CYAN}{'='*70}\n")

def display_stats_report(report):
    """Display statistics report in a formatted table"""
    if not report:
        print(f"{Fore.YELLOW}No statistics to display")
        return
    
    summary = report.get("summary", {})
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}Sniper Statistics Summary")
    print(f"{Fore.CYAN}{'='*70}")
    print(f"Total Usernames Checked:  {summary.get('total_usernames_checked', 0)}")
    print(f"Total Snipe Attempts:     {summary.get('total_snipe_attempts', 0)}")
    print(f"Successful Claims:        {summary.get('successful_claims', 0)}")
    print(f"Failed Claims:            {summary.get('failed_claims', 0)}")
    print(f"Success Rate:             {summary.get('overall_success_rate', 0):.2f}%")
    print(f"Total API Requests:       {summary.get('total_api_requests', 0)}")
    print(f"Avg Response Time:        {summary.get('average_response_time_ms', 0):.2f}ms")
    print(f"Rate Limited Count:       {summary.get('rate_limited_count', 0)}")
    
    # Display best strategy if available
    best_strategy = summary.get("best_strategy", {})
    if best_strategy:
        print(f"\n{Fore.GREEN}Best Strategy: {best_strategy.get('name')} ({best_strategy.get('success_rate', 0):.2f}% success rate)")
    
    # Show strategy stats
    strategies = report.get("strategies", {})
    if strategies:
        print(f"\n{Fore.CYAN}Strategy Performance")
        print(f"{'-'*70}")
        print(f"{'Strategy':<20} {'Success Rate':<15} {'Attempts':<10} {'Avg Time':<10}")
        print(f"{'-'*20} {'-'*15} {'-'*10} {'-'*10}")
        
        for name, stats in strategies.items():
            success_rate = f"{stats.get('success_rate', 0):.2f}%"
            attempts = stats.get('attempts', 0)
            avg_time = f"{stats.get('avg_time_per_snipe', 0):.2f}s"
            
            print(f"{name:<20} {success_rate:<15} {attempts:<10} {avg_time:<10}")
    
    # Show recent claims
    recent_claims = report.get("recent_claims", [])
    if recent_claims:
        print(f"\n{Fore.GREEN}Recent Successful Claims")
        print(f"{'-'*70}")
        for claim in recent_claims:
            timestamp = datetime.datetime.fromisoformat(claim["timestamp"]) if isinstance(claim["timestamp"], str) else claim["timestamp"]
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Fore.GREEN}{claim['username']} - {time_str} using {claim['strategy']} (took {claim['time_taken']:.2f}s)")
    
    print(f"{Fore.CYAN}{'='*70}\n")

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
    """Main function to run the advanced username sniper"""
    # Parse command line arguments
    args = parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Display banner and disclaimer
    display_banner()
    display_disclaimer()
    
    # Initialize the advanced sniper
    sniper = AdvancedSniper(max_threads=args.threads)
    
    # Handle authentication if requested
    if args.auth:
        logging.info(f"{Fore.CYAN}Authenticating with Microsoft...")
        if not sniper.authenticate():
            logging.error(f"{Fore.RED}Authentication failed")
            return
    
    # Execute the requested command
    if args.command == "check":
        # Load usernames
        usernames = []
        if args.username:
            usernames = [args.username]
        elif args.file:
            usernames = load_usernames_from_file(args.file)
        
        if not usernames:
            logging.error(f"{Fore.RED}No usernames to check")
            return
        
        logging.info(f"{Fore.CYAN}Checking {len(usernames)} usernames...")
        
        # Check availability
        results = {}
        for username in usernames:
            is_available = sniper.check_username(username)
            drop_time = None
            
            if not is_available:
                drop_time = sniper.core_sniper.get_drop_time(username)
            
            results[username] = {
                "available": is_available,
                "drop_time": drop_time,
                "timestamp": datetime.datetime.now()
            }
        
        # Display results
        display_check_results(results)
        
        # Save results if requested
        if args.save:
            sniper.save_to_file(results, args.save)
    
    elif args.command == "monitor":
        # Load usernames
        usernames = []
        if args.username:
            usernames = [args.username]
        elif args.file:
            usernames = load_usernames_from_file(args.file)
        
        if not usernames:
            logging.error(f"{Fore.RED}No usernames to monitor")
            return
        
        # Check if auto claim is enabled but not authenticated
        if args.claim and not args.auth:
            logging.error(f"{Fore.RED}Authentication required for auto-claim")
            return
        
        logging.info(f"{Fore.CYAN}Starting to monitor {len(usernames)} usernames...")
        logging.info(f"{Fore.CYAN}Press Ctrl+C to stop monitoring")
        
        # Start monitoring
        results = sniper.monitor_multiple_usernames(usernames, args.interval, args.claim)
        
        # Display final results
        print("\n")  # Add newline after the status summary
        for username, result in results.items():
            if result.get("available", False):
                status = f"{Fore.GREEN}Available"
                if result.get("claimed", False):
                    status += f" and {Fore.GREEN}Claimed"
            else:
                status = f"{Fore.RED}Not Available"
                if "error" in result:
                    status += f" (Error: {result['error']})"
            
            print(f"Username: {username} - Status: {status}")
        
        # Save results if requested
        if args.save:
            sniper.save_to_file(results, args.save)
    
    elif args.command == "snipe":
        # Check authentication
        if not args.auth:
            logging.error(f"{Fore.RED}Authentication required for sniping")
            return
        
        # Load usernames
        usernames = []
        if args.username:
            usernames = [args.username]
        elif args.file:
            usernames = load_usernames_from_file(args.file)
        
        if not usernames:
            logging.error(f"{Fore.RED}No usernames to snipe")
            return
        
        # Parse target time
        target_time = parse_target_time(args.target_time)
        
        # Create a mapping of usernames to target times
        target_times = {}
        for username in usernames:
            # If no manual target time, try to get it from NameMC
            if not target_time:
                username_target_time = sniper.core_sniper.get_drop_time(username)
                if username_target_time:
                    target_times[username] = username_target_time
                    logging.info(f"{Fore.CYAN}Using drop time for {username}: {username_target_time}")
            else:
                target_times[username] = target_time
        
        # Check eligibility
        if not sniper.core_sniper.is_eligible_for_name_change():
            logging.error(f"{Fore.RED}Your account is not eligible for a name change")
            return
        
        # Start sniping
        logging.info(f"{Fore.CYAN}Starting to snipe {len(usernames)} usernames using {args.strategy} strategy")
        
        # If using precision strategy and latency provided, use it
        latency_ms = args.latency
        if not latency_ms and args.strategy == "precision":
            # Run a quick latency test
            latency_results = sniper.test_network_latency(5)
            if latency_results:
                latency_ms = latency_results["average"]
                logging.info(f"{Fore.CYAN}Using measured latency: {latency_ms:.2f}ms")
        
        # Show target times if available
        for username, target in target_times.items():
            if target:
                now = datetime.datetime.now()
                time_until = target - now
                
                if time_until.total_seconds() > 0:
                    days = time_until.days
                    hours, remainder = divmod(time_until.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    print(f"{Fore.CYAN}Target time for {username}: {target}")
                    print(f"{Fore.CYAN}Time until target: {days}d {hours}h {minutes}m {seconds}s")
        
        # Execute the snipe
        results = {}
        for username in usernames:
            # Use single-username snipe for better control
            target = target_times.get(username)
            result = sniper.snipe_username(username, args.strategy, target, latency_ms)
            results[username] = result
            
            # Display result immediately
            if result.success:
                print(f"\n{Fore.GREEN}Successfully sniped username: {username}!")
                print(f"Attempts: {result.attempts}")
                print(f"Time taken: {result.time_taken:.2f}s")
            else:
                print(f"\n{Fore.RED}Failed to snipe username: {username}")
                if result.error:
                    print(f"Error: {result.error}")
                print(f"Attempts: {result.attempts}")
                print(f"Time taken: {result.time_taken:.2f}s")
        
        # Save results if requested
        if args.save:
            sniper.save_to_file(results, args.save)
    
    elif args.command == "upcoming":
        logging.info(f"{Fore.CYAN}Checking for upcoming available names...")
        names = sniper.get_upcoming_available_names(args.limit)
        
        # Display results
        display_upcoming_names(names)
    
    # Save results if requested
    if args.save:
            sniper.save_to_file({"upcoming_names": names}, args.save)
    
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
    
    elif args.command == "proxy":
        if args.proxy_command == "load":
            proxy_file = args.proxy_file
            count = sniper.load_proxies_from_file(proxy_file)
            if count > 0:
                print(f"{Fore.GREEN}Successfully loaded {count} proxies from {proxy_file}")
            else:
                print(f"{Fore.RED}Failed to load proxies from {proxy_file}")
        
        elif args.proxy_command == "test":
            timeout = args.timeout
            working_count = sniper.test_proxies(timeout)
            print(f"{Fore.GREEN}Found {working_count} working proxies")
    
    elif args.command == "stats":
        report = sniper.get_stats_report()
        display_stats_report(report)
        
        if args.save:
            sniper.save_to_file(report, args.save)
    
    elif args.command == "status":
        if not args.auth:
            logging.error(f"{Fore.RED}Authentication required to check account status")
            return
        
        current_username = sniper.core_sniper.auth.get_current_username()
        eligible = sniper.core_sniper.is_eligible_for_name_change()
        
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}Account Status")
        print(f"{Fore.CYAN}{'='*50}")
        print(f"Current Username: {Fore.GREEN}{current_username}")
        print(f"Eligible for name change: {Fore.GREEN if eligible else Fore.RED}{eligible}")
        print(f"{Fore.CYAN}{'='*50}")
    
    elif args.command == "notify" and notifications_available:
        if args.notif_command == "discord":
            webhook_url = args.webhook_url
            if sniper.configure_notifications(discord_webhook=webhook_url):
                print(f"{Fore.GREEN}Successfully configured Discord notifications")
            else:
                print(f"{Fore.RED}Failed to configure Discord notifications")
        
        elif args.notif_command == "email":
            email_config = (
                args.smtp_server,
                args.smtp_port,
                args.username,
                args.password,
                args.from_email,
                args.to_email
            )
            if sniper.configure_notifications(email_config=email_config):
                print(f"{Fore.GREEN}Successfully configured email notifications")
            else:
                print(f"{Fore.RED}Failed to configure email notifications")
        
        elif args.notif_command == "test":
            # Import directly here to avoid circular imports
            from notifications import NotificationManager
            notif = NotificationManager()
            if notif.test_all_notifications():
                print(f"{Fore.GREEN}Notification test sent successfully")
            else:
                print(f"{Fore.RED}Failed to send test notification")
    
    else:
        print(f"{Fore.YELLOW}No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main() 