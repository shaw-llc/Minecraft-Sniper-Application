import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';

// Create dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#42a5f5', // Light blue
    },
    secondary: {
      main: '#4caf50', // Green
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// Create light theme
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Blue
    },
    secondary: {
      main: '#2e7d32', // Dark green
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

// ThemeSelector component to handle theme switching
const ThemeSelector = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState(darkTheme);
  
  useEffect(() => {
    const loadThemeSetting = async () => {
      try {
        const settings = await window.api.getSettings();
        setCurrentTheme(settings.theme === 'light' ? lightTheme : darkTheme);
      } catch (error) {
        console.error('Failed to load theme setting:', error);
        // Default to dark theme if there's an error
        setCurrentTheme(darkTheme);
      }
    };
    
    loadThemeSetting();
    
    // Listen for theme changes
    window.api.on('themeChanged', (newTheme) => {
      setCurrentTheme(newTheme === 'light' ? lightTheme : darkTheme);
    });
    
    return () => {
      window.api.removeAllListeners('themeChanged');
    };
  }, []);
  
  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

// Render the React app
const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeSelector>
      <App />
    </ThemeSelector>
  </React.StrictMode>
); 