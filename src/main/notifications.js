const axios = require('axios');
const nodemailer = require('nodemailer');
const { app } = require('electron');
const Store = require('electron-store');
const store = new Store();

/**
 * Send a notification via Discord webhook
 * @param {string} webhook - Discord webhook URL
 * @param {string} message - Message to send
 * @param {string} title - Title of the embed
 * @param {string} color - Color of the embed (hex color without #)
 * @returns {Promise<boolean>} - Whether the notification was sent successfully
 */
async function sendDiscordNotification(webhook, message, title = 'OpenMC Username Sniper', color = '3498db') {
  if (!webhook) {
    console.error('No Discord webhook URL provided');
    return false;
  }

  try {
    const response = await axios.post(webhook, {
      embeds: [{
        title,
        description: message,
        color: parseInt(color, 16),
        timestamp: new Date().toISOString(),
        footer: {
          text: `OpenMC Username Sniper v${app.getVersion()}`
        }
      }]
    });
    
    if (response.status === 204) {
      console.log('Discord notification sent successfully');
      return true;
    } else {
      console.error('Discord notification failed:', response.status, response.statusText);
      return false;
    }
  } catch (error) {
    console.error('Error sending Discord notification:', error.message);
    return false;
  }
}

/**
 * Send an email notification
 * @param {string} to - Recipient email address
 * @param {string} subject - Email subject
 * @param {string} message - Email body
 * @returns {Promise<boolean>} - Whether the email was sent successfully
 */
async function sendEmailNotification(to, subject, message) {
  if (!to) {
    console.error('No recipient email address provided');
    return false;
  }

  // Create a test account using Ethereal if no SMTP settings are configured
  // In a production app, you would want to use a real SMTP server
  try {
    // Get SMTP settings from store or use default test account
    const smtpSettings = store.get('smtpSettings', null);
    let transporter;
    
    if (!smtpSettings) {
      // Create a test account
      const testAccount = await nodemailer.createTestAccount();
      
      // Create a transporter using the test account
      transporter = nodemailer.createTransport({
        host: 'smtp.ethereal.email',
        port: 587,
        secure: false,
        auth: {
          user: testAccount.user,
          pass: testAccount.pass,
        },
      });
    } else {
      // Use configured SMTP settings
      transporter = nodemailer.createTransport({
        host: smtpSettings.host,
        port: smtpSettings.port,
        secure: smtpSettings.secure,
        auth: {
          user: smtpSettings.user,
          pass: smtpSettings.pass,
        },
      });
    }

    // Send email
    const info = await transporter.sendMail({
      from: '"OpenMC Username Sniper" <noreply@openmcsniper.app>',
      to,
      subject,
      text: message,
      html: `<p>${message.replace(/\n/g, '<br>')}</p>`,
    });

    console.log('Email sent:', info.messageId);
    
    // If using Ethereal, log the URL where the message can be viewed
    if (!smtpSettings) {
      console.log('Preview URL:', nodemailer.getTestMessageUrl(info));
    }
    
    return true;
  } catch (error) {
    console.error('Error sending email notification:', error.message);
    return false;
  }
}

/**
 * Send a notification via all enabled channels
 * @param {string} message - Notification message
 * @param {string} title - Notification title
 * @param {string} type - Notification type (info, success, warning, error)
 */
async function sendNotification(message, title = 'OpenMC Username Sniper', type = 'info') {
  // Get notification settings from store
  const settings = store.get('settings', {});
  const colorMap = {
    info: '3498db',    // Blue
    success: '2ecc71', // Green
    warning: 'f39c12', // Orange
    error: 'e74c3c'    // Red
  };
  
  const color = colorMap[type] || colorMap.info;
  
  // Send Discord notification if enabled
  if (settings.discordEnabled && settings.discordWebhook) {
    await sendDiscordNotification(
      settings.discordWebhook,
      message,
      title,
      color
    );
  }
  
  // Send email notification if enabled
  if (settings.emailEnabled && settings.emailAddress) {
    await sendEmailNotification(
      settings.emailAddress,
      `${title} - ${type.toUpperCase()}`,
      message
    );
  }
}

module.exports = {
  sendDiscordNotification,
  sendEmailNotification,
  sendNotification
}; 