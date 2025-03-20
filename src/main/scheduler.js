const Store = require('electron-store');
const { notifyUser } = require('./notifications');

// Initialize storage for scheduled monitors
const store = new Store();

// Keep track of active scheduler timers
const schedulerTimers = new Map();

/**
 * Initialize the scheduler service
 * @param {BrowserWindow} mainWindow - The main application window
 */
function initializeScheduler(mainWindow) {
  // Load existing scheduled monitors
  const scheduledMonitors = getScheduledMonitors();
  
  // Schedule all active monitors
  scheduledMonitors.forEach(monitor => {
    if (monitor.status === 'scheduled') {
      scheduleMonitor(monitor, mainWindow);
    }
  });
  
  // Log initialization
  console.log(`Scheduler initialized with ${scheduledMonitors.length} monitors`);
}

/**
 * Get all scheduled monitors
 * @returns {Array} - Array of scheduled monitors
 */
function getScheduledMonitors() {
  return store.get('scheduledMonitors', []);
}

/**
 * Save a scheduled monitor
 * @param {Object} monitor - The monitor to save
 * @returns {Object} - The saved monitor
 */
function saveScheduledMonitor(monitor) {
  const monitors = getScheduledMonitors();
  
  // Find if monitor already exists
  const index = monitors.findIndex(m => m.id === monitor.id);
  
  if (index >= 0) {
    // Update existing monitor
    monitors[index] = monitor;
  } else {
    // Add new monitor
    monitors.push(monitor);
  }
  
  // Save to store
  store.set('scheduledMonitors', monitors);
  
  return monitor;
}

/**
 * Delete a scheduled monitor
 * @param {string} id - The ID of the monitor to delete
 * @returns {boolean} - Whether the monitor was deleted
 */
function deleteScheduledMonitor(id) {
  const monitors = getScheduledMonitors();
  
  // Find monitor
  const index = monitors.findIndex(m => m.id === id);
  
  if (index >= 0) {
    // Cancel any active timers for this monitor
    if (schedulerTimers.has(id)) {
      clearTimeout(schedulerTimers.get(id));
      schedulerTimers.delete(id);
    }
    
    // Remove from array
    monitors.splice(index, 1);
    
    // Save to store
    store.set('scheduledMonitors', monitors);
    
    return true;
  }
  
  return false;
}

/**
 * Schedule a monitor to start at the specified time
 * @param {Object} monitor - The monitor to schedule
 * @param {BrowserWindow} mainWindow - The main application window
 * @returns {Object} - The scheduled monitor
 */
function scheduleMonitor(monitor, mainWindow) {
  // If monitor is already scheduled, cancel it first
  if (schedulerTimers.has(monitor.id)) {
    clearTimeout(schedulerTimers.get(monitor.id));
    schedulerTimers.delete(monitor.id);
  }
  
  // Calculate time until monitoring starts
  const monitorStartTime = new Date(monitor.monitorStartTime);
  const now = new Date();
  const timeUntilStart = monitorStartTime - now;
  
  // If the start time is in the past, update monitor status to missed
  if (timeUntilStart <= 0) {
    monitor.status = 'missed';
    saveScheduledMonitor(monitor);
    
    // Notify user
    notifyUser(`Scheduled monitoring for "${monitor.username}" was missed.`, 'warning');
    
    // Send update to renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('scheduler-update', monitor);
    }
    
    return monitor;
  }
  
  // Set up timer for when monitoring should start
  const timerId = setTimeout(() => {
    // Start monitoring
    startMonitoring(monitor, mainWindow);
  }, timeUntilStart);
  
  // Store timer ID for cancellation if needed
  schedulerTimers.set(monitor.id, timerId);
  
  // Send notification for long intervals
  if (timeUntilStart > 5 * 60 * 1000) { // More than 5 minutes
    const minutesUntilStart = Math.round(timeUntilStart / (60 * 1000));
    notifyUser(`Username "${monitor.username}" will be monitored in ${minutesUntilStart} minutes.`, 'info');
  }
  
  // Log scheduling
  console.log(`Monitoring for "${monitor.username}" scheduled to start at ${monitorStartTime}`);
  
  return monitor;
}

/**
 * Start monitoring for a scheduled monitor
 * @param {Object} monitor - The monitor to start
 * @param {BrowserWindow} mainWindow - The main application window
 */
async function startMonitoring(monitor, mainWindow) {
  try {
    // Update monitor status
    monitor.status = 'active';
    saveScheduledMonitor(monitor);
    
    // Send update to renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('scheduler-update', monitor);
    }
    
    // Notify user
    notifyUser(`Scheduled monitoring for "${monitor.username}" has started.`, 'info');
    
    // Request the main process to start monitoring
    const result = {
      type: 'scheduled-monitor-start',
      username: monitor.username,
      autoClaim: monitor.autoClaim,
      strategy: monitor.strategy,
      monitorId: monitor.id
    };
    
    // Send to main window as a custom event
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('scheduler-monitor-start', result);
    }
    
    // Log start
    console.log(`Monitoring for "${monitor.username}" started at ${new Date()}`);
  } catch (error) {
    console.error(`Failed to start monitoring for "${monitor.username}":`, error);
    
    // Update monitor status
    monitor.status = 'failed';
    monitor.error = error.message || 'Unknown error';
    saveScheduledMonitor(monitor);
    
    // Send update to renderer
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('scheduler-update', monitor);
    }
    
    // Notify user
    notifyUser(`Failed to start monitoring for "${monitor.username}": ${error.message || 'Unknown error'}`, 'error');
  }
}

/**
 * Handle monitoring result for a scheduled monitor
 * @param {string} monitorId - The ID of the monitor
 * @param {Object} result - The monitoring result
 * @param {BrowserWindow} mainWindow - The main application window
 */
function handleMonitoringResult(monitorId, result, mainWindow) {
  // Find the monitor
  const monitors = getScheduledMonitors();
  const monitor = monitors.find(m => m.id === monitorId);
  
  if (!monitor) {
    console.error(`Monitor with ID ${monitorId} not found`);
    return;
  }
  
  // Update monitor status based on result
  if (result.success) {
    monitor.status = 'completed';
    monitor.result = result;
  } else {
    monitor.status = 'failed';
    monitor.error = result.error || 'Unknown error';
  }
  
  // Save updated monitor
  saveScheduledMonitor(monitor);
  
  // Send update to renderer
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('scheduler-update', monitor);
  }
  
  // Notify user
  if (result.success) {
    notifyUser(`Scheduled monitoring for "${monitor.username}" completed successfully.`, 'success');
  } else {
    notifyUser(`Scheduled monitoring for "${monitor.username}" failed: ${result.error || 'Unknown error'}`, 'error');
  }
}

/**
 * Cancel all scheduled monitors
 */
function cancelAllScheduledMonitors() {
  // Clear all timers
  for (const timerId of schedulerTimers.values()) {
    clearTimeout(timerId);
  }
  
  // Clear the map
  schedulerTimers.clear();
  
  console.log('All scheduled monitors cancelled');
}

module.exports = {
  initializeScheduler,
  getScheduledMonitors,
  saveScheduledMonitor,
  deleteScheduledMonitor,
  scheduleMonitor,
  handleMonitoringResult,
  cancelAllScheduledMonitors
}; 