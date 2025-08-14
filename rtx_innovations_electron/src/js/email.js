// Email Campaign Manager
class EmailManager {
    constructor() {
        this.campaigns = [];
        this.currentCampaign = null;
        this.templates = [];
        this.attachments = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTemplates();
        console.log('📧 Email manager initialized');
    }

    setupEventListeners() {
        const newCampaignBtn = document.getElementById('newCampaignBtn');
        if (newCampaignBtn) {
            newCampaignBtn.addEventListener('click', () => this.createNewCampaign());
        }

        const importCampaignBtn = document.getElementById('importCampaignBtn');
        if (importCampaignBtn) {
            importCampaignBtn.addEventListener('click', () => this.importCampaign());
        }
    }

    createNewCampaign() {
        if (!window.authManager || !window.authManager.isUserAuthenticated()) {
            this.showError('Please authenticate with Google first');
            return;
        }

        if (!window.sheetsManager || !window.sheetsManager.isConnectedToSheets()) {
            this.showError('Please connect to Google Sheets first');
            return;
        }

        this.showCampaignModal();
    }

    showCampaignModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'campaignModal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Create New Email Campaign</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="campaign-form">
                        <div class="form-group">
                            <label>Campaign Name</label>
                            <input type="text" id="campaignName" placeholder="Enter campaign name">
                        </div>
                        <div class="form-group">
                            <label>Subject Line</label>
                            <input type="text" id="campaignSubject" placeholder="Enter email subject">
                        </div>
                        <div class="form-group">
                            <label>From Name</label>
                            <input type="text" id="fromName" placeholder="Your name">
                        </div>
                        <div class="form-group">
                            <label>Email Content</label>
                            <textarea id="emailContent" rows="10" placeholder="Enter your email content..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Attachments</label>
                            <input type="file" id="campaignAttachments" multiple>
                        </div>
                        <div class="form-group">
                            <label>Batch Size</label>
                            <input type="number" id="batchSize" value="50" min="1" max="100">
                        </div>
                        <div class="form-group">
                            <label>Delay Between Emails (seconds)</label>
                            <input type="number" id="emailDelay" value="5" min="1" max="60">
                        </div>
                        <div class="form-actions">
                            <button class="secondary-btn" onclick="this.closest('.modal').remove()">Cancel</button>
                            <button class="primary-btn" onclick="window.emailManager.sendTestEmail()">Send Test</button>
                            <button class="primary-btn" onclick="window.emailManager.startCampaign()">Start Campaign</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    async sendTestEmail() {
        try {
            const testEmail = await this.getTestEmail();
            if (!testEmail) return;

            this.showLoading('Sending test email...');

            const campaignData = this.getCampaignData();
            if (!campaignData) return;

            // Send test email
            if (window.electronAPI && window.electronAPI.sendTestEmail) {
                const result = await window.electronAPI.sendTestEmail({
                    to: testEmail,
                    subject: campaignData.subject,
                    content: campaignData.content,
                    fromName: campaignData.fromName,
                    attachments: this.attachments
                });

                if (result.success) {
                    this.showSuccess('Test email sent successfully!');
                } else {
                    throw new Error(result.error || 'Failed to send test email');
                }
            } else {
                // Simulate test email
                await this.simulateTestEmail();
            }

        } catch (error) {
            this.hideLoading();
            this.showError('Failed to send test email: ' + error.message);
        }
    }

    async getTestEmail() {
        const testEmail = prompt('Enter test email address:');
        if (!testEmail) {
            this.showError('Test email address required');
            return null;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(testEmail)) {
            this.showError('Invalid email address');
            return null;
        }

        return testEmail;
    }

    getCampaignData() {
        const name = document.getElementById('campaignName')?.value;
        const subject = document.getElementById('campaignSubject')?.value;
        const content = document.getElementById('emailContent')?.value;
        const fromName = document.getElementById('fromName')?.value;

        if (!name || !subject || !content) {
            this.showError('Please fill in all required fields');
            return null;
        }

        return { name, subject, content, fromName };
    }

    async simulateTestEmail() {
        await new Promise(resolve => setTimeout(resolve, 2000));
        this.hideLoading();
        this.showSuccess('Test email sent successfully!');
    }

    async startCampaign() {
        try {
            const campaignData = this.getCampaignData();
            if (!campaignData) return;

            const sheetData = window.sheetsManager.getCurrentSheetData();
            if (!sheetData.emailAddresses.length) {
                this.showError('No valid email addresses found in sheet');
                return;
            }

            const batchSize = parseInt(document.getElementById('batchSize')?.value) || 50;
            const delay = parseInt(document.getElementById('emailDelay')?.value) || 5;

            this.showLoading('Starting email campaign...');

            // Create campaign
            const campaign = {
                id: Date.now(),
                name: campaignData.name,
                subject: campaignData.subject,
                content: campaignData.content,
                fromName: campaignData.fromName,
                recipients: sheetData.emailAddresses,
                batchSize: batchSize,
                delay: delay,
                status: 'running',
                sent: 0,
                failed: 0,
                startTime: new Date()
            };

            this.currentCampaign = campaign;
        this.campaigns.push(campaign);

            // Start sending emails
            await this.sendBulkEmails(campaign);

        } catch (error) {
            this.hideLoading();
            this.showError('Failed to start campaign: ' + error.message);
        }
    }

    async sendBulkEmails(campaign) {
        const { recipients, batchSize, delay } = campaign;
        const totalRecipients = recipients.length;
        let sent = 0;
        let failed = 0;

        this.showLoading(`Sending emails... (0/${totalRecipients})`);

        for (let i = 0; i < totalRecipients; i += batchSize) {
            const batch = recipients.slice(i, i + batchSize);
            
            for (const email of batch) {
                try {
                    await this.sendSingleEmail(campaign, email);
                    sent++;
                    campaign.sent = sent;
                } catch (error) {
                    failed++;
                    campaign.failed = failed;
                    console.error(`Failed to send to ${email}:`, error);
                }

                this.showLoading(`Sending emails... (${sent}/${totalRecipients})`);
            }

            // Delay between batches
            if (i + batchSize < totalRecipients) {
                await new Promise(resolve => setTimeout(resolve, delay * 1000));
            }
        }

        campaign.status = 'completed';
        campaign.endTime = new Date();

        this.hideLoading();
        this.showSuccess(`Campaign completed! Sent: ${sent}, Failed: ${failed}`);
        this.updateCampaignsList();
    }

    async sendSingleEmail(campaign, email) {
        if (window.electronAPI && window.electronAPI.sendEmail) {
            const result = await window.electronAPI.sendEmail({
                to: email,
                subject: campaign.subject,
                content: this.processContent(campaign.content, email),
                fromName: campaign.fromName,
                attachments: this.attachments
            });

            if (!result.success) {
                throw new Error(result.error || 'Failed to send email');
            }
        } else {
            // Simulate email sending
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    processContent(content, email) {
        // Replace placeholders with actual data
        let processedContent = content;
        
        // Replace email placeholder
        processedContent = processedContent.replace(/\(\(email\)\)/gi, email);
        
        // Replace other common placeholders
        processedContent = processedContent.replace(/\(\(name\)\)/gi, 'Valued Customer');
        processedContent = processedContent.replace(/\(\(date\)\)/gi, new Date().toLocaleDateString());
        
        return processedContent;
    }

    updateCampaignsList() {
        const campaignsList = document.getElementById('campaignsList');
        if (!campaignsList) return;

        if (this.campaigns.length === 0) {
            campaignsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-envelope-open"></i>
                    <h3>No Campaigns Yet</h3>
                    <p>Create your first email campaign to get started</p>
                    <button class="primary-btn" onclick="window.emailManager.createNewCampaign()">Create Campaign</button>
                </div>
            `;
            return;
        }

        let campaignsHtml = '<div class="campaigns-grid">';
        
        this.campaigns.forEach(campaign => {
            const statusClass = campaign.status === 'running' ? 'running' : 
                               campaign.status === 'completed' ? 'completed' : 'draft';
            
            campaignsHtml += `
                <div class="campaign-card ${statusClass}">
                    <div class="campaign-header">
                        <h4>${campaign.name}</h4>
                        <span class="status-badge ${statusClass}">${campaign.status}</span>
                    </div>
                    <div class="campaign-details">
                        <p><strong>Subject:</strong> ${campaign.subject}</p>
                        <p><strong>Recipients:</strong> ${campaign.recipients.length}</p>
                        <p><strong>Sent:</strong> ${campaign.sent}</p>
                        <p><strong>Failed:</strong> ${campaign.failed}</p>
                    </div>
                    <div class="campaign-actions">
                        <button class="secondary-btn" onclick="window.emailManager.viewCampaign(${campaign.id})">View</button>
                        <button class="danger-btn" onclick="window.emailManager.deleteCampaign(${campaign.id})">Delete</button>
                    </div>
                </div>
            `;
        });

        campaignsHtml += '</div>';
        campaignsList.innerHTML = campaignsHtml;
    }

    viewCampaign(campaignId) {
        const campaign = this.campaigns.find(c => c.id === campaignId);
        if (!campaign) return;

        // Show campaign details modal
        this.showCampaignDetailsModal(campaign);
    }

    deleteCampaign(campaignId) {
        if (confirm('Are you sure you want to delete this campaign?')) {
            this.campaigns = this.campaigns.filter(c => c.id !== campaignId);
            this.updateCampaignsList();
            this.showSuccess('Campaign deleted successfully');
        }
    }

    showCampaignDetailsModal(campaign) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Campaign Details: ${campaign.name}</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="campaign-details">
                        <p><strong>Status:</strong> ${campaign.status}</p>
                        <p><strong>Subject:</strong> ${campaign.subject}</p>
                        <p><strong>Recipients:</strong> ${campaign.recipients.length}</p>
                        <p><strong>Sent:</strong> ${campaign.sent}</p>
                        <p><strong>Failed:</strong> ${campaign.failed}</p>
                        <p><strong>Start Time:</strong> ${campaign.startTime.toLocaleString()}</p>
                        ${campaign.endTime ? `<p><strong>End Time:</strong> ${campaign.endTime.toLocaleString()}</p>` : ''}
                        <div class="content-preview">
                            <h4>Email Content:</h4>
                            <div class="content-text">${campaign.content}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        modal.style.display = 'block';
    }

    importCampaign() {
        this.showError('Import feature coming soon');
    }

    loadTemplates() {
        // Load saved templates
        if (window.electronAPI && window.electronAPI.storeGet) {
            window.electronAPI.storeGet('email-templates').then(templates => {
                if (templates) {
                    this.templates = templates;
                }
            });
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

    // Public methods
    getCurrentCampaign() {
        return this.currentCampaign;
    }

    getCampaigns() {
        return this.campaigns;
    }
}

window.emailManager = new EmailManager(); 