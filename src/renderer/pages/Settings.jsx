import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Switch, 
  FormControlLabel, 
  TextField, 
  Button, 
  Divider, 
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Slider,
  Stack,
  Collapse,
  CircularProgress
} from '@mui/material';
import { Update as UpdateIcon } from '@mui/icons-material';

function Settings({ settings, setSettings, setNotification }) {
  const [localSettings, setLocalSettings] = useState({
    ...settings,
    discordWebhook: settings.discordWebhook || '',
    discordEnabled: settings.discordEnabled || false,
    emailAddress: settings.emailAddress || '',
    emailEnabled: settings.emailEnabled || false,
    autoUpdates: settings.autoUpdates !== false, // Default to true if not set
    updateCheckInterval: settings.updateCheckInterval || 60 // Default to 60 minutes
  });
  const [saving, setSaving] = useState(false);
  const [checkingForUpdates, setCheckingForUpdates] = useState(false);
  const [updateStatus, setUpdateStatus] = useState('');

  const handleChange = (field, value) => {
    setLocalSettings({
      ...localSettings,
      [field]: value
    });
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await window.api.saveSettings(localSettings);
      setSettings(localSettings);
      setNotification({
        open: true,
        message: 'Settings saved successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      setNotification({
        open: true,
        message: 'Failed to save settings: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const checkForUpdates = async () => {
    setCheckingForUpdates(true);
    setUpdateStatus('Checking for updates...');
    
    try {
      const result = await window.api.checkForUpdates();
      
      if (result.success) {
        setUpdateStatus(result.message);
      } else {
        setUpdateStatus(`Error: ${result.message}`);
        setNotification({
          open: true,
          message: `Failed to check for updates: ${result.message}`,
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Failed to check for updates:', error);
      setUpdateStatus(`Error: ${error.message || 'Unknown error'}`);
      setNotification({
        open: true,
        message: `Failed to check for updates: ${error.message || 'Unknown error'}`,
        severity: 'error'
      });
    } finally {
      setTimeout(() => {
        setCheckingForUpdates(false);
      }, 1000);
    }
  };

  // Listen for update status events
  useEffect(() => {
    const handleUpdateStatus = (message, type) => {
      setUpdateStatus(message);
      
      // Also show as notification
      setNotification({
        open: true,
        message,
        severity: type
      });
    };
    
    window.api.on('update-status', handleUpdateStatus);
    
    return () => {
      window.api.removeAllListeners('update-status');
    };
  }, [setNotification]);

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Application Settings
        </Typography>
        <Typography variant="body1" paragraph>
          Configure your preferences for the Minecraft Username Sniper.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="default-strategy-label">Default Sniping Strategy</InputLabel>
              <Select
                labelId="default-strategy-label"
                value={localSettings.defaultStrategy}
                label="Default Sniping Strategy"
                onChange={(e) => handleChange('defaultStrategy', e.target.value)}
              >
                <MenuItem value="timing">Timing Strategy</MenuItem>
                <MenuItem value="burst">Burst Strategy</MenuItem>
                <MenuItem value="distributed">Distributed Strategy</MenuItem>
                <MenuItem value="precision">Precision Strategy</MenuItem>
                <MenuItem value="adaptive">Adaptive Strategy</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography id="check-interval-slider" gutterBottom>
              Default Check Interval (seconds)
            </Typography>
            <Slider
              value={localSettings.checkInterval}
              onChange={(e, newValue) => handleChange('checkInterval', newValue)}
              aria-labelledby="check-interval-slider"
              valueLabelDisplay="auto"
              step={0.5}
              marks
              min={1}
              max={10}
            />
            <Typography variant="caption" color="text.secondary">
              Note: Lower values check more frequently but may trigger rate limits
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Notifications
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.notifications}
                  onChange={(e) => handleChange('notifications', e.target.checked)}
                  color="primary"
                />
              }
              label="Enable desktop notifications"
            />
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.discordEnabled}
                  onChange={(e) => handleChange('discordEnabled', e.target.checked)}
                  color="primary"
                />
              }
              label="Enable Discord notifications"
            />
            <Collapse in={localSettings.discordEnabled} sx={{ mt: 1, ml: 4 }}>
              <TextField
                fullWidth
                label="Discord Webhook URL"
                value={localSettings.discordWebhook}
                onChange={(e) => handleChange('discordWebhook', e.target.value)}
                margin="normal"
                helperText="Enter your Discord webhook URL to receive notifications"
              />
            </Collapse>
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.emailEnabled}
                  onChange={(e) => handleChange('emailEnabled', e.target.checked)}
                  color="primary"
                />
              }
              label="Enable email notifications"
            />
            <Collapse in={localSettings.emailEnabled} sx={{ mt: 1, ml: 4 }}>
              <TextField
                fullWidth
                label="Email Address"
                value={localSettings.emailAddress}
                onChange={(e) => handleChange('emailAddress', e.target.value)}
                margin="normal"
                helperText="Enter your email address to receive notifications"
              />
            </Collapse>
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Updates
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.autoUpdates}
                  onChange={(e) => handleChange('autoUpdates', e.target.checked)}
                  color="primary"
                />
              }
              label="Automatically check for updates"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography id="update-interval-slider" gutterBottom>
              Update Check Interval (minutes)
            </Typography>
            <Slider
              value={localSettings.updateCheckInterval}
              onChange={(e, newValue) => handleChange('updateCheckInterval', newValue)}
              aria-labelledby="update-interval-slider"
              valueLabelDisplay="auto"
              step={10}
              marks
              min={10}
              max={240}
              disabled={!localSettings.autoUpdates}
            />
          </Grid>
          
          <Grid item xs={12} md={6} sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              variant="outlined"
              color="primary"
              startIcon={checkingForUpdates ? <CircularProgress size={20} /> : <UpdateIcon />}
              onClick={checkForUpdates}
              disabled={checkingForUpdates}
              sx={{ mr: 2 }}
            >
              Check for Updates
            </Button>
            {updateStatus && (
              <Typography variant="body2" color="text.secondary">
                {updateStatus}
              </Typography>
            )}
          </Grid>
          
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Appearance
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={localSettings.theme === 'dark'}
                  onChange={(e) => handleChange('theme', e.target.checked ? 'dark' : 'light')}
                  color="primary"
                />
              }
              label="Dark theme"
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={saveSettings}
            disabled={saving}
          >
            Save Settings
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

export default Settings;