// Google Authentication Manager
class GoogleAuthManager {
    constructor() {
        this.isAuthenticated = false;
        this.userEmail = null;
        this.credentials = null;
        this.gmailService = null;
        this.sheetsService = null;
        this.init();
    }

    init() {
        this.loadStoredCredentials();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Google login button
        const googleLoginBtn = document.getElementById('googleLoginBtn');
        if (googleLoginBtn) {
            googleLoginBtn.addEventListener('click', () => this.handleGoogleLogin());
        }

        // Credentials upload
        const uploadBtn = document.getElementById('uploadCredentialsBtn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.handleCredentialsUpload());
        }

        // File input change
        const fileInput = document.getElementById('credentialsFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    async handleGoogleLogin() {
        try {
            this.showLoading('Connecting to Google...');
            
            // Use Electron's dialog to get credentials file
            if (window.electronAPI) {
                const result = await window.electronAPI.showOpenDialog({
                    properties: ['openFile'],
                    filters: [
                        { name: 'JSON Files', extensions: ['json'] },
                        { name: 'All Files', extensions: ['*'] }
                    ],
                    title: 'Select Google API Credentials File'
                });

                if (!result.canceled && result.filePaths.length > 0) {
                    const credentialsPath = result.filePaths[0];
                    await this.authenticateWithCredentials(credentialsPath);
                } else {
                    this.hideLoading();
                    this.showError('No credentials file selected');
                }
            } else {
                // Fallback for web version
                this.showError('Please upload your credentials.json file');
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Login failed: ' + error.message);
        }
    }

    async handleCredentialsUpload() {
        const fileInput = document.getElementById('credentialsFile');
        if (fileInput && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            try {
                this.showLoading('Processing credentials...');
                const credentials = await this.readCredentialsFile(file);
                await this.authenticateWithCredentials(credentials);
            } catch (error) {
                this.hideLoading();
                this.showError('Failed to process credentials: ' + error.message);
            }
        } else {
            this.showError('Please select a credentials file first');
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const uploadBtn = document.getElementById('uploadCredentialsBtn');
            if (uploadBtn) {
                uploadBtn.textContent = `Upload ${file.name}`;
            }
        }
    }

    async readCredentialsFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const credentials = JSON.parse(e.target.result);
                    resolve(credentials);
                } catch (error) {
                    reject(new Error('Invalid JSON file'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    async authenticateWithCredentials(credentials) {
        try {
            // Store credentials
            this.credentials = credentials;
            
            // Use Electron's Google auth if available
            if (window.electronAPI && window.electronAPI.authenticateGoogle) {
                const result = await window.electronAPI.authenticateGoogle(credentials);
                if (result.success) {
                    this.onAuthenticationSuccess(result.userEmail);
                } else {
                    throw new Error(result.error || 'Authentication failed');
                }
            } else {
                // Simulate authentication for demo
                await this.simulateAuthentication();
            }
        } catch (error) {
            throw error;
        }
    }

    async simulateAuthentication() {
        // Simulate the authentication process
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // For demo purposes, use a mock email
        const mockEmail = 'user@example.com';
        this.onAuthenticationSuccess(mockEmail);
    }

    onAuthenticationSuccess(email) {
        this.isAuthenticated = true;
        this.userEmail = email;
        
        // Store authentication state
        this.saveAuthenticationState();
        
        // Update UI
        this.updateAuthenticationUI();
        
        // Hide loading and show success
        this.hideLoading();
        this.showSuccess(`Welcome back, ${email}!`);
        
        // Initialize services
        this.initializeServices();
        
        // Trigger app update
        if (window.rtxApp) {
            window.rtxApp.onLoginSuccess(email);
        }
    }

    updateAuthenticationUI() {
        // Update account display
        const accountName = document.querySelector('.account-name');
        const accountStatus = document.querySelector('.account-status');
        const loginBtn = document.getElementById('loginBtn');

        if (accountName) accountName.textContent = this.userEmail;
        if (accountStatus) accountStatus.textContent = 'Connected';
        
        if (loginBtn) {
            loginBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i>Logout';
            loginBtn.onclick = () => this.logout();
        }

        // Hide login modal
        const modal = document.getElementById('loginModal');
        if (modal) {
            modal.style.display = 'none';
        }

        // Show authenticated content
        this.showAuthenticatedContent();
    }

    showAuthenticatedContent() {
        // Enable features that require authentication
        const sheetsBtn = document.getElementById('connectSheetsBtn');
        if (sheetsBtn) {
            sheetsBtn.disabled = false;
            sheetsBtn.textContent = 'Connect Google Sheets';
        }

        // Update dashboard metrics
        this.updateDashboardMetrics();
    }

    updateDashboardMetrics() {
        // Update dashboard with real data
        const metrics = {
            emailsSent: 0,
            activeCampaigns: 0,
            openRate: '0%',
            scheduledJobs: 0
        };

        // Update cards
        const cards = document.querySelectorAll('.dashboard-card');
        cards.forEach((card, index) => {
            const valueEl = card.querySelector('.card-value');
            if (valueEl) {
                switch (index) {
                    case 0: valueEl.textContent = metrics.emailsSent; break;
                    case 1: valueEl.textContent = metrics.activeCampaigns; break;
                    case 2: valueEl.textContent = metrics.openRate; break;
                    case 3: valueEl.textContent = metrics.scheduledJobs; break;
                }
            }
        });
    }

    async initializeServices() {
        try {
            // Initialize Gmail service
            if (window.electronAPI && window.electronAPI.initializeGmailService) {
                await window.electronAPI.initializeGmailService(this.credentials);
            }

            // Initialize Sheets service
            if (window.electronAPI && window.electronAPI.initializeSheetsService) {
                await window.electronAPI.initializeSheetsService(this.credentials);
            }

            console.log('Services initialized successfully');
        } catch (error) {
            console.error('Failed to initialize services:', error);
        }
    }

    logout() {
        this.isAuthenticated = false;
        this.userEmail = null;
        this.credentials = null;
        
        // Clear stored data
        this.clearAuthenticationState();
        
        // Update UI
        this.updateLogoutUI();
        
        // Show success message
        this.showSuccess('Logged out successfully');
        
        // Trigger app update
        if (window.rtxApp) {
            window.rtxApp.logout();
        }
    }

    updateLogoutUI() {
        // Reset account display
        const accountName = document.querySelector('.account-name');
        const accountStatus = document.querySelector('.account-status');
        const loginBtn = document.getElementById('loginBtn');

        if (accountName) accountName.textContent = 'Not Connected';
        if (accountStatus) accountStatus.textContent = 'Click to login';
        
        if (loginBtn) {
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i>Login';
            loginBtn.onclick = () => this.showLoginModal();
        }

        // Disable authenticated features
        this.disableAuthenticatedFeatures();
    }

    disableAuthenticatedFeatures() {
        // Disable sheets connection
        const sheetsBtn = document.getElementById('connectSheetsBtn');
        if (sheetsBtn) {
            sheetsBtn.disabled = true;
            sheetsBtn.textContent = 'Connect Google Sheets';
        }

        // Reset dashboard
        this.resetDashboard();
    }

    resetDashboard() {
        const cards = document.querySelectorAll('.dashboard-card');
        cards.forEach((card, index) => {
            const valueEl = card.querySelector('.card-value');
            if (valueEl) {
                switch (index) {
                    case 0: valueEl.textContent = '0'; break;
                    case 1: valueEl.textContent = '0'; break;
                    case 2: valueEl.textContent = '0%'; break;
                    case 3: valueEl.textContent = '0'; break;
                }
            }
        });
    }

    showLoginModal() {
        const modal = document.getElementById('loginModal');
        if (modal) {
            modal.style.display = 'block';
        }
    }

    saveAuthenticationState() {
        if (window.electronAPI && window.electronAPI.storeSet) {
            window.electronAPI.storeSet('auth-state', {
                isAuthenticated: this.isAuthenticated,
                userEmail: this.userEmail,
                timestamp: Date.now()
            });
        }
    }

    loadStoredCredentials() {
        if (window.electronAPI && window.electronAPI.storeGet) {
            window.electronAPI.storeGet('auth-state').then(state => {
                if (state && state.isAuthenticated) {
                    // Check if token is still valid (24 hours)
                    const tokenAge = Date.now() - state.timestamp;
                    if (tokenAge < 24 * 60 * 60 * 1000) {
                        this.isAuthenticated = true;
                        this.userEmail = state.userEmail;
                        this.updateAuthenticationUI();
                    } else {
                        this.clearAuthenticationState();
                    }
                }
            });
        }
    }

    clearAuthenticationState() {
        if (window.electronAPI && window.electronAPI.storeDelete) {
            window.electronAPI.storeDelete('auth-state');
        }
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

    // Public methods for other modules
    isUserAuthenticated() {
        return this.isAuthenticated;
    }

    getUserEmail() {
        return this.userEmail;
    }

    getCredentials() {
        return this.credentials;
    }
}

// Initialize authentication manager
window.authManager = new GoogleAuthManager(); 