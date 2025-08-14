// Google Sheets Integration Manager
class SheetsManager {
    constructor() {
        this.isConnected = false;
        this.currentSheet = null;
        this.sheetData = null;
        this.headers = [];
        this.rows = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('📊 Sheets manager initialized');
    }

    setupEventListeners() {
        const connectBtn = document.getElementById('connectSheetsBtn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.connectToSheets());
        }

        const refreshBtn = document.getElementById('refreshSheetsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }
    }

    async connectToSheets() {
        try {
            if (!window.authManager || !window.authManager.isUserAuthenticated()) {
                this.showError('Please authenticate with Google first');
                return;
            }

            this.showLoading('Connecting to Google Sheets...');
            
            // Get sheet URL from user
            const sheetUrl = await this.getSheetUrl();
            if (!sheetUrl) {
                this.hideLoading();
                return;
            }

            // Extract sheet ID from URL
            const sheetId = this.extractSheetId(sheetUrl);
            if (!sheetId) {
            this.hideLoading();
                this.showError('Invalid Google Sheets URL');
                return;
            }

            // Simulate connection for now
            await this.simulateSheetsConnection(sheetId);

        } catch (error) {
            this.hideLoading();
            this.showError('Failed to connect to Google Sheets: ' + error.message);
        }
    }

    async getSheetUrl() {
        return prompt('Enter your Google Sheets URL:');
    }

    extractSheetId(url) {
        const patterns = [
            /\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
            /key=([a-zA-Z0-9-_]+)/,
            /^([a-zA-Z0-9-_]+)$/
        ];

        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) {
                return match[1];
        }
        }
        return null;
    }

    async simulateSheetsConnection(sheetId) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        const mockData = {
            headers: ['Name', 'Email', 'Company', 'Position', 'Status'],
            rows: [
                ['John Doe', 'john@example.com', 'Acme Corp', 'Manager', 'Active'],
                ['Jane Smith', 'jane@company.com', 'Tech Inc', 'Developer', 'Active'],
                ['Bob Johnson', 'bob@startup.com', 'Startup Co', 'Founder', 'Pending']
            ]
        };

        this.onSheetsConnected(sheetId, mockData);
    }

    onSheetsConnected(sheetId, data) {
        this.isConnected = true;
        this.currentSheet = sheetId;
        this.sheetData = data;
        this.headers = data.headers || [];
        this.rows = data.rows || [];

        this.updateConnectionStatus();
        this.displaySheetData();
        this.enableSheetsFeatures();

        this.hideLoading();
        this.showSuccess('Successfully connected to Google Sheets!');
    }

    updateConnectionStatus() {
        const statusIndicator = document.querySelector('.connection-status .status-indicator');
        const statusText = document.querySelector('.connection-status span');
        const refreshBtn = document.getElementById('refreshSheetsBtn');

        if (statusIndicator) {
            statusIndicator.className = 'status-indicator connected';
        }
        if (statusText) {
            statusText.textContent = 'Connected to Google Sheets';
        }
        if (refreshBtn) {
            refreshBtn.disabled = false;
        }
    }

    displaySheetData() {
        const dataContainer = document.getElementById('sheetsData');
        if (!dataContainer) return;

        dataContainer.style.display = 'block';
        const previewHtml = this.createDataPreview();
        dataContainer.innerHTML = previewHtml;
    }

    createDataPreview() {
        if (!this.headers.length || !this.rows.length) {
            return '<div class="no-data">No data found in sheet</div>';
        }

        let tableHtml = `
            <div class="data-preview">
                <h3>Data Preview (${this.rows.length} rows)</h3>
                <div class="table-container">
                    <table id="dataTable">
                        <thead><tr>
        `;

        this.headers.forEach(header => {
            tableHtml += `<th>${this.escapeHtml(header)}</th>`;
        });

        tableHtml += '</tr></thead><tbody>';

        this.rows.forEach(row => {
            tableHtml += '<tr>';
            this.headers.forEach((header, index) => {
                const value = row[index] || '';
                tableHtml += `<td>${this.escapeHtml(value)}</td>`;
            });
            tableHtml += '</tr>';
        });

        tableHtml += '</tbody></table></div></div>';
        return tableHtml;
    }

    enableSheetsFeatures() {
        const newCampaignBtn = document.getElementById('newCampaignBtn');
        if (newCampaignBtn) {
            newCampaignBtn.disabled = false;
        }
    }

    async refreshData() {
        if (!this.isConnected) {
            this.showError('Not connected to any sheet');
            return;
        }

        try {
            this.showLoading('Refreshing data...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.showSuccess('Data refreshed successfully!');
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to refresh data: ' + error.message);
        }
    }

    findEmailColumn() {
        const emailPatterns = ['email', 'mail', 'e-mail'];
        for (const header of this.headers) {
            if (emailPatterns.some(pattern => 
                header.toLowerCase().includes(pattern))) {
                return header;
            }
        }
        return null;
        }

    getEmailAddresses() {
        const emailColumn = this.findEmailColumn();
        if (!emailColumn) return [];

        const emailIndex = this.headers.indexOf(emailColumn);
        return this.rows
            .map(row => row[emailIndex])
            .filter(email => email && this.isValidEmail(email));
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            const messageEl = overlay.querySelector('p');
            if (messageEl) messageEl.textContent = message;
            overlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    showSuccess(message) {
        if (window.rtxApp) {
            window.rtxApp.showSuccess(message);
        }
    }

    showError(message) {
        if (window.rtxApp) {
            window.rtxApp.showError(message);
        }
    }

    isConnectedToSheets() {
        return this.isConnected;
    }

    getCurrentSheetData() {
        return {
            headers: this.headers,
            rows: this.rows,
            emailAddresses: this.getEmailAddresses()
        };
    }
}

window.sheetsManager = new SheetsManager(); 