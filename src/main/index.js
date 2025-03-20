const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');
const Store = require('electron-store');
const { sendNotification } = require('./notifications');
const { autoUpdater } = require('electron-updater');
const { 
  initializeScheduler, 
  getScheduledMonitors, 
  saveScheduledMonitor, 
  deleteScheduledMonitor, 
  scheduleMonitor, 
  handleMonitoringResult, 
  cancelAllScheduledMonitors 
} = require('./scheduler');

// Initialize store for app settings
const store = new Store();

// Keep track of active processes
let monitoringProcess = null;
let claimingProcess = null;
let authProcess = null;

// Keep track of active scheduled monitor ID
let activeScheduledMonitorId = null;

// Set up logging for auto-updater
autoUpdater.logger = require('electron-log');
autoUpdater.logger.transports.file.level = 'info';

// Handle creating/removing shortcuts on Windows when installing/uninstalling
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Keep a global reference of the window object to prevent it being garbage collected
let mainWindow;

// Auto-update events
autoUpdater.on('checking-for-update', () => {
  sendStatusToWindow('Checking for update...');
});

autoUpdater.on('update-available', (info) => {
  sendStatusToWindow('Update available.', 'info');
  // Automatically download the update
  sendStatusToWindow('Downloading update...', 'info');
});

autoUpdater.on('update-not-available', (info) => {
  sendStatusToWindow('Update not available.', 'info');
});

autoUpdater.on('error', (err) => {
  sendStatusToWindow(`Error in auto-updater: ${err.toString()}`, 'error');
});

autoUpdater.on('download-progress', (progressObj) => {
  let logMessage = `Download speed: ${progressObj.bytesPerSecond} - Downloaded ${progressObj.percent}% (${progressObj.transferred} / ${progressObj.total})`;
  sendStatusToWindow(logMessage, 'info');
});

autoUpdater.on('update-downloaded', (info) => {
  sendStatusToWindow('Update downloaded. It will be installed on restart.', 'success');
  // Ask user if they want to restart the app now
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Ready',
    message: 'A new version has been downloaded. Restart the application to apply the updates.',
    buttons: ['Restart Now', 'Later']
  }).then((returnValue) => {
    if (returnValue.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});

// Send auto-updater status to renderer
function sendStatusToWindow(text, type = 'info') {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('update-status', text, type);
    // Also send as a notification
    notifyUser(text, type);
  }
}

const createWindow = () => {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../../assets/icon.png'),
  });

  // In production, load the bundled app
  // In development, load from the local server
  if (app.isPackaged) {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  } else {
    mainWindow.loadURL('http://localhost:3000');
    // Open the DevTools in development mode
    mainWindow.webContents.openDevTools();
  }
};

// Create window when Electron has finished initialization
app.whenReady().then(() => {
  createWindow();

  // Initialize the scheduler
  initializeScheduler(mainWindow);

  app.on('activate', () => {
    // On macOS re-create a window when dock icon is clicked and no other windows open
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
  
  // Check for updates after app is ready
  if (app.isPackaged) {
    // Wait a bit to let the app fully initialize
    setTimeout(() => {
      autoUpdater.checkForUpdatesAndNotify();
    }, 3000);
    
    // Set up auto-update interval
    const settings = store.get('settings', {});
    const checkInterval = settings.updateCheckInterval || 60; // minutes
    
    // Check for updates at regular intervals
    setInterval(() => {
      autoUpdater.checkForUpdatesAndNotify();
    }, checkInterval * 60 * 1000);
  }

  // Listen for the scheduler monitor start event
  ipcMain.on('scheduler-monitor-start', async (event, monitor) => {
    try {
      // Start monitoring the username
      await startScheduledMonitoring(monitor.username, monitor.autoClaim, monitor.strategy, monitor.monitorId);
    } catch (error) {
      console.error('Failed to start scheduled monitoring:', error);
      
      // Handle the error
      handleMonitoringResult(monitor.monitorId, {
        success: false,
        error: error.message || 'Unknown error'
      }, mainWindow);
    }
  });
});

// Listen for theme change events
ipcMain.on('themeChanged', (event, theme) => {
  // Forward theme change to all renderer processes
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('themeChanged', theme);
  }
});

// Add IPC handler for manual update check
ipcMain.handle('check-for-updates', async () => {
  if (!app.isPackaged) {
    return { success: false, message: 'Updates are only available in the packaged app' };
  }
  
  try {
    await autoUpdater.checkForUpdatesAndNotify();
    return { success: true, message: 'Checking for updates...' };
  } catch (error) {
    console.error('Failed to check for updates:', error);
    return { success: false, message: error.message || 'Failed to check for updates' };
  }
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Clean up processes on app exit
app.on('before-quit', () => {
  stopMonitoring();
  stopClaiming();
  stopAuthentication();
  cancelAllScheduledMonitors();
});

// Stop any active monitoring process
function stopMonitoring() {
  if (monitoringProcess) {
    try {
      monitoringProcess.kill();
      monitoringProcess = null;
      
      // If this was a scheduled monitor, handle the result
      if (activeScheduledMonitorId) {
        handleMonitoringResult(activeScheduledMonitorId, {
          success: false,
          error: 'Monitoring stopped by user'
        }, mainWindow);
        activeScheduledMonitorId = null;
      }
    } catch (error) {
      console.error('Error stopping monitoring process:', error);
    }
  }
}

// Stop any active claiming process
function stopClaiming() {
  if (claimingProcess) {
    try {
      claimingProcess.kill();
      claimingProcess = null;
    } catch (error) {
      console.error('Error stopping claiming process:', error);
    }
  }
}

// Stop any active authentication process
function stopAuthentication() {
  if (authProcess) {
    try {
      authProcess.kill();
      authProcess = null;
    } catch (error) {
      console.error('Error stopping authentication process:', error);
    }
  }
}

// IPC handlers for Python interaction
ipcMain.handle('check-username', async (event, username) => {
  return new Promise((resolve, reject) => {
    let options = {
      mode: 'text',
      pythonPath: 'python', // Adjust if using specific Python path
      pythonOptions: ['-u'], // unbuffered
      scriptPath: path.join(__dirname, '../../src/python'),
      args: [username]
    };

    PythonShell.run('check_username.py', options)
      .then(results => {
        if (results && results.length > 0) {
          try {
            const result = JSON.parse(results[0]);
            resolve(result);
          } catch (error) {
            reject(new Error('Failed to parse Python script output'));
          }
        } else {
          reject(new Error('No result from Python script'));
        }
      })
      .catch(err => {
        reject(err);
      });
  });
});

// Create a helper function to send notifications to all channels
async function notifyUser(message, severity = 'info') {
  // Map severity to notification type
  const typeMap = {
    'info': 'info',
    'success': 'success',
    'warning': 'warning',
    'error': 'error'
  };
  const type = typeMap[severity] || 'info';
  
  // Get settings
  const settings = store.get('settings', {});
  
  // Send to the renderer process first
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('notification', message, severity);
  }
  
  // Send to Discord and/or email if enabled
  if ((settings.discordEnabled && settings.discordWebhook) || 
      (settings.emailEnabled && settings.emailAddress)) {
    await sendNotification(message, 'OpenMC Username Sniper', type);
  }
}

// Add scheduling IPC handlers
ipcMain.handle('get-scheduled-monitors', async () => {
  return getScheduledMonitors();
});

ipcMain.handle('schedule-monitor', async (event, monitor) => {
  try {
    const savedMonitor = saveScheduledMonitor(monitor);
    scheduleMonitor(savedMonitor, mainWindow);
    return { success: true, monitor: savedMonitor };
  } catch (error) {
    console.error('Failed to schedule monitor:', error);
    return { success: false, error: error.message || 'Unknown error scheduling monitor' };
  }
});

ipcMain.handle('delete-scheduled-monitor', async (event, id) => {
  try {
    const deleted = deleteScheduledMonitor(id);
    return { success: deleted };
  } catch (error) {
    console.error('Failed to delete scheduled monitor:', error);
    return { success: false, error: error.message || 'Unknown error deleting scheduled monitor' };
  }
});

// Helper function to start monitoring from a scheduled monitor
async function startScheduledMonitoring(username, autoClaim, strategy, monitorId) {
  // Store the active scheduled monitor ID
  activeScheduledMonitorId = monitorId;
  
  // Start monitoring
  await monitorUsername(username, 1, autoClaim, strategy);
}

ipcMain.handle('monitor-username', async (event, username, interval, autoClaim = false, strategy = 'timing') => {
  // Call the helper function
  return await monitorUsername(username, interval, autoClaim, strategy);
});

// Helper function to monitor a username
async function monitorUsername(username, interval, autoClaim = false, strategy = 'timing') {
  // Stop any existing monitoring
  stopMonitoring();
  
  // Start new monitoring process
  return new Promise((resolve, reject) => {
    try {
      const options = {
        mode: 'text',
        pythonPath: 'python', // Adjust if using specific Python path
        pythonOptions: ['-u'], // unbuffered
        scriptPath: path.join(__dirname, '../../src/python'),
        args: [username, interval.toString()]
      };
      
      monitoringProcess = new PythonShell('monitor_username.py', options);
      
      // Initial response
      resolve({ success: true, message: 'Monitoring started' });
      
      // Handle data from the Python script
      monitoringProcess.on('message', async (message) => {
        try {
          const data = JSON.parse(message);
          
          // Forward different message types to the renderer
          switch (data.type) {
            case 'status':
              mainWindow.webContents.send('monitoring-update', { 
                status: data.status,
                details: data
              });
              break;
              
            case 'check':
              mainWindow.webContents.send('monitoring-update', { 
                status: 'checking',
                details: data
              });
              break;
              
            case 'available':
              mainWindow.webContents.send('monitoring-update', { 
                status: 'available',
                details: data
              });
              
              // Send notification to all channels
              notifyUser(`Username ${data.username} is now available!`, 'success');
              
              // Auto-claim if enabled
              if (autoClaim) {
                mainWindow.webContents.send('monitoring-update', { 
                  status: 'auto-claiming',
                  details: {
                    username: data.username,
                    strategy: strategy
                  }
                });
                
                try {
                  // Get authentication token if available
                  const authToken = store.get('authToken', null);
                  
                  // Call claim username
                  const claimResult = await claimUsername(data.username, strategy, authToken);
                  
                  mainWindow.webContents.send('monitoring-update', {
                    status: claimResult.success ? 'claim-success' : 'claim-failure',
                    details: claimResult
                  });
                  
                  mainWindow.webContents.send('claim-status', claimResult);
                  
                  // Send notification about claim result
                  if (claimResult.success) {
                    notifyUser(`Successfully claimed username ${data.username}!`, 'success');
                  } else {
                    notifyUser(`Failed to claim username ${data.username}: ${claimResult.error || 'Unknown error'}`, 'error');
                  }
                  
                  // If this was a scheduled monitor, handle the result
                  if (activeScheduledMonitorId) {
                    handleMonitoringResult(activeScheduledMonitorId, claimResult, mainWindow);
                    activeScheduledMonitorId = null;
                  }
                  
                } catch (claimError) {
                  mainWindow.webContents.send('monitoring-update', {
                    status: 'claim-failure',
                    error: claimError.message || 'Failed to auto-claim username'
                  });
                  
                  mainWindow.webContents.send('claim-status', {
                    success: false,
                    error: claimError.message || 'Failed to auto-claim username'
                  });
                  
                  // Send notification about claim failure
                  notifyUser(`Error while claiming ${data.username}: ${claimError.message || 'Unknown error'}`, 'error');
                  
                  // If this was a scheduled monitor, handle the result
                  if (activeScheduledMonitorId) {
                    handleMonitoringResult(activeScheduledMonitorId, {
                      success: false,
                      error: claimError.message || 'Failed to auto-claim username'
                    }, mainWindow);
                    activeScheduledMonitorId = null;
                  }
                }
              }
              break;
              
            case 'drop_time':
              mainWindow.webContents.send('monitoring-update', { 
                status: 'drop_time',
                details: data
              });
              
              // Send notification about upcoming drop
              if (data.drop_time) {
                const dropDate = new Date(data.drop_time);
                const timeUntilDrop = Math.max(0, Math.floor((dropDate - new Date()) / 1000 / 60)); // in minutes
                
                if (timeUntilDrop <= 60) { // If less than an hour until drop
                  notifyUser(`Username ${data.username} will be available in approximately ${timeUntilDrop} minutes!`, 'info');
                }
              }
              break;
              
            case 'error':
              mainWindow.webContents.send('monitoring-update', { 
                status: 'error',
                error: data.error,
                details: data
              });
              
              // Send notification about error
              notifyUser(`Error monitoring ${data.username || 'username'}: ${data.error || 'Unknown error'}`, 'error');
              
              // If this was a scheduled monitor, handle the result
              if (activeScheduledMonitorId) {
                handleMonitoringResult(activeScheduledMonitorId, {
                  success: false,
                  error: data.error || 'Unknown error'
                }, mainWindow);
                activeScheduledMonitorId = null;
              }
              break;
              
            case 'warning':
              mainWindow.webContents.send('monitoring-update', { 
                status: 'warning',
                warning: data.warning,
                details: data
              });
              
              // Send notification about warning
              notifyUser(`Warning while monitoring ${data.username || 'username'}: ${data.warning || 'Unknown warning'}`, 'warning');
              break;
          }
        } catch (error) {
          console.error('Error parsing Python output:', error);
          mainWindow.webContents.send('monitoring-update', { 
            status: 'error',
            error: 'Failed to parse output from monitoring script',
            raw: message
          });
          
          // If this was a scheduled monitor, handle the result
          if (activeScheduledMonitorId) {
            handleMonitoringResult(activeScheduledMonitorId, {
              success: false,
              error: 'Failed to parse output from monitoring script'
            }, mainWindow);
            activeScheduledMonitorId = null;
          }
        }
      });
      
      // Handle errors
      monitoringProcess.on('error', (err) => {
        console.error('Monitoring process error:', err);
        
        // Send error to renderer
        mainWindow.webContents.send('monitoring-update', { 
          status: 'error',
          error: err.message
        });
        
        // If this was a scheduled monitor, handle the result
        if (activeScheduledMonitorId) {
          handleMonitoringResult(activeScheduledMonitorId, {
            success: false,
            error: err.message
          }, mainWindow);
          activeScheduledMonitorId = null;
        }
      });
      
      // Handle process exit
      monitoringProcess.on('close', (code) => {
        console.log(`Monitoring process exited with code ${code}`);
        
        // If code is not 0, there was an error
        if (code !== 0) {
          mainWindow.webContents.send('monitoring-update', { 
            status: 'error',
            error: `Monitoring process exited with code ${code}`
          });
          
          // If this was a scheduled monitor, handle the result
          if (activeScheduledMonitorId) {
            handleMonitoringResult(activeScheduledMonitorId, {
              success: false,
              error: `Monitoring process exited with code ${code}`
            }, mainWindow);
            activeScheduledMonitorId = null;
          }
        }
        
        monitoringProcess = null;
      });
      
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      reject(error);
    }
  });
}

// Add back the stop-monitoring handler
ipcMain.handle('stop-monitoring', async () => {
  stopMonitoring();
  mainWindow.webContents.send('monitoring-update', { 
    status: 'stopped',
    message: 'Monitoring stopped by user'
  });
  return { success: true, message: 'Monitoring stopped' };
});

// We need to implement getDropTime for checking when a username will be available
ipcMain.handle('get-drop-time', async (event, username) => {
  return new Promise((resolve, reject) => {
    let options = {
      mode: 'text',
      pythonPath: 'python',
      pythonOptions: ['-u'],
      scriptPath: path.join(__dirname, '../../src/python'),
      args: [username]
    };

    PythonShell.run('get_drop_time.py', options)
      .then(results => {
        if (results && results.length > 0) {
          try {
            const result = JSON.parse(results[0]);
            resolve(result);
          } catch (error) {
            reject(new Error('Failed to parse Python script output'));
          }
        } else {
          reject(new Error('No result from Python script'));
        }
      })
      .catch(err => {
        reject(err);
      });
  });
});

// Helper function to claim a username
async function claimUsername(username, strategy, authToken = null) {
  return new Promise((resolve, reject) => {
    // Stop any existing claiming process
    stopClaiming();
    
    const options = {
      mode: 'text',
      pythonPath: 'python',
      pythonOptions: ['-u'],
      scriptPath: path.join(__dirname, '../../src/python'),
      args: [username, strategy]
    };
    
    // Add auth token if available
    if (authToken) {
      options.args.push(authToken);
    }
    
    claimingProcess = new PythonShell('claim_username.py', options);
    
    let statusMessages = [];
    
    // Handle output from the claiming script
    claimingProcess.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        
        // If it's a status update, collect it
        if (data.status) {
          statusMessages.push(data);
          
          // Forward status updates to the renderer
          mainWindow.webContents.send('claim-status-update', data);
        } else {
          // Final result
          data.statusMessages = statusMessages;
          resolve(data);
        }
      } catch (error) {
        console.error('Error parsing claim output:', error, message);
      }
    });
    
    // Handle errors
    claimingProcess.on('error', (err) => {
      console.error('Claiming process error:', err);
      reject(err);
    });
    
    // Handle process exit
    claimingProcess.on('close', (code) => {
      console.log(`Claiming process exited with code ${code}`);
      claimingProcess = null;
      
      // If we haven't resolved yet, do it now with an error
      if (code !== 0) {
        reject(new Error(`Claiming process exited with code ${code}`));
      }
    });
  });
}

ipcMain.handle('claim-username', async (event, username, strategy, credentials) => {
  try {
    // Store auth token if provided
    if (credentials && credentials.authToken) {
      store.set('authToken', credentials.authToken);
    }
    
    // Call the claim function
    return await claimUsername(username, strategy, credentials ? credentials.authToken : null);
  } catch (error) {
    console.error('Failed to claim username:', error);
    return {
      success: false,
      error: error.message || 'Unknown error during claiming process'
    };
  }
});

// Helper function to authenticate with Microsoft
async function authenticateWithMicrosoft(useStoredToken = false, email = null, password = null) {
  return new Promise((resolve, reject) => {
    // Stop any existing authentication process
    stopAuthentication();
    
    const options = {
      mode: 'text',
      pythonPath: 'python',
      pythonOptions: ['-u'],
      scriptPath: path.join(__dirname, '../../src/python'),
      args: [useStoredToken.toString()]
    };
    
    // Add email and password if provided
    if (email && password) {
      options.args.push(email, password);
    }
    
    authProcess = new PythonShell('authenticate.py', options);
    
    let statusMessages = [];
    
    // Handle output from the authentication script
    authProcess.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        
        // If it's a status update, collect it
        if (data.status) {
          statusMessages.push(data);
          
          // Forward status updates to the renderer
          mainWindow.webContents.send('auth-status-update', data);
        } else {
          // Final result
          data.statusMessages = statusMessages;
          
          // Store auth token if authentication was successful
          if (data.success && data.profile && data.profile.token) {
            store.set('authToken', data.profile.token);
            store.set('authProfile', {
              username: data.profile.username,
              uuid: data.profile.uuid,
              authenticated_at: data.profile.authenticated_at,
              name_change_eligible: data.profile.name_change_eligible
            });
          }
          
          resolve(data);
        }
      } catch (error) {
        console.error('Error parsing authentication output:', error, message);
      }
    });
    
    // Handle errors
    authProcess.on('error', (err) => {
      console.error('Authentication process error:', err);
      reject(err);
    });
    
    // Handle process exit
    authProcess.on('close', (code) => {
      console.log(`Authentication process exited with code ${code}`);
      authProcess = null;
      
      // If we haven't resolved yet, do it now with an error
      if (code !== 0) {
        reject(new Error(`Authentication process exited with code ${code}`));
      }
    });
  });
}

ipcMain.handle('authenticate', async (event, useStoredToken = false, credentials = null) => {
  try {
    // Call the authenticate function
    return await authenticateWithMicrosoft(
      useStoredToken, 
      credentials ? credentials.email : null, 
      credentials ? credentials.password : null
    );
  } catch (error) {
    console.error('Failed to authenticate:', error);
    return {
      success: false,
      error: error.message || 'Unknown error during authentication process'
    };
  }
});

ipcMain.handle('check-account', async () => {
  // Return stored profile if available
  const profile = store.get('authProfile', null);
  const token = store.get('authToken', null);
  
  if (profile && token) {
    return {
      success: true,
      profile,
      isAuthenticated: true
    };
  }
  
  return {
    success: false,
    isAuthenticated: false,
    message: 'Not authenticated'
  };
});

ipcMain.handle('logout', async () => {
  // Clear stored tokens and profile
  store.delete('authToken');
  store.delete('authProfile');
  
  return {
    success: true,
    message: 'Logged out successfully'
  };
});

// Store and retrieve user settings
ipcMain.handle('save-settings', async (event, settings) => {
  Object.keys(settings).forEach(key => {
    store.set(key, settings[key]);
  });
  return { success: true };
});

ipcMain.handle('get-settings', async () => {
  return {
    checkInterval: store.get('checkInterval', 3),
    defaultStrategy: store.get('defaultStrategy', 'timing'),
    notifications: store.get('notifications', true),
    theme: store.get('theme', 'dark')
  };
}); 