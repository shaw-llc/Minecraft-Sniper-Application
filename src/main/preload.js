const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Username operations
    checkUsername: (username) => {
      return ipcRenderer.invoke('check-username', username);
    },
    monitorUsername: (username, interval, autoClaim = false, strategy = 'timing') => {
      return ipcRenderer.invoke('monitor-username', username, interval, autoClaim, strategy);
    },
    stopMonitoring: () => {
      return ipcRenderer.invoke('stop-monitoring');
    },
    claimUsername: (username, strategy, credentials) => {
      return ipcRenderer.invoke('claim-username', username, strategy, credentials);
    },
    
    // Account operations
    checkAccount: () => {
      return ipcRenderer.invoke('check-account');
    },
    authenticate: (useStoredToken = false, credentials = null) => {
      return ipcRenderer.invoke('authenticate', useStoredToken, credentials);
    },
    logout: () => {
      return ipcRenderer.invoke('logout');
    },
    
    // Settings operations
    getSettings: () => {
      return ipcRenderer.invoke('get-settings');
    },
    saveSettings: (settings) => {
      return ipcRenderer.invoke('save-settings', settings);
    },

    // Utility operations
    getDropTime: (username) => {
      return ipcRenderer.invoke('get-drop-time', username);
    },
    
    // Scheduling operations
    getScheduledMonitors: () => {
      return ipcRenderer.invoke('get-scheduled-monitors');
    },
    scheduleMonitor: (monitor) => {
      return ipcRenderer.invoke('schedule-monitor', monitor);
    },
    deleteScheduledMonitor: (id) => {
      return ipcRenderer.invoke('delete-scheduled-monitor', id);
    },
    
    // Update operations
    checkForUpdates: () => {
      return ipcRenderer.invoke('check-for-updates');
    },
    
    // Event listeners
    on: (channel, callback) => {
      // Whitelist channels we are allowed to listen to
      const validChannels = [
        'monitoring-update', 
        'claim-status',
        'claim-status-update',
        'auth-status',
        'auth-status-update',
        'notification',
        'themeChanged',
        'update-status',
        'scheduler-update'
      ];
      if (validChannels.includes(channel)) {
        // Deliberately strip event as it includes `sender` 
        ipcRenderer.on(channel, (event, ...args) => callback(...args));
      }
    },
    
    // Remove event listeners
    removeAllListeners: (channel) => {
      const validChannels = [
        'monitoring-update', 
        'claim-status',
        'claim-status-update',
        'auth-status',
        'auth-status-update',
        'notification',
        'themeChanged',
        'update-status',
        'scheduler-update'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.removeAllListeners(channel);
      }
    },
    
    // Event emitters
    emit: (channel, ...args) => {
      const validChannels = [
        'themeChanged'
      ];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, ...args);
      }
    }
  }
); 