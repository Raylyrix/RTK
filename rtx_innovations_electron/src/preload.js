const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
	// App information
	getAppVersion: () => ipcRenderer.invoke('get-app-version'),
	getAppName: () => ipcRenderer.invoke('get-app-name'),
	
	// Updates
	onUpdateStatus: (callback) => ipcRenderer.on('update-status', (_e, data) => callback(data)),
	checkForUpdates: () => ipcRenderer.invoke('update-check'),
	downloadUpdate: () => ipcRenderer.invoke('update-download'),
	quitAndInstall: () => ipcRenderer.invoke('update-quit-and-install'),
	
	// File dialogs
	showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
	showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
	showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
	
	// Store operations (match main.js handler names)
	storeGet: (key) => ipcRenderer.invoke('storeGet', key),
	storeSet: (key, value) => ipcRenderer.invoke('storeSet', key, value),
	// Optional delete kept for compatibility only if handler exists
	storeDelete: (key) => ipcRenderer.invoke('storeDelete', key),
	
	// Menu actions
	onMenuAction: (callback) => ipcRenderer.on('menu-action', callback),
	onAppQuitting: (callback) => ipcRenderer.on('app-quitting', callback),

	// Auth events
	onAuthSuccess: (callback) => ipcRenderer.on('auth-success', (_e, data) => callback(data)),
	
	// Google API Integration
	updateClientCredentials: (credentials) => ipcRenderer.invoke('updateClientCredentials', credentials),
	authenticateGoogle: (credentials) => ipcRenderer.invoke('authenticateGoogle', credentials),
	initializeGmailService: (credentials) => ipcRenderer.invoke('initializeGmailService', credentials),
	initializeSheetsService: (credentials) => ipcRenderer.invoke('initializeSheetsService', credentials),
	connectToSheets: (sheetId, sheetTitle) => ipcRenderer.invoke('connectToSheets', { sheetId, sheetTitle }),
	sendTestEmail: (emailData) => ipcRenderer.invoke('sendTestEmail', emailData),
	sendEmail: (emailData) => ipcRenderer.invoke('sendEmail', emailData),

	// Gmail extras
	listSendAs: () => ipcRenderer.invoke('gmail-list-send-as'),
	getGmailSignature: () => ipcRenderer.invoke('gmail-get-signature'),

	// Sheets extras
	listSheetTabs: (sheetId) => ipcRenderer.invoke('sheets-list-tabs', sheetId),
	updateSheetStatus: (args) => ipcRenderer.invoke('sheets-update-status', args),
	
	// Scheduler
	scheduleOneTime: (params) => ipcRenderer.invoke('schedule-campaign-one-time', params),
	listSchedules: () => ipcRenderer.invoke('schedule-list'),
	cancelSchedule: (id) => ipcRenderer.invoke('schedule-cancel', id),

	// Local files and logs
	loadLocalSpreadsheet: (filePath) => ipcRenderer.invoke('load-local-spreadsheet', filePath),
	appendLog: (payload) => ipcRenderer.invoke('app-log-append', payload),
	readSessionLog: () => ipcRenderer.invoke('app-log-read'),
	onAppLog: (callback) => ipcRenderer.on('app-log', (_e, data) => callback(data)),
	writeFile: (path, content) => ipcRenderer.invoke('write-file', { path, content }),
	readJsonFile: (path) => ipcRenderer.invoke('read-json-file', path),
	
	// Telemetry
	telemetryTrack: (event, meta) => ipcRenderer.invoke('telemetry-track', { event, meta }),
	
	// Templates
	listTemplates: () => ipcRenderer.invoke('templates-list'),
	saveTemplateJson: (name, data) => ipcRenderer.invoke('templates-save', { name, data }),
	loadTemplateJson: (filePath) => ipcRenderer.invoke('templates-load', filePath),
	deleteTemplateJson: (filePath) => ipcRenderer.invoke('templates-delete', filePath),
	
	// Remove listeners
	removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Expose platform information
contextBridge.exposeInMainWorld('platform', {
	isWindows: process.platform === 'win32',
	isMac: process.platform === 'darwin',
	isLinux: process.platform === 'linux',
	platform: process.platform
});

// Expose development mode
contextBridge.exposeInMainWorld('isDev', process.env.NODE_ENV === 'development'); 