# OpenMC Username Sniper - Desktop Application

A modern, user-friendly desktop application for checking, monitoring, and claiming Minecraft usernames when they become available.

![OpenMC Username Sniper](https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/img/header/logo.png)

## Features

- **User-Friendly Interface**: Modern, intuitive UI built with React and Material UI
- **Username Availability Checker**: Instantly check if a Minecraft username is available
- **Real-Time Monitoring**: Monitor usernames until they become available
- **Smart Sniping**: Multiple strategies for claiming usernames at the perfect moment
- **Account Management**: Easy Microsoft account authentication
- **Customizable Settings**: Configure the app to your preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Batch Processing**: Handle multiple usernames at once
- **Smart Scheduling**: Schedule monitoring for upcoming username drops
- **Notifications**: Get notified on desktop, Discord, or via email
- **Themes**: Choose between dark and light themes with customizable accent colors

## Download

Download the latest version for your platform:

- [Windows (64-bit)](https://github.com/yourusername/OpenMC-Username-Sniper/releases/latest/download/OpenMC-Username-Sniper-Setup-Windows.exe)
- [macOS](https://github.com/yourusername/OpenMC-Username-Sniper/releases/latest/download/OpenMC-Username-Sniper-macOS.dmg)
- [Linux (deb)](https://github.com/yourusername/OpenMC-Username-Sniper/releases/latest/download/openmc-username-sniper_linux.deb)
- [Linux (AppImage)](https://github.com/yourusername/OpenMC-Username-Sniper/releases/latest/download/openmc-username-sniper_linux.AppImage)

## Installation Instructions

### Windows
1. Download the Windows installer (.exe)
2. Run the installer and follow the prompts
3. The application will be installed in your Program Files directory
4. Launch the app from the Start menu or desktop shortcut

### macOS
1. Download the macOS disk image (.dmg)
2. Open the DMG file
3. Drag the application to your Applications folder
4. Right-click the app and select "Open" (required for first launch due to security settings)
5. Allow the app in your security preferences if prompted

### Linux
#### Debian/Ubuntu:
```bash
sudo dpkg -i openmc-username-sniper_linux.deb
sudo apt-get install -f # Install any missing dependencies
```

#### AppImage:
```bash
chmod +x openmc-username-sniper_linux.AppImage
./openmc-username-sniper_linux.AppImage
```

## Quick Start Guide

1. **Check a Username**:
   - In the app, go to the "Check Username" tab
   - Enter the Minecraft username you want to check
   - Click the "Check" button to see if it's available

2. **Monitor a Username**:
   - Go to the "Monitor Username" tab
   - Enter the username you want to monitor
   - Set your preferred check interval
   - Click "Start Monitoring" to begin watching for availability

3. **Claim a Username**:
   - When a username becomes available, go to the "Claim Username" tab
   - Enter the username you want to claim
   - Choose your preferred sniping strategy
   - Click "Claim Username" to attempt to claim it

4. **Batch Processing**:
   - Go to the "Batch Processor" tab
   - Enter multiple usernames separated by commas, or
   - Click "Import from File" to load a text file with usernames
   - Click "Process Batch" to check multiple usernames at once

5. **Schedule Monitoring**:
   - Go to the "Schedule Monitor" tab
   - Search for usernames that will be available soon
   - Select a username and set the monitoring parameters
   - The app will automatically start monitoring at the appropriate time

## For Developers

### Prerequisites

- Node.js 16 or newer
- Python 3.6 or newer
- npm or yarn

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/OpenMC-Username-Sniper.git
   cd OpenMC-Username-Sniper
   ```

2. Run the setup script:
   ```bash
   node setup-app.js
   ```

3. Or manually install dependencies:
   ```bash
   npm install
   npm run copy-python
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. In a separate terminal, start Electron:
   ```bash
   npm start
   ```

### Building the Application

To build the application for your current platform:

```bash
npm run make
```

This will create distributables in the `out` directory.

## Keyboard Shortcuts

- `Ctrl/Cmd + C`: Check username (when in the Check Username tab)
- `Ctrl/Cmd + M`: Start/stop monitoring (when in the Monitor tab)
- `Ctrl/Cmd + S`: Open settings
- `Ctrl/Cmd + B`: Switch to Batch Processor
- `Ctrl/Cmd + ,`: Toggle theme (light/dark)
- `Ctrl/Cmd + Q`: Quit application

## Auto-Updates

The application will automatically check for updates on startup. You can also manually check for updates in the Settings tab.

## ⚠️ Disclaimer

This tool is provided for educational purposes only. Please be aware that:

- Using automated tools to interact with Mojang's API may violate their Terms of Service
- Excessive use can lead to IP bans or account suspensions
- We do not encourage or support any violation of Mojang's Terms of Service
- Use at your own risk

## License

This project is licensed under the MIT License - see the LICENSE file for details. 