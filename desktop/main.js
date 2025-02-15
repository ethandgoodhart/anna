import { app, BrowserWindow, ipcMain, systemPreferences } from 'electron';
import { Hono } from 'hono'
import { serve } from '@hono/node-server'

const server = new Hono()

app.on('ready', () => {
  // Request camera and microphone permissions
  systemPreferences.askForMediaAccess('camera');
  systemPreferences.askForMediaAccess('microphone');
});

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    transparent: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Add CSP headers before loading the file
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.daily.co https://*.sentry.io; " +
          "connect-src 'self' https://*.daily.co https://*.sentry.io wss://*.daily.co https://tavusapi.com; " +
          "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.daily.co; " +
          "style-src 'self' 'unsafe-inline'; " +
          "img-src 'self' data: blob: https://*.daily.co; " +
          "media-src 'self' https://*.daily.co blob:; " +
          "frame-src 'self' https://*.daily.co;"
        ]
      }
    });
  });

  mainWindow.loadFile('index.html');
  
  // Uncomment to open DevTools on startup
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});



server.post('/webhook', async (c) => {

  const jsonBody = await c.req.json();
  mainWindow?.webContents.send('webhook-event', jsonBody);
  return c.json({ message: 'Webhook received' });
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

serve(server, (info) => {
  console.log(`Listening on http://localhost:${info.port}`) // Listening on http://localhost:3000
})

// Handle API calls
ipcMain.handle('create-conversation', async (event, token) => {
  try {
    const response = await fetch('https://tavusapi.com/v2/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': "a335c04a5be24585af0ddae7e08c40e5"
      },
      body: JSON.stringify({
        persona_id: 'p9a95912',
        properties: {
          apply_greenscreen: true
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
});

ipcMain.handle('end-conversation', async (event, { conversationId, token }) => {
  try {
    const response = await fetch(
      `https://tavusapi.com/v2/conversations/${conversationId}/end`,
      {
        method: 'POST',
        headers: {
          'x-api-key': token
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to end conversation');
    }

    return null;
  } catch (error) {
    console.error('Error ending conversation:', error);
    throw error;
  }
});