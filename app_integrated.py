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

# Load .env file if present (for local development configuration)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on real env vars

# Import core components
try:
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
    from core.cloudwatch_logger import CloudWatchLogger
    from core.content_manager import ContentSyncMonitor
except ImportError as e:
    logger.error(f"Error importing core components: {e}")
    # Create minimal placeholder classes
    class SessionManager:
        def __init__(self, *args, **kwargs): 
            self.sessions = {}
        def create_session(self, language): 
            from dataclasses import dataclass
            @dataclass
            class Session:
                session_id: str = "mock-session"
            return Session()
        def update_session(self, *args, **kwargs): pass
        def get_active_session_count(self): return 0
        def get_session_count(self): return 0
    
    class ContentManager:
        def __init__(self, *args, **kwargs): pass
        def health_check(self): return {'status': 'mock'}
    
    class SpeechProcessor:
        def __init__(self, *args, **kwargs): pass
    
    class VoiceInterface:
        def __init__(self, *args, **kwargs): pass
        def health_check(self): return {'status': 'mock'}
        def get_interaction_stats(self): return {}
        def process_voice_input(self, *args, **kwargs):
            from dataclasses import dataclass
            @dataclass
            class Result:
                success: bool = False
                error_message: str = "Mock mode"
                user_query: str = ""
                response_text: str = ""
                response_audio_url: str = ""
                language_code: str = "hi"
                confidence_score: float = 0.0
                processing_time_ms: int = 0
                module_used: str = ""
                fallback_used: bool = False
                emergency_detected: bool = False
            return Result()
        def process_text_input(self, *args, **kwargs):
            return self.process_voice_input()
    
    class ReminderSystem:
        def __init__(self, *args, **kwargs): pass
        def health_check(self): return {'status': 'mock'}
        def get_user_reminders(self, *args): return []
        def get_upcoming_reminders(self, *args, **kwargs): return []
        def get_reminder_statistics(self, *args): return {}
        def create_reminder(self, *args, **kwargs):
            from dataclasses import dataclass
            @dataclass
            class Reminder:
                def to_dict(self): return {}
            return Reminder()
        def create_prenatal_appointment_reminder(self, *args, **kwargs):
            return self.create_reminder()
    
    class ReminderType:
        pass
    
    class ContentSafetyValidator:
        def __init__(self, *args, **kwargs): pass
        def health_check(self): return {'status': 'mock'}
        def validate_system_response(self, text, lang):
            from dataclasses import dataclass
            @dataclass
            class Validation:
                is_safe: bool = True
                detected_issues: list = None
                requires_medical_referral: bool = False
                def __post_init__(self):
                    if self.detected_issues is None:
                        self.detected_issues = []
            return Validation()
        def validate_user_query(self, text, lang):
            return self.validate_system_response(text, lang)
        def sanitize_response(self, text, lang):
            return text, False
    
    class ErrorHandler:
        def __init__(self, *args, **kwargs): pass
        def handle_error(self, error, context, lang):
            from dataclasses import dataclass
            @dataclass
            class ErrorResponse:
                user_message: str = "An error occurred"
                recovery_options: list = None
                def __post_init__(self):
                    if self.recovery_options is None:
                        self.recovery_options = []
            return ErrorResponse()
    
    class GracefulDegradation:
        pass
    
    class OfflineEmergencyAccess:
        @staticmethod
        def get_contacts(lang):
            return [
                {
                    'type': 'helpline',
                    'phone': '181',
                    'region': 'India',
                    'languages': ['Hindi', 'English'],
                    'hours': '24/7',
                    'description': 'Women Helpline'
                }
            ]
    
    def handle_errors(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class ErrorCategory:
        pass

    class CloudWatchLogger:
        def __init__(self, *args, **kwargs): pass
        def log_interaction(self, *args, **kwargs): pass
        def log_error(self, *args, **kwargs): pass
        def log_session_event(self, *args, **kwargs): pass
        def health_check(self): return {'status': 'mock', 'mode': 'mock'}

    class ContentSyncMonitor:
        def __init__(self, *args, **kwargs): pass
        def get_sync_status(self): return {'status': 'mock', 'last_check': None, 'last_sync': None, 'content_counts': {}, 'is_stale': True}
        def check_for_updates(self): return False
        def force_sync(self): return self.get_sync_status()
        def start_background_monitoring(self): pass
        def stop_background_monitoring(self): pass

# Import health modules
try:
    from modules.puberty_education_module import PubertyEducationModule
    from modules.safety_mental_support_module import SafetyMentalSupportModule
    from modules.menstrual_guide_module import MenstrualGuideModule
    from modules.pregnancy_guidance_module import PregnancyGuidanceModule
    from modules.government_resources_module import GovernmentResourcesModule
except ImportError as e:
    logger.error(f"Error importing health modules: {e}")
    # Create placeholder classes if imports fail
    class PubertyEducationModule:
        def __init__(self, *args, **kwargs): pass
        def get_module_info(self): return {'name': 'Puberty Education', 'description': 'Mock module'}
        def get_module_topics(self, lang): return []
    class SafetyMentalSupportModule:
        def __init__(self, *args, **kwargs): pass
        def get_module_info(self): return {'name': 'Safety & Mental Support', 'description': 'Mock module'}
        def get_module_topics(self, lang): return []
        def get_emergency_resources(self, lang): return []
    class MenstrualGuideModule:
        def __init__(self, *args, **kwargs): pass
        def get_module_info(self): return {'name': 'Menstrual Guide', 'description': 'Mock module'}
        def get_module_topics(self, lang): return []
    class PregnancyGuidanceModule:
        def __init__(self, *args, **kwargs): pass
        def get_module_info(self): return {'name': 'Pregnancy Guidance', 'description': 'Mock module'}
        def get_module_topics(self, lang): return []
    class GovernmentResourcesModule:
        def __init__(self, *args, **kwargs): pass
        def get_module_info(self): return {'name': 'Government Resources', 'description': 'Mock module'}
        def get_module_topics(self, lang): return []

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-sakhi-dev-key-change-in-production')
app.config['PORT'] = 8080
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'ai_sakhi_session'

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
    # 1. Flask session (set server-side on language change - most trusted)
    if 'language' in session:
        lang = session['language']
        if lang in app.config['LANGUAGES']:
            return lang
    # 2. Cookie set by explicit user action via /language/<code> endpoint
    lang_cookie = request.cookies.get('preferred_language')
    if lang_cookie and lang_cookie in app.config['LANGUAGES']:
        session['language'] = lang_cookie
        return lang_cookie
    # 3. Default to Hindi
    session['language'] = 'hi'
    return 'hi'

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
    s3_bucket_name=os.environ.get('S3_BUCKET_NAME', 'ai-sakhi-content'),
    aws_region=os.environ.get('AWS_REGION', 'us-east-1'),
    use_mock=os.environ.get('USE_MOCK', 'true').lower() == 'true'
)

# Speech Processor
speech_processor = SpeechProcessor(
    aws_region=os.environ.get('AWS_REGION', 'us-east-1'),
    use_mock=os.environ.get('USE_MOCK', 'true').lower() == 'true'
)

# Voice Interface
voice_interface = VoiceInterface(
    speech_processor=speech_processor,
    content_manager=content_manager,
    session_manager=session_manager,
    use_mock=os.environ.get('USE_MOCK', 'true').lower() == 'true'
)

# Reminder System
reminder_system = ReminderSystem()

# Content Safety Validator
content_safety_validator = ContentSafetyValidator()

# Error Handler
error_handler = ErrorHandler()

# CloudWatch Logger (mock mode for development)
cloudwatch_logger = CloudWatchLogger(
    log_group=os.environ.get('CLOUDWATCH_LOG_GROUP', '/ai-sakhi/application'),
    aws_region=os.environ.get('AWS_REGION', 'us-east-1'),
    use_mock=os.environ.get('USE_MOCK', 'true').lower() == 'true'
)

# Content Sync Monitor
sync_monitor = ContentSyncMonitor(content_manager, cloudwatch_logger)

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
    # Auto-reset language to Hindi if it was never explicitly set by the user.
    # We track explicit user choice with the 'language_explicitly_set' flag.
    if not session.get('language_explicitly_set') and session.get('language') == 'ta':
        session['language'] = 'hi'
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
        
        # Check CloudWatch logger
        cw_health = cloudwatch_logger.health_check()
        health_status['components']['cloudwatch_logger'] = cw_health

        # Check content sync monitor
        health_status['components']['content_sync'] = sync_monitor.get_sync_status()

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


@app.route('/modules/<module_name>')
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
        
        # Log the interaction to CloudWatch
        cloudwatch_logger.log_interaction(
            session_id=session_id,
            query=result.user_query or '',
            response=result.response_text or '',
            language=result.language_code,
            module_used=result.module_used or '',
            processing_time_ms=result.processing_time_ms or 0
        )

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
        cloudwatch_logger.log_error(
            error_type='voice_processing_error',
            error_message=str(e),
            context_data={'route': '/api/voice/process'}
        )
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to process voice input')
        }), 500


@app.route('/api/text/process', methods=['POST'])
def process_text():
    """Process text input as fallback."""
    try:
        session_id = get_or_create_session_id()
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': gettext('No text provided')
            }), 400
        
        # Language priority: request body > Flask session > cookie > default
        language_code = (
            data.get('language') or
            session.get('language') or
            request.cookies.get('preferred_language') or
            'hi'
        )
        # Strip speech code suffix if sent (e.g. 'hi-IN' -> 'hi')
        if '-' in language_code:
            language_code = language_code.split('-')[0]
        if language_code not in app.config.get('LANGUAGES', {}):
            language_code = 'hi'
        
        user_text = data['text']
        logger.info(f"Processing text input: {user_text[:50]}... (language: {language_code})")
        
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
        
        logger.info(f"Processing result - success: {result.success}, response: {result.response_text[:50] if result.response_text else 'None'}")
        
        # Validate and sanitize response
        response_text = result.response_text
        if result.success and response_text:
            sanitized = validate_and_sanitize_response(
                response_text,
                result.language_code
            )
            response_text = sanitized['text']
        elif not response_text:
            # Provide a default response if none was generated
            response_text = gettext('I am AI Sakhi. How can I help you with your health questions?')
        
        # Log the interaction to CloudWatch
        cloudwatch_logger.log_interaction(
            session_id=session_id,
            query=user_text,
            response=response_text,
            language=result.language_code,
            module_used=result.module_used or '',
            processing_time_ms=result.processing_time_ms or 0
        )

        return jsonify({
            'status': 'success' if result.success else 'error',
            'user_query': result.user_query or user_text,
            'response_text': response_text,
            'response_audio_url': result.response_audio_url,
            'language_code': result.language_code,
            'processing_time_ms': result.processing_time_ms,
            'module_used': result.module_used,
            'emergency_detected': result.emergency_detected,
            'requires_medical_referral': query_validation.requires_medical_referral,
            'error_message': result.error_message
        })
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}", exc_info=True)
        cloudwatch_logger.log_error(
            error_type='text_processing_error',
            error_message=str(e),
            context_data={'route': '/api/text/process'}
        )
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to process text input'),
            'error_details': str(e)
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
        
        # Set the new language and make session permanent
        session['language'] = language_code
        session['language_explicitly_set'] = True
        session.permanent = True
        
        # Update session manager
        session_manager.update_session(session_id, language_preference=language_code)
        
        logger.info(f"Language changed to: {language_code} ({app.config['LANGUAGES'][language_code]}) for session {session_id}")
        
        resp = jsonify({
            'status': 'success',
            'language': language_code,
            'language_name': app.config['LANGUAGES'][language_code],
            'message': gettext('Language changed successfully')
        })
        # Set a persistent cookie so get_locale() can read it even after session expiry
        resp.set_cookie('preferred_language', language_code, max_age=60*60*24*30, samesite='Lax')
        return resp
        
    except Exception as e:
        logger.error(f"Error changing language to {language_code}: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': gettext('Failed to change language')
        }), 500


@app.route('/language/reset', methods=['GET', 'POST'])
def reset_language():
    """Reset language preference to Hindi (default)."""
    session.pop('language', None)
    session.pop('language_explicitly_set', None)
    session['language'] = 'hi'
    session.permanent = True
    resp = jsonify({'status': 'success', 'language': 'hi'})
    resp.set_cookie('preferred_language', 'hi', max_age=60*60*24*30, samesite='Lax')
    return resp


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


@app.route('/api/content/sync/status')
def content_sync_status():
    """Return current content synchronization status."""
    return jsonify(sync_monitor.get_sync_status())


@app.route('/api/content/sync/force', methods=['POST'])
def content_sync_force():
    """Force an immediate content synchronization."""
    result = sync_monitor.force_sync()
    return jsonify(result)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    cloudwatch_logger.log_error(
        error_type='http_404',
        error_message=str(error),
        context_data={'path': request.path}
    )
    return render_template('error.html', 
                         error_code=404,
                         error_message=gettext('Page not found')), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    cloudwatch_logger.log_error(
        error_type='http_500',
        error_message=str(error),
        context_data={'path': request.path}
    )
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
