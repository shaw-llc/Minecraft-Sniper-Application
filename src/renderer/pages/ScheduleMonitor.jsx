import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Divider,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  AccessTime as TimeIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';

function ScheduleMonitor({ settings, setNotification }) {
  const [username, setUsername] = useState('');
  const [dropTime, setDropTime] = useState(null);
  const [loading, setLoading] = useState(false);
  const [usernameError, setUsernameError] = useState('');
  const [scheduledMonitors, setScheduledMonitors] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedMonitor, setSelectedMonitor] = useState(null);
  const [startBeforeMinutes, setStartBeforeMinutes] = useState(10);
  const [strategy, setStrategy] = useState(settings.defaultStrategy || 'timing');
  const [autoClaim, setAutoClaim] = useState(true);
  const [editMode, setEditMode] = useState(false);

  // Load scheduled monitors on component mount
  useEffect(() => {
    loadScheduledMonitors();
  }, []);

  const loadScheduledMonitors = async () => {
    try {
      const monitors = await window.api.getScheduledMonitors();
      setScheduledMonitors(monitors || []);
    } catch (error) {
      console.error('Failed to load scheduled monitors:', error);
      setNotification({
        open: true,
        message: 'Failed to load scheduled monitors: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const checkDropTime = async () => {
    if (!username.trim()) {
      setUsernameError('Username is required');
      return;
    }

    setUsernameError('');
    setLoading(true);

    try {
      const result = await window.api.getDropTime(username);
      
      if (result.success) {
        if (result.dropTime) {
          const dropDate = new Date(result.dropTime);
          setDropTime(dropDate);
          
          setNotification({
            open: true,
            message: `Username "${username}" will be available on ${dropDate.toLocaleString()}`,
            severity: 'info'
          });
        } else {
          setNotification({
            open: true,
            message: `No drop time found for "${username}"`,
            severity: 'warning'
          });
        }
      } else {
        setNotification({
          open: true,
          message: result.message || 'Failed to check drop time',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Failed to check drop time:', error);
      setNotification({
        open: true,
        message: 'Failed to check drop time: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (edit = false) => {
    if (!username.trim() || !dropTime) {
      setUsernameError('Username and drop time are required');
      return;
    }
    
    setEditMode(edit);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSchedule = async () => {
    const now = new Date();
    const monitorStartTime = new Date(dropTime.getTime() - startBeforeMinutes * 60 * 1000);
    
    if (monitorStartTime < now) {
      setNotification({
        open: true,
        message: 'Monitoring start time must be in the future',
        severity: 'error'
      });
      return;
    }

    const newMonitor = {
      id: editMode && selectedMonitor ? selectedMonitor.id : Date.now().toString(),
      username,
      dropTime: dropTime.toISOString(),
      monitorStartTime: monitorStartTime.toISOString(),
      autoClaim,
      strategy,
      status: 'scheduled'
    };

    try {
      await window.api.scheduleMonitor(newMonitor);
      setOpenDialog(false);
      await loadScheduledMonitors();
      
      // Reset fields
      if (!editMode) {
        setUsername('');
        setDropTime(null);
      }
      
      setNotification({
        open: true,
        message: `Username "${username}" ${editMode ? 'updated' : 'scheduled'} for monitoring`,
        severity: 'success'
      });
    } catch (error) {
      console.error('Failed to schedule monitor:', error);
      setNotification({
        open: true,
        message: 'Failed to schedule monitor: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const handleEditMonitor = (monitor) => {
    setUsername(monitor.username);
    setDropTime(new Date(monitor.dropTime));
    setStartBeforeMinutes(Math.round((new Date(monitor.dropTime) - new Date(monitor.monitorStartTime)) / (60 * 1000)));
    setStrategy(monitor.strategy);
    setAutoClaim(monitor.autoClaim);
    setSelectedMonitor(monitor);
    handleOpenDialog(true);
  };

  const handleDeleteMonitor = async (id) => {
    try {
      await window.api.deleteScheduledMonitor(id);
      await loadScheduledMonitors();
      
      setNotification({
        open: true,
        message: 'Scheduled monitor deleted',
        severity: 'success'
      });
    } catch (error) {
      console.error('Failed to delete scheduled monitor:', error);
      setNotification({
        open: true,
        message: 'Failed to delete scheduled monitor: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const getStatusChipColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'default';
      case 'active':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h1" gutterBottom>
          Schedule Username Monitoring
        </Typography>
        <Typography variant="body1" paragraph>
          Schedule monitoring for usernames that will become available in the future.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Username to monitor"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              error={!!usernameError}
              helperText={usernameError}
            />
          </Grid>
          
          <Grid item xs={12} md={6} sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={checkDropTime}
              disabled={loading || !username.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <TimeIcon />}
            >
              Check Drop Time
            </Button>
          </Grid>
          
          {dropTime && (
            <>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Username "{username}" will be available on {dropTime.toLocaleString()}
                </Alert>
              </Grid>
              
              <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<ScheduleIcon />}
                  onClick={() => handleOpenDialog(false)}
                >
                  Schedule Monitoring
                </Button>
              </Grid>
            </>
          )}
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Scheduled Monitors
        </Typography>
        
        {scheduledMonitors.length === 0 ? (
          <Typography variant="body1" sx={{ py: 3, textAlign: 'center', color: 'text.secondary' }}>
            No scheduled monitors yet. Use the form above to schedule username monitoring.
          </Typography>
        ) : (
          <List>
            {scheduledMonitors.map((monitor) => (
              <ListItem key={monitor.id} divider>
                <ListItemText
                  primary={monitor.username}
                  secondary={
                    <>
                      <Typography component="span" variant="body2" display="block">
                        Available: {new Date(monitor.dropTime).toLocaleString()}
                      </Typography>
                      <Typography component="span" variant="body2" display="block">
                        Monitoring starts: {new Date(monitor.monitorStartTime).toLocaleString()}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip 
                          label={monitor.status} 
                          size="small" 
                          color={getStatusChipColor(monitor.status)}
                          sx={{ mr: 1 }}
                        />
                        <Chip 
                          label={monitor.strategy} 
                          size="small" 
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                        {monitor.autoClaim && (
                          <Chip 
                            label="Auto-claim" 
                            size="small" 
                            color="secondary" 
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton 
                    edge="end" 
                    aria-label="edit" 
                    onClick={() => handleEditMonitor(monitor)}
                    disabled={monitor.status === 'active'}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    edge="end" 
                    aria-label="delete" 
                    onClick={() => handleDeleteMonitor(monitor.id)}
                    disabled={monitor.status === 'active'}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>{editMode ? 'Edit Scheduled Monitor' : 'Schedule Monitor'}</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 3 }}>
            Configure when to start monitoring username "{username}" before it becomes available.
          </DialogContentText>

          <Grid container spacing={2}>
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateTimePicker
                  label="Username Available Time"
                  value={dropTime}
                  onChange={setDropTime}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                  readOnly
                />
              </LocalizationProvider>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Start Monitoring Minutes Before"
                type="number"
                value={startBeforeMinutes}
                onChange={(e) => setStartBeforeMinutes(parseInt(e.target.value) || 10)}
                helperText="How many minutes before the drop time to start monitoring"
                inputProps={{ min: 1, max: 60 }}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Claim Strategy</InputLabel>
                <Select
                  value={strategy}
                  label="Claim Strategy"
                  onChange={(e) => setStrategy(e.target.value)}
                >
                  <MenuItem value="timing">Timing Strategy</MenuItem>
                  <MenuItem value="burst">Burst Strategy</MenuItem>
                  <MenuItem value="distributed">Distributed Strategy</MenuItem>
                  <MenuItem value="precision">Precision Strategy</MenuItem>
                  <MenuItem value="adaptive">Adaptive Strategy</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoClaim}
                    onChange={(e) => setAutoClaim(e.target.checked)}
                    color="primary"
                  />
                }
                label="Automatically attempt to claim when available"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSchedule} variant="contained" color="primary">
            {editMode ? 'Update Schedule' : 'Schedule'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ScheduleMonitor; 