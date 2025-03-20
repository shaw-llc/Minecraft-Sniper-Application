const { notarize } = require('@electron/notarize');
const path = require('path');
const fs = require('fs');

module.exports = async function (params) {
  // Only notarize the app on Mac OS
  if (process.platform !== 'darwin') {
    return;
  }

  console.log('Notarizing macOS application...');
  
  // Same appId in package.json
  const appId = 'com.openmc.usernameSniper';
  
  const appPath = path.join(
    params.appOutDir, 
    `${params.packager.appInfo.productFilename}.app`
  );
  
  if (!fs.existsSync(appPath)) {
    console.log(`App path not found: ${appPath}`);
    return;
  }

  try {
    // Environment variables must be set for this to work:
    // APPLE_ID: your Apple ID
    // APPLE_ID_PASSWORD: app-specific password (not your regular password)
    // APPLE_TEAM_ID: your Team ID
    await notarize({
      appBundleId: appId,
      appPath: appPath,
      appleId: process.env.APPLE_ID,
      appleIdPassword: process.env.APPLE_ID_PASSWORD,
      teamId: process.env.APPLE_TEAM_ID,
    });
    
    console.log(`Notarization completed successfully for: ${appPath}`);
  } catch (error) {
    console.error(`Notarization failed: ${error.message}`);
    throw error;
  }
}; 