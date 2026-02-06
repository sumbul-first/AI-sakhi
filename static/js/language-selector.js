/**
 * Enhanced Language Selector Component for AI Sakhi
 * Supports text and audio labels, mid-session switching, and session state preservation
 */

class LanguageSelector {
    constructor() {
        this.currentLanguage = this.getCurrentLanguage();
        this.supportedLanguages = {
            'hi': {
                name: 'हिंदी',
                englishName: 'Hindi',
                speechCode: 'hi-IN',
                audioLabel: 'हिंदी भाषा चुनें',
                flag: '🇮🇳'
            },
            'en': {
                name: 'English',
                englishName: 'English',
                speechCode: 'en-IN',
                audioLabel: 'Select English language',
                flag: '🇮🇳'
            },
            'bn': {
                name: 'বাংলা',
                englishName: 'Bengali',
                speechCode: 'bn-IN',
                audioLabel: 'বাংলা ভাষা নির্বাচন করুন',
                flag: '🇮🇳'
            },
            'ta': {
                name: 'தமிழ்',
                englishName: 'Tamil',
                speechCode: 'ta-IN',
                audioLabel: 'தமிழ் மொழியைத் தேர்ந்தெடுக்கவும்',
                flag: '🇮🇳'
            },
            'te': {
                name: 'తెలుగు',
                englishName: 'Telugu',
                speechCode: 'te-IN',
                audioLabel: 'తెలుగు భాషను ఎంచుకోండి',
                flag: '🇮🇳'
            },
            'mr': {
                name: 'मराठी',
                englishName: 'Marathi',
                speechCode: 'mr-IN',
                audioLabel: 'मराठी भाषा निवडा',
                flag: '🇮🇳'
            }
        };
        
        this.sessionData = this.loadSessionData();
        this.synthesis = window.speechSynthesis;
        
        this.init();
    }
    
    /**
     * Initialize the language selector
     */
    init() {
        this.createEnhancedSelector();
        this.setupEventListeners();
        this.preserveSessionState();
        
        console.log('Enhanced Language Selector initialized');
    }
    
    /**
     * Create enhanced language selector with audio labels
     */
    createEnhancedSelector() {
        const existingSelector = document.querySelector('.language-selector');
        if (!existingSelector) return;
        
        // Create new enhanced selector
        const enhancedSelector = document.createElement('div');
        enhancedSelector.className = 'enhanced-language-selector';
        enhancedSelector.innerHTML = this.generateSelectorHTML();
        
        // Replace existing selector
        existingSelector.parentNode.replaceChild(enhancedSelector, existingSelector);
        
        // Add CSS styles
        this.addStyles();
    }
    
    /**
     * Generate HTML for enhanced language selector
     */
    generateSelectorHTML() {
        const currentLang = this.supportedLanguages[this.currentLanguage];
        
        return `
            <div class="language-selector-container">
                <button class="language-selector-button" id="languageSelectorButton" 
                        aria-label="Select Language" aria-expanded="false">
                    <span class="current-language">
                        <span class="language-flag">${currentLang.flag}</span>
                        <span class="language-name">${currentLang.name}</span>
                        <span class="language-english">(${currentLang.englishName})</span>
                    </span>
                    <span class="dropdown-arrow">▼</span>
                </button>
                
                <div class="language-dropdown" id="languageDropdown" role="menu">
                    ${this.generateLanguageOptions()}
                </div>
                
                <button class="audio-help-button" id="audioHelpButton" 
                        aria-label="Play audio instructions" title="Audio help">
                    🔊
                </button>
            </div>
        `;
    }
    
    /**
     * Generate language options
     */
    generateLanguageOptions() {
        return Object.entries(this.supportedLanguages).map(([code, lang]) => `
            <div class="language-option ${code === this.currentLanguage ? 'selected' : ''}" 
                 data-language="${code}" role="menuitem" tabindex="0">
                <span class="language-flag">${lang.flag}</span>
                <div class="language-info">
                    <span class="language-name">${lang.name}</span>
                    <span class="language-english">${lang.englishName}</span>
                </div>
                <button class="play-audio-button" data-language="${code}" 
                        aria-label="Play ${lang.englishName} audio" title="Play audio">
                    🔊
                </button>
            </div>
        `).join('');
    }
    
    /**
     * Add CSS styles for enhanced selector
     */
    addStyles() {
        if (document.getElementById('language-selector-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'language-selector-styles';
        styles.textContent = `
            .enhanced-language-selector {
                position: relative;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .language-selector-container {
                position: relative;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .language-selector-button {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #FF69B4;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-family: inherit;
                font-size: 14px;
                min-width: 140px;
            }
            
            .language-selector-button:hover {
                background: rgba(255, 105, 180, 0.1);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(255, 105, 180, 0.2);
            }
            
            .language-selector-button:focus {
                outline: 3px solid #FF69B4;
                outline-offset: 2px;
            }
            
            .current-language {
                display: flex;
                align-items: center;
                gap: 6px;
                flex: 1;
            }
            
            .language-flag {
                font-size: 16px;
            }
            
            .language-name {
                font-weight: 600;
                color: #333;
            }
            
            .language-english {
                font-size: 12px;
                color: #666;
                font-weight: normal;
            }
            
            .dropdown-arrow {
                color: #FF69B4;
                transition: transform 0.3s ease;
            }
            
            .language-selector-button[aria-expanded="true"] .dropdown-arrow {
                transform: rotate(180deg);
            }
            
            .language-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 2px solid #FF69B4;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                max-height: 300px;
                overflow-y: auto;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-10px);
                transition: all 0.3s ease;
            }
            
            .language-dropdown.show {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }
            
            .language-option {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                cursor: pointer;
                transition: background-color 0.2s ease;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .language-option:last-child {
                border-bottom: none;
            }
            
            .language-option:hover {
                background-color: rgba(255, 105, 180, 0.1);
            }
            
            .language-option:focus {
                background-color: rgba(255, 105, 180, 0.2);
                outline: none;
            }
            
            .language-option.selected {
                background-color: rgba(255, 105, 180, 0.15);
                font-weight: 600;
            }
            
            .language-option.selected::after {
                content: '✓';
                color: #FF69B4;
                font-weight: bold;
                margin-left: auto;
            }
            
            .language-info {
                display: flex;
                flex-direction: column;
                flex: 1;
            }
            
            .language-option .language-name {
                font-size: 14px;
                font-weight: 600;
                color: #333;
            }
            
            .language-option .language-english {
                font-size: 12px;
                color: #666;
            }
            
            .play-audio-button {
                background: none;
                border: none;
                cursor: pointer;
                padding: 4px;
                border-radius: 50%;
                transition: background-color 0.2s ease;
                font-size: 14px;
            }
            
            .play-audio-button:hover {
                background-color: rgba(255, 105, 180, 0.2);
            }
            
            .play-audio-button:focus {
                outline: 2px solid #FF69B4;
                outline-offset: 1px;
            }
            
            .audio-help-button {
                background: rgba(255, 105, 180, 0.1);
                border: 2px solid #FF69B4;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .audio-help-button:hover {
                background: rgba(255, 105, 180, 0.2);
                transform: scale(1.1);
            }
            
            .audio-help-button:focus {
                outline: 3px solid #FF69B4;
                outline-offset: 2px;
            }
            
            .language-switching-indicator {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 105, 180, 0.95);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                z-index: 10000;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .language-switching-indicator.show {
                opacity: 1;
                visibility: visible;
            }
            
            @media (max-width: 768px) {
                .language-selector-button {
                    min-width: 120px;
                    font-size: 13px;
                    padding: 6px 10px;
                }
                
                .language-english {
                    display: none;
                }
                
                .language-dropdown {
                    left: -50px;
                    right: -50px;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        const audioHelpButton = document.getElementById('audioHelpButton');
        
        if (button) {
            button.addEventListener('click', () => this.toggleDropdown());
            button.addEventListener('keydown', (e) => this.handleButtonKeydown(e));
        }
        
        if (dropdown) {
            dropdown.addEventListener('click', (e) => this.handleDropdownClick(e));
            dropdown.addEventListener('keydown', (e) => this.handleDropdownKeydown(e));
        }
        
        if (audioHelpButton) {
            audioHelpButton.addEventListener('click', () => this.playAudioHelp());
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.enhanced-language-selector')) {
                this.closeDropdown();
            }
        });
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });
    }
    
    /**
     * Toggle dropdown visibility
     */
    toggleDropdown() {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        
        if (!button || !dropdown) return;
        
        const isOpen = button.getAttribute('aria-expanded') === 'true';
        
        if (isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    /**
     * Open dropdown
     */
    openDropdown() {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        
        if (!button || !dropdown) return;
        
        button.setAttribute('aria-expanded', 'true');
        dropdown.classList.add('show');
        
        // Focus first option
        const firstOption = dropdown.querySelector('.language-option');
        if (firstOption) {
            firstOption.focus();
        }
    }
    
    /**
     * Close dropdown
     */
    closeDropdown() {
        const button = document.getElementById('languageSelectorButton');
        const dropdown = document.getElementById('languageDropdown');
        
        if (!button || !dropdown) return;
        
        button.setAttribute('aria-expanded', 'false');
        dropdown.classList.remove('show');
    }
    
    /**
     * Handle button keydown events
     */
    handleButtonKeydown(e) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
            e.preventDefault();
            this.openDropdown();
        }
    }
    
    /**
     * Handle dropdown click events
     */
    handleDropdownClick(e) {
        const option = e.target.closest('.language-option');
        const audioButton = e.target.closest('.play-audio-button');
        
        if (audioButton) {
            e.stopPropagation();
            const language = audioButton.dataset.language;
            this.playLanguageAudio(language);
        } else if (option) {
            const language = option.dataset.language;
            this.changeLanguage(language);
        }
    }
    
    /**
     * Handle dropdown keydown events
     */
    handleDropdownKeydown(e) {
        const options = Array.from(document.querySelectorAll('.language-option'));
        const currentIndex = options.indexOf(e.target);
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = (currentIndex + 1) % options.length;
                options[nextIndex].focus();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex === 0 ? options.length - 1 : currentIndex - 1;
                options[prevIndex].focus();
                break;
                
            case 'Enter':
            case ' ':
                e.preventDefault();
                const language = e.target.dataset.language;
                this.changeLanguage(language);
                break;
                
            case 'Escape':
                e.preventDefault();
                this.closeDropdown();
                document.getElementById('languageSelectorButton').focus();
                break;
        }
    }
    
    /**
     * Change language with session state preservation
     */
    async changeLanguage(languageCode) {
        if (languageCode === this.currentLanguage) {
            this.closeDropdown();
            return;
        }
        
        console.log('Changing language to:', languageCode);
        
        // Show switching indicator
        this.showSwitchingIndicator(languageCode);
        
        try {
            // Preserve current session state
            await this.preserveSessionState();
            
            // Make language change request
            const response = await fetch(`/language/${languageCode}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    preserve_session: true,
                    session_data: this.sessionData
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Update current language
                this.currentLanguage = languageCode;
                
                // Play confirmation audio
                this.playLanguageChangeConfirmation(languageCode);
                
                // Update UI
                this.updateCurrentLanguageDisplay();
                
                // Close dropdown
                this.closeDropdown();
                
                // Reload page after a short delay to apply new language
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
                
            } else {
                throw new Error(data.message || 'Language change failed');
            }
            
        } catch (error) {
            console.error('Language change error:', error);
            this.showError('Error changing language. Please try again.');
        } finally {
            this.hideSwitchingIndicator();
        }
    }
    
    /**
     * Play audio for specific language
     */
    playLanguageAudio(languageCode) {
        const language = this.supportedLanguages[languageCode];
        if (!language || !this.synthesis) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(language.audioLabel);
        utterance.lang = language.speechCode;
        utterance.rate = 0.8;
        utterance.pitch = 1.0;
        
        // Try to find appropriate voice
        const voices = this.synthesis.getVoices();
        const voice = voices.find(v => v.lang.startsWith(languageCode)) || 
                     voices.find(v => v.lang.startsWith(language.speechCode));
        
        if (voice) {
            utterance.voice = voice;
        }
        
        this.synthesis.speak(utterance);
    }
    
    /**
     * Play audio help
     */
    playAudioHelp() {
        const helpMessages = {
            'hi': 'भाषा बदलने के लिए यहाँ क्लिक करें। आप अपनी पसंदीदा भाषा चुन सकते हैं।',
            'en': 'Click here to change language. You can select your preferred language.',
            'bn': 'ভাষা পরিবর্তন করতে এখানে ক্লিক করুন। আপনি আপনার পছন্দের ভাষা নির্বাচন করতে পারেন।',
            'ta': 'மொழியை மாற்ற இங்கே கிளிக் செய்யவும். நீங்கள் உங்கள் விருப்பமான மொழியைத் தேர்ந்தெடுக்கலாம்.',
            'te': 'భాషను మార్చడానికి ఇక్కడ క్లిక్ చేయండి. మీరు మీ ఇష్టమైన భాషను ఎంచుకోవచ్చు.',
            'mr': 'भाषा बदलण्यासाठी येथे क्लिक करा. तुम्ही तुमची आवडती भाषा निवडू शकता.'
        };
        
        const message = helpMessages[this.currentLanguage] || helpMessages['hi'];
        
        if (this.synthesis) {
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.lang = this.supportedLanguages[this.currentLanguage].speechCode;
            utterance.rate = 0.8;
            
            this.synthesis.speak(utterance);
        }
    }
    
    /**
     * Play language change confirmation
     */
    playLanguageChangeConfirmation(languageCode) {
        const confirmationMessages = {
            'hi': 'भाषा हिंदी में बदल दी गई है।',
            'en': 'Language changed to English.',
            'bn': 'ভাষা বাংলায় পরিবর্তিত হয়েছে।',
            'ta': 'மொழி தமிழுக்கு மாற்றப்பட்டது.',
            'te': 'భాష తెలుగులోకి మార్చబడింది.',
            'mr': 'भाषा मराठीत बदलली आहे.'
        };
        
        const message = confirmationMessages[languageCode];
        
        if (message && this.synthesis) {
            setTimeout(() => {
                const utterance = new SpeechSynthesisUtterance(message);
                utterance.lang = this.supportedLanguages[languageCode].speechCode;
                utterance.rate = 0.8;
                
                this.synthesis.speak(utterance);
            }, 500);
        }
    }
    
    /**
     * Show language switching indicator
     */
    showSwitchingIndicator(languageCode) {
        const language = this.supportedLanguages[languageCode];
        
        let indicator = document.getElementById('languageSwitchingIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'languageSwitchingIndicator';
            indicator.className = 'language-switching-indicator';
            document.body.appendChild(indicator);
        }
        
        indicator.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 20px; height: 20px; border: 2px solid white; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <span>Switching to ${language.name}...</span>
            </div>
        `;
        
        // Add spin animation
        if (!document.getElementById('spin-animation')) {
            const style = document.createElement('style');
            style.id = 'spin-animation';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        indicator.classList.add('show');
    }
    
    /**
     * Hide language switching indicator
     */
    hideSwitchingIndicator() {
        const indicator = document.getElementById('languageSwitchingIndicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    }
    
    /**
     * Update current language display
     */
    updateCurrentLanguageDisplay() {
        const currentLang = this.supportedLanguages[this.currentLanguage];
        const button = document.getElementById('languageSelectorButton');
        
        if (button && currentLang) {
            const currentLanguageSpan = button.querySelector('.current-language');
            if (currentLanguageSpan) {
                currentLanguageSpan.innerHTML = `
                    <span class="language-flag">${currentLang.flag}</span>
                    <span class="language-name">${currentLang.name}</span>
                    <span class="language-english">(${currentLang.englishName})</span>
                `;
            }
        }
        
        // Update selected option in dropdown
        const options = document.querySelectorAll('.language-option');
        options.forEach(option => {
            option.classList.toggle('selected', option.dataset.language === this.currentLanguage);
        });
    }
    
    /**
     * Get current language
     */
    getCurrentLanguage() {
        // Try to get from URL parameter, session storage, or default to Hindi
        const urlParams = new URLSearchParams(window.location.search);
        const urlLang = urlParams.get('lang');
        
        if (urlLang && this.supportedLanguages && this.supportedLanguages[urlLang]) {
            return urlLang;
        }
        
        const sessionLang = sessionStorage.getItem('ai_sakhi_language');
        if (sessionLang && this.supportedLanguages && this.supportedLanguages[sessionLang]) {
            return sessionLang;
        }
        
        // Try to get from HTML lang attribute
        const htmlLang = document.documentElement.lang;
        if (htmlLang && this.supportedLanguages && this.supportedLanguages[htmlLang]) {
            return htmlLang;
        }
        
        return 'hi'; // Default to Hindi
    }
    
    /**
     * Preserve session state
     */
    async preserveSessionState() {
        try {
            // Collect current session data
            this.sessionData = {
                currentModule: this.getCurrentModule(),
                conversationHistory: this.getConversationHistory(),
                userPreferences: this.getUserPreferences(),
                timestamp: Date.now()
            };
            
            // Store in session storage
            sessionStorage.setItem('ai_sakhi_session_data', JSON.stringify(this.sessionData));
            sessionStorage.setItem('ai_sakhi_language', this.currentLanguage);
            
        } catch (error) {
            console.error('Error preserving session state:', error);
        }
    }
    
    /**
     * Load session data
     */
    loadSessionData() {
        try {
            const data = sessionStorage.getItem('ai_sakhi_session_data');
            return data ? JSON.parse(data) : {};
        } catch (error) {
            console.error('Error loading session data:', error);
            return {};
        }
    }
    
    /**
     * Get current module (placeholder)
     */
    getCurrentModule() {
        // This would be implemented based on the current page/module
        return window.location.pathname.split('/')[1] || 'home';
    }
    
    /**
     * Get conversation history (placeholder)
     */
    getConversationHistory() {
        // This would be implemented to collect current conversation
        return [];
    }
    
    /**
     * Get user preferences (placeholder)
     */
    getUserPreferences() {
        // This would be implemented to collect user preferences
        return {
            voiceEnabled: true,
            audioSpeed: 0.8
        };
    }
    
    /**
     * Show error message
     */
    showError(message) {
        // This would integrate with the main app's message system
        console.error(message);
        
        if (window.showMessage) {
            window.showMessage(message, 'error');
        } else {
            alert(message);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait for voices to be loaded
    if (window.speechSynthesis) {
        const initSelector = () => {
            window.languageSelector = new LanguageSelector();
        };
        
        if (window.speechSynthesis.getVoices().length > 0) {
            initSelector();
        } else {
            window.speechSynthesis.addEventListener('voiceschanged', initSelector, { once: true });
        }
    } else {
        // Initialize without speech synthesis
        window.languageSelector = new LanguageSelector();
    }
});

// Export for global access
window.LanguageSelector = LanguageSelector;