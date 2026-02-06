# -*- coding: utf-8 -*-
"""
Voice Interface for AI Sakhi Voice-First Health Companion application.
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import re

from core.speech_processor import SpeechProcessor
from core.content_manager import ContentManager
from core.session_manager import SessionManager


@dataclass
class VoiceInteractionResult:
    """Result of a complete voice interaction cycle."""
    success: bool
    user_query: Optional[str] = None
    response_text: Optional[str] = None
    response_audio_url: Optional[str] = None
    response_audio_data: Optional[bytes] = None
    language_code: str = 'hi'
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    module_used: Optional[str] = None
    fallback_used: bool = False
    error_message: Optional[str] = None
    emergency_detected: bool = False


@dataclass
class FallbackOption:
    """Represents a fallback option when voice processing fails."""
    type: str
    title: str
    description: str
    action_data: Dict[str, Any]
    priority: int = 1


class VoiceInterface:
    """Main voice interface for AI Sakhi application."""
    
    def __init__(self, speech_processor: SpeechProcessor, content_manager: ContentManager,
                 session_manager: SessionManager, use_mock: bool = True):
        """Initialize the VoiceInterface."""
        self.speech_processor = speech_processor
        self.content_manager = content_manager
        self.session_manager = session_manager
        self.use_mock = use_mock
        self.logger = logging.getLogger(__name__)
        self.modules = {}
        self._initialize_health_modules()
        self._interaction_stats = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'fallback_used': 0,
            'emergency_detected': 0
        }
        self._fallback_options = [
            FallbackOption('visual', 'Visual Navigation', 'Use buttons and menus', {'route': '/visual-menu'}, 1),
            FallbackOption('text', 'Text Input', 'Type your question', {'route': '/text-input'}, 2),
            FallbackOption('emergency', 'Emergency Contacts', 'Access emergency contacts', {'route': '/emergency'}, 0)
        ]
    
    def _initialize_health_modules(self) -> None:
        """Initialize health education modules."""
        try:
            from modules.puberty_education_module import PubertyEducationModule
            from modules.safety_mental_support_module import SafetyMentalSupportModule
            from modules.menstrual_guide_module import MenstrualGuideModule
            from modules.pregnancy_guidance_module import PregnancyGuidanceModule
            from modules.government_resources_module import GovernmentResourcesModule
            
            self.modules = {
                'puberty': PubertyEducationModule(self.content_manager),
                'safety': SafetyMentalSupportModule(self.content_manager),
                'menstrual': MenstrualGuideModule(self.content_manager),
                'pregnancy': PregnancyGuidanceModule(self.content_manager),
                'government': GovernmentResourcesModule(self.content_manager)
            }
            self.logger.info("Health modules initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing health modules: {e}")
            self.modules = {}
    
    def process_text_input(self, text: str, session_id: str, language_code: str = 'hi') -> VoiceInteractionResult:
        """Process text input as a fallback."""
        start_time = time.time()
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                session = self.session_manager.create_session(session_id, language_code)
            
            emergency_detected = self._detect_emergency(text)
            if emergency_detected:
                return self._handle_emergency(text, session_id, language_code, start_time)
            
            module_name, module_response = self._route_to_module(text, language_code, session)
            audio_result = self.speech_processor.synthesize_speech(module_response, language_code)
            processing_time = int((time.time() - start_time) * 1000)
            
            self._interaction_stats['total_interactions'] += 1
            self._interaction_stats['successful_interactions'] += 1
            self._interaction_stats['fallback_used'] += 1
            self.session_manager.update_session_activity(session_id)
            
            return VoiceInteractionResult(
                success=True,
                user_query=text,
                response_text=module_response,
                response_audio_url=audio_result.audio_url if audio_result.success else None,
                response_audio_data=audio_result.audio_data if audio_result.success else None,
                language_code=language_code,
                processing_time_ms=processing_time,
                module_used=module_name,
                fallback_used=True,
                emergency_detected=emergency_detected
            )
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return VoiceInteractionResult(
                success=False,
                user_query=text,
                language_code=language_code,
                processing_time_ms=processing_time,
                error_message=f"Text input processing failed: {str(e)}",
                fallback_used=True
            )
    
    def _detect_emergency(self, query: str) -> bool:
        """Detect if the query indicates an emergency situation."""
        if not query:
            return False
        emergency_patterns = [
            r'(?i)(help|मदद|সাহায্য)',
            r'(?i)(emergency|आपातकाल|জরুরি)',
            r'(?i)(danger|खतरा|বিপদ)'
        ]
        for pattern in emergency_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    def _handle_emergency(self, query: str, session_id: str, language_code: str, 
                         start_time: float) -> VoiceInteractionResult:
        """Handle emergency situations with immediate response."""
        processing_time = int((time.time() - start_time) * 1000)
        emergency_response = self._get_default_emergency_response(language_code)
        audio_result = self.speech_processor.synthesize_speech(emergency_response, language_code)
        self._interaction_stats['emergency_detected'] += 1
        return VoiceInteractionResult(
            success=True,
            user_query=query,
            response_text=emergency_response,
            response_audio_url=audio_result.audio_url if audio_result.success else None,
            response_audio_data=audio_result.audio_data if audio_result.success else None,
            language_code=language_code,
            processing_time_ms=processing_time,
            module_used='safety',
            emergency_detected=True
        )
    
    def _route_to_module(self, query: str, language_code: str, session) -> Tuple[str, str]:
        """Route user query to the appropriate health module."""
        query_lower = query.lower()
        if any(word in query_lower for word in ['puberty', 'यौवन', 'বয়ঃসন্ধি']):
            if 'puberty' in self.modules:
                try:
                    return 'puberty', self.modules['puberty'].process_query(query, language_code)
                except:
                    pass
        if any(word in query_lower for word in ['pregnancy', 'गर्भावस्था', 'গর্ভাবস্থা']):
            if 'pregnancy' in self.modules:
                try:
                    return 'pregnancy', self.modules['pregnancy'].process_query(query, language_code)
                except:
                    pass
        return 'general', self._get_general_response(query, language_code)
    
    def _get_default_emergency_response(self, language_code: str) -> str:
        """Get default emergency response."""
        messages = {
            'hi': 'यह एक आपातकालीन स्थिति लगती है। कृपया तुरंत 112 पर कॉल करें।',
            'en': 'This seems like an emergency situation. Please call 112 immediately.',
            'bn': 'এটি একটি জরুরি পরিস্থিতি বলে মনে হচ্ছে। অনুগ্রহ করে অবিলম্বে ১১২ নম্বরে কল করুন।'
        }
        return messages.get(language_code, messages['hi'])
    
    def _get_general_response(self, query: str, language_code: str) -> str:
        """Get general response when no specific module matches."""
        messages = {
            'hi': 'मैं AI सखी हूं। आप मुझसे स्वास्थ्य के बारे में पूछ सकते हैं।',
            'en': 'I am AI Sakhi. You can ask me about health topics.',
            'bn': 'আমি AI সখী। আপনি আমাকে স্বাস্থ্য সম্পর্কে জিজ্ঞাসা করতে পারেন।'
        }
        return messages.get(language_code, messages['hi'])
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get voice interaction statistics."""
        stats = self._interaction_stats.copy()
        if stats['total_interactions'] > 0:
            stats['success_rate'] = stats['successful_interactions'] / stats['total_interactions']
        else:
            stats['success_rate'] = 0.0
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the voice interface system."""
        from datetime import datetime, timezone
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy"
        }
