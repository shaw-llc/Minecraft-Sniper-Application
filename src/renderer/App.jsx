import React, { useState, useEffect } from 'react';
import { 
  Box, 
  CssBaseline, 
  Drawer, 
  AppBar, 
  Toolbar, 
  Typography, 
  Divider, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText,
  IconButton,
  Snackbar,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Visibility as MonitorIcon,
  Add as ClaimIcon,
  Person as AccountIcon,
  Settings as SettingsIcon,
  ViewList as BatchIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';

// Import pages
import CheckUsername from './pages/CheckUsername';
import MonitorUsername from './pages/MonitorUsername';
import ClaimUsername from './pages/ClaimUsername';
import AccountStatus from './pages/AccountStatus';
import Settings from './pages/Settings';
import BatchProcessor from './pages/BatchProcessor';
import ScheduleMonitor from './pages/ScheduleMonitor';

const drawerWidth = 240;

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [selectedPage, setSelectedPage] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [settings, setSettings] = useState({
    checkInterval: 3,
    defaultStrategy: 'timing',
    notifications: true,
    theme: 'dark'
  });

  // Load settings on component mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const savedSettings = await window.api.getSettings();
        setSettings(savedSettings);
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    };

    loadSettings();

    // Set up event listeners for notifications
    window.api.on('notification', (message, severity) => {
      setNotification({ 
        open: true, 
        message, 
        severity: severity || 'info' 
      });
    });

    // Clean up event listeners on unmount
    return () => {
      window.api.removeAllListeners('notification');
    };
  }, []);

  // Watch for settings changes, specifically theme changes
  useEffect(() => {
    // Emit theme change event when theme setting changes
    window.api.emit('themeChanged', settings.theme);
  }, [settings.theme]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handlePageSelect = (index) => {
    setSelectedPage(index);
    setMobileOpen(false);
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const pages = [
    { name: 'Check Username', icon: <SearchIcon />, component: <CheckUsername setNotification={setNotification} /> },
    { name: 'Monitor Username', icon: <MonitorIcon />, component: <MonitorUsername settings={settings} setNotification={setNotification} /> },
    { name: 'Schedule Monitor', icon: <ScheduleIcon />, component: <ScheduleMonitor settings={settings} setNotification={setNotification} /> },
    { name: 'Claim Username', icon: <ClaimIcon />, component: <ClaimUsername settings={settings} setNotification={setNotification} /> },
    { name: 'Batch Processor', icon: <BatchIcon />, component: <BatchProcessor settings={settings} setNotification={setNotification} /> },
    { name: 'Account Status', icon: <AccountIcon />, component: <AccountStatus setNotification={setNotification} /> },
    { name: 'Settings', icon: <SettingsIcon />, component: <Settings settings={settings} setSettings={setSettings} setNotification={setNotification} /> }
  ];

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          OpenMC Sniper
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {pages.map((page, index) => (
          <ListItem key={page.name} disablePadding>
            <ListItemButton 
              selected={selectedPage === index}
              onClick={() => handlePageSelect(index)}
            >
              <ListItemIcon>
                {page.icon}
              </ListItemIcon>
              <ListItemText primary={page.name} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            {pages[selectedPage].name}
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          marginTop: '64px'
        }}
      >
        {pages[selectedPage].component}
      </Box>

      <Snackbar 
        open={notification.open} 
        autoHideDuration={6000} 
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity} 
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App; 