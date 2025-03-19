MINECRAFT USERNAME SNIPER
=======================

A powerful tool for checking, monitoring, and claiming Minecraft usernames when they become available with high precision.

DISCLAIMER
----------

This tool is provided for educational purposes only. Please be aware that:

- Using automated tools to interact with Mojang's API may violate their Terms of Service
- Excessive use can lead to IP bans or account suspensions
- We do not encourage or support any violation of Mojang's Terms of Service
- Use at your own risk

NEW! BEGINNER-FRIENDLY INTERFACE
--------------------------------

We've added a brand new beginner-friendly interface that makes it easy for anyone to use this tool, even if you have no coding experience!

Getting Started for Beginners:

1. Install Python: If you don't have Python installed, download and install it from python.org (version 3.6 or higher)

2. Run the Setup Script: Double-click on setup.py or run it from the command line:
   python setup.py
   
   This will guide you through the installation process with simple instructions.

3. Launch the Easy Interface: Once setup is complete, run:
   python easy_sniper.py
   
   Or use the desktop shortcut (Windows users)

4. Use the Menu System: The easy interface provides simple menus to:
   - Check if a username is available
   - Monitor a username until it becomes available
   - Claim a username when it's available
   - Check your account status
   - Get help and instructions

No coding knowledge required! The tool will walk you through each step.

FEATURES
--------

Core Features:
- Check if a Minecraft username is currently available
- Monitor one or multiple usernames for availability
- Bulk check hundreds of usernames at once
- Automatically claim usernames when they become available
- Integration with NameMC for target drop time detection

Advanced Features:
- Multiple Sniping Strategies - Choose from 5 different strategies:
  - Timing Strategy: Precise timing with pre-emptive checks
  - Burst Strategy: Rapid-fire requests at the target time
  - Distributed Strategy: Multi-threaded approach for maximum coverage
  - Precision Strategy: Network latency compensation with adaptive timing
  - Adaptive Strategy: Self-tuning approach based on historical success patterns
- Proxy Support - Rotate between multiple proxies to avoid rate limits
- Microsoft Authentication - Full OAuth implementation for secure login
- Advanced Analytics - Track success rates and optimize your approach
- Comprehensive Notifications - Get alerts via Discord, email, and desktop
- High-Precision Timing - Millisecond-level precision for critical timing
- Smart Error Handling - Automatic recovery from rate limits and network issues

Technical Features:
- Multithreaded architecture for high performance
- Automatic proxy rotation and testing
- Detailed statistics and success tracking
- Network latency compensation
- Color-coded console output
- Comprehensive logging
- Configurable notification channels
- Cross-platform compatibility

INSTALLATION
------------

Easy Installation (Recommended for Beginners):

1. Download this repository by clicking the green "Code" button and selecting "Download ZIP"
2. Extract the ZIP file to a folder on your computer
3. Run the setup script by double-clicking setup.py or running:
   python setup.py
4. Follow the on-screen instructions

Advanced Installation (For Developers):

1. Clone this repository:
   git clone https://github.com/yourusername/minecraft-sniper.git
   cd minecraft-sniper

2. Install the required dependencies:
   pip install -r requirements.txt

3. (Optional) Set up a file with proxies (one per line) if you want to use proxy rotation:
   http://user:pass@host:port
   http://host:port

USAGE
-----

Beginner-Friendly Interface:

Run the easy interface:
python easy_sniper.py

This will open a menu-driven interface where you can:
- Check a username's availability
- Monitor a username until it becomes available
- Claim an available username
- Check your account status
- See help and instructions

Advanced Command-Line Interface:

The tool also provides two command-line interfaces: a simple one for basic use and an advanced interface with more features.

Basic Usage:

To check if a username is available:
python minecraft_sniper.py check username

To monitor a username until it becomes available:
python minecraft_sniper.py monitor username

To snipe a username at a specific time:
python minecraft_sniper.py snipe username -t "2023-08-15 14:30:00" -s distributed

Advanced Usage:

The advanced version includes more features and options:
python advanced_sniper.py check -f usernames.txt --save results.json
python advanced_sniper.py snipe -u coolname -s adaptive -a

Command Line Arguments (Basic Sniper):
Commands:
  check     Check if a username is available
  monitor   Monitor a username until it becomes available
  snipe     Snipe a username at the specified time
  status    Check account status and eligibility
  test      Test network latency and other functions

Global options:
  -a, --auth          Use authentication (requires browser login or .env file)
  -v, --verbose       Enable verbose output for debugging

Command Line Arguments (Advanced Sniper):
Commands:
  check     Check username availability
  monitor   Monitor usernames until they become available
  snipe     Snipe usernames at specific times
  upcoming  Check for upcoming available usernames
  test      Test network latency and other functions
  status    Check account status and eligibility

Global options:
  -a, --auth          Use authentication (required for claiming and sniping)
  --threads THREADS   Maximum number of concurrent threads (default: 5)
  -v, --verbose       Enable verbose output for debugging

Authentication:

The tool uses Microsoft's OAuth flow for authentication. When you run a command with the -a flag, it will:
1. Open a browser window for you to log in with your Microsoft account
2. Wait for successful authentication
3. Store the tokens securely for future use

You can also create a .env file in the same directory with the following content (though browser auth is more secure):
EMAIL=your_microsoft_email@example.com
PASSWORD=your_microsoft_password

Configuring Notifications:

To set up notifications, you can configure the notification channels in the tool.

Discord Notifications:
python notifications.py configure discord "your_webhook_url"

Email Notifications:
python notifications.py configure email "smtp.gmail.com" 587 "your_email@gmail.com" "password" "from@gmail.com" "to@gmail.com"

Testing Notifications:
python notifications.py test

SNIPING STRATEGIES
-----------------

Timing Strategy:
Best for: Names with known drop times where precision is key
- Makes pre-emptive checks before the target time
- Increases check frequency as the target time approaches
- Adjusts claim attempts based on availability detection

Burst Strategy:
Best for: Quick claims when a name is just found to be available
- Sends a rapid burst of claim requests
- Low delay between attempts
- Simple but effective for immediate availability

Distributed Strategy:
Best for: High-competition usernames
- Uses multiple threads to maximize chances
- Distributes requests across multiple workers
- Coordinates between threads to avoid conflicts

Precision Strategy:
Best for: Names with exact drop times where milliseconds matter
- Compensates for network latency
- Uses adaptive timing windows
- Adjusts behavior based on availability status

Adaptive Strategy:
Best for: When you're not sure which strategy will work best
- Analyzes historical successes
- Adapts based on time of day and username characteristics
- Learns from past attempts and improves over time

FUTURE IMPROVEMENTS
------------------

- ✅ GUI interface for easier use (now available with easy_sniper.py!)
- More advanced proxy rotation and management
- Machine learning for optimal strategy selection
- Integration with more notification services
- Support for automatic batch operations
- Detection of rare/valuable usernames
- Support for cross-platform desktop notifications

TIPS FOR SUCCESSFUL SNIPING
--------------------------

1. Test Your Connection: Use the latency test feature to understand your network characteristics
2. Use Proxies: Distribute requests across multiple IPs to avoid rate limits
3. Target Specific Times: Focus on known drop times rather than continuous monitoring
4. Choose the Right Strategy: Use the adaptive strategy if you're unsure, or select a specific strategy based on the username type
5. Be Patient: Username sniping is competitive, and success often requires multiple attempts
6. Monitor Stats: Check your statistics to see which strategies work best for you

PROJECT STRUCTURE
----------------

- minecraft_sniper.py - Simple command-line interface
- advanced_sniper.py - Advanced features and multi-username support
- easy_sniper.py - Beginner-friendly interface with menus
- setup.py - Setup assistant for easy installation
- sniper.py - Core sniping functionality and strategies
- minecraft_auth.py - Microsoft authentication implementation
- name_utils.py - Username checking and utilities
- notifications.py - Notification system for various channels

CONTRIBUTORS
-----------

- Your Name - Initial work

LICENSE
-------

This project is licensed under the MIT License - see the LICENSE file for details. 