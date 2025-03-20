import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Card, 
  CardContent, 
  CircularProgress,
  Divider,
  Grid,
  Alert,
  Stack,
  Chip,
  Slider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  FormControlLabel,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  CheckCircleOutline as AvailableIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  AccessTime as TimeIcon,
  Sync as SyncIcon,
  Schedule as ScheduleIcon,
  Bolt as ClaimIcon
} from '@mui/icons-material';

function MonitorUsername({ settings, setNotification }) {
  const [username, setUsername] = useState('');
  const [interval, setInterval] = useState(settings.checkInterval);
  const [monitoring, setMonitoring] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [dropTime, setDropTime] = useState(null);
  const [logMessages, setLogMessages] = useState([]);
  const [checkCount, setCheckCount] = useState(0);
  const [autoClaim, setAutoClaim] = useState(false);
  const [strategy, setStrategy] = useState(settings.defaultStrategy);
  const [claimResult, setClaimResult] = useState(null);
  const logEndRef = useRef(null);

  // Add a log message with timestamp
  const addLogMessage = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogMessages(prev => [...prev, { message, timestamp, type }]);
  };

  // Scroll to bottom of log when new messages are added
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logMessages]);

  // Set up event listeners when component mounts
  useEffect(() => {
    // Listen for status updates
    window.api.on('claim-status-update', handleClaimStatusUpdate);
    window.api.on('claim-status', handleClaimStatus);
    
    return () => {
      window.api.removeAllListeners('monitoring-update');
      window.api.removeAllListeners('claim-status-update');
      window.api.removeAllListeners('claim-status');
      if (monitoring) {
        handleStopMonitoring();
      }
    };
  }, [monitoring]);

  const handleClaimStatusUpdate = (data) => {
    if (data.status && data.message) {
      addLogMessage(`Claim status: ${data.message}`, data.status === 'error' ? 'error' : 'info');
    }
  };
  
  const handleClaimStatus = (result) => {
    setClaimResult(result);
    if (result.success) {
      addLogMessage(`✅ Successfully claimed username: ${result.username}!`, 'success');
      setStatus('claimed');
      setNotification({
        open: true,
        message: `Successfully claimed username: ${result.username}!`,
        severity: 'success'
      });
    } else {
      addLogMessage(`❌ Failed to claim username: ${result.error || 'Unknown error'}`, 'error');
      setStatus('claim-failed');
      setNotification({
        open: true,
        message: `Failed to claim username: ${result.error || 'Unknown error'}`,
        severity: 'error'
      });
    }
  };

  const handleMonitoringUpdate = (data) => {
    console.log('Monitoring update:', data);
    
    if (data.status === 'error') {
      setError(data.error || 'Unknown error during monitoring');
      addLogMessage(`Error: ${data.error || 'Unknown error'}`, 'error');
      setMonitoring(false);
      setStatus('error');
      setNotification({
        open: true,
        message: data.error || 'Unknown error during monitoring',
        severity: 'error'
      });
      return;
    }
    
    if (data.status === 'warning') {
      addLogMessage(`Warning: ${data.warning || 'Unknown warning'}`, 'warning');
      return;
    }
    
    if (data.status === 'starting') {
      setStatus('starting');
      addLogMessage(`Monitoring started for username: ${username}`);
      return;
    }
    
    if (data.status === 'stopped' || data.status === 'stopping') {
      setStatus('stopped');
      setMonitoring(false);
      addLogMessage('Monitoring stopped');
      return;
    }
    
    if (data.status === 'checking') {
      setStatus('monitoring');
      setCheckCount(data.details.check_count);
      if (data.details.check_count % 10 === 0) { // Log every 10 checks to avoid spamming
        addLogMessage(`Check #${data.details.check_count}: Username still unavailable`);
      }
      return;
    }
    
    if (data.status === 'available') {
      setStatus('available');
      setMonitoring(false);
      addLogMessage(`✅ Username "${data.details.username}" is now AVAILABLE!`, 'success');
      setNotification({
        open: true,
        message: `Username "${data.details.username}" is now AVAILABLE!`,
        severity: 'success'
      });
      return;
    }
    
    if (data.status === 'auto-claiming') {
      setStatus('claiming');
      addLogMessage(`🚀 Auto-claiming username "${data.details.username}" with ${data.details.strategy} strategy`, 'info');
      return;
    }
    
    if (data.status === 'claim-success') {
      // Claim result will be handled by the claim-status event
      setStatus('claimed');
      return;
    }
    
    if (data.status === 'claim-failure') {
      // Claim result will be handled by the claim-status event
      setStatus('claim-failed');
      return;
    }
    
    if (data.status === 'drop_time') {
      setDropTime(data.details);
      addLogMessage(`Drop time found: ${data.details.drop_time} UTC`);
      return;
    }
  };

  const handleStartMonitoring = async () => {
    // Validate input
    if (!username.trim()) {
      setError('Please enter a username to monitor');
      return;
    }

    setLoading(true);
    setError('');
    setLogMessages([]);
    setCheckCount(0);
    setDropTime(null);
    setClaimResult(null);

    try {
      // Set up event listener for monitoring updates
      window.api.on('monitoring-update', handleMonitoringUpdate);
      
      // Start monitoring
      const response = await window.api.monitorUsername(username.trim(), interval, autoClaim, strategy);
      
      if (response.success) {
        setMonitoring(true);
        setStatus('starting');
        addLogMessage(`Starting monitoring for username: ${username}`);
        if (autoClaim) {
          addLogMessage(`Auto-claim is enabled with ${strategy} strategy`);
        }
      } else {
        setError(response.error || 'Failed to start monitoring');
        addLogMessage(`Error: ${response.error || 'Failed to start monitoring'}`, 'error');
        setStatus('error');
      }
    } catch (err) {
      console.error('Failed to start monitoring:', err);
      setError('Failed to start monitoring: ' + (err.message || 'Unknown error'));
      addLogMessage(`Error: Failed to start monitoring: ${err.message || 'Unknown error'}`, 'error');
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const handleStopMonitoring = async () => {
    try {
      await window.api.stopMonitoring();
      setMonitoring(false);
      setStatus('stopped');
      addLogMessage('Monitoring stopped by user');
    } catch (err) {
      console.error('Failed to stop monitoring:', err);
      setNotification({
        open: true,
        message: 'Failed to stop monitoring: ' + (err.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };
  
  const handleManualClaim = async () => {
    setStatus('claiming');
    addLogMessage(`Manually claiming username "${username}" with ${strategy} strategy`, 'info');
    
    try {
      const result = await window.api.claimUsername(username, strategy);
      handleClaimStatus(result);
    } catch (err) {
      console.error('Failed to claim username:', err);
      addLogMessage(`Error: Failed to claim username: ${err.message || 'Unknown error'}`, 'error');
      setStatus('claim-failed');
    }
  };

  const formatTimeUntil = (timeUntil) => {
    if (!timeUntil) return null;
    
    const { days, hours, minutes, seconds } = timeUntil;
    
    const parts = [];
    if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
    if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
    if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
    if (seconds > 0) parts.push(`${seconds} second${seconds !== 1 ? 's' : ''}`);
    
    if (parts.length === 0) return 'less than a second';
    return parts.join(', ');
  };

  return (
    <Box>
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 3,
          maxWidth: 800,
          mx: 'auto',
          background: monitoring 
            ? 'linear-gradient(to right, #004d40, #00796b)' 
            : status === 'claiming' || status === 'claimed'
              ? 'linear-gradient(to right, #4a148c, #7b1fa2)'
              : 'linear-gradient(to right, #1a237e, #01579b)'
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom sx={{ color: 'white' }}>
          Monitor Minecraft Username Availability
        </Typography>
        <Typography variant="body1" paragraph sx={{ color: 'white' }}>
          Continuously check if a username becomes available and get notified immediately.
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mt: 2 }}>
          <TextField
            fullWidth
            label="Minecraft Username"
            variant="outlined"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter a username to monitor"
            disabled={monitoring || loading || status === 'claiming'}
            sx={{ 
              mr: 2,
              '& .MuiOutlinedInput-root': {
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'white',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
              '& .MuiInputBase-input': {
                color: 'white',
              },
            }}
            error={!!error}
            helperText={error}
          />
          
          {!monitoring && status !== 'claiming' ? (
            <Button
              variant="contained"
              color="secondary"
              onClick={handleStartMonitoring}
              disabled={loading || !username.trim()}
              sx={{ 
                height: 56,
                whiteSpace: 'nowrap',
                px: 3
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Start Monitoring'}
            </Button>
          ) : status === 'claiming' ? (
            <Button
              variant="contained"
              color="secondary"
              disabled
              sx={{ 
                height: 56,
                whiteSpace: 'nowrap',
                px: 3
              }}
            >
              <CircularProgress size={24} color="inherit" />
            </Button>
          ) : (
            <Button
              variant="contained"
              color="error"
              onClick={handleStopMonitoring}
              sx={{ 
                height: 56,
                whiteSpace: 'nowrap',
                px: 3
              }}
            >
              Stop Monitoring
            </Button>
          )}
        </Box>
        
        {!monitoring && status !== 'claiming' && (
          <>
            <Box sx={{ mt: 3 }}>
              <Typography id="check-interval-slider" gutterBottom sx={{ color: 'white' }}>
                Check Interval: {interval} seconds
              </Typography>
              <Slider
                value={interval}
                onChange={(e, newValue) => setInterval(newValue)}
                aria-labelledby="check-interval-slider"
                valueLabelDisplay="auto"
                step={0.5}
                marks
                min={0.5}
                max={10}
                disabled={monitoring || status === 'claiming'}
                sx={{
                  color: 'white',
                  '& .MuiSlider-rail': {
                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  },
                  '& .MuiSlider-track': {
                    backgroundColor: 'white',
                  },
                  '& .MuiSlider-thumb': {
                    backgroundColor: 'white',
                  },
                }}
              />
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Note: Lower values check more frequently but may trigger rate limits
              </Typography>
            </Box>
            
            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column' }}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={autoClaim}
                    onChange={(e) => setAutoClaim(e.target.checked)}
                    sx={{ 
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: 'white',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: 'rgba(255, 255, 255, 0.5)',
                      },
                    }}
                  />
                }
                label={
                  <Typography sx={{ color: 'white' }}>
                    Auto-claim when available
                  </Typography>
                }
              />
              
              {autoClaim && (
                <FormControl variant="outlined" sx={{ mt: 2 }}>
                  <InputLabel id="strategy-select-label" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Claiming Strategy
                  </InputLabel>
                  <Select
                    labelId="strategy-select-label"
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    label="Claiming Strategy"
                    sx={{ 
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                      },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'white',
                      },
                      '& .MuiSvgIcon-root': {
                        color: 'white',
                      },
                    }}
                  >
                    <MenuItem value="timing">Timing Strategy (Recommended for most cases)</MenuItem>
                    <MenuItem value="burst">Burst Strategy (Multiple rapid requests)</MenuItem>
                    <MenuItem value="distributed">Distributed Strategy (Multi-threaded)</MenuItem>
                    <MenuItem value="precision">Precision Strategy (Latency compensation)</MenuItem>
                    <MenuItem value="adaptive">Adaptive Strategy (Self-tuning)</MenuItem>
                  </Select>
                </FormControl>
              )}
            </Box>
          </>
        )}
      </Paper>

      {/* Status Card */}
      {(monitoring || ['available', 'error', 'claiming', 'claimed', 'claim-failed'].includes(status)) && (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              {status === 'available' ? (
                <AvailableIcon fontSize="large" color="success" />
              ) : status === 'error' ? (
                <ErrorIcon fontSize="large" color="error" />
              ) : status === 'claiming' ? (
                <ClaimIcon fontSize="large" color="secondary" />
              ) : status === 'claimed' ? (
                <AvailableIcon fontSize="large" color="success" />
              ) : status === 'claim-failed' ? (
                <ErrorIcon fontSize="large" color="error" />
              ) : (
                <SyncIcon fontSize="large" color="primary" />
              )}
              
              <Typography variant="h6">
                {username}
              </Typography>
              
              <Chip 
                label={
                  status === 'available' ? 'Available' : 
                  status === 'error' ? 'Error' :
                  status === 'monitoring' ? 'Monitoring' :
                  status === 'starting' ? 'Starting' :
                  status === 'stopped' ? 'Stopped' :
                  status === 'claiming' ? 'Claiming' :
                  status === 'claimed' ? 'Claimed' :
                  status === 'claim-failed' ? 'Claim Failed' :
                  'Processing'
                }
                color={
                  status === 'available' ? 'success' : 
                  status === 'error' || status === 'claim-failed' ? 'error' :
                  status === 'claiming' ? 'secondary' :
                  status === 'claimed' ? 'success' :
                  'primary'
                }
                size="small"
              />
              
              {monitoring && (
                <Chip 
                  label={`Check #${checkCount}`}
                  color="secondary"
                  size="small"
                  variant="outlined"
                />
              )}
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {status === 'available' && (
              <Alert severity="success" sx={{ mb: 2 }}>
                The username "{username}" is now available and can be claimed!
              </Alert>
            )}
            
            {status === 'error' && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error || 'An error occurred while monitoring the username.'}
              </Alert>
            )}
            
            {status === 'claiming' && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Attempting to claim username "{username}" with {strategy} strategy...
              </Alert>
            )}
            
            {status === 'claimed' && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {claimResult?.message || `Successfully claimed username "${username}"!`}
              </Alert>
            )}
            
            {status === 'claim-failed' && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {claimResult?.error || claimResult?.details || `Failed to claim username "${username}".`}
              </Alert>
            )}
            
            {monitoring && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Monitoring for username availability. This will continue running in the background.
                {autoClaim && (
                  <strong> Auto-claim is enabled with {strategy} strategy.</strong>
                )}
              </Alert>
            )}
            
            {dropTime && (
              <Box sx={{ mt: 3 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item>
                    <ScheduleIcon color="primary" fontSize="large" />
                  </Grid>
                  <Grid item xs>
                    <Typography variant="body1">
                      This username is scheduled to become available on:
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {dropTime.drop_time} UTC
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Time until available: {formatTimeUntil(dropTime.time_until)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              {status === 'available' ? (
                <>
                  <Button 
                    variant="outlined" 
                    onClick={() => {
                      setUsername('');
                      setStatus('idle');
                    }}
                  >
                    Monitor Another
                  </Button>
                  
                  <Button 
                    variant="contained" 
                    color="success"
                    onClick={handleManualClaim}
                  >
                    Claim This Username
                  </Button>
                </>
              ) : status === 'claimed' || status === 'claim-failed' ? (
                <>
                  <Button 
                    variant="outlined" 
                    onClick={() => {
                      setUsername('');
                      setStatus('idle');
                      setClaimResult(null);
                    }}
                  >
                    Start New
                  </Button>
                  
                  {status === 'claim-failed' && (
                    <Button 
                      variant="contained" 
                      color="warning"
                      onClick={handleManualClaim}
                    >
                      Try Again
                    </Button>
                  )}
                </>
              ) : (
                <>
                  {monitoring ? (
                    <Button 
                      variant="outlined" 
                      color="error"
                      onClick={handleStopMonitoring}
                    >
                      Stop Monitoring
                    </Button>
                  ) : (
                    <Button 
                      variant="outlined" 
                      onClick={() => {
                        setUsername('');
                        setStatus('idle');
                        setError('');
                      }}
                    >
                      Try Again
                    </Button>
                  )}
                </>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Log Display */}
      <Card sx={{ maxWidth: 800, mx: 'auto', maxHeight: 300, overflow: 'auto' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Monitoring Log
          </Typography>
          
          {logMessages.length === 0 ? (
            <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic' }}>
              Monitoring events will appear here...
            </Typography>
          ) : (
            <List dense>
              {logMessages.map((log, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {log.type === 'error' ? (
                      <ErrorIcon fontSize="small" color="error" />
                    ) : log.type === 'warning' ? (
                      <WarningIcon fontSize="small" color="warning" />
                    ) : log.type === 'success' ? (
                      <AvailableIcon fontSize="small" color="success" />
                    ) : (
                      <TimeIcon fontSize="small" color="primary" />
                    )}
                  </ListItemIcon>
                  <ListItemText 
                    primary={log.message}
                    secondary={log.timestamp}
                    primaryTypographyProps={{
                      variant: 'body2',
                      color: log.type === 'error' ? 'error.main' : 
                             log.type === 'warning' ? 'warning.main' : 
                             log.type === 'success' ? 'success.main' : 'inherit'
                    }}
                  />
                </ListItem>
              ))}
              <div ref={logEndRef} />
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default MonitorUsername; 