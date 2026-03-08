#!/usr/bin/env python3
"""
AI Sakhi - Voice-First Health Companion
Main Flask Application (Integrated Version)

A trusted health companion for women and girls in rural areas,
providing voice-first health education, safety awareness, and guidance.

This integrated version wires together all components:
- Session Management
- Content Management
- Voice Processing
- Health Modules
- Reminder System
- Content Safety Validation
"""

from flask import Flask, render_template, request, jsonify, session
from flask_babel import Babel, gettext
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import base64

# Import core components
from core.session_manager import SessionManager
from core.content_manager import ContentManager
from core.speech_processor import SpeechProcessor
from core.voice_interface import VoiceInterface
from core.reminder_system import ReminderSystem, ReminderType
from core.content_safety import ContentSafetyValidator
from core.error_handler import (
    ErrorHandler, GracefulDegradation, OfflineEmergencyAccess,
    handle_errors, ErrorCategory
)

# Import health modules
from modules.puberty_education_module import PubertyEducationModule
from modules.safety_mental_support_module import SafetyMentalSupportModule
from modules.menstrual_guide_module import MenstrualGuideModule
from modules.pregnancy_guidance_module import PregnancyGuidanceModule
from modules.government_resources_module import GovernmentResourcesModule

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-sakhi-dev-key-change-in-production')
app.config['PORT'] = 8080
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure Babel for multi-language support
app.config['LANGUAGES'] = {
    'en': 'English',
    'hi': 'हिंदी',
    'bn': 'বাংলা', 
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'mr': 'मराठी'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'hi'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Kolkata'

def get_locale():
    """Select the best language based on user preference or browser settings."""
    if 'language' in session:
        return session['language']
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'hi'

babel = Babel(app, locale_selector=get_locale)

# Make get_locale available to templates
@app.context_processor
def inject_locale():
    """Inject get_locale function into template context."""
    return dict(get_locale=get_locale)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize core components
logger.info("Initializing AI Sakhi core components...")

# Session Manager
session_manager = SessionManager(timeout_minutes=30, enable_persistence=False)

# Content Manager (using mock mode for development)
content_manager = ContentManager(
    s3_bucket_name='ai-sakhi-content',
    aws_region='us-east-1',
    use_mock=True
)

# Speech Processor
speech_processor = SpeechProcessor(
    aws_region='us-east-1',
    use_mock=True
)

# Voice Interface
voice_interface = VoiceInterface(
    speech_processor=speech_processor,
    content_manager=content_manager,
    session_manager=session_manager,
    use_mock=True
)

# Reminder System
reminder_system = ReminderSystem()

# Content Safety Validator
content_safety_validator = ContentSafetyValidator()

# Error Handler
error_handler = ErrorHandler()

# Initialize health modules
logger.info("Initializing health education modules...")
health_modules = {
    'puberty': PubertyEducationModule(content_manager, session_manager),
    'safety': SafetyMentalSupportModule(content_manager, session_manager),
    'menstrual': MenstrualGuideModule(content_manager, session_manager),
    'pregnancy': PregnancyGuidanceModule(content_manager, session_manager),
    'government': GovernmentResourcesModule(content_manager, session_manager)
}

logger.info("AI Sakhi initialization complete!")


# Helper functions
def get_or_create_session_id() -> str:
    """Get existing session ID or create a new one."""
    if 'session_id' not in session:
        # Create new session
        language = session.get('language', 'hi')
        user_session = session_manager.create_session(language)
        session['session_id'] = user_session.session_id
        logger.info(f"Created new session: {user_session.session_id}")
    return session['session_id']


def validate_and_sanitize_response(response_text: str, language_code: str) -> Dict[str, Any]:
    """Validate and sanitize response for medical boundary compliance."""
    validation = content_safety_validator.validate_system_response(response_text, language_code)
    
    if not validation.is_safe:
        sanitized_text, was_modified = content_safety_validator.sanitize_response(
            response_text, language_code
        )
        return {
            'text': sanitized_text,
            'was_sanitized': was_modified,
            'safety_warnings': validation.detected_issues,
            'requires_medical_referral': validation.requires_medical_referral
        }
    
    return {
        'text': response_text,
        'was_sanitized': False,
        'safety_warnings': [],
        'requires_medical_referral': False
    }


# Routes
@app.route('/')
def index():
    """Main landing page for AI Sakhi."""
    session_id = get_or_create_session_id()
    logger.info(f"User accessed main page (session: {session_id})")
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        health_status = {
            'status': 'healthy',
            'service': 'AI Sakhi',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {}
        }
        
        # Check session manager
        health_status['components']['session_manager'] = {
            'status': 'healthy',
            'active_sessions': session_manager.get_active_session_count()
        }
        
        # Check content manager
        content_health = content_manager.health_check()
        health_status['components']['content_manager'] = content_health
        
        # Check voice interface
        voice_health = voice_interface.health_check()
        health_status['components']['voice_interface'] = voice_health
        
        # Check reminder system
        reminder_health = reminder_system.health_check()
        health_status['components']['reminder_system'] = reminder_health
        
        # Check content safety
        safety_health = content_safety_validator.health_check()
        health_status['components']['content_safety'] = safety_health
        
        # Check health modules
        health_status['components']['health_modules'] = {
            'available': list(health_modules.keys()),
            'count': len(health_modules)
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


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


@app.route('/module/<module_name>')
def module_detail(module_name):
    """Display detailed view of a specific health module."""
    if module_name not in health_modules:
        return render_template('error.html', 
                             error_code=404,
                             error_message=gettext('Module not found')), 404
    
    session_id = get_or_create_session_id()
    language_code = session.get('language', 'hi')
    
    try:
        # Get module info
        module = health_modules[module_name]
        module_info = module.get_module_info()
        
        # Get available topics
        topics = module.get_module_topics(language_code)
        
        return render_template('module.html',
                             module_name=module_name,
                             module_info=module_info,
                             topics=topics)
    except Exception as e:
        logger.error(f"Error loading module {module_name}: {e}")
        return render_template('error.html',
                             error_code=500,
                             error_message=gettext('Error loading module')), 500


@app.route('/api/voice/process', methods=['POST'])
def process_voice():
    """Process voice input from users."""
    try:
        session_id = get_or_create_session_id()
        language_code = session.get('language', 'hi')
        
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': gettext('No audio file provided')
            }), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Process voice input
        result = voice_interface.process_voice_input(
            audio_data=audio_data,
            session_id=session_id,
            language_code=language_code
        )
        
        # Validate and sanitize response
        if result.success and result.response_text:
            sanitized = validate_and_sanitize_response(
                result.response_text,
                result.language_code
            )
            result.response_text = sanitized['text']
        
        return jsonify({
            'status': 'success' if result.success else 'error',
            'user_query': result.user_query,
            'response_text': result.response_text,
            'response_audio_url': result.response_audio_url,
            'language_code': result.language_code,
            'confidence_score': result.confidence_score,
            'processing_time_ms': result.processing_time_ms,
            'module_used': result.module_used,
            'fallback_used': result.fallback_used,
            'emergency_detected': result.emergency_detected,
            'error_message': result.error_message
        })
        
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to process voice input')
        }), 500


@app.route('/api/text/process', methods=['POST'])
def process_text():
    """Process text input as fallback."""
    try:
        session_id = get_or_create_session_id()
        language_code = session.get('language', 'hi')
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': gettext('No text provided')
            }), 400
        
        user_text = data['text']
        
        # Validate user query for safety
        query_validation = content_safety_validator.validate_user_query(
            user_text, language_code
        )
        
        # Process text input
        result = voice_interface.process_text_input(
            text=user_text,
            session_id=session_id,
            language_code=language_code
        )
        
        # Validate and sanitize response
        if result.success and result.response_text:
            sanitized = validate_and_sanitize_response(
                result.response_text,
                result.language_code
            )
            result.response_text = sanitized['text']
        
        return jsonify({
            'status': 'success' if result.success else 'error',
            'user_query': result.user_query,
            'response_text': result.response_text,
            'response_audio_url': result.response_audio_url,
            'language_code': result.language_code,
            'processing_time_ms': result.processing_time_ms,
            'module_used': result.module_used,
            'emergency_detected': result.emergency_detected,
            'requires_medical_referral': query_validation.requires_medical_referral,
            'error_message': result.error_message
        })
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to process text input')
        }), 500


@app.route('/api/reminders', methods=['GET', 'POST'])
def manage_reminders():
    """Manage user reminders."""
    try:
        session_id = get_or_create_session_id()
        language_code = session.get('language', 'hi')
        
        if request.method == 'GET':
            # Get user reminders
            reminders = reminder_system.get_user_reminders(session_id)
            upcoming = reminder_system.get_upcoming_reminders(session_id, hours_ahead=48)
            
            return jsonify({
                'status': 'success',
                'reminders': [r.to_dict() for r in reminders],
                'upcoming': [r.to_dict() for r in upcoming]
            })
        
        elif request.method == 'POST':
            # Create new reminder
            data = request.get_json()
            
            if data.get('type') == 'prenatal_appointment':
                appointment_date = datetime.fromisoformat(data['appointment_date'])
                reminder = reminder_system.create_prenatal_appointment_reminder(
                    user_id=session_id,
                    appointment_date=appointment_date,
                    doctor_name=data.get('doctor_name'),
                    clinic_name=data.get('clinic_name'),
                    language_code=language_code
                )
            else:
                reminder = reminder_system.create_reminder(
                    user_id=session_id,
                    reminder_type=ReminderType(data['type']),
                    title=data['title'],
                    description=data['description'],
                    scheduled_time=datetime.fromisoformat(data['scheduled_time']),
                    language_code=language_code
                )
            
            return jsonify({
                'status': 'success',
                'reminder': reminder.to_dict()
            })
            
    except Exception as e:
        logger.error(f"Error managing reminders: {e}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to manage reminders')
        }), 500


@app.route('/language/<language_code>', methods=['GET', 'POST'])
def set_language(language_code):
    """Set user's preferred language with session preservation."""
    if language_code not in app.config['LANGUAGES']:
        return jsonify({
            'status': 'error',
            'message': f'Unsupported language: {language_code}'
        }), 400
    
    try:
        session_id = get_or_create_session_id()
        
        # Get session preservation data if provided
        session_data = None
        if request.method == 'POST':
            data = request.get_json() or {}
            session_data = data.get('session_data', {})
            preserve_session = data.get('preserve_session', False)
            
            if preserve_session and session_data:
                session['preserved_data'] = session_data
                logger.info(f"Session data preserved for language change to {language_code}")
        
        # Set the new language
        session['language'] = language_code
        
        # Update session manager
        session_manager.update_session(session_id, language_preference=language_code)
        
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


@app.route('/api/emergency')
def get_emergency_contacts():
    """Get emergency contact information."""
    try:
        language_code = session.get('language', 'hi')
        
        # Try to get from safety module
        try:
            safety_module = health_modules['safety']
            contacts = safety_module.get_emergency_resources(language_code)
            
            return jsonify({
                'status': 'success',
                'contacts': [
                    {
                        'type': c.contact_type,
                        'phone': c.phone_number,
                        'region': c.region,
                        'languages': c.language_support,
                        'hours': c.availability_hours,
                        'description': c.description
                    }
                    for c in contacts
                ],
                'source': 'online'
            })
        except Exception as e:
            # Fallback to offline emergency contacts
            logger.warning(f"Using offline emergency contacts: {e}")
            offline_contacts = OfflineEmergencyAccess.get_contacts(language_code)
            
            return jsonify({
                'status': 'success',
                'contacts': offline_contacts,
                'source': 'offline',
                'message': gettext('Showing offline emergency contacts')
            })
        
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {e}")
        error_response = error_handler.handle_error(
            e,
            {'route': 'emergency_contacts'},
            session.get('language', 'hi')
        )
        return jsonify({
            'status': 'error',
            'message': error_response.user_message,
            'recovery_options': error_response.recovery_options
        }), 500


@app.route('/api/stats')
def get_stats():
    """Get system statistics."""
    try:
        session_id = get_or_create_session_id()
        
        stats = {
            'voice_interface': voice_interface.get_interaction_stats(),
            'reminders': reminder_system.get_reminder_statistics(session_id),
            'session': {
                'active_sessions': session_manager.get_active_session_count(),
                'total_sessions': session_manager.get_session_count()
            }
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to get statistics')
        }), 500


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


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        'status': 'error',
        'message': gettext('File too large. Maximum size is 16MB.')
    }), 413


if __name__ == '__main__':
    logger.info("Starting AI Sakhi - Voice-First Health Companion")
    logger.info(f"Available languages: {list(app.config['LANGUAGES'].keys())}")
    logger.info(f"Available modules: {list(health_modules.keys())}")
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=True
    )
