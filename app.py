#!/usr/bin/env python3
"""
AI Sakhi - Voice-First Health Companion
Main Flask Application

A trusted health companion for women and girls in rural areas,
providing voice-first health education, safety awareness, and guidance.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_babel import Babel, gettext, ngettext
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-sakhi-dev-key-change-in-production')
app.config['PORT'] = 8080

# Configure Babel for multi-language support
app.config['LANGUAGES'] = {
    'en': 'English',
    'hi': 'हिंदी',
    'bn': 'বাংলা', 
    'ta': 'தமிழ்',
    'te': 'తెলুগু',
    'mr': 'मराठी'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'hi'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Kolkata'

def get_locale():
    """Select the best language based on user preference or browser settings."""
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    
    # Check if language is provided in request
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
        return session['language']
    
    # Use browser's preferred language
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'hi'

babel = Babel(app, locale_selector=get_locale)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main landing page for AI Sakhi."""
    logger.info("User accessed main page")
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Sakhi',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/modules')
def modules():
    """Display all available health education modules."""
    modules_data = {
        'puberty': {
            'name': gettext('Puberty Education'),
            'description': gettext('Body changes, menstruation, and hygiene'),
            'icon': '🌸'
        },
        'safety': {
            'name': gettext('Safety & Mental Support'),
            'description': gettext('Good/bad touch awareness and emotional support'),
            'icon': '🛡️'
        },
        'menstrual': {
            'name': gettext('Menstrual Shopping Guide'),
            'description': gettext('Product comparison and selection guidance'),
            'icon': '🩸'
        },
        'pregnancy': {
            'name': gettext('Pregnancy Guidance'),
            'description': gettext('Nutrition tips and danger signs'),
            'icon': '🤱'
        },
        'government': {
            'name': gettext('Government Resources'),
            'description': gettext('Health schemes and programs information'),
            'icon': '🏛️'
        }
    }
    return render_template('modules.html', modules=modules_data)

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
                logger.info(f"Session data preserved for language change to {language_code}")
        
        # Set the new language
        session['language'] = language_code
        
        # Log the language change
        logger.info(f"Language changed to: {language_code} ({app.config['LANGUAGES'][language_code]})")
        
        return jsonify({
            'status': 'success',
            'language': language_code,
            'language_name': app.config['LANGUAGES'][language_code],
            'message': gettext('Language changed successfully')
        })
        
    except Exception as e:
        logger.error(f"Error changing language to {language_code}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to change language')
        }), 500

@app.route('/language/restore-session', methods=['POST'])
def restore_session():
    """Restore session data after language change."""
    try:
        preserved_data = session.get('preserved_data')
        if preserved_data:
            # Restore relevant session data
            current_module = preserved_data.get('currentModule')
            user_preferences = preserved_data.get('userPreferences', {})
            
            # Apply restored data
            if current_module:
                session['current_module'] = current_module
            
            if user_preferences:
                session['user_preferences'] = user_preferences
            
            # Clear preserved data
            session.pop('preserved_data', None)
            
            logger.info("Session data restored after language change")
            
            return jsonify({
                'status': 'success',
                'message': gettext('Session restored successfully'),
                'restored_data': {
                    'current_module': current_module,
                    'preferences': user_preferences
                }
            })
        else:
            return jsonify({
                'status': 'info',
                'message': gettext('No session data to restore')
            })
            
    except Exception as e:
        logger.error(f"Error restoring session: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to restore session')
        }), 500

@app.route('/voice/process', methods=['POST'])
def process_voice():
    """Process voice input from users."""
    # Placeholder for voice processing
    # This will be implemented in later tasks
    return jsonify({
        'status': 'received',
        'message': gettext('Voice processing will be implemented soon')
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404,
                         error_message=gettext('Page not found')), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html',
                         error_code=500,
                         error_message=gettext('Internal server error')), 500

if __name__ == '__main__':
    logger.info("Starting AI Sakhi - Voice-First Health Companion")
    logger.info(f"Available languages: {list(app.config['LANGUAGES'].keys())}")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=True
    )