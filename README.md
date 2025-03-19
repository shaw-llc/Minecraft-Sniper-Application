# Minecraft Username Sniper

A powerful tool for checking, monitoring, and claiming Minecraft usernames when they become available with high precision. **Updated and verified working as of October 2023.**

![Minecraft Username Sniper](https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/img/header/logo.png)

## ⚠️ Disclaimer

This tool is provided for educational purposes only. Please be aware that:

- Using automated tools to interact with Mojang's API may violate their Terms of Service
- Excessive use can lead to IP bans or account suspensions
- We do not encourage or support any violation of Mojang's Terms of Service
- Use at your own risk

## 📢 Latest Updates (2023)

**Important API Information**: According to current research, Mojang's API enforces a rate limit of approximately 60 requests per minute. Our tool intelligently manages these limits to avoid temporary blocks while maximizing effectiveness.

**Key Improvements**:
- Smart rate limiting system that respects Mojang's 60 requests/minute constraint
- Optimized batch processing of username availability checks
- Enhanced proxy support for distributed requests
- Improved error handling and recovery from rate limiting

## ⚖️ Ethical Considerations

Based on the latest research about Minecraft username sniping, it's important to understand:

1. **Terms of Service**: Using automated tools to interact with Mojang's API may violate their EULA, especially for commercial purposes.

2. **Personal Use**: While personal, non-commercial use exists in a gray area, you should be aware of the potential risks:
   - Account suspension or ban
   - IP rate limiting
   - Loss of access to Minecraft services

3. **Rate Limiting**: Our tool is designed to respect Mojang's rate limits (60 requests/minute) to minimize impact on their services and reduce your risk of penalties.

4. **Community Impact**: Aggressive sniping can create artificial scarcity and potentially prevent legitimate users from obtaining usernames through normal means.

We've designed this tool primarily for educational purposes and personal use. It includes safeguards to respect rate limits and reduce potential negative impacts.

## 🚀 Quick Setup for Complete Beginners

Never used Python before? No problem! Follow these simple steps:

1. **Download this tool**:
   - Click the green "Code" button above, then "Download ZIP"
   - Extract the ZIP file to a folder on your computer

2. **Install Python**:
   - Download and install Python from [python.org](https://python.org) (version 3.6 or higher)
   - **IMPORTANT**: During installation, check the box that says "Add Python to PATH"

3. **Run the Setup Helper**:
   - Double-click on `setup.py` to run the setup wizard
   - If double-clicking doesn't work, open Command Prompt (Windows) or Terminal (Mac/Linux) and type:
     ```
     cd path/to/extracted/folder
     python setup.py
     ```
   - Follow the simple on-screen instructions

4. **Launch the Easy Interface**:
   - Double-click on `easy_sniper.py`
   - If that doesn't work, use Command Prompt/Terminal:
     ```
     python easy_sniper.py
     ```
   - For Windows users, a desktop shortcut is also created during setup

5. **Use the Simple Menu System**:
   - Just follow the numbered options on screen!
   - No coding knowledge required!

## ✨ Features

### Core Features
- Check if a Minecraft username is currently available
- Monitor one or multiple usernames for availability
- Bulk check hundreds of usernames at once
- Automatically claim usernames when they become available
- Integration with NameMC for target drop time detection

### Advanced Features
- **Multiple Sniping Strategies** - Choose from 5 different strategies:
  - Timing Strategy: Precise timing with pre-emptive checks
  - Burst Strategy: Rapid-fire requests at the target time
  - Distributed Strategy: Multi-threaded approach for maximum coverage
  - Precision Strategy: Network latency compensation with adaptive timing
  - Adaptive Strategy: Self-tuning approach based on historical success patterns
- **Proxy Support** - Rotate between multiple proxies to avoid rate limits
- **Microsoft Authentication** - Up-to-date Microsoft OAuth implementation for secure login
- **Advanced Analytics** - Track success rates and optimize your approach
- **Comprehensive Notifications** - Get alerts via Discord, email, and desktop
- **High-Precision Timing** - Millisecond-level precision for critical timing
- **Smart Error Handling** - Automatic recovery from rate limits and network issues

## 🛠️ Detailed Setup Guide

### System Requirements
- Windows, macOS, or Linux
- Python 3.6 or higher
- Internet connection
- A Microsoft/Minecraft account

### Step-by-Step Installation

#### For Windows Users:
1. Download Python 3.9+ from [python.org](https://python.org)
   - During installation, **make sure to check "Add Python to PATH"**
2. Download this tool by clicking the green "Code" button, then "Download ZIP"
3. Extract the ZIP file to a folder
4. Double-click `setup.py` to run the setup wizard
   - If double-clicking doesn't work, open Command Prompt and type:
   ```
   cd path\to\extracted\folder
   python setup.py
   ```
5. Once setup completes, use the desktop shortcut or double-click `easy_sniper.py`

#### For macOS Users:
1. Install Python using Homebrew (recommended) or from [python.org](https://python.org)
   ```bash
   # Install Homebrew if you don't have it
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   # Install Python
   brew install python
   ```
2. Download this tool by clicking the green "Code" button, then "Download ZIP"
3. Open Terminal and navigate to the extracted folder:
   ```bash
   cd path/to/extracted/folder
   ```
4. Run the setup wizard:
   ```bash
   python3 setup.py
   ```
5. Launch the easy interface:
   ```bash
   python3 easy_sniper.py
   ```

#### For Linux Users:
1. Install Python using your package manager:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip
   
   # Fedora
   sudo dnf install python3 python3-pip
   ```
2. Download and extract this tool
3. Open Terminal and navigate to the folder:
   ```bash
   cd path/to/extracted/folder
   ```
4. Run the setup wizard:
   ```bash
   python3 setup.py
   ```
5. Launch the easy interface:
   ```bash
   python3 easy_sniper.py
   ```

## 📋 How to Use (Easy Interface)

The easy interface provides a simple menu system:

1. **Check if a username is available**:
   - Select option 1 from the main menu
   - Enter the username you want to check
   - The tool will tell you if it's available or when it might become available

2. **Monitor a username until it becomes available**:
   - Select option 2 from the main menu
   - Enter the username you want to monitor
   - Specify how often to check (in seconds)
   - Choose whether to automatically claim when available
   - The tool will notify you when the username becomes available

3. **Claim a username**:
   - Select option 3 from the main menu
   - Enter the username you want to claim
   - Choose a sniping strategy
   - The tool will attempt to claim the username

4. **Check your account status**:
   - Select option 4 from the main menu
   - The tool will check if your account is eligible for a name change

## 🔍 Troubleshooting

### Common Issues and Solutions:

1. **"Python is not recognized" error**:
   - Make sure you checked "Add Python to PATH" during installation
   - Restart your computer and try again
   - Try using `python3` instead of `python`

2. **Setup fails with dependency errors**:
   - Run this command manually: `pip install requests colorama python-dotenv urllib3 beautifulsoup4`
   - Make sure your internet connection is working

3. **Authentication issues**:
   - Make sure you're using a valid Microsoft account with Minecraft ownership
   - Clear the `auth_cache.json` file and try again
   - Check your internet connection

4. **"No module named..." errors**:
   - Re-run the setup script: `python setup.py`
   - Try manually installing the missing module: `pip install module_name`

5. **Rate limiting issues**:
   - The Mojang API has strict rate limits
   - Decrease check frequency to avoid rate limits
   - Consider using proxies for advanced usage

## 📞 Need More Help?

If you encounter issues not covered in this guide:

1. Check for errors in the console output
2. Make sure you're using the latest version of this tool
3. Verify your Python installation is working correctly
4. Try running the tool with the `-v` flag for verbose output:
   ```bash
   python easy_sniper.py -v
   ```

## 🛡️ Security Notes

This tool uses Microsoft's official OAuth flow. Your credentials are never stored in plain text. When you authenticate:

1. A browser window will open for you to log in directly on Microsoft's website
2. After login, Microsoft provides a secure token to the tool
3. This token is stored locally in `auth_cache.json`

If you prefer not to use browser authentication, you can create a `.env` file with your credentials, but this is less secure.

## 🔥 Pro Tips for Maximum Success

1. **Research usernames before they drop**: Use the tool to check when names will become available.
2. **Test your connection**: Run the latency test before attempting to snipe.
3. **Use the right strategy**:
   - For low-competition names: Timing Strategy is often sufficient
   - For high-competition names: Distributed or Adaptive Strategies work best
4. **Prepare your account**: Make sure your account is eligible for a name change before the name drops.
5. **Use a stable internet connection**: Wired connections are more reliable than Wi-Fi.

## 🙏 Credits and Acknowledgements

This tool was developed for educational purposes. Special thanks to:
- The Minecraft community for feedback and testing
- Contributors who have helped improve this tool

---

By using this tool, you agree to the disclaimer at the top of this README. Remember to use this tool responsibly and in accordance with Mojang's Terms of Service. 