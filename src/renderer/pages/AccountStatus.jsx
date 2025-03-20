import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Card, 
  CardContent, 
  CircularProgress,
  Divider,
  Grid,
  Alert,
  Stack,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TextField,
  Stepper,
  Step,
  StepLabel,
  Chip
} from '@mui/material';
import { 
  Person as PersonIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  CheckCircleOutline as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  AccountCircle as AccountIcon,
  HowToReg as RegisterIcon
} from '@mui/icons-material';

function AccountStatus({ setNotification }) {
  const [profile, setProfile] = useState(null);
  const [authenticating, setAuthenticating] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState('');
  const [logMessages, setLogMessages] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const logEndRef = useRef(null);

  const steps = ['Start Authentication', 'Browser Login', 'Minecraft Authentication'];

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

  // Check if user is already authenticated on component mount
  useEffect(() => {
    checkAccountStatus();
    
    // Set up event listeners
    window.api.on('auth-status-update', handleAuthStatusUpdate);
    
    return () => {
      window.api.removeAllListeners('auth-status-update');
    };
  }, []);

  const checkAccountStatus = async () => {
    try {
      const result = await window.api.checkAccount();
      
      if (result.success && result.isAuthenticated) {
        setProfile(result.profile);
        setAuthenticated(true);
        addLogMessage(`You are logged in as ${result.profile.username}`, 'success');
      } else {
        setProfile(null);
        setAuthenticated(false);
        addLogMessage('You are not currently logged in', 'info');
      }
    } catch (err) {
      console.error('Failed to check account status:', err);
      setError('Failed to check account status: ' + (err.message || 'Unknown error'));
      addLogMessage(`Error checking account status: ${err.message || 'Unknown error'}`, 'error');
    }
  };

  const handleAuthStatusUpdate = (data) => {
    if (data.status && data.message) {
      addLogMessage(data.message, data.status === 'error' ? 'error' : 'info');
      
      // Update stepper based on status
      if (data.status === 'starting') {
        setActiveStep(0);
      } else if (data.status === 'authenticating') {
        setActiveStep(1);
      } else if (data.status === 'authenticated' || data.status === 'fetching_details') {
        setActiveStep(2);
      }
    }
  };

  const handleAuthenticate = async () => {
    setAuthenticating(true);
    setError('');
    addLogMessage('Starting authentication process', 'info');
    
    try {
      const result = await window.api.authenticate();
      
      if (result.success) {
        setProfile(result.profile);
        setAuthenticated(true);
        addLogMessage(`Successfully authenticated as ${result.profile.username}`, 'success');
        setNotification({
          open: true,
          message: `Successfully authenticated as ${result.profile.username}`,
          severity: 'success'
        });
      } else {
        setError(result.error || 'Authentication failed');
        addLogMessage(`Authentication failed: ${result.error || 'Unknown error'}`, 'error');
        setNotification({
          open: true,
          message: `Authentication failed: ${result.error || 'Unknown error'}`,
          severity: 'error'
        });
      }
    } catch (err) {
      console.error('Authentication error:', err);
      setError('Authentication error: ' + (err.message || 'Unknown error'));
      addLogMessage(`Authentication error: ${err.message || 'Unknown error'}`, 'error');
      setNotification({
        open: true,
        message: 'Authentication error: ' + (err.message || 'Unknown error'),
        severity: 'error'
      });
    } finally {
      setAuthenticating(false);
    }
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    
    try {
      const result = await window.api.logout();
      
      if (result.success) {
        setProfile(null);
        setAuthenticated(false);
        addLogMessage('Successfully logged out', 'success');
        setNotification({
          open: true,
          message: 'Successfully logged out',
          severity: 'success'
        });
      } else {
        setError(result.error || 'Logout failed');
        addLogMessage(`Logout failed: ${result.error || 'Unknown error'}`, 'error');
      }
    } catch (err) {
      console.error('Logout error:', err);
      setError('Logout error: ' + (err.message || 'Unknown error'));
      addLogMessage(`Logout error: ${err.message || 'Unknown error'}`, 'error');
    } finally {
      setLoggingOut(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (err) {
      return dateString;
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
          background: authenticated
            ? 'linear-gradient(to right, #1b5e20, #2e7d32)'
            : 'linear-gradient(to right, #1a237e, #01579b)'
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom sx={{ color: 'white' }}>
          {authenticated ? 'Account Status' : 'Microsoft Authentication'}
        </Typography>
        <Typography variant="body1" paragraph sx={{ color: 'white' }}>
          {authenticated 
            ? `You are currently logged in as ${profile?.username}`
            : 'Authenticate with your Microsoft account to claim Minecraft usernames'
          }
        </Typography>
        
        {authenticated ? (
          <Button
            variant="contained"
            color="error"
            onClick={handleLogout}
            disabled={loggingOut}
            startIcon={loggingOut ? <CircularProgress size={20} color="inherit" /> : <LogoutIcon />}
            sx={{ mt: 2 }}
          >
            {loggingOut ? 'Logging Out...' : 'Log Out'}
          </Button>
        ) : (
          <Button
            variant="contained"
            color="secondary"
            onClick={handleAuthenticate}
            disabled={authenticating}
            startIcon={authenticating ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
            sx={{ mt: 2 }}
          >
            {authenticating ? 'Authenticating...' : 'Authenticate with Microsoft'}
          </Button>
        )}
      </Paper>

      {/* Authentication Process Card */}
      {authenticating && (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Authentication Process
            </Typography>
            
            <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              {activeStep === 0 ? (
                'Starting authentication process...'
              ) : activeStep === 1 ? (
                'A browser window will open for you to sign in with Microsoft. Please complete the login in your browser.'
              ) : (
                'Authenticating with Minecraft services...'
              )}
            </Alert>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
              <CircularProgress />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Account Info Card */}
      {authenticated && profile && (
        <Card sx={{ maxWidth: 800, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <AccountIcon fontSize="large" color="primary" />
              <Typography variant="h6">
                {profile.username}
              </Typography>
              <Chip 
                label={profile.name_change_eligible ? 'Can Change Name' : 'Name Change Locked'}
                color={profile.name_change_eligible ? 'success' : 'warning'}
                size="small"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Username
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {profile.username}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  UUID
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {profile.uuid}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Authentication Date
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {formatDate(profile.authenticated_at)}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Name Change Status
                </Typography>
                <Typography variant="body1" gutterBottom>
                  {profile.name_change_eligible 
                    ? 'Eligible to change name' 
                    : 'Not eligible to change name (30 day cooldown)'
                  }
                </Typography>
              </Grid>
            </Grid>

            {!profile.name_change_eligible && (
              <Alert severity="warning" sx={{ mt: 3 }}>
                Your account is not currently eligible for a name change. 
                There is a 30-day cooldown period between name changes.
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Log Display */}
      <Card sx={{ maxWidth: 800, mx: 'auto', maxHeight: 300, overflow: 'auto' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Authentication Log
          </Typography>
          
          {logMessages.length === 0 ? (
            <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic' }}>
              Authentication events will appear here...
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
                      <CheckCircleIcon fontSize="small" color="success" />
                    ) : (
                      <InfoIcon fontSize="small" color="primary" />
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

export default AccountStatus; 