#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('===================================================');
console.log('  OpenMC Username Sniper - Desktop App Setup      ');
console.log('===================================================');
console.log('This script will help you set up the application.');
console.log('It will install dependencies and prepare the app for development.');
console.log('');

// Check if Node.js and npm are installed
function checkDependencies() {
  try {
    const nodeVersion = execSync('node --version', { encoding: 'utf8' });
    console.log(`Node.js version: ${nodeVersion.trim()}`);
    
    const npmVersion = execSync('npm --version', { encoding: 'utf8' });
    console.log(`npm version: ${npmVersion.trim()}`);
    
    return true;
  } catch (error) {
    console.error('Error: Node.js or npm is not installed.');
    console.error('Please install Node.js from https://nodejs.org/');
    return false;
  }
}

// Check if Python is installed
function checkPython() {
  try {
    const pythonVersion = execSync('python --version', { encoding: 'utf8' });
    console.log(`Python version: ${pythonVersion.trim()}`);
    return true;
  } catch (error) {
    try {
      const python3Version = execSync('python3 --version', { encoding: 'utf8' });
      console.log(`Python version: ${python3Version.trim()}`);
      return true;
    } catch (error) {
      console.error('Error: Python is not installed or not in PATH.');
      console.error('Please install Python from https://python.org/');
      return false;
    }
  }
}

// Install npm dependencies
function installNpmDependencies() {
  console.log('\nInstalling npm dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('npm dependencies installed successfully.');
    return true;
  } catch (error) {
    console.error('Error installing npm dependencies:', error.message);
    return false;
  }
}

// Copy Python files
function copyPythonFiles() {
  console.log('\nCopying Python files...');
  try {
    execSync('node copy_python_files.js', { stdio: 'inherit' });
    console.log('Python files copied successfully.');
    return true;
  } catch (error) {
    console.error('Error copying Python files:', error.message);
    return false;
  }
}

// Install Python dependencies
function installPythonDependencies() {
  console.log('\nInstalling Python dependencies...');
  const pythonCmd = fs.existsSync('./src/python/requirements.txt') ? 
    'pip install -r ./src/python/requirements.txt' : 
    'pip install requests colorama python-dotenv urllib3 beautifulsoup4';
  
  try {
    execSync(pythonCmd, { stdio: 'inherit' });
    console.log('Python dependencies installed successfully.');
    return true;
  } catch (error) {
    console.error('Error installing Python dependencies:', error.message);
    console.log('Trying with pip3...');
    
    try {
      const pip3Cmd = pythonCmd.replace('pip', 'pip3');
      execSync(pip3Cmd, { stdio: 'inherit' });
      console.log('Python dependencies installed successfully with pip3.');
      return true;
    } catch (pip3Error) {
      console.error('Error installing Python dependencies with pip3:', pip3Error.message);
      return false;
    }
  }
}

// Start development server
function startDevServer() {
  console.log('\nStarting development server...');
  console.log('The application should open in a new window.');
  console.log('If it doesn\'t, you can manually start it with:');
  console.log('  npm run dev');
  console.log('  npm start (in a separate terminal)');
  
  try {
    // Create a detached process to run the development server
    execSync('npm run dev', { stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error('Error starting development server:', error.message);
    return false;
  }
}

// Main function
async function main() {
  console.log('Checking dependencies...');
  const hasNodeNpm = checkDependencies();
  const hasPython = checkPython();
  
  if (!hasNodeNpm || !hasPython) {
    console.error('\nRequired dependencies are missing. Please install them and try again.');
    rl.close();
    return;
  }
  
  rl.question('\nReady to proceed with installation? (y/n): ', (answer) => {
    if (answer.toLowerCase() !== 'y') {
      console.log('Setup aborted.');
      rl.close();
      return;
    }
    
    const npmSuccess = installNpmDependencies();
    if (!npmSuccess) {
      console.error('Failed to install npm dependencies. Aborting setup.');
      rl.close();
      return;
    }
    
    const copySuccess = copyPythonFiles();
    if (!copySuccess) {
      console.error('Failed to copy Python files. Continuing anyway...');
    }
    
    const pythonSuccess = installPythonDependencies();
    if (!pythonSuccess) {
      console.error('Failed to install Python dependencies. The app may not work correctly.');
      console.log('You can try to install them manually:');
      console.log('  pip install requests colorama python-dotenv urllib3 beautifulsoup4');
    }
    
    console.log('\n===================================================');
    console.log('  Setup Complete!                                  ');
    console.log('===================================================');
    console.log('To start the application in development mode:');
    console.log('  1. Run "npm run dev" in one terminal');
    console.log('  2. Run "npm start" in another terminal');
    console.log('\nTo build the application for distribution:');
    console.log('  npm run make');
    console.log('\nHappy sniping!');
    
    rl.question('\nWould you like to start the app now? (y/n): ', (startAnswer) => {
      if (startAnswer.toLowerCase() === 'y') {
        startDevServer();
      } else {
        console.log('You can start the app later with "npm run dev" and "npm start".');
      }
      rl.close();
    });
  });
}

main(); 