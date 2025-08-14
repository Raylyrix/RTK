// Batch Management
class BatchManager {
    constructor() {
        this.batches = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        console.log('🏷️ Batch manager initialized');
    }

    setupEventListeners() {
        const createBatchBtn = document.getElementById('createBatchBtn');
        if (createBatchBtn) {
            createBatchBtn.addEventListener('click', () => this.createBatch());
        }

        const editLabelsBtn = document.getElementById('editLabelsBtn');
        if (editLabelsBtn) {
            editLabelsBtn.addEventListener('click', () => this.editLabels());
        }
    }

    createBatch() {
        this.showSuccess('Create batch dialog opened');
    }

    editLabels() {
        this.showSuccess('Edit labels dialog opened');
    }

    showSuccess(message) {
        if (window.rtxApp) {
            window.rtxApp.showSuccess(message);
        }
    }
}

window.batchManager = new BatchManager(); 