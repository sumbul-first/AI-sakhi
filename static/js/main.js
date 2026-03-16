/**
 * AI Sakhi - Main JavaScript
 * Voice-First Health Companion for Women and Girls
 */

// Global variables
let isVoiceActive = false;
let recognition = null;
let synthesis = null;
let noSpeechTimer = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    restoreLanguage();
    setupVoiceRecognition();
    setupLanguageSelector();
    setupAccessibility();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('AI Sakhi - Voice-First Health Companion initialized');
    const logo = document.querySelector('.main-logo');
    if (logo) {
        logo.addEventListener('load', function() { this.style.opacity = '1'; });
    }
}

/**
 * Restore language - sync LanguageSelector instance with server-rendered value.
 */
function restoreLanguage() {
    // The server-rendered <select> is the ground truth.
    // Sync the LanguageSelector instance if it's already initialized.
    const select = document.getElementById('languageSelect');
    const serverLang = select ? select.value : null;
    if (serverLang && window.languageSelector && window.languageSelector.currentLanguage !== serverLang) {
        window.languageSelector.currentLanguage = serverLang;
        window.languageSelector.updateCurrentLanguageDisplay();
    }
}

/**
 * Setup voice recognition
 */
function setupVoiceRecognition() {
    // Check for Web Speech API support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = true;   // show interim so user sees it's working
        recognition.maxAlternatives = 1;
        recognition.lang = getCurrentLanguage();
        
        recognition.onstart = function() {
            console.log('Voice recognition started');
            updateVoiceButton(true);
            startListeningCountdown();
        };
        
        recognition.onresult = function(event) {
            stopListeningCountdown();
            // Use the final result
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    const transcript = event.results[i][0].transcript.trim();
                    if (transcript) {
                        console.log('Voice input received:', transcript);
                        // If on module page, put in chat input
                        const chatInput = document.getElementById('textInput');
                        if (chatInput) {
                            chatInput.value = transcript;
                            if (window.sendTextQuery) sendTextQuery();
                        } else {
                            processVoiceInput(transcript);
                        }
                    }
                }
            }
        };
        
        recognition.onerror = function(event) {
            stopListeningCountdown();
            updateVoiceButton(false);
            if (event.error === 'no-speech') {
                // Silent - just stop, don't alarm the user
                console.log('No speech detected, stopped listening');
            } else if (event.error === 'not-allowed') {
                showMessage('Microphone access denied. Please allow microphone in browser settings.', 'error');
            } else {
                console.warn('Voice recognition error:', event.error);
            }
        };
        
        recognition.onend = function() {
            stopListeningCountdown();
            console.log('Voice recognition ended');
            updateVoiceButton(false);
        };
    } else {
        console.warn('Web Speech API not supported');
        // Hide voice button if not supported
        const voiceBtn = document.getElementById('voiceButton');
        if (voiceBtn) {
            voiceBtn.style.display = 'none';
        }
    }
    
    // Setup speech synthesis
    if ('speechSynthesis' in window) {
        synthesis = window.speechSynthesis;
    }
}

/**
 * Toggle voice recognition
 */
function toggleVoice() {
    if (!recognition) {
        showMessage('Voice recognition not supported in this browser', 'error');
        return;
    }
    
    if (isVoiceActive) {
        recognition.stop();
    } else {
        recognition.lang = getCurrentLanguage();
        recognition.start();
    }
}

/**
 * Update voice button state
 */
function updateVoiceButton(active) {
    isVoiceActive = active;
    // Update all voice buttons on the page (header + module page)
    document.querySelectorAll('#voiceButton').forEach(btn => {
        if (active) {
            btn.innerHTML = '🔴 Listening...';
            btn.classList.add('listening');
        } else {
            btn.innerHTML = '🎤 Voice';
            btn.classList.remove('listening');
        }
    });
}

let _countdownTimer = null;
let _countdownSecs = 0;

function startListeningCountdown() {
    _countdownSecs = 8;
    _countdownTimer = setInterval(() => {
        _countdownSecs--;
        document.querySelectorAll('#voiceButton').forEach(btn => {
            btn.innerHTML = `🔴 Listening... ${_countdownSecs}s`;
        });
        if (_countdownSecs <= 0) stopListeningCountdown();
    }, 1000);
}

function stopListeningCountdown() {
    if (_countdownTimer) {
        clearInterval(_countdownTimer);
        _countdownTimer = null;
    }
}

/**
 * Process voice input
 */
function processVoiceInput(transcript) {
    console.log('Processing voice input:', transcript);
    
    // Send to backend for processing (using text endpoint since we already have transcript)
    fetch('/api/text/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            text: transcript,
            language: getCurrentLanguage()
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Voice processing response:', data);
        
        if (data.status === 'success') {
            if (data.response_text) {
                speakText(data.response_text);
                // Display the response
                showMessage(data.response_text, 'success');
            } else {
                console.warn('No response text in successful response');
                showMessage('Received empty response', 'warning');
            }
        } else if (data.status === 'error') {
            const errorMsg = data.message || data.error_message || 'Error processing input';
            console.error('Error from server:', errorMsg, data);
            showMessage(errorMsg, 'error');
        }
    })
    .catch(error => {
        console.error('Voice processing error:', error);
        showMessage('Error processing voice input: ' + error.message, 'error');
    });
}

/**
 * Speak text using speech synthesis
 */
function speakText(text) {
    if (!synthesis) {
        console.warn('Speech synthesis not supported');
        return;
    }
    
    // Cancel any ongoing speech
    synthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getCurrentLanguage();
    utterance.rate = 0.8; // Slower speech for better comprehension
    utterance.pitch = 1.0;
    
    // Try to use a female voice if available
    const voices = synthesis.getVoices();
    const femaleVoice = voices.find(voice => 
        voice.lang.startsWith(getCurrentLanguage().split('-')[0]) && 
        voice.name.toLowerCase().includes('female')
    );
    
    if (femaleVoice) {
        utterance.voice = femaleVoice;
    }
    
    utterance.onstart = function() {
        console.log('Speech synthesis started');
    };
    
    utterance.onend = function() {
        console.log('Speech synthesis ended');
    };
    
    utterance.onerror = function(event) {
        console.error('Speech synthesis error:', event.error);
    };
    
    synthesis.speak(utterance);
}

/**
 * Setup language selector
 */
function setupLanguageSelector() {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            changeLanguage(this.value);
        });
    }
}

/**
 * Change application language
 */
function changeLanguage(languageCode) {
    console.log('Changing language to:', languageCode);
    
    fetch(`/language/${languageCode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preserve_session: true })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Language change response:', data);
        if (data.status === 'success') {
            // Store in localStorage AND cookie as backup
            localStorage.setItem('preferred_language', languageCode);
            document.cookie = `preferred_language=${languageCode}; max-age=${60*60*24*30}; path=/; SameSite=Lax`;
            window.location.reload();
        } else {
            console.error('Language change failed:', data);
        }
    })
    .catch(error => {
        console.error('Language change error:', error);
        // Still try to reload with cookie set
        document.cookie = `preferred_language=${languageCode}; max-age=${60*60*24*30}; path=/; SameSite=Lax`;
        window.location.reload();
    });
}

/**
 * Get current language - reads from languageSelector instance, cookie, or localStorage
 */
function getCurrentLanguage() {
    // 1. Ask the LanguageSelector instance if available
    if (window.languageSelector) {
        const code = window.languageSelector.currentLanguage;
        if (code) {
            const langMap = { 'hi': 'hi-IN', 'en': 'en-US', 'bn': 'bn-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN' };
            return langMap[code] || 'hi-IN';
        }
    }

    // 2. Fallback: read the native <select> if it still exists
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect && languageSelect.value) {
        const langMap = { 'hi': 'hi-IN', 'en': 'en-US', 'bn': 'bn-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN' };
        return langMap[languageSelect.value] || 'hi-IN';
    }

    // 3. Cookie (set by server - most reliable persistent source)
    const cookieMatch = document.cookie.match(/(?:^|;\s*)preferred_language=([^;]+)/);
    if (cookieMatch && cookieMatch[1]) {
        const langMap = { 'hi': 'hi-IN', 'en': 'en-US', 'bn': 'bn-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'mr': 'mr-IN' };
        return langMap[cookieMatch[1]] || 'hi-IN';
    }

    return 'hi-IN';
}

/**
 * Setup accessibility features
 */
function setupAccessibility() {
    // Add keyboard navigation support
    document.addEventListener('keydown', function(event) {
        // Space bar to toggle voice
        if (event.code === 'Space' && event.target === document.body) {
            event.preventDefault();
            toggleVoice();
        }
        
        // Escape to stop voice
        if (event.code === 'Escape' && isVoiceActive) {
            recognition.stop();
        }
    });
    
    // Add focus indicators for keyboard navigation
    const focusableElements = document.querySelectorAll('button, a, select, input');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '3px solid #FF69B4';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
}

/**
 * Show message to user
 */
function showMessage(message, type = 'info') {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    
    // Find or create messages container
    let messagesContainer = document.querySelector('.messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'messages';
        const mainContent = document.querySelector('.main-content .container');
        if (mainContent) {
            mainContent.insertBefore(messagesContainer, mainContent.firstChild);
        }
    }
    
    // Add message
    messagesContainer.appendChild(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
    
    // Speak the message if it's important
    if (type === 'error' || type === 'success') {
        speakText(message);
    }
}

/**
 * Navigate to module (real navigation)
 */
function navigateToModule(moduleName) {
    window.location.href = '/modules/' + moduleName;
}

/**
 * Start voice interaction
 */
function startVoiceInteraction() {
    console.log('Starting voice interaction');
    toggleVoice();
}

/**
 * Emergency contact quick access
 */
function callEmergencyHelp() {
    const emergencyNumbers = {
        'women': '1091',
        'medical': '108',
        'police': '1090'
    };
    
    const message = `Emergency helplines: Women helpline ${emergencyNumbers.women}, Medical emergency ${emergencyNumbers.medical}, Police women helpline ${emergencyNumbers.police}`;
    
    speakText(message);
    showMessage(message, 'error');
}

// Export functions for global access
window.toggleVoice = toggleVoice;
window.changeLanguage = changeLanguage;
window.navigateToModule = navigateToModule;
window.startVoiceInteraction = startVoiceInteraction;
window.callEmergencyHelp = callEmergencyHelp;