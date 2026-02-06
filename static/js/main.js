/**
 * AI Sakhi - Main JavaScript
 * Voice-First Health Companion for Women and Girls
 */

// Global variables
let isVoiceActive = false;
let recognition = null;
let synthesis = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupVoiceRecognition();
    setupLanguageSelector();
    setupAccessibility();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('AI Sakhi - Voice-First Health Companion initialized');
    
    // Add loading animation to logo
    const logo = document.querySelector('.main-logo');
    if (logo) {
        logo.addEventListener('load', function() {
            this.style.opacity = '1';
        });
    }
    
    // Setup service worker for offline functionality (future enhancement)
    if ('serviceWorker' in navigator) {
        // Will be implemented in later tasks
        console.log('Service Worker support detected');
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
        recognition.interimResults = false;
        recognition.lang = getCurrentLanguage();
        
        recognition.onstart = function() {
            console.log('Voice recognition started');
            updateVoiceButton(true);
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log('Voice input received:', transcript);
            processVoiceInput(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('Voice recognition error:', event.error);
            showMessage('Voice recognition error: ' + event.error, 'error');
            updateVoiceButton(false);
        };
        
        recognition.onend = function() {
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
    const voiceBtn = document.getElementById('voiceButton');
    if (voiceBtn) {
        if (active) {
            voiceBtn.innerHTML = '🔴 Listening...';
            voiceBtn.classList.add('listening');
        } else {
            voiceBtn.innerHTML = '🎤 Voice';
            voiceBtn.classList.remove('listening');
        }
    }
}

/**
 * Process voice input
 */
function processVoiceInput(transcript) {
    console.log('Processing voice input:', transcript);
    
    // Send to backend for processing
    fetch('/voice/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            transcript: transcript,
            language: getCurrentLanguage()
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Voice processing response:', data);
        if (data.response) {
            speakText(data.response);
        }
    })
    .catch(error => {
        console.error('Voice processing error:', error);
        showMessage('Error processing voice input', 'error');
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
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Reload page to apply new language
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Language change error:', error);
        showMessage('Error changing language', 'error');
    });
}

/**
 * Get current language
 */
function getCurrentLanguage() {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        const selectedLang = languageSelect.value;
        // Map language codes to speech recognition codes
        const langMap = {
            'hi': 'hi-IN',
            'en': 'en-US',
            'bn': 'bn-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'mr': 'mr-IN'
        };
        return langMap[selectedLang] || 'hi-IN';
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
 * Navigate to module (placeholder)
 */
function navigateToModule(moduleName) {
    console.log('Navigating to module:', moduleName);
    showMessage(`${moduleName} module will be implemented soon!`, 'info');
}

/**
 * Start voice interaction (placeholder)
 */
function startVoiceInteraction() {
    console.log('Starting voice interaction');
    speakText('Welcome to AI Sakhi! I am your voice-first health companion. How can I help you today?');
    
    // Start listening after greeting
    setTimeout(() => {
        toggleVoice();
    }, 3000);
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