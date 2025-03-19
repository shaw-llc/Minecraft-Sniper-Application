#!/usr/bin/env python3
"""
Minecraft Username Utilities

This module handles Minecraft username availability checking and related utilities.
"""

import re
import time
import random
import logging
import requests
import datetime
import threading
import concurrent.futures
from bs4 import BeautifulSoup
from colorama import Fore
from requests.exceptions import ProxyError, SSLError, ConnectionError

# Constants
API_BASE_URL = "https://api.mojang.com"
NAME_AVAILABILITY_ENDPOINT = "/users/profiles/minecraft/{username}"
NAMEMC_URL = "https://namemc.com/search?q={username}"
NAMEMC_UPCOMING_URL = "https://namemc.com/minecraft-names"
DROPTIME_PATTERN = r'Availability: <span.+?data-datetime="(\d+)"'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
]

# Default delay between requests to avoid rate limiting
DEFAULT_DELAY = 1.5  # seconds
MAX_RETRIES = 3
PROXY_TIMEOUT = 10  # seconds

class NameChecker:
    """Handle Minecraft username checking and availability"""
    
    def __init__(self, base_delay=DEFAULT_DELAY, proxies=None):
        """
        Initialize the name checker with configurable delay and optional proxies
        
        Args:
            base_delay: Base delay between requests in seconds
            proxies: List of proxy URLs (format: "http://user:pass@host:port" or "http://host:port")
        """
        self.session = requests.Session()
        self.base_delay = base_delay
        self.last_request_time = 0
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.proxy_lock = threading.Lock()
        self.failed_proxies = set()
        self.proxy_performance = {}  # Track response times for each proxy
        
        # Rotate user agents to avoid detection
        self._rotate_user_agent()
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS)
        })
    
    def _get_next_proxy(self):
        """Get the next proxy in the rotation with locking for thread safety"""
        if not self.proxies:
            return None
            
        with self.proxy_lock:
            # Skip failed proxies
            attempts = 0
            while attempts < len(self.proxies):
                proxy_url = self.proxies[self.current_proxy_index]
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                
                if proxy_url not in self.failed_proxies:
                    return {"http": proxy_url, "https": proxy_url}
                
                attempts += 1
            
            # If all proxies have failed, try using a random one from failed list
            if self.failed_proxies:
                proxy_url = random.choice(list(self.failed_proxies))
                return {"http": proxy_url, "https": proxy_url}
            
            return None
    
    def add_proxy(self, proxy_url):
        """Add a proxy to the rotation"""
        if proxy_url and proxy_url not in self.proxies:
            self.proxies.append(proxy_url)
            return True
        return False
    
    def load_proxies_from_file(self, filename):
        """Load proxies from a file (one proxy per line)"""
        try:
            with open(filename, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.proxies.extend(proxies)
            logging.info(f"{Fore.GREEN}Loaded {len(proxies)} proxies from {filename}")
            return len(proxies)
        except Exception as e:
            logging.error(f"{Fore.RED}Error loading proxies from file: {str(e)}")
            return 0
    
    def test_proxies(self, timeout=5):
        """Test all proxies and remove non-working ones"""
        working_proxies = []
        
        logging.info(f"{Fore.CYAN}Testing {len(self.proxies)} proxies...")
        
        def test_proxy(proxy_url):
            try:
                proxies = {"http": proxy_url, "https": proxy_url}
                start_time = time.time()
                response = requests.get(
                    "https://api.mojang.com/status", 
                    proxies=proxies, 
                    timeout=timeout
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    return (proxy_url, elapsed)
                return None
            except Exception:
                return None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(test_proxy, proxy) for proxy in self.proxies]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    proxy_url, elapsed = result
                    working_proxies.append(proxy_url)
                    self.proxy_performance[proxy_url] = elapsed
        
        # Update proxies list with only working proxies
        self.proxies = working_proxies
        
        # Sort proxies by performance (fastest first)
        self.proxies.sort(key=lambda p: self.proxy_performance.get(p, float('inf')))
        
        logging.info(f"{Fore.GREEN}Found {len(working_proxies)} working proxies out of {len(self.proxies)}")
        return len(working_proxies)
    
    def _throttle(self):
        """Apply throttling to avoid rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.base_delay:
            # Add some randomness to the delay to avoid patterns
            jitter = random.uniform(0, 0.5)
            sleep_time = self.base_delay - time_since_last + jitter
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url, method="get", data=None, headers=None, timeout=PROXY_TIMEOUT, retry_count=0):
        """
        Make a request with proxy support and automatic retries
        
        Args:
            url: The URL to request
            method: HTTP method (get or post)
            data: Optional data for POST requests
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            retry_count: Current retry count (used internally)
            
        Returns:
            requests.Response object or None on failure
        """
        if retry_count >= MAX_RETRIES:
            logging.error(f"{Fore.RED}Maximum retries exceeded for URL: {url}")
            return None
        
        # Apply throttling
        self._throttle()
        
        # Rotate user agent occasionally
        if random.random() < 0.2:
            self._rotate_user_agent()
        
        # Get the next proxy (if available)
        proxy = self._get_next_proxy() if self.proxies else None
        
        # Merge headers with session headers
        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)
        
        try:
            if method.lower() == "post":
                response = self.session.post(
                    url, 
                    json=data, 
                    headers=merged_headers, 
                    proxies=proxy, 
                    timeout=timeout
                )
            else:
                response = self.session.get(
                    url, 
                    headers=merged_headers, 
                    proxies=proxy, 
                    timeout=timeout
                )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logging.warning(f"{Fore.YELLOW}Rate limited. Waiting {retry_after} seconds.")
                time.sleep(retry_after)
                return self.make_request(url, method, data, headers, timeout, retry_count + 1)
            
            return response
            
        except (ProxyError, SSLError, ConnectionError) as e:
            # Mark proxy as failed and retry with a different one
            if proxy:
                proxy_url = proxy.get("http")
                with self.proxy_lock:
                    self.failed_proxies.add(proxy_url)
                logging.warning(f"{Fore.YELLOW}Proxy failed: {proxy_url}, trying another proxy.")
            
            return self.make_request(url, method, data, headers, timeout, retry_count + 1)
            
        except Exception as e:
            logging.error(f"{Fore.RED}Request error: {str(e)}")
            time.sleep(1)  # Brief delay before retry
            return self.make_request(url, method, data, headers, timeout, retry_count + 1)
    
    def is_username_available(self, username):
        """Check if a username is available via Mojang API"""
        url = f"{API_BASE_URL}{NAME_AVAILABILITY_ENDPOINT.format(username=username)}"
        response = self.make_request(url)
        
        if not response:
            return None
        
        # Status code 204 (No Content) means the username is available
        if response.status_code == 204:
            return True
        # Status code 200 means the username is taken
        elif response.status_code == 200:
            return False
        else:
            logging.error(f"{Fore.RED}Error checking username availability: {response.status_code}")
            return None
    
    def get_drop_time(self, username):
        """
        Get the estimated drop time for a username using NameMC.
        Returns a datetime object if a drop time is found, None otherwise.
        """
        url = NAMEMC_URL.format(username=username)
        response = self.make_request(url)
        
        if not response or response.status_code != 200:
            return None
        
        try:
            # Look for the drop time in the HTML using both regex and BeautifulSoup for robustness
            match = re.search(DROPTIME_PATTERN, response.text)
            
            if match:
                drop_timestamp = int(match.group(1)) / 1000  # Convert from milliseconds to seconds
                drop_time = datetime.datetime.fromtimestamp(drop_timestamp)
                return drop_time
            
            # If regex failed, try with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            availability_row = soup.find('tr', text=lambda t: t and 'Availability' in t if t else False)
            
            if availability_row:
                date_span = availability_row.find('span', attrs={'data-datetime': True})
                if date_span:
                    drop_timestamp = int(date_span['data-datetime']) / 1000
                    drop_time = datetime.datetime.fromtimestamp(drop_timestamp)
                    return drop_time
            
            return None
            
        except Exception as e:
            logging.error(f"{Fore.RED}Error checking drop time for {username}: {str(e)}")
            return None
    
    def get_name_length(self, username):
        """Get the character length of a username"""
        return len(username)
    
    def is_valid_minecraft_username(self, username):
        """Check if a username follows Minecraft username rules"""
        # Minecraft usernames can only contain letters, numbers, and underscores
        # They must be between 3 and 16 characters long
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
            return False
        return True
    
    def is_premium_username(self, username):
        """
        Check if a username belongs to a premium (paid) account.
        This is determined by checking if the API returns user data.
        """
        url = f"{API_BASE_URL}{NAME_AVAILABILITY_ENDPOINT.format(username=username)}"
        response = self.make_request(url)
        
        if not response:
            return None, None
        
        # Status code 200 means it's a premium account
        if response.status_code == 200:
            user_data = response.json()
            return True, user_data
        # Status code 204 means it's not a premium account
        elif response.status_code == 204:
            return False, None
        else:
            logging.error(f"{Fore.RED}Error checking premium status: {response.status_code}")
            return None, None
    
    def get_all_account_info(self, username):
        """
        Get comprehensive info about a Minecraft account from various sources.
        Returns a dictionary with all available info.
        """
        info = {"username": username}
        
        # Check premium status
        is_premium, user_data = self.is_premium_username(username)
        info["exists"] = bool(is_premium)
        
        if is_premium and user_data:
            info["uuid"] = user_data.get("id")
            info["legacy"] = user_data.get("legacy", False)
            info["demo"] = user_data.get("demo", False)
            
            # Get profile skin info (if available)
            try:
                if info["uuid"]:
                    profile_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{info['uuid']}"
                    profile_resp = self.make_request(profile_url)
                    if profile_resp and profile_resp.status_code == 200:
                        info["profile"] = profile_resp.json()
            except Exception as e:
                logging.debug(f"Error getting profile info: {str(e)}")
        
        # Get drop time if username is taken
        if is_premium:
            drop_time = self.get_drop_time(username)
            if drop_time:
                info["drop_time"] = drop_time
                info["time_until_drop"] = drop_time - datetime.datetime.now()
        
        # Add name properties
        info["length"] = len(username)
        info["is_valid"] = self.is_valid_minecraft_username(username)
        
        # Categorize name type
        if info["length"] <= 4:
            info["name_type"] = "short"
        elif re.match(r'^[a-zA-Z]+$', username):
            info["name_type"] = "alphabetical"
        elif re.match(r'^[0-9]+$', username):
            info["name_type"] = "numerical"
        elif "_" in username:
            info["name_type"] = "underscored"
        else:
            info["name_type"] = "regular"
        
        return info
    
    def get_upcoming_available_names(self, limit=10, max_pages=2):
        """
        Get upcoming available names from NameMC by scraping the website.
        
        Args:
            limit: Maximum number of names to return
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of dictionaries with name, drop_time, and time_until
        """
        logging.info(f"{Fore.CYAN}Fetching upcoming available names from NameMC...")
        
        upcoming_names = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{NAMEMC_UPCOMING_URL}?sort=asc&page={page}"
                response = self.make_request(url)
                
                if not response or response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                name_cards = soup.select('.card-body')
                
                for card in name_cards:
                    if len(upcoming_names) >= limit:
                        break
                    
                    try:
                        name_link = card.select_one('a[href*="/name/"]')
                        if not name_link:
                            continue
                            
                        name = name_link.text.strip()
                        
                        # Find timestamp
                        time_element = card.select_one('time[data-timestamp]')
                        if not time_element:
                            continue
                            
                        timestamp = int(time_element['data-timestamp'])
                        drop_time = datetime.datetime.fromtimestamp(timestamp / 1000)
                        time_until = drop_time - datetime.datetime.now()
                        
                        # Only include names that will be available in the future
                        if time_until.total_seconds() > 0:
                            upcoming_names.append({
                                "name": name,
                                "drop_time": drop_time,
                                "time_until": time_until,
                                "length": len(name)
                            })
                    except Exception as e:
                        logging.debug(f"Error parsing name card: {str(e)}")
                
            except Exception as e:
                logging.error(f"{Fore.RED}Error fetching upcoming names page {page}: {str(e)}")
        
        # Sort by drop time
        upcoming_names.sort(key=lambda x: x["drop_time"])
        
        if not upcoming_names:
            # Fallback to simulated data if scraping failed
            logging.warning(f"{Fore.YELLOW}Failed to scrape real data, using simulated upcoming names")
            upcoming_names = self._get_simulated_upcoming_names(limit)
        
        return upcoming_names[:limit]
    
    def _get_simulated_upcoming_names(self, limit=10):
        """Generate simulated upcoming names for demonstration purposes"""
        sample_names = [
            "diamond", "emerald", "obsidian", "redstone", "netherite",
            "zombie", "creeper", "phantom", "wither", "ender",
            "crafting", "brewing", "mining", "fishing", "adventuring",
            "nether", "overworld", "end", "aether", "twilight"
        ]
        
        # Shuffle the list
        random.shuffle(sample_names)
        
        # Create fake drop times
        now = datetime.datetime.now()
        upcoming_names = []
        
        for i, name in enumerate(sample_names[:limit]):
            # Random drop time in the next 30 days
            drop_time = now + datetime.timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            upcoming_names.append({
                "name": name,
                "drop_time": drop_time,
                "time_until": drop_time - now,
                "length": len(name)
            })
        
        # Sort by drop time
        upcoming_names.sort(key=lambda x: x["drop_time"])
        
        return upcoming_names
    
    def check_names_by_length(self, length, limit=100):
        """
        Find available usernames of specific length.
        Returns a list of available usernames.
        
        This is an experimental feature and might be slow and inefficient.
        """
        if length < 3 or length > 16:
            logging.error(f"{Fore.RED}Invalid name length. Minecraft usernames must be 3-16 characters.")
            return []
        
        available_names = []
        
        # Character sets to try
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789_'
        
        # For shorter lengths, we can try more combinations
        if length <= 4:
            # For very short names, use a limited character set to avoid too many requests
            pattern_chars = chars[:12] if length == 3 else chars[:20]
            patterns = [''.join(p) for p in self._generate_patterns(pattern_chars, length)]
            
            # Randomize and limit the patterns
            random.shuffle(patterns)
            patterns = patterns[:limit*3]  # Try more to reach our limit
            
            for pattern in patterns:
                if len(available_names) >= limit:
                    break
                    
                if self.is_username_available(pattern):
                    available_names.append(pattern)
        else:
            # For longer lengths, use random generation
            attempts = 0
            max_attempts = limit * 10  # Try harder to find names
            
            while len(available_names) < limit and attempts < max_attempts:
                attempts += 1
                
                # Generate a random username of specified length
                username = ''.join(random.choice(chars) for _ in range(length))
                
                if self.is_username_available(username):
                    available_names.append(username)
        
        return available_names
    
    def _generate_patterns(self, chars, length, current=''):
        """Helper function to generate all possible patterns of given length"""
        if length == 0:
            yield current
            return
            
        for char in chars:
            yield from self._generate_patterns(chars, length - 1, current + char)


if __name__ == "__main__":
    # Simple test of the name checker
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    checker = NameChecker()
    
    test_username = "notch"
    print(f"Checking username: {test_username}")
    
    if checker.is_username_available(test_username):
        print(f"{test_username} is available!")
    else:
        print(f"{test_username} is taken.")
        
    drop_time = checker.get_drop_time(test_username)
    if drop_time:
        print(f"{test_username} will be available at: {drop_time}")
    else:
        print(f"No drop time found for {test_username}")
        
    # Test upcoming names
    upcoming = checker.get_upcoming_available_names(5)
    print("\nUpcoming available names:")
    for name in upcoming:
        print(f"{name['name']} - Available in: {name['time_until'].days}d {name['time_until'].seconds//3600}h") 