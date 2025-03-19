#!/usr/bin/env python3
"""
Minecraft Username Sniper Core

This module handles the core sniping functionality with high-precision timing.
"""

import os
import time
import json
import random
import logging
import datetime
import threading
import statistics
import traceback
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style

from minecraft_auth import MinecraftAuth
from name_utils import NameChecker
try:
    from notifications import NotificationManager
    notifications_available = True
except ImportError:
    notifications_available = False

# Constants
VERSION = "2.0.0"
MAX_THREADS = 10
MAX_ATTEMPTS = 50
SNIPE_WINDOW_START = 1.0  # seconds before target time
SNIPE_WINDOW_END = 5.0  # seconds after target time
STATS_FILE = "sniper_stats.json"
ATTACK_PATTERNS_FILE = "attack_patterns.json"

class SniperResult:
    """Container for sniper results"""
    
    def __init__(self, username, success=False, attempts=0, time_taken=0, error=None):
        self.username = username
        self.success = success
        self.attempts = attempts
        self.time_taken = time_taken
        self.error = error
        self.timestamp = datetime.datetime.now()
        self.strategy = None
        self.latency = None
        self.requests = []  # Store timestamps of all requests
        self.claim_time = None  # When the claim was successful


class SniperStats:
    """Track and analyze sniper statistics"""
    
    def __init__(self, stats_file=STATS_FILE):
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self):
        """Load statistics from file"""
        default_stats = {
            "total_attempts": 0,
            "successful_claims": 0,
            "failed_claims": 0,
            "usernames_checked": 0,
            "total_requests": 0,
            "rate_limited_count": 0,
            "avg_response_time": 0,
            "strategy_stats": {},
            "recent_results": [],
            "claim_history": []
        }
        
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    
                    # Add any missing fields from default_stats
                    for key, value in default_stats.items():
                        if key not in stats:
                            stats[key] = value
                    
                    return stats
            except Exception as e:
                logging.error(f"{Fore.RED}Error loading stats: {str(e)}")
        
        return default_stats
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=4, default=self._json_serializer)
            return True
        except Exception as e:
            logging.error(f"{Fore.RED}Error saving stats: {str(e)}")
            return False
    
    def _json_serializer(self, obj):
        """Helper to serialize datetime objects in JSON"""
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def update_check_stats(self, username, is_available):
        """Update statistics for username checks"""
        self.stats["usernames_checked"] += 1
        self.stats["total_requests"] += 1
        self.save_stats()
    
    def update_attempt_stats(self, attempts, rate_limited=False, response_time=None):
        """Update statistics for snipe attempts"""
        self.stats["total_attempts"] += 1
        self.stats["total_requests"] += attempts
        
        if rate_limited:
            self.stats["rate_limited_count"] += 1
        
        if response_time:
            # Update average response time
            current_avg = self.stats["avg_response_time"]
            current_count = self.stats["total_requests"] - attempts
            
            if current_count > 0:
                new_avg = ((current_avg * current_count) + response_time) / (current_count + 1)
                self.stats["avg_response_time"] = new_avg
        
        self.save_stats()
    
    def record_snipe_result(self, result):
        """Record the result of a snipe attempt"""
        strategy_name = result.strategy if result.strategy else "unknown"
        
        # Initialize strategy stats if not present
        if strategy_name not in self.stats["strategy_stats"]:
            self.stats["strategy_stats"][strategy_name] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "avg_attempts": 0,
                "avg_time": 0
            }
        
        # Update strategy stats
        strategy_stats = self.stats["strategy_stats"][strategy_name]
        strategy_stats["attempts"] += 1
        
        if result.success:
            self.stats["successful_claims"] += 1
            strategy_stats["successes"] += 1
            
            # Add to claim history
            self.stats["claim_history"].append({
                "username": result.username,
                "timestamp": result.timestamp.isoformat(),
                "strategy": strategy_name,
                "attempts": result.attempts,
                "time_taken": result.time_taken
            })
            
            # Limit claim history to last 100 entries
            if len(self.stats["claim_history"]) > 100:
                self.stats["claim_history"] = self.stats["claim_history"][-100:]
        else:
            self.stats["failed_claims"] += 1
            strategy_stats["failures"] += 1
        
        # Update average attempts and time
        old_avg_attempts = strategy_stats["avg_attempts"]
        old_count = strategy_stats["attempts"] - 1
        strategy_stats["avg_attempts"] = (old_avg_attempts * old_count + result.attempts) / strategy_stats["attempts"]
        
        old_avg_time = strategy_stats["avg_time"]
        strategy_stats["avg_time"] = (old_avg_time * old_count + result.time_taken) / strategy_stats["attempts"]
        
        # Add to recent results
        result_dict = {
            "username": result.username,
            "success": result.success,
            "strategy": strategy_name,
            "attempts": result.attempts,
            "time_taken": result.time_taken,
            "timestamp": result.timestamp.isoformat()
        }
        
        if result.error:
            result_dict["error"] = result.error
        
        self.stats["recent_results"].append(result_dict)
        
        # Limit recent results to last 20 entries
        if len(self.stats["recent_results"]) > 20:
            self.stats["recent_results"] = self.stats["recent_results"][-20:]
        
        self.save_stats()
    
    def get_success_rate(self):
        """Calculate the overall success rate"""
        total = self.stats["successful_claims"] + self.stats["failed_claims"]
        if total == 0:
            return 0
        return (self.stats["successful_claims"] / total) * 100
    
    def get_strategy_success_rate(self, strategy_name):
        """Calculate the success rate for a specific strategy"""
        if strategy_name not in self.stats["strategy_stats"]:
            return 0
        
        stats = self.stats["strategy_stats"][strategy_name]
        total = stats["successes"] + stats["failures"]
        
        if total == 0:
            return 0
        
        return (stats["successes"] / total) * 100
    
    def get_best_strategy(self):
        """Determine the most successful strategy based on success rate"""
        best_strategy = None
        best_rate = -1
        
        for strategy, stats in self.stats["strategy_stats"].items():
            total = stats["successes"] + stats["failures"]
            if total < 5:  # Require at least 5 attempts for meaningful data
                continue
                
            success_rate = (stats["successes"] / total) * 100
            if success_rate > best_rate:
                best_rate = success_rate
                best_strategy = strategy
        
        return best_strategy, best_rate
    
    def generate_report(self):
        """Generate a comprehensive statistics report"""
        report = {
            "summary": {
                "total_usernames_checked": self.stats["usernames_checked"],
                "total_snipe_attempts": self.stats["total_attempts"],
                "successful_claims": self.stats["successful_claims"],
                "failed_claims": self.stats["failed_claims"],
                "overall_success_rate": self.get_success_rate(),
                "total_api_requests": self.stats["total_requests"],
                "average_response_time_ms": self.stats["avg_response_time"],
                "rate_limited_count": self.stats["rate_limited_count"]
            },
            "strategies": {},
            "recent_results": self.stats["recent_results"][-5:],  # Last 5 results
            "recent_claims": [c for c in self.stats["claim_history"][-5:] if c]  # Last 5 claims
        }
        
        # Add strategy-specific stats
        for strategy, stats in self.stats["strategy_stats"].items():
            total = stats["successes"] + stats["failures"]
            success_rate = 0
            if total > 0:
                success_rate = (stats["successes"] / total) * 100
                
            report["strategies"][strategy] = {
                "attempts": stats["attempts"],
                "successes": stats["successes"],
                "failures": stats["failures"],
                "success_rate": success_rate,
                "avg_attempts_per_snipe": stats["avg_attempts"],
                "avg_time_per_snipe": stats["avg_time"]
            }
        
        # Identify best strategy
        best_strategy, best_rate = self.get_best_strategy()
        if best_strategy:
            report["summary"]["best_strategy"] = {
                "name": best_strategy,
                "success_rate": best_rate
            }
        
        return report


class SnipeStrategy:
    """Base class for sniping strategies"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def execute(self, auth, name_checker, username, target_time):
        """Execute the strategy"""
        raise NotImplementedError("Subclasses must implement execute()")


class BurstStrategy(SnipeStrategy):
    """Send a rapid burst of requests right at the target time"""
    
    def __init__(self, burst_count=10, burst_delay=0.1):
        super().__init__(
            "Burst Strategy",
            "Send a rapid burst of requests right at the target time"
        )
        self.burst_count = burst_count
        self.burst_delay = burst_delay
    
    def execute(self, auth, name_checker, username, target_time=None):
        result = SniperResult(username)
        result.strategy = self.name
        start_time = time.time()
        
        # If no target time, use current time
        if not target_time:
            target_time = datetime.datetime.now()
        
        # Calculate wait time until just before target
        now = datetime.datetime.now()
        time_diff = (target_time - now).total_seconds()
        
        # If target time is in the future, wait until just before
        if time_diff > SNIPE_WINDOW_START:
            wait_time = time_diff - SNIPE_WINDOW_START
            logging.info(f"{Fore.CYAN}Waiting {wait_time:.2f} seconds until snipe window...")
            time.sleep(wait_time)
        
        # Start the burst attempts
        logging.info(f"{Fore.GREEN}Starting burst snipe for {username}...")
        
        success = False
        attempts = 0
        
        try:
            # Check if available first
            if name_checker.is_username_available(username):
                for i in range(self.burst_count):
                    attempts += 1
                    result.requests.append(time.time())
                    
                    # Try to claim
                    if auth.change_username(username):
                        success = True
                        result.claim_time = time.time()
                        break
                    
                    # Brief delay between attempts
                    time.sleep(self.burst_delay)
            else:
                # If not available yet, keep checking and attempt to claim when available
                max_wait = SNIPE_WINDOW_START + SNIPE_WINDOW_END
                attempt_start = time.time()
                
                while time.time() - attempt_start < max_wait and attempts < MAX_ATTEMPTS:
                    attempts += 1
                    check_time = time.time()
                    result.requests.append(check_time)
                    
                    if name_checker.is_username_available(username):
                        if auth.change_username(username):
                            success = True
                            result.claim_time = time.time()
                            break
                    
                    # Brief delay between checks
                    time.sleep(self.burst_delay)
        
        except Exception as e:
            result.error = str(e)
            logging.error(f"{Fore.RED}Error during burst snipe: {str(e)}")
            logging.debug(traceback.format_exc())
        
        time_taken = time.time() - start_time
        
        result.success = success
        result.attempts = attempts
        result.time_taken = time_taken
        
        if success:
            logging.info(f"{Fore.GREEN}Successfully claimed {username} using Burst Strategy!")
        else:
            logging.info(f"{Fore.RED}Failed to claim {username} after {attempts} attempts ({time_taken:.2f}s)")
        
        return result


class TimingStrategy(SnipeStrategy):
    """More sophisticated timing-based strategy with pre-emptive checks"""
    
    def __init__(self, pre_checks=3, check_interval=0.5, max_post_attempts=15):
        super().__init__(
            "Timing Strategy",
            "Sophisticated timing-based strategy with pre-emptive checks"
        )
        self.pre_checks = pre_checks
        self.check_interval = check_interval
        self.max_post_attempts = max_post_attempts
    
    def execute(self, auth, name_checker, username, target_time=None):
        result = SniperResult(username)
        result.strategy = self.name
        start_time = time.time()
        
        # If no target time, use current time
        if not target_time:
            target_time = datetime.datetime.now()
        
        # Calculate wait time until just before target
        now = datetime.datetime.now()
        time_diff = (target_time - now).total_seconds()
        
        attempts = 0
        success = False
        
        try:
            # If target time is in the future, perform pre-emptive checks
            if time_diff > SNIPE_WINDOW_START:
                wait_between_checks = time_diff / (self.pre_checks + 2)
                
                for i in range(self.pre_checks):
                    logging.info(f"{Fore.CYAN}Pre-check {i+1}/{self.pre_checks} for {username}...")
                    check_time = time.time()
                    result.requests.append(check_time)
                    available = name_checker.is_username_available(username)
                    
                    if available:
                        logging.info(f"{Fore.GREEN}Username {username} is already available! Attempting to claim...")
                        if auth.change_username(username):
                            success = True
                            result.claim_time = time.time()
                            attempts += 1
                            break
                    
                    time.sleep(wait_between_checks)
                
                # If not claimed during pre-checks, wait until just before target
                if not success:
                    now = datetime.datetime.now()
                    remaining = (target_time - now).total_seconds() - SNIPE_WINDOW_START/2
                    if remaining > 0:
                        logging.info(f"{Fore.CYAN}Waiting {remaining:.2f}s until final snipe window...")
                        time.sleep(remaining)
            
            # Main snipe attempt near target time
            if not success:
                # Try rapid-fire attempts around the drop time
                logging.info(f"{Fore.CYAN}Starting main snipe attempts for {username}...")
                
                # Keep trying until max attempts or success
                retry_delay = 0.2
                for i in range(self.max_post_attempts):
                    attempts += 1
                    check_time = time.time()
                    result.requests.append(check_time)
                    
                    # Check if available
                    if name_checker.is_username_available(username):
                        # Try to claim
                        if auth.change_username(username):
                            success = True
                            result.claim_time = time.time()
                            break
                        else:
                            # If claim failed but it's available, try again faster
                            retry_delay = 0.1
                    
                    # Add some jitter to avoid pattern detection
                    jitter = random.uniform(0, 0.1)
                    time.sleep(retry_delay + jitter)
            
        except Exception as e:
            result.error = str(e)
            logging.error(f"{Fore.RED}Error during timing snipe: {str(e)}")
            logging.debug(traceback.format_exc())
        
        time_taken = time.time() - start_time
        
        result.success = success
        result.attempts = attempts
        result.time_taken = time_taken
        
        if success:
            logging.info(f"{Fore.GREEN}Successfully claimed {username} using Timing Strategy!")
        else:
            logging.info(f"{Fore.RED}Failed to claim {username} after {attempts} attempts ({time_taken:.2f}s)")
        
        return result


class DistributedStrategy(SnipeStrategy):
    """Uses multiple threads for more aggressive sniping"""
    
    def __init__(self, thread_count=5, attempts_per_thread=8):
        super().__init__(
            "Distributed Strategy",
            "Uses multiple threads for more aggressive sniping"
        )
        self.thread_count = min(thread_count, MAX_THREADS)
        self.attempts_per_thread = attempts_per_thread
        self._stop_flag = threading.Event()
        self._success_flag = threading.Event()
    
    def _snipe_worker(self, auth, name_checker, username, result_dict, thread_id, result):
        """Worker function for threaded sniping"""
        attempts = 0
        
        try:
            start_time = time.time()
            
            # Add some slight offset to distribute thread timing
            time.sleep(thread_id * 0.05)
            
            for i in range(self.attempts_per_thread):
                # Stop if another thread succeeded or we should stop
                if self._stop_flag.is_set() or self._success_flag.is_set():
                    break
                
                attempts += 1
                check_time = time.time()
                result.requests.append(check_time)
                
                # Check if available
                if name_checker.is_username_available(username):
                    # Try to claim
                    if auth.change_username(username):
                        self._success_flag.set()  # Signal other threads to stop
                        result.claim_time = time.time()
                        result_dict[thread_id] = {
                            "success": True,
                            "attempts": attempts,
                            "time": time.time() - start_time
                        }
                        return
                
                # Brief delay between attempts with jitter
                jitter = random.uniform(0, 0.1)
                time.sleep(0.2 + jitter)
            
            result_dict[thread_id] = {
                "success": False,
                "attempts": attempts,
                "time": time.time() - start_time
            }
            
        except Exception as e:
            result_dict[thread_id] = {
                "success": False,
                "attempts": attempts,
                "time": time.time() - start_time,
                "error": str(e)
            }
    
    def execute(self, auth, name_checker, username, target_time=None):
        result = SniperResult(username)
        result.strategy = self.name
        start_time = time.time()
        
        # Reset flags
        self._stop_flag.clear()
        self._success_flag.clear()
        
        # If no target time, use current time
        if not target_time:
            target_time = datetime.datetime.now()
        
        # Calculate wait time until just before target
        now = datetime.datetime.now()
        time_diff = (target_time - now).total_seconds()
        
        # If target time is in the future, wait until just before
        if time_diff > SNIPE_WINDOW_START:
            wait_time = time_diff - SNIPE_WINDOW_START
            logging.info(f"{Fore.CYAN}Waiting {wait_time:.2f} seconds until snipe window...")
            time.sleep(wait_time)
        
        logging.info(f"{Fore.GREEN}Starting distributed snipe for {username} with {self.thread_count} threads...")
        
        thread_results = {}
        threads = []
        
        try:
            # Create and start threads
            for i in range(self.thread_count):
                thread = threading.Thread(
                    target=self._snipe_worker,
                    args=(auth, name_checker, username, thread_results, i, result)
                )
                thread.start()
                threads.append(thread)
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            total_attempts = sum(r.get("attempts", 0) for r in thread_results.values())
            success = any(r.get("success", False) for r in thread_results.values())
            
            result.success = success
            result.attempts = total_attempts
            result.time_taken = time.time() - start_time
            
            if success:
                logging.info(f"{Fore.GREEN}Successfully claimed {username} using Distributed Strategy!")
            else:
                logging.info(f"{Fore.RED}Failed to claim {username} after {total_attempts} attempts ({result.time_taken:.2f}s)")
            
        except Exception as e:
            result.error = str(e)
            logging.error(f"{Fore.RED}Error during distributed snipe: {str(e)}")
            logging.debug(traceback.format_exc())
            self._stop_flag.set()  # Signal all threads to stop
        
        return result


class PrecisionStrategy(SnipeStrategy):
    """
    High-precision strategy that focuses on exact timing using
    network latency compensation and adaptive claiming
    """
    
    def __init__(self, latency_ms=100, pre_window=0.8, post_window=3.0, attempts=20):
        super().__init__(
            "Precision Strategy",
            "High-precision strategy with network latency compensation"
        )
        self.latency_ms = latency_ms / 1000.0  # Convert to seconds
        self.pre_window = pre_window
        self.post_window = post_window
        self.max_attempts = attempts
    
    def execute(self, auth, name_checker, username, target_time=None):
        result = SniperResult(username)
        result.strategy = self.name
        result.latency = self.latency_ms
        start_time = time.time()
        
        # If no target time, use current time
        if not target_time:
            target_time = datetime.datetime.now()
        
        # Calculate wait time until just before target, compensating for latency
        now = datetime.datetime.now()
        time_diff = (target_time - now).total_seconds()
        
        attempts = 0
        success = False
        
        try:
            # If target time is in the future
            if time_diff > self.pre_window:
                # Wait until just before target time, accounting for latency
                wait_time = time_diff - self.pre_window - self.latency_ms
                if wait_time > 0:
                    logging.info(f"{Fore.CYAN}Precision waiting {wait_time:.3f}s until snipe window...")
                    time.sleep(wait_time)
            
            # Start precise sniping attempts
            logging.info(f"{Fore.CYAN}Starting precision snipe with latency compensation of {self.latency_ms*1000:.1f}ms")
            
            # Pre-window attempts (before expected drop)
            pre_start = time.time()
            while time.time() - pre_start < self.pre_window and attempts < self.max_attempts / 2:
                attempts += 1
                check_time = time.time()
                result.requests.append(check_time)
                
                if name_checker.is_username_available(username):
                    if auth.change_username(username):
                        success = True
                        result.claim_time = time.time()
                        logging.info(f"{Fore.GREEN}Successfully claimed in pre-window!")
                        break
                
                # Exponentially decrease delay as we approach target time
                remaining = self.pre_window - (time.time() - pre_start)
                delay = max(0.05, remaining / 4)  # Minimum 50ms delay
                time.sleep(delay)
            
            # If we haven't succeeded yet, continue with post-window attempts
            if not success:
                # Critical period - try rapid-fire attempts
                post_start = time.time()
                attempt_delay = 0.1
                
                while time.time() - post_start < self.post_window and attempts < self.max_attempts:
                    attempts += 1
                    check_time = time.time()
                    result.requests.append(check_time)
                    
                    if name_checker.is_username_available(username):
                        if auth.change_username(username):
                            success = True
                            result.claim_time = time.time()
                            logging.info(f"{Fore.GREEN}Successfully claimed in post-window!")
                            break
                        else:
                            # If we found it's available but claim failed, try even faster
                            attempt_delay = 0.05
                    
                    # Brief delay with slight jitter
                    jitter = random.uniform(0, 0.02)
                    time.sleep(attempt_delay + jitter)
            
        except Exception as e:
            result.error = str(e)
            logging.error(f"{Fore.RED}Error during precision snipe: {str(e)}")
            logging.debug(traceback.format_exc())
        
        time_taken = time.time() - start_time
        
        result.success = success
        result.attempts = attempts
        result.time_taken = time_taken
        
        if success:
            logging.info(f"{Fore.GREEN}Successfully claimed {username} using Precision Strategy!")
        else:
            logging.info(f"{Fore.RED}Failed to claim {username} after {attempts} attempts ({time_taken:.2f}s)")
        
        return result


class AdaptiveStrategy(SnipeStrategy):
    """
    Adaptive strategy that analyzes historical data and adapts its approach
    based on past successes, time of day, and Mojang API behavior
    """
    
    def __init__(self, patterns_file=ATTACK_PATTERNS_FILE):
        super().__init__(
            "Adaptive Strategy",
            "Self-tuning strategy that analyzes historical data"
        )
        self.patterns_file = patterns_file
        self.patterns = self._load_attack_patterns()
        self.selected_strategy = None
    
    def _load_attack_patterns(self):
        """Load attack patterns from file or use defaults"""
        default_patterns = {
            "time_of_day": {
                "morning": {"strategy": "timing", "params": {"pre_checks": 4, "max_post_attempts": 12}},
                "afternoon": {"strategy": "distributed", "params": {"thread_count": 4, "attempts_per_thread": 6}},
                "evening": {"strategy": "burst", "params": {"burst_count": 8, "burst_delay": 0.15}},
                "night": {"strategy": "precision", "params": {"latency_ms": 120, "attempts": 15}}
            },
            "name_length": {
                "short": {"strategy": "burst", "params": {"burst_count": 12, "burst_delay": 0.1}},
                "medium": {"strategy": "distributed", "params": {"thread_count": 4, "attempts_per_thread": 5}},
                "long": {"strategy": "timing", "params": {"pre_checks": 3, "max_post_attempts": 10}}
            },
            "known_successes": {}
        }
        
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    patterns = json.load(f)
                    
                    # Add any missing fields from default_patterns
                    for key, value in default_patterns.items():
                        if key not in patterns:
                            patterns[key] = value
                    
                    return patterns
            except Exception as e:
                logging.error(f"{Fore.RED}Error loading attack patterns: {str(e)}")
        
        return default_patterns
    
    def _save_attack_patterns(self):
        """Save attack patterns to file"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"{Fore.RED}Error saving attack patterns: {str(e)}")
            return False
    
    def _update_known_successes(self, username, strategy_name, params):
        """Update the known successes with a new successful strategy"""
        self.patterns["known_successes"][username] = {
            "strategy": strategy_name,
            "params": params,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._save_attack_patterns()
    
    def _select_best_strategy(self, username, target_time=None):
        """
        Select the best strategy based on historical data,
        time of day, and username characteristics
        """
        # Check if we have a known successful strategy for this username
        if username in self.patterns["known_successes"]:
            known = self.patterns["known_successes"][username]
            logging.info(f"{Fore.CYAN}Using previously successful strategy for {username}")
            return known["strategy"], known["params"]
        
        # Determine time of day
        current_hour = datetime.datetime.now().hour
        time_of_day = "night"
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 22:
            time_of_day = "evening"
        
        # Determine username length category
        length = len(username)
        length_category = "medium"
        if length <= 5:
            length_category = "short"
        elif length >= 10:
            length_category = "long"
        
        # Get strategies based on time of day and name length
        time_strategy = self.patterns["time_of_day"][time_of_day]
        length_strategy = self.patterns["name_length"][length_category]
        
        # Select strategy (prioritize time of day)
        strategy_name = time_strategy["strategy"]
        params = time_strategy["params"]
        
        logging.info(f"{Fore.CYAN}Selected {strategy_name} strategy based on time ({time_of_day}) and name length ({length_category})")
        return strategy_name, params
    
    def execute(self, auth, name_checker, username, target_time=None):
        # Select the best strategy based on analysis
        strategy_name, params = self._select_best_strategy(username, target_time)
        self.selected_strategy = strategy_name
        
        # Create the appropriate strategy with custom parameters
        if strategy_name == "burst":
            strategy = BurstStrategy(**params)
        elif strategy_name == "timing":
            strategy = TimingStrategy(**params)
        elif strategy_name == "distributed":
            strategy = DistributedStrategy(**params)
        elif strategy_name == "precision":
            strategy = PrecisionStrategy(**params)
        else:
            strategy = TimingStrategy()  # Default fallback
        
        # Execute the selected strategy
        result = strategy.execute(auth, name_checker, username, target_time)
        
        # Record successful strategies
        if result.success:
            self._update_known_successes(username, strategy_name, params)
        
        # Ensure we set the strategy name correctly in the result
        result.strategy = f"Adaptive ({strategy_name})"
        
        return result


class Sniper:
    """Main sniper class that orchestrates the sniping process"""
    
    def __init__(self, email=None, password=None, base_delay=1.5, proxies=None):
        """Initialize the sniper with optional authentication"""
        self.auth = MinecraftAuth()
        self.name_checker = NameChecker(base_delay=base_delay, proxies=proxies)
        self.authenticated = False
        self.stats = SniperStats()
        self.strategies = {
            "burst": BurstStrategy(),
            "timing": TimingStrategy(),
            "distributed": DistributedStrategy(),
            "precision": PrecisionStrategy(),
            "adaptive": AdaptiveStrategy()
        }
        
        # Initialize notification manager if available
        self.notifications = None
        if notifications_available:
            self.notifications = NotificationManager()
        
        # Try to authenticate if credentials provided
        if email and password:
            self.authenticate()
    
    def authenticate(self):
        """Authenticate with Minecraft services"""
        if self.auth.authenticate():
            self.authenticated = True
            current_username = self.auth.get_current_username()
            logging.info(f"{Fore.GREEN}Authenticated as {current_username}")
            
            # Send notification
            if self.notifications:
                self.notifications.notify(
                    "authentication_success", 
                    details={"current_user": current_username}
                )
            
            return True
        return False
    
    def is_eligible_for_name_change(self):
        """Check if the account is eligible for a name change"""
        if not self.authenticated:
            logging.error(f"{Fore.RED}Authentication required to check eligibility")
            return False
        
        return self.auth.is_eligible_for_name_change()
    
    def check_username(self, username):
        """Check if a username is available"""
        is_available = self.name_checker.is_username_available(username)
        self.stats.update_check_stats(username, is_available)
        return is_available
    
    def check_usernames_bulk(self, usernames):
        """Check multiple usernames and return available ones"""
        available = []
        
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            results = list(executor.map(self.check_username, usernames))
            
            # Collect available usernames
            for username, is_available in zip(usernames, results):
                if is_available:
                    available.append(username)
        
        return available
    
    def get_drop_time(self, username):
        """Get the estimated drop time for a username"""
        drop_time = self.name_checker.get_drop_time(username)
        
        # Send notification if drop time found
        if drop_time and self.notifications:
            time_until = drop_time - datetime.datetime.now()
            time_until_str = f"{time_until.days}d {time_until.seconds//3600}h {(time_until.seconds//60)%60}m"
            
            self.notifications.notify(
                "drop_time_found",
                username=username,
                details={
                    "drop_time": drop_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "time_until": time_until_str
                }
            )
        
        return drop_time
    
    def claim_username(self, username):
        """Attempt to claim a username immediately"""
        if not self.authenticated:
            logging.error(f"{Fore.RED}Authentication required to claim username")
            return False
        
        # Check eligibility
        if not self.is_eligible_for_name_change():
            logging.error(f"{Fore.RED}Account not eligible for name change")
            return False
        
        # Check availability
        if not self.check_username(username):
            logging.error(f"{Fore.RED}Username {username} is not available")
            return False
        
        # Attempt to claim
        success = self.auth.change_username(username)
        
        # Send notification
        if success and self.notifications:
            self.notifications.notify("username_claimed", username=username)
        
        return success
    
    def snipe_username(self, username, strategy_name="timing", target_time=None, latency_ms=None):
        """
        Snipe a username with the specified strategy.
        
        Args:
            username: The username to snipe
            strategy_name: The strategy to use (burst, timing, distributed, precision, adaptive)
            target_time: Optional target time for the snipe (datetime object)
            latency_ms: Optional network latency in milliseconds for precise timing
        
        Returns:
            SniperResult object with the results
        """
        if not self.authenticated:
            logging.error(f"{Fore.RED}Authentication required to snipe username")
            return SniperResult(username, error="Not authenticated")
        
        # Check eligibility
        if not self.is_eligible_for_name_change():
            logging.error(f"{Fore.RED}Account not eligible for name change")
            return SniperResult(username, error="Account not eligible for name change")
        
        # Get the appropriate strategy
        strategy = self.strategies.get(strategy_name.lower())
        if not strategy:
            logging.error(f"{Fore.RED}Unknown strategy: {strategy_name}")
            return SniperResult(username, error=f"Unknown strategy: {strategy_name}")
        
        # Configure latency compensation for precision strategy
        if strategy_name.lower() == "precision" and latency_ms is not None:
            strategy = PrecisionStrategy(latency_ms=latency_ms)
        
        # If no target time provided, check if we can get it from NameMC
        if not target_time:
            drop_time = self.get_drop_time(username)
            if drop_time:
                target_time = drop_time
                logging.info(f"{Fore.CYAN}Using NameMC drop time: {target_time}")
        
        # Execute the strategy
        logging.info(f"{Fore.CYAN}Starting snipe for {username} using {strategy.name}...")
        result = strategy.execute(self.auth, self.name_checker, username, target_time)
        
        # Record statistics
        self.stats.record_snipe_result(result)
        
        # Send notification if available
        if self.notifications:
            if result.success:
                self.notifications.notify("username_claimed", username=username)
            
            # If the snipe failed but we found it was available, notify
            elif any(self.name_checker.is_username_available(username) for _ in range(2)):
                self.notifications.notify("username_available", username=username)
        
        return result
    
    def monitor_username(self, username, check_interval=1.5, auto_claim=False, callback=None):
        """
        Monitor a username until it becomes available.
        
        Args:
            username: The username to monitor
            check_interval: How often to check (in seconds)
            auto_claim: Whether to automatically claim when available
            callback: Optional callback function to call when status changes
        """
        logging.info(f"{Fore.CYAN}Starting to monitor username: {username}")
        
        checks = 0
        start_time = time.time()
        
        while True:
            checks += 1
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Check if available
            is_available = self.check_username(username)
            
            if is_available:
                logging.info(f"{Fore.GREEN}[{current_time}] Username {username} is AVAILABLE!")
                
                # Send notification
                if self.notifications:
                    self.notifications.notify("username_available", username=username)
                
                # Call callback if provided
                if callback:
                    callback(username, True)
                
                # Attempt to claim if requested
                if auto_claim and self.authenticated:
                    if self.claim_username(username):
                        logging.info(f"{Fore.GREEN}Successfully claimed {username}!")
                        
                        # Send notification
                        if self.notifications:
                            self.notifications.notify("username_claimed", username=username)
                        
                        return True
                    else:
                        logging.error(f"{Fore.RED}Failed to claim {username}")
                
                return True
            else:
                if checks % 10 == 0:  # Only log every 10 checks to avoid spam
                    elapsed = time.time() - start_time
                    logging.info(f"{Fore.RED}[{current_time}] Username {username} is taken. (Check #{checks}, elapsed: {elapsed:.1f}s)")
                
                # Call callback if provided
                if callback:
                    callback(username, False)
            
            # Add jitter to the delay
            jitter = random.uniform(0, 0.5)
            time.sleep(check_interval + jitter)
    
    def test_network_latency(self, iterations=10):
        """Test network latency to Mojang API for timing calibration"""
        logging.info(f"{Fore.CYAN}Testing network latency to Mojang API...")
        
        latencies = []
        for i in range(iterations):
            start = time.time()
            
            try:
                # Make a simple request to the API
                response = self.name_checker.make_request(f"{API_BASE_URL}/status")
                end = time.time()
                
                if response and response.status_code == 200:
                    latency = (end - start) * 1000  # Convert to ms
                    latencies.append(latency)
                    logging.info(f"Request {i+1}/{iterations}: {latency:.2f}ms")
                else:
                    logging.warning(f"Request {i+1}/{iterations}: Failed with status {response.status_code if response else 'N/A'}")
            
            except Exception as e:
                logging.warning(f"Request {i+1}/{iterations}: Failed with error: {str(e)}")
            
            # Add delay between requests
            time.sleep(0.5)
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            logging.info(f"{Fore.CYAN}Latency test results:")
            logging.info(f"  Average: {avg_latency:.2f}ms")
            logging.info(f"  Minimum: {min_latency:.2f}ms")
            logging.info(f"  Maximum: {max_latency:.2f}ms")
            
            return {
                "average": avg_latency,
                "minimum": min_latency,
                "maximum": max_latency,
                "samples": latencies
            }
        else:
            logging.error(f"{Fore.RED}No valid latency measurements obtained")
            return None
    
    def load_proxies_from_file(self, filename):
        """Load proxies from a file"""
        return self.name_checker.load_proxies_from_file(filename)
    
    def test_proxies(self, timeout=5):
        """Test all loaded proxies and remove non-working ones"""
        return self.name_checker.test_proxies(timeout)
    
    def get_stats_report(self):
        """Get a comprehensive statistics report"""
        return self.stats.generate_report()
    
    def configure_notifications(self, discord_webhook=None, email_config=None):
        """Configure notifications"""
        if not self.notifications:
            if notifications_available:
                self.notifications = NotificationManager()
            else:
                logging.error(f"{Fore.RED}Notifications module not available")
                return False
        
        # Configure Discord webhook if provided
        if discord_webhook:
            self.notifications.configure_discord(discord_webhook)
        
        # Configure email if provided
        if email_config and len(email_config) >= 6:
            self.notifications.configure_email(*email_config)
        
        return True


if __name__ == "__main__":
    # Simple test of the sniper
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    sniper = Sniper()
    
    # Test latency
    latency_results = sniper.test_network_latency(5)
    
    # Test check
    username = "notch"
    is_available = sniper.check_username(username)
    print(f"Username {username} is {'available' if is_available else 'taken'}")
    
    # Try to authenticate - will open browser
    if sniper.authenticate():
        print(f"Authenticated as: {sniper.auth.get_current_username()}")
        print(f"Eligible for name change: {sniper.is_eligible_for_name_change()}")
    else:
        print("Authentication failed") 