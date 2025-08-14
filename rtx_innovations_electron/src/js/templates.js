// Templates Manager
class TemplateManager {
    constructor() {
        this.templates = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('📄 Template manager initialized');
    }

    setupEventListeners() {
        const newTemplateBtn = document.getElementById('newTemplateBtn');
        if (newTemplateBtn) {
            newTemplateBtn.addEventListener('click', () => this.createTemplate());
        }

        const importTemplateBtn = document.getElementById('importTemplateBtn');
        if (importTemplateBtn) {
            importTemplateBtn.addEventListener('click', () => this.importTemplate());
        }
    }

    createTemplate() {
        this.showSuccess('Create template dialog opened');
    }

    importTemplate() {
        this.showSuccess('Import template dialog opened');
    }

    showSuccess(message) {
        if (window.rtxApp) {
            window.rtxApp.showSuccess(message);
        }
    }
}

window.templateManager = new TemplateManager(); 