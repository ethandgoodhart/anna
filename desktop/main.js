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
    width: 1400,
    height: 800,
    transparent: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.test.html');
  
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
  const { type, data } = jsonBody;
  console.log("RECEIVED WEBHOOK",type, data)
  mainWindow?.webContents.send('webhook-event', {
    serviceName: type,
    data: data
  });
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
        persona_id: 'p91850b706d1',
        replica_id: "r315bff4de",
        properties: {
          apply_greenscreen: true
        }
      })
    });

    if (!response.ok) {
      const json = await response.json();
      throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(json)}`);
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