import React, { useState } from 'react';
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
  Chip
} from '@mui/material';
import { 
  CheckCircleOutline as AvailableIcon,
  HighlightOff as UnavailableIcon,
  Schedule as ScheduleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

function CheckUsername({ setNotification }) {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleCheckUsername = async () => {
    // Validate input
    if (!username.trim()) {
      setError('Please enter a username to check');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await window.api.checkUsername(username.trim());
      
      if (response.success) {
        setResult(response);
        if (response.available) {
          setNotification({
            open: true,
            message: `Username '${username}' is available!`,
            severity: 'success'
          });
        }
      } else {
        setError(response.error || 'An error occurred while checking the username');
        setNotification({
          open: true,
          message: response.error || 'An error occurred while checking the username',
          severity: 'error'
        });
      }
    } catch (err) {
      console.error('Failed to check username:', err);
      setError('Failed to check username: ' + (err.message || 'Unknown error'));
      setNotification({
        open: true,
        message: 'Failed to check username: ' + (err.message || 'Unknown error'),
        severity: 'error'
      });
    } finally {
      setLoading(false);
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
          background: 'linear-gradient(to right, #1a237e, #01579b)'
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom sx={{ color: 'white' }}>
          Check Minecraft Username Availability
        </Typography>
        <Typography variant="body1" paragraph sx={{ color: 'white' }}>
          Enter a Minecraft username to check if it's currently available or when it might become available.
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mt: 2 }}>
          <TextField
            fullWidth
            label="Minecraft Username"
            variant="outlined"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter a username to check"
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
            onKeyPress={(e) => e.key === 'Enter' && handleCheckUsername()}
          />
          <Button
            variant="contained"
            color="secondary"
            onClick={handleCheckUsername}
            disabled={loading}
            sx={{ 
              height: 56,
              whiteSpace: 'nowrap',
              px: 3
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Check'}
          </Button>
        </Box>
      </Paper>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {result && (
        <Card sx={{ maxWidth: 800, mx: 'auto' }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              {result.available ? (
                <AvailableIcon fontSize="large" color="success" />
              ) : (
                <UnavailableIcon fontSize="large" color="error" />
              )}
              <Typography variant="h6">
                {result.username}
              </Typography>
              <Chip 
                label={result.available ? 'Available' : 'Unavailable'} 
                color={result.available ? 'success' : 'error'}
                size="small"
              />
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {result.available ? (
              <Alert severity="success" sx={{ mb: 2 }}>
                Good news! This username is currently available and can be claimed.
              </Alert>
            ) : (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  This username is currently unavailable.
                </Alert>
                
                {result.drop_time && (
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
                          {result.drop_time} UTC
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Time until available: {formatTimeUntil(result.time_until)}
                        </Typography>
                      </Grid>
                    </Grid>

                    {result.soon_available && (
                      <Alert severity="warning" sx={{ mt: 2 }}>
                        This username should be available now or very soon! Consider using the Monitor or Claim features.
                      </Alert>
                    )}
                  </Box>
                )}
              </>
            )}

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
              <Button 
                variant="outlined" 
                onClick={() => setUsername('')}
              >
                Check Another
              </Button>
              
              {result.available && (
                <Button 
                  variant="contained" 
                  color="success"
                  onClick={() => {
                    // This would navigate to claim username page with this username
                    setNotification({
                      open: true,
                      message: 'Navigate to claim page (feature coming soon)',
                      severity: 'info'
                    });
                  }}
                >
                  Claim This Username
                </Button>
              )}
              
              {!result.available && (
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => {
                    // This would navigate to monitor username page with this username
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
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default CheckUsername; 