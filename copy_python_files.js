const fs = require('fs');
const path = require('path');

// Define the source Python files
const pythonFiles = [
  'minecraft_auth.py',
  'name_utils.py',
  'sniper.py',
  'notifications.py',
  'easy_sniper.py',
  'advanced_sniper.py',
  'minecraft_sniper.py',
  'notification_config.json',
  'requirements.txt',
  '.env.example'
];

// Source and destination directories
const sourceDir = './';
const destDir = './src/python';

// Ensure the destination directory exists
if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
  console.log(`Created directory: ${destDir}`);
}

// Copy each file
let successCount = 0;
for (const file of pythonFiles) {
  const sourceFile = path.join(sourceDir, file);
  const destFile = path.join(destDir, file);
  
  try {
    if (fs.existsSync(sourceFile)) {
      fs.copyFileSync(sourceFile, destFile);
      console.log(`Copied: ${file}`);
      successCount++;
    } else {
      console.warn(`Warning: Source file not found: ${file}`);
    }
  } catch (error) {
    console.error(`Error copying ${file}: ${error.message}`);
  }
}

console.log(`Copied ${successCount} of ${pythonFiles.length} Python files to ${destDir}`); 