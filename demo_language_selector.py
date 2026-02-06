#!/usr/bin/env python3
"""
Demo for Enhanced Language Selector Component
"""

import sys
import os
import time
from flask import Flask, render_template_string, session, request, jsonify
from flask_babel import Babel, gettext

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app for demo
app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'

# Configure languages
app.config['LANGUAGES'] = {
    'hi': 'हिंदी',
    'en': 'English',
    'bn': 'বাংলা',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'mr': 'मराठी'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'hi'

def get_locale():
    """Select the best language based on user preference."""
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'hi'

babel = Babel(app, locale_selector=get_locale)

# Demo template with enhanced language selector
DEMO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ get_locale() }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Sakhi - Enhanced Language Selector Demo</title>
    
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #FFE5F1 0%, #E5F3FF 100%);
            min-height: 100vh;
        }
        
        .demo-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .demo-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .demo-title {
            color: #FF69B4;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .demo-subtitle {
            color: #666;
            font-size: 1.2em;
            margin-bottom: 20px;
        }
        
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: rgba(255, 105, 180, 0.1);
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo-icon {
            width: 50px;
            height: 50px;
            background: #FF69B4;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }
        
        .brand-text h1 {
            margin: 0;
            color: #FF69B4;
            font-size: 1.8em;
        }
        
        .brand-text p {
            margin: 5px 0 0 0;
            color: #666;
            font-size: 0.9em;
        }
        
        .demo-content {
            margin-top: 30px;
        }
        
        .feature-list {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .feature-list h3 {
            color: #FF69B4;
            margin-top: 0;
        }
        
        .feature-list ul {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .feature-list li:last-child {
            border-bottom: none;
        }
        
        .feature-list li::before {
            content: '✓';
            color: #FF69B4;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .demo-instructions {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .demo-instructions h4 {
            margin-top: 0;
            color: #1976d2;
        }
        
        .current-language-display {
            text-align: center;
            padding: 20px;
            background: rgba(255, 105, 180, 0.05);
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .current-language-display h3 {
            color: #FF69B4;
            margin-bottom: 10px;
        }
        
        .language-info {
            font-size: 1.2em;
            color: #333;
        }
        
        .test-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        
        .test-button {
            padding: 10px 20px;
            background: #FF69B4;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .test-button:hover {
            background: #E55A9B;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .app-header {
                flex-direction: column;
                gap: 20px;
            }
            
            .demo-container {
                padding: 20px;
                margin: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <div class="demo-header">
            <h1 class="demo-title">🎤 AI SAKHI</h1>
            <p class="demo-subtitle">Enhanced Language Selector Demo</p>
        </div>
        
        <div class="app-header">
            <div class="logo-section">
                <div class="logo-icon">👩‍⚕️</div>
                <div class="brand-text">
                    <h1>AI SAKHI</h1>
                    <p>Voice-First Health Companion</p>
                </div>
            </div>
            
            <!-- Enhanced Language Selector will be inserted here -->
            <div class="language-selector">
                <select id="languageSelect" onchange="changeLanguage(this.value)">
                    {% for code, name in config.LANGUAGES.items() %}
                    <option value="{{ code }}" {% if code == get_locale() %}selected{% endif %}>
                        {{ name }}
                    </option>
                    {% endfor %}
                </select>
            </div>
        </div>
        
        <div class="current-language-display">
            <h3>Current Language</h3>
            <div class="language-info">
                <strong>{{ config.LANGUAGES[get_locale()] }}</strong> ({{ get_locale() }})
            </div>
        </div>
        
        <div class="demo-content">
            <div class="demo-instructions">
                <h4>🎯 How to Test the Enhanced Language Selector:</h4>
                <ol>
                    <li><strong>Click the language selector</strong> - Notice the enhanced dropdown with flags and audio buttons</li>
                    <li><strong>Try the audio help button (🔊)</strong> - Hear instructions in the current language</li>
                    <li><strong>Click audio buttons</strong> next to each language option to hear the language name</li>
                    <li><strong>Select a different language</strong> - Watch the smooth transition with loading indicator</li>
                    <li><strong>Use keyboard navigation</strong> - Tab to the selector and use arrow keys</li>
                    <li><strong>Test accessibility</strong> - All components support screen readers</li>
                </ol>
            </div>
            
            <div class="feature-list">
                <h3>✨ Enhanced Features</h3>
                <ul>
                    <li>Visual language selector with flags and native names</li>
                    <li>Audio labels for each language option</li>
                    <li>Audio help button with instructions</li>
                    <li>Mid-session language switching with smooth transitions</li>
                    <li>Session state preservation during language changes</li>
                    <li>Full keyboard navigation support</li>
                    <li>Screen reader accessibility</li>
                    <li>Mobile-responsive design</li>
                    <li>Loading indicators and confirmation messages</li>
                    <li>Error handling with user-friendly messages</li>
                </ul>
            </div>
            
            <div class="test-buttons">
                <button class="test-button" onclick="testAudioHelp()">🔊 Test Audio Help</button>
                <button class="test-button" onclick="testKeyboardNav()">⌨️ Test Keyboard Navigation</button>
                <button class="test-button" onclick="testSessionPreservation()">💾 Test Session Preservation</button>
                <button class="test-button" onclick="showAccessibilityInfo()">♿ Accessibility Info</button>
            </div>
        </div>
    </div>
    
    <!-- Include the enhanced language selector script -->
    <script>
        // Mock functions for demo
        function changeLanguage(languageCode) {
            console.log('Changing language to:', languageCode);
            window.location.href = '/?lang=' + languageCode;
        }
        
        function testAudioHelp() {
            if (window.languageSelector) {
                window.languageSelector.playAudioHelp();
            } else {
                alert('Enhanced language selector not loaded yet. Please wait a moment and try again.');
            }
        }
        
        function testKeyboardNav() {
            alert('Use Tab to navigate to the language selector, then use Enter/Space to open it and arrow keys to navigate options.');
            const selector = document.getElementById('languageSelectorButton');
            if (selector) {
                selector.focus();
            }
        }
        
        function testSessionPreservation() {
            alert('Session preservation works automatically when you change languages. Your current module, conversation history, and preferences are maintained.');
        }
        
        function showAccessibilityInfo() {
            const info = `
Accessibility Features:
• Full keyboard navigation support
• Screen reader compatible with ARIA labels
• High contrast focus indicators
• Audio feedback for all interactions
• Mobile-friendly touch targets
• Clear visual hierarchy
• Semantic HTML structure
            `;
            alert(info);
        }
        
        // Show loading message
        console.log('Loading enhanced language selector...');
    </script>
    
    <script src="/static/js/language-selector.js"></script>
</body>
</html>
'''

@app.route('/')
def demo_index():
    """Demo page with enhanced language selector."""
    return render_template_string(DEMO_TEMPLATE)

@app.route('/language/<language_code>', methods=['GET', 'POST'])
def set_language(language_code):
    """Set user's preferred language with session preservation."""
    if language_code not in app.config['LANGUAGES']:
        return jsonify({
            'status': 'error',
            'message': f'Unsupported language: {language_code}'
        }), 400
    
    try:
        # Get session preservation data if provided
        session_data = None
        if request.method == 'POST':
            data = request.get_json() or {}
            session_data = data.get('session_data', {})
            preserve_session = data.get('preserve_session', False)
            
            if preserve_session and session_data:
                # Store session data temporarily
                session['preserved_data'] = session_data
                print(f"Session data preserved for language change to {language_code}")
        
        # Set the new language
        session['language'] = language_code
        
        # Log the language change
        print(f"Language changed to: {language_code} ({app.config['LANGUAGES'][language_code]})")
        
        return jsonify({
            'status': 'success',
            'language': language_code,
            'language_name': app.config['LANGUAGES'][language_code],
            'message': 'Language changed successfully'
        })
        
    except Exception as e:
        print(f"Error changing language to {language_code}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to change language'
        }), 500

@app.route('/static/js/language-selector.js')
def serve_language_selector_js():
    """Serve the language selector JavaScript file."""
    try:
        with open('static/js/language-selector.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        from flask import Response
        return Response(content, mimetype='application/javascript')
    except FileNotFoundError:
        return "// Language selector script not found", 404

def main():
    """Run the demo server."""
    print("=== AI Sakhi Enhanced Language Selector Demo ===\n")
    print("🎯 Features being demonstrated:")
    print("   • Enhanced visual language selector with flags")
    print("   • Audio labels for each language option")
    print("   • Audio help button with instructions")
    print("   • Mid-session language switching")
    print("   • Session state preservation")
    print("   • Full keyboard navigation")
    print("   • Screen reader accessibility")
    print("   • Mobile-responsive design")
    print("   • Loading indicators and confirmations")
    print("   • Error handling")
    print()
    print("🚀 Starting demo server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🎤 Test the voice features and language switching!")
    print()
    print("Press Ctrl+C to stop the demo")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped. Thank you for testing AI Sakhi!")

if __name__ == "__main__":
    main()