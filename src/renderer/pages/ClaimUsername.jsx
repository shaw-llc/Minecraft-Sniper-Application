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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import { 
  CheckCircleOutline as AvailableIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Bolt as ClaimIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Search as SearchIcon,
  Done as SuccessIcon
} from '@mui/icons-material';

function ClaimUsername({ settings, setNotification }) {
  const [username, setUsername] = useState('');
  const [strategy, setStrategy] = useState(settings.defaultStrategy);
  const [claiming, setClaiming] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [logMessages, setLogMessages] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const logEndRef = useRef(null);

  const steps = ['Check Availability', 'Authentication', 'Claim Username'];

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

  // Set up event listeners
  useEffect(() => {
    window.api.on('claim-status-update', handleClaimStatusUpdate);
    
    return () => {
      window.api.removeAllListeners('claim-status-update');
    };
  }, []);

  const handleClaimStatusUpdate = (data) => {
    if (data.status && data.message) {
      addLogMessage(data.message, data.status === 'error' ? 'error' : 'info');
      
      // Update stepper based on status
      if (data.status === 'checking') {
        setActiveStep(0);
      } else if (data.status === 'authenticating' || data.status === 'authenticated') {
        setActiveStep(1);
      } else if (data.status === 'preparing' || data.status === 'claiming') {
        setActiveStep(2);
      }
    }
  };

  const handleCheckUsername = async () => {
    // Validate input
    if (!username.trim()) {
      setError('Please enter a username to check');
      return;
    }

    setChecking(true);
    setError('');
    addLogMessage(`Checking if username "${username}" is available`);

    try {
      const response = await window.api.checkUsername(username.trim());
      
      if (response.success) {
        if (response.available) {
          addLogMessage(`✅ Username "${username}" is available and can be claimed!`, 'success');
          setStatus('available');
          setNotification({
            open: true,
            message: `Username "${username}" is available!`,
            severity: 'success'
          });
        } else {
          addLogMessage(`❌ Username "${username}" is not available.`, 'warning');
          setStatus('unavailable');
          if (response.drop_time) {
            addLogMessage(`This username may become available on: ${response.drop_time}`, 'info');
          }
        }
        setResult(response);
      } else {
        setError(response.error || 'An error occurred while checking the username');
        addLogMessage(`Error: ${response.error || 'An error occurred while checking the username'}`, 'error');
        setStatus('error');
      }
    } catch (err) {
      console.error('Failed to check username:', err);
      setError('Failed to check username: ' + (err.message || 'Unknown error'));
      addLogMessage(`Error: Failed to check username: ${err.message || 'Unknown error'}`, 'error');
      setStatus('error');
    } finally {
      setChecking(false);
    }
  };

  const handleClaimUsername = async () => {
    // Validate input
    if (!username.trim()) {
      setError('Please enter a username to claim');
      return;
    }

    setClaiming(true);
    setLoading(true);
    setError('');
    addLogMessage(`Starting claim process for username "${username}" with ${strategy} strategy`, 'info');
    setActiveStep(0);

    try {
      // First check if the username is available
      addLogMessage(`Checking if username "${username}" is available`);
      const checkResponse = await window.api.checkUsername(username.trim());
      
      if (!checkResponse.success || !checkResponse.available) {
        addLogMessage(`❌ Username "${username}" is not available for claiming.`, 'error');
        setError('Username is not available for claiming');
        setClaiming(false);
        setLoading(false);
        setStatus('unavailable');
        return;
      }
      
      setActiveStep(1);
      
      // Call the claim function
      const claimResult = await window.api.claimUsername(username, strategy);
      
      setResult(claimResult);
      
      if (claimResult.success) {
        addLogMessage(`✅ Successfully claimed username: ${claimResult.username}!`, 'success');
        setStatus('claimed');
        setNotification({
          open: true,
          message: `Successfully claimed username: ${claimResult.username}!`,
          severity: 'success'
        });
      } else {
        addLogMessage(`❌ Failed to claim username: ${claimResult.error || 'Unknown error'}`, 'error');
        setStatus('claim-failed');
        setError(claimResult.error || claimResult.details || 'Failed to claim username');
        setNotification({
          open: true,
          message: `Failed to claim username: ${claimResult.error || 'Unknown error'}`,
          severity: 'error'
        });
      }
    } catch (err) {
      console.error('Failed to claim username:', err);
      addLogMessage(`Error: Failed to claim username: ${err.message || 'Unknown error'}`, 'error');
      setStatus('claim-failed');
      setError('Failed to claim username: ' + (err.message || 'Unknown error'));
    } finally {
      setClaiming(false);
      setLoading(false);
    }
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
          background: claiming 
            ? 'linear-gradient(to right, #4a148c, #7b1fa2)'
            : status === 'claimed'
              ? 'linear-gradient(to right, #2e7d32, #388e3c)'
              : 'linear-gradient(to right, #1a237e, #01579b)'
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom sx={{ color: 'white' }}>
          Claim Minecraft Username
        </Typography>
        <Typography variant="body1" paragraph sx={{ color: 'white' }}>
          Claim an available Minecraft username with your preferred strategy.
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mt: 2 }}>
          <TextField
            fullWidth
            label="Minecraft Username"
            variant="outlined"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter a username to claim"
            disabled={claiming || loading}
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
          
          {!checking && !claiming ? (
            <Button
              variant="contained"
              color="secondary"
              onClick={handleCheckUsername}
              disabled={!username.trim()}
              sx={{ 
                height: 56,
                whiteSpace: 'nowrap',
                px: 3
              }}
            >
              Check Availability
            </Button>
          ) : (
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
          )}
        </Box>
        
        {status === 'available' && !claiming && (
          <Box sx={{ mt: 3 }}>
            <FormControl fullWidth variant="outlined">
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
                  mb: 2
                }}
              >
                <MenuItem value="timing">Timing Strategy (Recommended for most cases)</MenuItem>
                <MenuItem value="burst">Burst Strategy (Multiple rapid requests)</MenuItem>
                <MenuItem value="distributed">Distributed Strategy (Multi-threaded)</MenuItem>
                <MenuItem value="precision">Precision Strategy (Latency compensation)</MenuItem>
                <MenuItem value="adaptive">Adaptive Strategy (Self-tuning)</MenuItem>
              </Select>
            </FormControl>
            
            <Button
              variant="contained"
              color="success"
              fullWidth
              onClick={handleClaimUsername}
              disabled={claiming || loading}
              startIcon={<ClaimIcon />}
              sx={{ mt: 1 }}
            >
              Claim Username
            </Button>
          </Box>
        )}
      </Paper>

      {/* Claim Process Card */}
      {claiming && (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Claiming Process
            </Typography>
            
            <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Attempting to claim username "{username}" with {strategy} strategy...
            </Alert>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
              <CircularProgress />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Result Card */}
      {status === 'claimed' || status === 'claim-failed' || status === 'unavailable' ? (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              {status === 'claimed' ? (
                <SuccessIcon fontSize="large" color="success" />
              ) : status === 'claim-failed' ? (
                <ErrorIcon fontSize="large" color="error" />
              ) : (
                <WarningIcon fontSize="large" color="warning" />
              )}
              
              <Typography variant="h6">
                {username}
              </Typography>
              
              <Chip 
                label={
                  status === 'claimed' ? 'Claimed' : 
                  status === 'claim-failed' ? 'Claim Failed' :
                  'Unavailable'
                }
                color={
                  status === 'claimed' ? 'success' : 
                  status === 'claim-failed' ? 'error' :
                  'warning'
                }
                size="small"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {status === 'claimed' && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {result?.message || `Successfully claimed username "${username}"!`}
              </Alert>
            )}
            
            {status === 'claim-failed' && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error || `Failed to claim username "${username}".`}
              </Alert>
            )}
            
            {status === 'unavailable' && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                This username is currently not available for claiming.
                {result?.drop_time && (
                  <div>It may become available on {result.drop_time} UTC.</div>
                )}
              </Alert>
            )}

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button 
                variant="outlined" 
                onClick={() => {
                  setUsername('');
                  setStatus('idle');
                  setResult(null);
                  setError('');
                }}
              >
                Try Another
              </Button>
              
              {status === 'unavailable' && result?.drop_time && (
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => {
                    // Navigate to monitor page with this username
                    setNotification({
                      open: true,
                      message: 'Navigate to monitor page (feature coming soon)',
                      severity: 'info'
                    });
                  }}
                >
                  Monitor This Username
                </Button>
              )}
              
              {status === 'claim-failed' && (
                <Button 
                  variant="contained" 
                  color="warning"
                  onClick={handleClaimUsername}
                >
                  Try Again
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      ) : status === 'available' && (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <AvailableIcon fontSize="large" color="success" />
              <Typography variant="h6">
                {username}
              </Typography>
              <Chip 
                label="Available"
                color="success"
                size="small"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            <Alert severity="success" sx={{ mb: 2 }}>
              Good news! This username is currently available and can be claimed.
            </Alert>
            
            <Typography variant="body2" paragraph>
              Click "Claim Username" above to attempt claiming this username. 
              The claim will be processed using your selected strategy.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Log Display */}
      <Card sx={{ maxWidth: 800, mx: 'auto', maxHeight: 300, overflow: 'auto' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Claim Process Log
          </Typography>
          
          {logMessages.length === 0 ? (
            <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic' }}>
              Check or claim a username to see the process log...
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
                      <SearchIcon fontSize="small" color="primary" />
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

export default ClaimUsername; 