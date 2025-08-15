const { contextBridge, ipcRenderer } = require('electron');
const { contextBridge, ipcRenderer } = require('electron');

function wrapInvoke(channel, ...args) {
    return ipcRenderer.invoke(channel, ...args);
}

// Event subscriptions
const subscriptions = {
    onMenuAction: (cb) => ipcRenderer.on('menu-action', (_e, action) => cb && cb(action)),
    onAppQuitting: (cb) => ipcRenderer.on('app-quitting', () => cb && cb()),
    onUpdateStatus: (cb) => ipcRenderer.on('update-status', (_e, data) => cb && cb(data)),
    onAuthProgress: (cb) => ipcRenderer.on('auth-progress', (_e, data) => cb && cb(data)),
    onAuthSuccess: (cb) => ipcRenderer.on('auth-success', (_e, data) => cb && cb(data)),
    onAppLog: (cb) => ipcRenderer.on('app-log', (_e, data) => cb && cb(data)),
};

contextBridge.exposeInMainWorld('electronAPI', {
    // UI events
    onMenuAction: subscriptions.onMenuAction,
    onAppQuitting: subscriptions.onAppQuitting,
    onUpdateStatus: subscriptions.onUpdateStatus,
    onAuthProgress: subscriptions.onAuthProgress,
    onAuthSuccess: subscriptions.onAuthSuccess,
    onAppLog: subscriptions.onAppLog,

    // Dialogs / FS
    showOpenDialog: (options) => wrapInvoke('show-open-dialog', options),
    showSaveDialog: (options) => wrapInvoke('show-save-dialog', options),
    showMessageBox: (options) => wrapInvoke('show-message-box', options),
    writeFile: (args) => wrapInvoke('write-file', args),

    // App info
    getAppVersion: () => wrapInvoke('get-app-version'),
    getAppName: () => wrapInvoke('get-app-name'),

    // Telemetry/logs
    appendLog: (payload) => wrapInvoke('app-log-append', payload),
    readSessionLog: () => wrapInvoke('app-log-read'),
    track: (args) => wrapInvoke('telemetry-track', args),

    // Store
    storeGet: (key) => wrapInvoke('storeGet', key),
    storeSet: (key, value) => wrapInvoke('storeSet', key, value),
    storeDelete: (key) => wrapInvoke('storeDelete', key),

    // Accounts
    listAccounts: () => wrapInvoke('accounts-list'),
    useAccount: (email) => wrapInvoke('accounts-use', email),

    // Auth (OAuth)
    authenticateGoogle: (credentials) => wrapInvoke('authenticateGoogle', credentials),
    initializeGmailService: () => wrapInvoke('initializeGmailService'),
    initializeSheetsService: () => wrapInvoke('initializeSheetsService'),
    getCurrentAuth: () => wrapInvoke('auth-current-user'),

    // SMTP/App Password mode
    smtpSaveCreds: ({ email, appPassword }) => wrapInvoke('smtp-save-creds', { email, appPassword }),
    smtpClearCreds: (email) => wrapInvoke('smtp-clear-creds', email),
    smtpExtractSignature: (email) => wrapInvoke('smtp-extract-signature', email),

    // Gmail features
    listSendAs: () => wrapInvoke('gmail-list-send-as'),
    getGmailSignature: () => wrapInvoke('gmail-get-signature'),

    // Sheets
    listSheetTabs: (sheetId) => wrapInvoke('sheets-list-tabs', sheetId),
    connectToSheets: (arg1, arg2, arg3) => {
        const payload = (typeof arg1 === 'object') ? arg1 : { sheetId: arg1, sheetTitle: arg2, rawUrl: arg3 };
        return wrapInvoke('connectToSheets', payload);
    },
    updateSheetStatus: (args) => wrapInvoke('sheets-update-status', args),

    // Email send
    sendTestEmail: (emailData) => wrapInvoke('sendTestEmail', emailData),
    sendEmail: (emailData) => wrapInvoke('sendEmail', emailData),

    // Templates
    listTemplates: () => wrapInvoke('templates-list'),
    saveTemplateJson: (name, data) => wrapInvoke('templates-save', { name, data }),
    loadTemplateJson: (path) => wrapInvoke('templates-load', path),
    deleteTemplateJson: (path) => wrapInvoke('templates-delete', path),
    readJsonFile: (path) => wrapInvoke('read-json-file', path),

    // Scheduler
    scheduleOneTime: (params) => wrapInvoke('schedule-campaign-one-time', params),
    listSchedules: () => wrapInvoke('schedule-list'),
    cancelSchedule: (id) => wrapInvoke('schedule-cancel', id),

    // Import local spreadsheets
    loadLocalSpreadsheet: (filePath) => wrapInvoke('load-local-spreadsheet', filePath),

    // Updates
    checkForUpdates: () => wrapInvoke('update-check'),
    downloadUpdate: () => wrapInvoke('update-download'),
    quitAndInstall: () => wrapInvoke('update-quit-and-install'),
});

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
  // Auth progress
  onAuthProgress: (callback) => ipcRenderer.on('auth-progress', (_e, data) => callback(data)),
	
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
  getCurrentAuth: () => ipcRenderer.invoke('auth-current-user'),
	
	// Google API Integration
  listAccounts: () => ipcRenderer.invoke('accounts-list'),
  useAccount: (email) => ipcRenderer.invoke('accounts-use', email),
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