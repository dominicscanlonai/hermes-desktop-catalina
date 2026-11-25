// Static Catalina window fixture: no network, IPC, preload or backend.
'use strict';
const { app, BrowserWindow } = require('electron');
app.whenReady().then(async () => {
  const win = new BrowserWindow({ width: 850, height: 550, title: 'Hermes Catalina runtime smoke',
    webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true } });
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', event => event.preventDefault());
  await win.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(
    '<!doctype html><meta charset=utf-8><title>Runtime smoke</title><h1>Catalina runtime smoke</h1><p>This window does not verify the Hermes Desktop renderer or backend.</p>'
  ));
}).catch(() => { console.error('Runtime smoke failed'); app.exit(1); });
app.on('window-all-closed', () => app.quit());
