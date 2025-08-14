const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const Store = require('electron-store');
const { google } = require('googleapis');
const http = require('http');
const url = require('url');
const cron = require('node-cron');

// Auto-update and env helpers
const isDev = (() => {
	try { return require('electron-is-dev'); } catch (_) { return process.env.NODE_ENV === 'development'; }})();
let autoUpdater; // lazy require to avoid issues if module not present

// Telemetry setup
const fs = require('fs');
const mime = require('mime-types');
const os = require('os');
const crypto = require('crypto');

// Initialize store
const store = new Store();

// Global variables for Google services
let oauth2Client = null;
let gmailService = null;
let sheetsService = null;
let mainWindow = null;

function getInstallId() {
	let id = store.get('installId');
	if (!id) {
		id = (crypto.randomUUID ? crypto.randomUUID() : (Date.now().toString(36) + Math.random().toString(36).slice(2)));
		store.set('installId', id);
	}
	return id;
}

function getTelemetryEndpoint() {
	return process.env.RTX_TELEMETRY_URL || store.get('telemetry.url') || null;
}

const TELEMETRY_INTERVAL_MS = 60000;
let telemetryQueue = [];
let telemetryTimer = null;

function trackTelemetry(eventName, meta) {
	try {
		telemetryQueue.push({
			ts: new Date().toISOString(),
			event: eventName,
			meta: meta || null,
			appVersion: app.getVersion ? app.getVersion() : null,
			platform: process.platform,
			installId: getInstallId()
		});
		logEvent('info', 'telemetry-event', { event: eventName });
	} catch (e) {
		// swallow
	}
}

function flushTelemetry() {
	const endpoint = getTelemetryEndpoint();
	if (!endpoint || telemetryQueue.length === 0) return;
	const events = telemetryQueue.splice(0, telemetryQueue.length);
	try {
		const target = new URL(endpoint);
		const payload = JSON.stringify({
			installId: getInstallId(),
			appVersion: app.getVersion ? app.getVersion() : null,
			platform: process.platform,
			events
		});
		const opts = {
			method: 'POST',
			hostname: target.hostname,
			port: target.port || (target.protocol === 'https:' ? 443 : 80),
			path: target.pathname + (target.search || ''),
			headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
		};
		const lib = target.protocol === 'https:' ? require('https') : require('http');
		const req = lib.request(opts, (res) => { res.on('data', () => {}); res.on('end', () => {}); });
		req.on('error', (err) => { logEvent('error', 'telemetry-send-failed', { error: err.message }); });
		req.write(payload);
		req.end();
	} catch (e) {
		logEvent('error', 'telemetry-exception', { error: e.message });
	}
}

function startTelemetry() {
	if (telemetryTimer) return;
	telemetryTimer = setInterval(flushTelemetry, TELEMETRY_INTERVAL_MS);
	trackTelemetry('app_start');
}

// Global scheduled jobs map accessor
function getJobsMap() {
	if (!global.__rtxScheduledJobs) global.__rtxScheduledJobs = new Map();
	return global.__rtxScheduledJobs;
}

// Google API Scopes
const SCOPES = [
	'https://www.googleapis.com/auth/spreadsheets',
	'https://www.googleapis.com/auth/gmail.send',
	'https://www.googleapis.com/auth/gmail.readonly',
	'https://www.googleapis.com/auth/gmail.settings.basic'
];

function createWindow() {
  mainWindow = new BrowserWindow({
		width: 1200,
		height: 800,
		minWidth: 1100,
		minHeight: 700,
		resizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icons/icon.png'),
		show: false
	});

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
	});

	mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
	createMenu();
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Campaign',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
					if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('menu-action', 'new-campaign');
          }
				}
			},
        {
          label: 'Import Data',
          accelerator: 'CmdOrCtrl+I',
          click: () => {
					if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('menu-action', 'import-data');
          }
          }
        },
        { type: 'separator' },
        {
					label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
					click: () => app.quit()
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
				{ role: 'paste' }
      ]
    },
    {
			label: 'View',
			submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
			label: 'Window',
			submenu: [ { role: 'minimize' }, { role: 'close' } ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

function normalizeCredentials(raw) {
	// Accept structures: {installed:{...}}, {web:{...}}, or flat
	if (raw?.web) {
		const web = raw.web;
		if (!web.client_id || !web.client_secret) throw new Error('Missing client_id/client_secret');
		const exact = Array.isArray(web.redirect_uris) ? web.redirect_uris.find(u => u.startsWith('http://localhost')) : null;
		if (!exact) {
			return { client_id: web.client_id, client_secret: web.client_secret, redirect_uri: null, fixed: false };
		}
		return { client_id: web.client_id, client_secret: web.client_secret, redirect_uri: exact, fixed: true };
	}
	const creds = raw?.installed || raw;
	if (!creds) throw new Error('Invalid credentials file format');
	if (!creds.client_id || !creds.client_secret) throw new Error('Missing client_id/client_secret in credentials');
	const hasLocalhost = Array.isArray(creds.redirect_uris) && creds.redirect_uris.some(u => u.startsWith('http://localhost'));
	return { client_id: creds.client_id, client_secret: creds.client_secret, redirect_uri: null, fixed: false, host: hasLocalhost ? 'localhost' : '127.0.0.1' };
}

function buildOAuthClient(norm, redirectUriOverride) {
	const redirect = redirectUriOverride || norm.redirect_uri || 'http://localhost';
	return new google.auth.OAuth2(norm.client_id, norm.client_secret, redirect);
}

async function ensureServices() {
	if (!oauth2Client) {
		const token = store.get('googleToken');
		const norm = store.get('googleCreds');
		if (!token || !norm) throw new Error('Not authenticated');
		oauth2Client = buildOAuthClient(norm);
		oauth2Client.setCredentials(token);
	}
	if (!gmailService) gmailService = google.gmail({ version: 'v1', auth: oauth2Client });
	if (!sheetsService) sheetsService = google.sheets({ version: 'v4', auth: oauth2Client });
}

// Google API Integration
async function authenticateGoogle(credentialsData) {
	try {
		const norm = normalizeCredentials(credentialsData);
		store.set('googleCreds', norm);

		const existing = store.get('googleToken');
		if (existing) {
			oauth2Client = buildOAuthClient(norm);
			oauth2Client.setCredentials(existing);
			await ensureServices();
			const profile = await gmailService.users.getProfile({ userId: 'me' });
			logEvent('info', 'Authenticated with existing token', { email: profile.data.emailAddress });
			trackTelemetry('auth_success');
			return { success: true, userEmail: profile.data.emailAddress };
		}

		const { shell } = require('electron');

		const token = await new Promise((resolve, reject) => {
			let settled = false;
			let server;

			const startServer = (host, port, pathName) => {
				server = http.createServer(async (req, res) => {
					try {
						const base = `http://${host}:${server.address().port}`;
						const reqUrl = new URL(req.url, base);
						// Accept any path as long as code exists
						const code = reqUrl.searchParams.get('code');
						if (!code) { res.writeHead(400); res.end('Missing code'); return; }
						const { tokens } = await oauth2Client.getToken(code);
						oauth2Client.setCredentials(tokens);
						res.writeHead(200, { 'Content-Type': 'text/html' });
						res.end('<html><body><h2>Authentication successful. You can close this window.</h2></body></html>');
						settled = true;
						server.close(() => resolve(tokens));
					} catch (err) {
						if (!settled) { settled = true; try { server.close(); } catch (_) {} reject(err); }
					}
				});

				// Try to bind; if privileged or fails, fall back to random port and alternate host
				const tryListen = (h, p) => server.listen(p, h, async () => {
					try {
						oauth2Client = buildOAuthClient(norm, `http://${h}:${server.address().port}${pathName}`);
						const authUrl = oauth2Client.generateAuthUrl({ access_type: 'offline', scope: SCOPES, prompt: 'consent' });
						await shell.openExternal(authUrl);
					} catch (openErr) {
						try { server.close(); } catch (_) {}
						reject(openErr);
					}
				}).on('error', (e) => {
					// fallback to alternate host/port
					try { server.close(); } catch (_) {}
					if (!settled) {
						const altHost = h === 'localhost' ? '127.0.0.1' : 'localhost';
						server = http.createServer(() => {});
						tryListen(altHost, 0);
					}
				});
				tryListen(host, port);
			};

			if (norm.fixed && norm.redirect_uri) {
				const parsed = new URL(norm.redirect_uri);
				const host = parsed.hostname || 'localhost';
				// If no port provided, use random port instead of 80
				const port = parsed.port ? parseInt(parsed.port, 10) : 0;
				const pathName = parsed.pathname || '/';
				startServer(host, port, pathName);
			} else {
				const host = norm.host || 'localhost';
				const pathName = '/';
				startServer(host, 0, pathName);
			}

			setTimeout(() => {
				if (!settled) {
					settled = true;
					try { server && server.close(); } catch (_) {}
					reject(new Error('Authentication timed out. Please try again.'));
				}
			}, 300000); // 5 minutes
		});

		store.set('googleToken', token);
		await ensureServices();
		const profile = await gmailService.users.getProfile({ userId: 'me' });
		if (mainWindow && mainWindow.webContents) {
			mainWindow.webContents.send('auth-success', { email: profile.data.emailAddress });
		}
		logEvent('info', 'Authenticated and token stored', { email: profile.data.emailAddress });
		trackTelemetry('auth_success');
		return { success: true, userEmail: profile.data.emailAddress };
	} catch (error) {
		console.error('Authentication error:', error);
		logEvent('error', 'Authentication error', { error: error.message });
		trackTelemetry('auth_error', { error: error.message });
		return { success: false, error: error.message };
	}
}

async function initializeGmailService() {
	try {
		await ensureServices();
		return { success: true };
	} catch (error) {
		return { success: false, error: error.message };
	}
}

async function initializeSheetsService() {
	try {
		await ensureServices();
		return { success: true };
	} catch (error) {
		return { success: false, error: error.message };
	}
}

async function connectToSheets(arg) {
	try {
		await ensureServices();
		let sheetId = arg;
		let sheetTitle = null;
		if (arg && typeof arg === 'object') {
			sheetId = arg.sheetId;
			sheetTitle = arg.sheetTitle || null;
		}
		const range = sheetTitle ? `${sheetTitle}!A:Z` : 'A:Z';
		const response = await sheetsService.spreadsheets.values.get({ spreadsheetId: sheetId, range });
		const values = response.data.values || [];
		if (!values.length) throw new Error('No data found in sheet');
		const headers = values[0];
		const rows = values.slice(1);
		return { success: true, data: { headers, rows } };
	} catch (error) {
		console.error('Sheets connection error:', error);
		return { success: false, error: error.message };
	}
}

function toBase64Url(str) {
	return Buffer.from(str).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function listSendAs() {
	await ensureServices();
	const res = await gmailService.users.settings.sendAs.list({ userId: 'me' });
	return (res.data.sendAs || []).map(s => ({
		email: s.sendAsEmail,
		name: s.displayName || '',
		isPrimary: !!s.isPrimary,
		verificationStatus: s.verificationStatus,
		signature: s.signature || ''
	}));
}

async function getPrimarySignature() {
	await ensureServices();
	const res = await gmailService.users.settings.sendAs.list({ userId: 'me' });
	const list = res.data.sendAs || [];
	const pri = list.find(s => s.isPrimary) || list[0];
	return pri?.signature || '';
}

async function listSheets(sheetId) {
	await ensureServices();
	const meta = await sheetsService.spreadsheets.get({ spreadsheetId: sheetId });
	return (meta.data.sheets || []).map(s => s.properties.title);
}

function columnIndexToA1(n) {
	let s = '';
	while (n >= 0) {
		s = String.fromCharCode((n % 26) + 65) + s;
		n = Math.floor(n / 26) - 1;
	}
	return s;
}

async function ensureStatusColumn(sheetId, sheetTitle, headers) {
	let idx = headers.findIndex(h => String(h).trim().toLowerCase() === 'status');
	if (idx === -1) {
		// add Status header at the end
		headers.push('Status');
		const range = `${sheetTitle}!A1:${columnIndexToA1(headers.length - 1)}1`;
		try {
			await sheetsService.spreadsheets.values.update({
				spreadsheetId: sheetId,
				range,
				valueInputOption: 'RAW',
				requestBody: { values: [headers] }
			});
			idx = headers.length - 1;
		} catch (e) {
			logEvent('error', 'Failed to ensure Status column (insufficient scope?)', { error: e.message, sheetId, sheetTitle, range });
			return -1; // signal we cannot write
		}
	}
	return idx;
}

async function updateSheetStatus(sheetId, sheetTitle, headers, rowIndexZeroBased, statusText) {
	await ensureServices();
	// Resolve sheetTitle if missing
	let title = sheetTitle;
	if (!title) {
		const meta = await sheetsService.spreadsheets.get({ spreadsheetId: sheetId });
		title = meta.data.sheets?.[0]?.properties?.title || 'Sheet1';
	}
	const col = await ensureStatusColumn(sheetId, title, headers);
	const a1col = columnIndexToA1(col);
	const rowA1 = rowIndexZeroBased + 2; // +1 header, +1 1-indexed
	const range = `${title}!${a1col}${rowA1}`;
	try {
		await sheetsService.spreadsheets.values.update({
			spreadsheetId: sheetId,
			range,
			valueInputOption: 'RAW',
			requestBody: { values: [[statusText]] }
		});
		return { success: true };
	} catch (error) {
		logEvent('error', 'Sheets status update failed', { error: error.message, sheetId, title, range });
		return { success: false, error: error.message };
	}
}

// App logging
const appLogsDir = path.join(__dirname, '../logs');
if (!fs.existsSync(appLogsDir)) { try { fs.mkdirSync(appLogsDir, { recursive: true }); } catch (_) {} }
const sessionLogFile = path.join(appLogsDir, `session-${new Date().toISOString().replace(/[:.]/g,'-')}.log`);

function logEvent(level, message, meta) {
	try {
		const line = JSON.stringify({ ts: new Date().toISOString(), level, message, meta: meta || null }) + os.EOL;
		fs.appendFileSync(sessionLogFile, line);
		if (mainWindow && mainWindow.webContents) {
			mainWindow.webContents.send('app-log', { level, message, meta, ts: Date.now() });
		}
	} catch (e) {
		// swallow
	}
}

// Global error handlers with guidance
process.on('uncaughtException', (err) => {
	logEvent('error', 'uncaught-exception', { error: err.message, stack: err.stack });
	showPlatformGuidance('An unexpected error occurred', err);
});
process.on('unhandledRejection', (reason) => {
	const msg = (reason && reason.message) ? reason.message : String(reason);
	logEvent('error', 'unhandled-rejection', { error: msg });
	showPlatformGuidance('An unexpected error occurred', { message: msg });
});

function showPlatformGuidance(title, err) {
	try {
		const isWin = process.platform === 'win32';
		const isMac = process.platform === 'darwin';
		let message = `${err?.message || ''}`;
		message += `\n\nTroubleshooting steps:`;
		if (isWin) {
			message += `\n- If Windows Defender SmartScreen blocks the app, click More info > Run anyway.`;
			message += `\n- If you see permission issues, try running the installer as Administrator.`;
			message += `\n- Ensure your firewall or proxy allows the app to access the Internet.`;
		}
		if (isMac) {
			message += `\n- If macOS says the app is from an unidentified developer, right-click the app and click Open.`;
			message += `\n- In System Settings > Privacy & Security, allow the app to run if it was blocked.`;
			message += `\n- Ensure the app has network access and try again.`;
		}
		message += `\n- Check the in-app Logs panel for more details.`;
		dialog.showMessageBoxSync({ type: 'error', title, message });
	} catch (_) {}
}

ipcMain.handle('app-log-append', async (e, payload) => { logEvent(payload?.level || 'info', payload?.message || '', payload?.meta || null); return true; });
ipcMain.handle('app-log-read', async () => {
	try {
		const content = fs.existsSync(sessionLogFile) ? fs.readFileSync(sessionLogFile, 'utf8') : '';
		return { success: true, content };
	} catch (e) { return { success: false, error: e.message }; }
});

// Telemetry IPC (renderer optional)
ipcMain.handle('telemetry-track', async (e, args) => { try { trackTelemetry(args?.event || 'event', args?.meta || null); return { success: true }; } catch (error) { return { success: false, error: error.message }; } });

// Auto-update wiring
function initAutoUpdater() {
	try {
		if (isDev) { logEvent('info', 'AutoUpdater disabled in development'); return; }
		autoUpdater = require('electron-updater').autoUpdater;
		autoUpdater.autoDownload = false;
		// Forward events to renderer
		autoUpdater.on('checking-for-update', () => { if (mainWindow) mainWindow.webContents.send('update-status', { status: 'checking' }); });
		autoUpdater.on('update-available', (info) => {
			trackTelemetry('update_available', { version: info?.version });
			if (mainWindow) mainWindow.webContents.send('update-status', { status: 'available', info });
			dialog.showMessageBox(mainWindow, {
				type: 'info',
				title: 'Update Available',
				message: `A new version (${info?.version}) is available. Download now?`,
				buttons: ['Download', 'Later']
			}).then(res => { if (res.response === 0) autoUpdater.downloadUpdate(); });
		});
		autoUpdater.on('update-not-available', (info) => { if (mainWindow) mainWindow.webContents.send('update-status', { status: 'none', info }); });
		autoUpdater.on('error', (err) => { logEvent('error', 'auto-updater-error', { error: err?.message }); if (mainWindow) mainWindow.webContents.send('update-status', { status: 'error', error: err?.message }); });
		autoUpdater.on('download-progress', (progress) => { if (mainWindow) mainWindow.webContents.send('update-status', { status: 'downloading', progress }); });
		autoUpdater.on('update-downloaded', (info) => {
			trackTelemetry('update_downloaded', { version: info?.version });
			if (mainWindow) mainWindow.webContents.send('update-status', { status: 'downloaded', info });
			dialog.showMessageBox(mainWindow, {
				type: 'info', title: 'Update Ready', message: 'The update has been downloaded. Install and restart now?', buttons: ['Install', 'Later']
			}).then(res => { if (res.response === 0) autoUpdater.quitAndInstall(); });
		});
		// Trigger initial check shortly after ready
		setTimeout(() => { try { autoUpdater.checkForUpdates(); } catch (_) {} }, 5000);
	} catch (e) {
		logEvent('error', 'auto-updater-init-failed', { error: e.message });
	}
}

ipcMain.handle('update-check', async () => { try { if (!autoUpdater) initAutoUpdater(); await autoUpdater.checkForUpdates(); return { success: true }; } catch (e) { return { success: false, error: e.message }; } });
ipcMain.handle('update-download', async () => { try { if (!autoUpdater) initAutoUpdater(); await autoUpdater.downloadUpdate(); return { success: true }; } catch (e) { return { success: false, error: e.message }; } });
ipcMain.handle('update-quit-and-install', async () => { try { if (!autoUpdater) initAutoUpdater(); autoUpdater.quitAndInstall(); return { success: true }; } catch (e) { return { success: false, error: e.message }; } });

// Local spreadsheet loader
ipcMain.handle('load-local-spreadsheet', async (e, filePath) => {
	try {
		await ensureServices().catch(() => {});
		const XLSX = require('xlsx');
		const wb = XLSX.readFile(filePath);
		const sheetName = wb.SheetNames[0];
		const ws = wb.Sheets[sheetName];
		const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
		if (!rows || !rows.length) throw new Error('No data in spreadsheet');
		const headers = rows[0];
		const body = rows.slice(1);
		logEvent('info', 'Loaded local spreadsheet', { filePath, rows: body.length, headers: headers.length });
		return { success: true, data: { headers, rows: body } };
	} catch (error) {
		logEvent('error', 'Local spreadsheet load failed', { error: error.message, filePath });
		return { success: false, error: error.message };
	}
});

function buildRawEmail({ from, to, subject, text, html, attachments }) {
	const boundary = 'mixed_' + Math.random().toString(36).slice(2);
	const wrap76 = (b64) => b64.replace(/.{1,76}/g, (m) => m + '\r\n');
	let headers = [];
	if (from) headers.push(`From: ${from}`);
	headers.push(`To: ${to}`);
	headers.push(`Subject: ${subject}`);
	headers.push('MIME-Version: 1.0');
	if (attachments && attachments.length) {
		headers.push(`Content-Type: multipart/mixed; boundary="${boundary}"`);
		let body = '';
		// text part
		body += `--${boundary}\r\n`;
		body += `Content-Type: text/plain; charset="UTF-8"\r\n`;
		body += `Content-Transfer-Encoding: 7bit\r\n\r\n`;
		body += (text || '') + `\r\n`;
		// attachments
		for (const p of attachments) {
			try {
				const data = fs.readFileSync(p);
				const filename = path.basename(p);
				const ctype = mime.lookup(filename) || 'application/octet-stream';
				body += `--${boundary}\r\n`;
				body += `Content-Type: ${ctype}; name="${filename}"\r\n`;
				body += `Content-Transfer-Encoding: base64\r\n`;
				body += `Content-Disposition: attachment; filename="${filename}"\r\n\r\n`;
				body += wrap76(data.toString('base64')) + `\r\n`;
			} catch (e) {
				logEvent('error', 'Attachment read failed', { path: p, error: e.message });
			}
		}
		body += `--${boundary}--\r\n`;
		return headers.join('\r\n') + '\r\n\r\n' + body;
	}
	// no attachments
	headers.push('Content-Type: text/plain; charset="UTF-8"');
	headers.push('Content-Transfer-Encoding: 7bit');
	return headers.join('\r\n') + '\r\n\r\n' + (text || '');
}

async function sendTestEmail(emailData) {
	try {
		await ensureServices();
		logEvent('info', 'Sending test email', { to: emailData.to, attachments: (emailData.attachmentsPaths || []).length });
		const rawStr = buildRawEmail({
			from: emailData.from,
			to: emailData.to,
			subject: emailData.subject,
			text: emailData.content,
			attachments: emailData.attachmentsPaths || []
		});
		const res = await gmailService.users.messages.send({ userId: 'me', requestBody: { raw: toBase64Url(rawStr) } });
		logEvent('info', 'Test email sent', { to: emailData.to, id: res.data.id });
		trackTelemetry('test_email_sent', { hasAttachments: (emailData.attachmentsPaths || []).length > 0 });
		return { success: true, messageId: res.data.id };
	} catch (error) {
		console.error('Email sending error:', error);
		logEvent('error', 'Email sending error', { error: error.message, to: emailData?.to });
		trackTelemetry('email_send_error', { error: error.message });
		return { success: false, error: error.message };
	}
}

async function sendEmail(emailData) {
	try {
		await ensureServices();
		logEvent('info', 'Sending email', { to: emailData.to, attachments: (emailData.attachmentsPaths || []).length });
		const rawStr = buildRawEmail({
			from: emailData.from,
			to: emailData.to,
			subject: emailData.subject,
			text: emailData.content,
			attachments: emailData.attachmentsPaths || []
		});
		const res = await gmailService.users.messages.send({ userId: 'me', requestBody: { raw: toBase64Url(rawStr) } });
		logEvent('info', 'Email sent', { to: emailData.to, id: res.data.id });
		trackTelemetry('email_sent', { hasAttachments: (emailData.attachmentsPaths || []).length > 0 });
		return { success: true, messageId: res.data.id };
	} catch (error) {
		console.error('Email sending error:', error);
		logEvent('error', 'Email sending error', { error: error.message, to: emailData?.to });
		trackTelemetry('email_send_error', { error: error.message });
		return { success: false, error: error.message };
	}
}

function findEmailColumnIndex(headers) {
	if (!headers) return -1;
	const lower = headers.map(h => String(h).toLowerCase());
	let idx = lower.findIndex(h => h.includes('email'));
	return idx;
}

function renderWithRow(content, headers, row, signature) {
	let out = content;
	headers.forEach((h, i) => {
		const key = String(h).trim();
		const re = new RegExp(`\\(\\(${key.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')}\\)\\)`, 'g');
		out = out.replace(re, row[i] != null ? String(row[i]) : '');
	});
	if (signature) out = out + '\n\n' + signature.replace(/<[^>]+>/g, '');
	return out;
}

async function executeCampaignRun(params) {
	await ensureServices();
	const { sheetId, sheetTitle, subject, content, from, attachmentsPaths, delaySeconds, useSignature } = params;
	const range = sheetTitle ? `${sheetTitle}!A:Z` : 'A:Z';
	const res = await sheetsService.spreadsheets.values.get({ spreadsheetId: sheetId, range });
	const values = res.data.values || [];
	if (!values.length) throw new Error('No data found in sheet');
	const headers = values[0];
	const rows = values.slice(1);
	const emailIdx = findEmailColumnIndex(headers);
	if (emailIdx < 0) throw new Error('No Email column found');
	const signature = useSignature ? await getPrimarySignature() : '';
	for (let i = 0; i < rows.length; i++) {
		const row = rows[i];
		const to = row[emailIdx];
		if (!to) continue;
		const text = renderWithRow(content, headers, row, signature);
		const rawStr = buildRawEmail({ from, to, subject, text, attachments: attachmentsPaths || [] });
		await gmailService.users.messages.send({ userId: 'me', requestBody: { raw: toBase64Url(rawStr) } });
		try {
			await updateSheetStatus(sheetId, sheetTitle || 'Sheet1', headers, i, 'SENT');
		} catch (_) {}
		const jitter = Math.floor(Math.random() * 2000);
		await new Promise(r => setTimeout(r, (delaySeconds || 5) * 1000 + jitter));
	}
	trackTelemetry('campaign_run', { recipients: rows.length });
}

function scheduleOneTimeCampaign(params) {
	const id = 'job_' + Date.now() + '_' + Math.random().toString(36).slice(2);
	const startAt = new Date(params.startAt).getTime();
	const now = Date.now();
	const ms = Math.max(0, startAt - now);
	const timer = setTimeout(async () => {
		try { await executeCampaignRun(params); } catch (e) { console.error('Scheduled run failed:', e); logEvent('error', 'Scheduled run failed', { error: e.message }); }
		finally { getJobsMap().delete(id); }
	}, ms);
	getJobsMap().set(id, { id, type: 'one-time', startAt, params, timer });
	trackTelemetry('campaign_scheduled', { startAt });
	return { id, startAt };
}

function listScheduledJobs() {
	const jobs = getJobsMap();
	return Array.from(jobs.values()).map(j => ({ id: j.id, type: j.type, startAt: j.startAt, sheetId: j.params?.sheetId, subject: j.params?.subject }));
}

function cancelScheduledJob(id) {
	const jobs = getJobsMap();
	const job = jobs.get(id);
	if (!job) return false;
	clearTimeout(job.timer);
	jobs.delete(id);
	return true;
}

// IPC Handlers
ipcMain.handle('authenticateGoogle', async (event, credentialsData) => authenticateGoogle(credentialsData));
ipcMain.handle('initializeGmailService', async () => initializeGmailService());
ipcMain.handle('initializeSheetsService', async () => initializeSheetsService());
ipcMain.handle('connectToSheets', async (event, payload) => connectToSheets(payload));
ipcMain.handle('sendTestEmail', async (event, emailData) => sendTestEmail(emailData));
ipcMain.handle('sendEmail', async (event, emailData) => sendEmail(emailData));
ipcMain.handle('gmail-list-send-as', async () => listSendAs());
ipcMain.handle('gmail-get-signature', async () => getPrimarySignature());
ipcMain.handle('sheets-list-tabs', async (e, sheetId) => listSheets(sheetId));
ipcMain.handle('sheets-update-status', async (e, args) => updateSheetStatus(args.sheetId, args.sheetTitle, args.headers, args.rowIndexZeroBased, args.status));
ipcMain.handle('show-open-dialog', async (e, options) => dialog.showOpenDialog(mainWindow, options));
ipcMain.handle('show-save-dialog', async (e, options) => dialog.showSaveDialog(mainWindow, options));
ipcMain.handle('show-message-box', async (e, options) => dialog.showMessageBox(mainWindow, options));

ipcMain.handle('write-file', async (e, args) => {
	try { await fs.promises.writeFile(args.path, args.content, 'utf8'); return { success: true }; }
	catch (error) { logEvent('error', 'Write file failed', { error: error.message, path: args.path }); return { success: false, error: error.message }; }
});

ipcMain.handle('read-json-file', async (e, filePath) => {
	try { const txt = await fs.promises.readFile(filePath, 'utf8'); const obj = JSON.parse(txt); return { success: true, data: obj }; }
	catch (error) { logEvent('error', 'Read JSON failed', { error: error.message, path: filePath }); return { success: false, error: error.message }; }
});

ipcMain.handle('schedule-campaign-one-time', async (e, params) => scheduleOneTimeCampaign(params));
ipcMain.handle('schedule-list', async () => listScheduledJobs());
ipcMain.handle('schedule-cancel', async (e, id) => cancelScheduledJob(id));

// Store handlers
ipcMain.handle('storeGet', async (event, key) => store.get(key));
ipcMain.handle('storeSet', async (event, key, value) => { store.set(key, value); return true; });
ipcMain.handle('storeDelete', async (event, key) => { store.delete(key); return true; });

// Template management under user data
function getTemplatesDir() {
	const dir = path.join(app.getPath('userData'), 'templates');
	try { fs.mkdirSync(dir, { recursive: true }); } catch (_) {}
	return dir;
}
function sanitizeName(name) {
	return String(name || 'template').replace(/[^a-z0-9-_]+/gi, '_').slice(0, 80);
}
ipcMain.handle('templates-list', async () => {
	const dir = getTemplatesDir();
	const files = fs.readdirSync(dir).filter(f => f.toLowerCase().endsWith('.json'));
	return files.map(f => ({ id: path.join(dir, f), name: path.basename(f, '.json'), path: path.join(dir, f) }));
});
ipcMain.handle('templates-save', async (e, args) => {
	try {
		const dir = getTemplatesDir();
		const fname = sanitizeName(args.name) + '.json';
		const fpath = path.join(dir, fname);
		await fs.promises.writeFile(fpath, JSON.stringify(args.data || {}, null, 2), 'utf8');
		return { success: true, path: fpath };
	} catch (error) {
		logEvent('error', 'Template save failed', { error: error.message });
		return { success: false, error: error.message };
	}
});
ipcMain.handle('templates-load', async (e, fpath) => {
	try {
		const txt = await fs.promises.readFile(fpath, 'utf8');
		return { success: true, data: JSON.parse(txt) };
	} catch (error) {
		logEvent('error', 'Template load failed', { error: error.message, path: fpath });
		return { success: false, error: error.message };
	}
});
ipcMain.handle('templates-delete', async (e, fpath) => {
	try { await fs.promises.unlink(fpath); return { success: true }; }
	catch (error) { return { success: false, error: error.message }; }
});

// App info handlers for preload
ipcMain.handle('get-app-version', async () => app.getVersion());
ipcMain.handle('get-app-name', async () => app.getName());

app.whenReady().then(() => {
	try { createWindow(); } catch (e) { logEvent('error', 'createWindow-failed', { error: e.message }); }
	startTelemetry();
	initAutoUpdater();
});
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
app.on('before-quit', () => { if (mainWindow && mainWindow.webContents) mainWindow.webContents.send('app-quitting'); try { flushTelemetry(); } catch (_) {} }); 