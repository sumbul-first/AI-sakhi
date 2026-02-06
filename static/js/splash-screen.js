/**
 * AI Sakhi Splash Screen
 * Shows mother-daughter logo with brand messaging on app load
 */

class SplashScreen {
    constructor(options = {}) {
        this.duration = options.duration || 3000;
        this.showOnce = options.showOnce !== false;
        this.storageKey = 'ai_sakhi_splash_shown';
        
        this.init();
    }
    
    /**
     * Initialize splash screen
     */
    init() {
        // Check if splash should be shown
        if (this.showOnce && this.hasBeenShown()) {
            return;
        }
        
        this.createSplashScreen();
        this.showSplash();
        
        // Mark as shown
        if (this.showOnce) {
            this.markAsShown();
        }
    }
    
    /**
     * Create splash screen HTML
     */
    createSplashScreen() {
        const splash = document.createElement('div');
        splash.id = 'ai-sakhi-splash';
        splash.className = 'splash-screen';
        splash.innerHTML = `
            <img src="/static/images/ai-sakhi-logo.svg" 
                 alt="AI Sakhi Logo" 
                 class="splash-logo">
            <h1 class="splash-tagline">आपकी सखी, आपके साथ</h1>
            <p class="splash-subtitle">Voice-First Health Companion</p>
            <div class="loading-spinner"></div>
        `;
        
        document.body.appendChild(splash);
    }
    
    /**
     * Show splash screen
     */
    showSplash() {
        const splash = document.getElementById('ai-sakhi-splash');
        if (!splash) return;
        
        // Prevent scrolling while splash is visible
        document.body.style.overflow = 'hidden';
        
        // Auto-hide after duration
        setTimeout(() => {
            this.hideSplash();
        }, this.duration);
    }
    
    /**
     * Hide splash screen
     */
    hideSplash() {
        const splash = document.getElementById('ai-sakhi-splash');
        if (!splash) return;
        
        splash.style.animation = 'fadeOut 0.5s ease forwards';
        
        setTimeout(() => {
            splash.remove();
            document.body.style.overflow = '';
        }, 500);
    }
    
    /**
     * Check if splash has been shown
     */
    hasBeenShown() {
        try {
            return sessionStorage.getItem(this.storageKey) === 'true';
        } catch (e) {
            return false;
        }
    }
    
    /**
     * Mark splash as shown
     */
    markAsShown() {
        try {
            sessionStorage.setItem(this.storageKey, 'true');
        } catch (e) {
            console.warn('Could not save splash screen state');
        }
    }
}

// Initialize splash screen on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Only show splash on home page
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        new SplashScreen({
            duration: 3000,
            showOnce: true
        });
    }
});

// Export for global access
window.SplashScreen = SplashScreen;