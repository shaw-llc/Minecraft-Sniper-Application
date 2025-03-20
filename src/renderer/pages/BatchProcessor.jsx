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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Tooltip
} from '@mui/material';
import { 
  Delete as DeleteIcon,
  Upload as UploadIcon,
  CloudUpload as CloudUploadIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  CheckCircleOutline as AvailableIcon,
  HighlightOff as UnavailableIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Save as SaveIcon
} from '@mui/icons-material';

function BatchProcessor({ settings, setNotification }) {
  const [usernames, setUsernames] = useState([]);
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState({});
  const [processing, setProcessing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  // Add usernames from input text
  const handleAddUsernames = () => {
    if (!inputText.trim()) {
      setError('Please enter at least one username');
      return;
    }

    // Split by any whitespace or comma
    const newUsernames = inputText
      .split(/[\s,]+/)
      .filter(name => name.trim())
      .map(name => name.trim());

    if (newUsernames.length === 0) {
      setError('No valid usernames found');
      return;
    }

    // Add to existing usernames, removing duplicates
    setUsernames(prev => {
      const combined = [...prev, ...newUsernames];
      return [...new Set(combined)]; // Remove duplicates
    });

    setInputText('');
    setError('');
  };

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      const lines = content.split(/[\r\n]+/);
      
      const newUsernames = lines
        .map(line => line.trim())
        .filter(line => line && !line.startsWith('#'));

      if (newUsernames.length === 0) {
        setError('No valid usernames found in file');
        return;
      }

      // Add to existing usernames, removing duplicates
      setUsernames(prev => {
        const combined = [...prev, ...newUsernames];
        return [...new Set(combined)]; // Remove duplicates
      });

      setNotification({
        open: true,
        message: `Imported ${newUsernames.length} usernames`,
        severity: 'success'
      });
    };

    reader.onerror = () => {
      setError('Error reading file');
    };

    reader.readAsText(file);
    // Reset the file input
    event.target.value = null;
  };

  // Remove username at index
  const handleRemoveUsername = (index) => {
    setUsernames(prev => prev.filter((_, i) => i !== index));
  };

  // Clear all usernames
  const handleClearUsernames = () => {
    setUsernames([]);
    setResults({});
  };

  // Process the usernames
  const handleProcessUsernames = async () => {
    if (usernames.length === 0) {
      setError('No usernames to process');
      return;
    }

    setProcessing(true);
    setCurrentIndex(0);
    setResults({});

    for (let i = 0; i < usernames.length; i++) {
      setCurrentIndex(i);
      
      const username = usernames[i];
      
      try {
        // Skip empty usernames
        if (!username.trim()) continue;
        
        // Check username
        const response = await window.api.checkUsername(username);
        
        setResults(prev => ({
          ...prev,
          [username]: response
        }));
        
      } catch (err) {
        console.error(`Error checking ${username}:`, err);
        setResults(prev => ({
          ...prev,
          [username]: {
            success: false,
            error: err.message || 'Unknown error',
            username
          }
        }));
      }
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setProcessing(false);
    setNotification({
      open: true,
      message: `Processed ${usernames.length} usernames`,
      severity: 'success'
    });
  };

  // Cancel processing
  const handleCancelProcess = () => {
    setProcessing(false);
  };

  // Export results to file
  const handleExportResults = () => {
    const resultArray = usernames.map(username => {
      const result = results[username] || { success: false, error: 'Not processed' };
      
      let status = 'Unknown';
      if (result.success) {
        status = result.available ? 'Available' : 'Unavailable';
      } else {
        status = `Error: ${result.error || 'Unknown error'}`;
      }
      
      let dropTime = '';
      if (result.drop_time) {
        dropTime = result.drop_time;
      }
      
      return `${username},${status},${dropTime}`;
    });
    
    const csvContent = [
      'Username,Status,Drop Time',
      ...resultArray
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'username_results.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setNotification({
      open: true,
      message: 'Results exported to CSV file',
      severity: 'success'
    });
  };

  // Format drop date for display
  const formatDropDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (err) {
      return dateString;
    }
  };

  // Get available username count
  const getAvailableCount = () => {
    return Object.values(results).filter(r => r.success && r.available).length;
  };

  // Get soon available username count
  const getSoonAvailableCount = () => {
    return Object.values(results).filter(r => r.success && !r.available && r.drop_time).length;
  };

  // Get error count
  const getErrorCount = () => {
    return Object.values(results).filter(r => !r.success).length;
  };

  return (
    <Box>
      <Paper
        elevation={2}
        sx={{
          p: 3,
          mb: 3,
          maxWidth: 1000,
          mx: 'auto',
          background: 'linear-gradient(to right, #1a237e, #01579b)'
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom sx={{ color: 'white' }}>
          Batch Username Processor
        </Typography>
        <Typography variant="body1" paragraph sx={{ color: 'white' }}>
          Check the availability of multiple Minecraft usernames at once.
        </Typography>
        
        <TextField
          fullWidth
          label="Enter usernames (separated by space, comma, or new line)"
          variant="outlined"
          multiline
          rows={3}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter usernames to check"
          disabled={processing}
          sx={{ 
            mb: 2,
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
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Button
            variant="contained"
            color="secondary"
            onClick={handleAddUsernames}
            disabled={processing || !inputText.trim()}
            startIcon={<CloudUploadIcon />}
          >
            Add Usernames
          </Button>
          
          <input
            type="file"
            id="file-upload"
            accept=".txt,.csv"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            ref={fileInputRef}
          />
          
          <Button
            variant="outlined"
            color="inherit"
            onClick={() => fileInputRef.current.click()}
            disabled={processing}
            startIcon={<UploadIcon />}
            sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.5)' }}
          >
            Import from File
          </Button>
        </Box>
        
        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.2)', my: 2 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1" sx={{ color: 'white' }}>
            {usernames.length} {usernames.length === 1 ? 'username' : 'usernames'} in queue
          </Typography>
          
          <Box>
            {processing ? (
              <Button
                variant="contained"
                color="error"
                onClick={handleCancelProcess}
                startIcon={<StopIcon />}
                sx={{ mr: 1 }}
              >
                Stop Processing
              </Button>
            ) : (
              <Button
                variant="contained"
                color="success"
                onClick={handleProcessUsernames}
                disabled={usernames.length === 0}
                startIcon={<StartIcon />}
                sx={{ mr: 1 }}
              >
                Process All
              </Button>
            )}
            
            <Button
              variant="outlined"
              color="inherit"
              onClick={handleClearUsernames}
              disabled={processing || usernames.length === 0}
              startIcon={<DeleteIcon />}
              sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.5)' }}
            >
              Clear All
            </Button>
          </Box>
        </Box>
        
        {processing && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
              Processing {currentIndex + 1} of {usernames.length}: {usernames[currentIndex]}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={(currentIndex / usernames.length) * 100} 
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>
        )}
      </Paper>

      {/* Results */}
      {Object.keys(results).length > 0 && (
        <Card sx={{ maxWidth: 1000, mx: 'auto', mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Results
              </Typography>
              
              <Button
                variant="contained"
                color="primary"
                onClick={handleExportResults}
                startIcon={<SaveIcon />}
              >
                Export to CSV
              </Button>
            </Box>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
              <Chip 
                icon={<AvailableIcon />} 
                label={`${getAvailableCount()} Available`} 
                color="success" 
              />
              <Chip 
                icon={<ScheduleIcon />} 
                label={`${getSoonAvailableCount()} Soon Available`} 
                color="warning" 
              />
              <Chip 
                icon={<ErrorIcon />} 
                label={`${getErrorCount()} Errors`} 
                color="error" 
              />
            </Box>
            
            <TableContainer>
              <Table sx={{ minWidth: 650 }} size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Username</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Drop Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {usernames.map((username, index) => {
                    const result = results[username];
                    if (!result) return null;
                    
                    return (
                      <TableRow 
                        key={index}
                        sx={{ 
                          '&:nth-of-type(odd)': { backgroundColor: 'rgba(0, 0, 0, 0.04)' },
                          backgroundColor: result.success && result.available ? 'rgba(76, 175, 80, 0.08)' : undefined
                        }}
                      >
                        <TableCell component="th" scope="row">
                          {username}
                        </TableCell>
                        <TableCell>
                          {result.success ? (
                            result.available ? (
                              <Chip 
                                icon={<AvailableIcon />} 
                                label="Available" 
                                color="success" 
                                size="small" 
                              />
                            ) : (
                              <Chip 
                                icon={<UnavailableIcon />} 
                                label="Unavailable" 
                                color="default" 
                                size="small" 
                              />
                            )
                          ) : (
                            <Chip 
                              icon={<ErrorIcon />} 
                              label="Error" 
                              color="error" 
                              size="small" 
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          {result.success && !result.available && result.drop_time ? (
                            <Tooltip title={result.drop_time}>
                              <span>{formatDropDate(result.drop_time)}</span>
                            </Tooltip>
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {result.success && result.available && (
                              <Tooltip title="Claim this username">
                                <IconButton 
                                  size="small" 
                                  color="success"
                                  onClick={() => {
                                    // Navigate to claim username page with this username
                                    setNotification({
                                      open: true,
                                      message: 'Navigate to claim page (feature coming soon)',
                                      severity: 'info'
                                    });
                                  }}
                                >
                                  <CloudUploadIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            
                            {result.success && !result.available && result.drop_time && (
                              <Tooltip title="Monitor this username">
                                <IconButton 
                                  size="small" 
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
                                  <SearchIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            
                            <Tooltip title="Check again">
                              <IconButton 
                                size="small"
                                onClick={async () => {
                                  try {
                                    const response = await window.api.checkUsername(username);
                                    setResults(prev => ({
                                      ...prev,
                                      [username]: response
                                    }));
                                  } catch (err) {
                                    console.error(`Error checking ${username}:`, err);
                                    setResults(prev => ({
                                      ...prev,
                                      [username]: {
                                        success: false,
                                        error: err.message || 'Unknown error',
                                        username
                                      }
                                    }));
                                  }
                                }}
                              >
                                <RefreshIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            
                            <Tooltip title="Remove">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleRemoveUsername(index)}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default BatchProcessor; 