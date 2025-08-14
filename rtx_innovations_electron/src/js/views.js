// Views Management
class ViewsManager {
    constructor() {
        this.currentView = 'dashboard';
        this.viewHistory = [];
        this.init();
    }

    init() {
        this.setupViewTransitions();
        console.log('📱 Views manager initialized');
    }

    setupViewTransitions() {
        // Add smooth transitions between views
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.getAttribute('data-view');
                this.navigateToView(view);
            });
        });
    }

    navigateToView(viewName) {
        if (this.currentView === viewName) return;

        // Add to history
        this.viewHistory.push(this.currentView);
        if (this.viewHistory.length > 10) {
            this.viewHistory.shift();
        }

        // Update current view
        this.currentView = viewName;
        
        // Animate transition
        this.animateViewTransition(viewName);
    }

    animateViewTransition(viewName) {
        const currentView = document.querySelector('.view.active');
        const targetView = document.getElementById(viewName);

        if (!currentView || !targetView) return;

        // Fade out current view
        currentView.style.opacity = '0';
        currentView.style.transform = 'translateX(-20px)';

        setTimeout(() => {
            // Hide current view
            currentView.classList.remove('active');
            currentView.style.opacity = '';
            currentView.style.transform = '';

            // Show target view
            targetView.classList.add('active');
            targetView.style.opacity = '0';
            targetView.style.transform = 'translateX(20px)';

            // Fade in target view
            setTimeout(() => {
                targetView.style.opacity = '1';
                targetView.style.transform = 'translateX(0)';
            }, 50);
        }, 200);
    }

    goBack() {
        if (this.viewHistory.length > 0) {
            const previousView = this.viewHistory.pop();
            this.navigateToView(previousView);
        }
    }

    getCurrentView() {
        return this.currentView;
    }

    getViewHistory() {
        return [...this.viewHistory];
    }
}

// Initialize views manager
window.viewsManager = new ViewsManager(); 