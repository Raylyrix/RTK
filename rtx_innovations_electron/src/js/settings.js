// Settings Manager
class SettingsManager {
    constructor() {
        this.settings = {};
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        console.log('⚙️ Settings manager initialized');
    }

    setupEventListeners() {
        // Settings change handlers
        const enableAnimations = document.getElementById('enableAnimations');
        if (enableAnimations) {
            enableAnimations.addEventListener('change', (e) => {
                this.updateSetting('enableAnimations', e.target.checked);
            });
        }

        const enableNotifications = document.getElementById('enableNotifications');
        if (enableNotifications) {
            enableNotifications.addEventListener('change', (e) => {
                this.updateSetting('enableNotifications', e.target.checked);
            });
        }
    }

    updateSetting(key, value) {
        this.settings[key] = value;
        this.saveSettings();
        this.showSuccess('Setting updated');
    }

    saveSettings() {
        if (window.electronAPI) {
            window.electronAPI.storeSet('user-settings', this.settings);
        }
    }

    loadSettings() {
        if (window.electronAPI) {
            window.electronAPI.storeGet('user-settings').then(settings => {
                if (settings) {
                    this.settings = settings;
                    this.applySettings();
                }
            });
        }
    }

    applySettings() {
        // Apply animation setting
        const enableAnimations = document.getElementById('enableAnimations');
        if (enableAnimations && this.settings.enableAnimations !== undefined) {
            enableAnimations.checked = this.settings.enableAnimations;
        }

        // Apply notification setting
        const enableNotifications = document.getElementById('enableNotifications');
        if (enableNotifications && this.settings.enableNotifications !== undefined) {
            enableNotifications.checked = this.settings.enableNotifications;
        }
    }

    showSuccess(message) {
        if (window.rtxApp) {
            window.rtxApp.showSuccess(message);
        }
    }
}

window.settingsManager = new SettingsManager(); 