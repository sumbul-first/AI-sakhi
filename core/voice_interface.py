# -*- coding: utf-8 -*-
"""
Voice Interface for AI Sakhi Voice-First Health Companion application.

This module provides the VoiceInterface class that handles voice input processing
with error handling, fallback mechanisms, and natural language query processing.

Requirements: 6.2, 6.5
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
        
        # Initialize modules
        self.modules = {}
        self._initialize_health_modules()
        
        # Statistics
        self._interaction_stats = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'fallback_used': 0,
            'emergency_detected': 0,
            'module_usage': {},
            'language_usage': {},
            'average_processing_time_ms': 0.0
        }
        
        # Fallback options
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
                'puberty': PubertyEducationModule(self.content_manager, self.session_manager),
                'safety': SafetyMentalSupportModule(self.content_manager, self.session_manager),
                'menstrual': MenstrualGuideModule(self.content_manager, self.session_manager),
                'pregnancy': PregnancyGuidanceModule(self.content_manager, self.session_manager),
                'government': GovernmentResourcesModule(self.content_manager, self.session_manager)
            }
            self.logger.info("Health modules initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing health modules: {e}")
            self.modules = {}

    
    def process_voice_input(self, audio_data: bytes, session_id: str, 
                          language_code: Optional[str] = None) -> VoiceInteractionResult:
        """Process voice input through the complete pipeline."""
        start_time = time.time()
        
        try:
            self._interaction_stats['total_interactions'] += 1
            
            # Get or create session
            session = self.session_manager.get_session(session_id)
            if not session:
                session = self.session_manager.create_session(language_code or 'hi')
            
            # Process voice query
            voice_result = self.speech_processor.process_voice_query(audio_data, language_code)
            
            if not voice_result['success']:
                return self._handle_voice_processing_failure(
                    voice_result.get('error', 'Unknown error'), session_id, 
                    language_code or session.language, start_time
                )
            
            # Extract results
            user_query = voice_result['transcribed_text']
            detected_language = voice_result['language_code']
            confidence_score = voice_result.get('confidence_score', 0.0)
            
            # Check for emergency
            emergency_detected = self._detect_emergency(user_query)
            if emergency_detected:
                return self._handle_emergency(user_query, session_id, detected_language, start_time)
            
            # Route to module
            module_name, module_response = self._route_to_module(user_query, detected_language, session)
            
            # Generate audio response
            audio_result = self.speech_processor.synthesize_speech(module_response, detected_language)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = VoiceInteractionResult(
                success=True,
                user_query=user_query,
                response_text=module_response,
                response_audio_url=audio_result.audio_url if audio_result.success else None,
                response_audio_data=audio_result.audio_data if audio_result.success else None,
                language_code=detected_language,
                confidence_score=confidence_score,
                processing_time_ms=processing_time,
                module_used=module_name,
                fallback_used=False,
                emergency_detected=emergency_detected
            )
            
            # Update statistics
            self._interaction_stats['successful_interactions'] += 1
            self.session_manager.update_session_activity(session_id)
            
            return result
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_msg = f"Voice interaction failed: {str(e)}"
            self.logger.error(error_msg)
            
            return VoiceInteractionResult(
                success=False,
                language_code=language_code or 'hi',
                processing_time_ms=processing_time,
                error_message=error_msg,
                fallback_used=True
            )

    
    def process_text_input(self, text: str, session_id: str, language_code: str = 'hi') -> VoiceInteractionResult:
        """Process text input as a fallback."""
        start_time = time.time()
        
        try:
            # Get or create session
            session = self.session_manager.get_session(session_id)
            if not session:
                session = self.session_manager.create_session(language_code)
            
            # Check for emergency
            emergency_detected = self._detect_emergency(text)
            if emergency_detected:
                return self._handle_emergency(text, session_id, language_code, start_time)
            
            # Route to module
            module_name, module_response = self._route_to_module(text, language_code, session)
            
            # Generate audio response
            audio_result = self.speech_processor.synthesize_speech(module_response, language_code)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = VoiceInteractionResult(
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
            
            # Update statistics
            self._interaction_stats['total_interactions'] += 1
            self._interaction_stats['successful_interactions'] += 1
            self._interaction_stats['fallback_used'] += 1
            self.session_manager.update_session_activity(session_id)
            
            return result
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_msg = f"Text input processing failed: {str(e)}"
            self.logger.error(error_msg)
            
            return VoiceInteractionResult(
                success=False,
                user_query=text,
                language_code=language_code,
                processing_time_ms=processing_time,
                error_message=error_msg,
                fallback_used=True
            )
    
    def _handle_voice_processing_failure(self, error: str, session_id: str, 
                                       language_code: str, start_time: float) -> VoiceInteractionResult:
        """Handle voice processing failures with fallback mechanisms."""
        processing_time = int((time.time() - start_time) * 1000)
        
        fallback_message = self._get_fallback_message(language_code)
        audio_result = self.speech_processor.synthesize_speech(fallback_message, language_code)
        
        self._interaction_stats['fallback_used'] += 1
        
        return VoiceInteractionResult(
            success=True,
            response_text=fallback_message,
            response_audio_url=audio_result.audio_url if audio_result.success else None,
            response_audio_data=audio_result.audio_data if audio_result.success else None,
            language_code=language_code,
            processing_time_ms=processing_time,
            fallback_used=True,
            error_message=f"Voice processing failed: {error}"
        )

    
    def _detect_emergency(self, query: str) -> bool:
        """Detect if the query indicates an emergency situation."""
        if not query:
            return False
        
        emergency_patterns = [
            r'(?i)(help|मदद|সাহায্য|உதவி|సహాయం|मदत)',
            r'(?i)(emergency|आपातकाल|জরুরি|அவசரம்|అత్యవసర|आपत्कालीन)',
            r'(?i)(danger|खतरा|বিপদ|ஆபத்து|ప్రమాదం|धोका)'
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
        self.logger.warning(f"Emergency detected in session {session_id}: {query}")
        
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
        """Route user query to the appropriate health module or AI model."""
        # Try to use Amazon Bedrock AI for intelligent response
        try:
            bedrock_response = self._get_bedrock_response(query, language_code)
            if bedrock_response:
                self.logger.info(f"Using Bedrock AI response for query: {query[:50]}...")
                return 'ai_bedrock', bedrock_response
        except Exception as e:
            self.logger.warning(f"Bedrock AI failed, falling back to pattern matching: {e}")

        # If not mock mode and Bedrock failed, use mock response as graceful fallback
        # (better than a generic one-liner)
        if not self.use_mock:
            self.logger.info("Bedrock unavailable - using mock response as fallback")
            return 'ai_bedrock_fallback', self._get_mock_bedrock_response(query, language_code)
        
        # Fallback to simple pattern matching for module routing
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['puberty', 'यौवन', 'বয়ঃসন্ধি']):
            if 'puberty' in self.modules:
                try:
                    response = self.modules['puberty'].process_query(query, language_code)
                    return 'puberty', response
                except:
                    pass
        
        if any(word in query_lower for word in ['pregnancy', 'गर्भावस्था', 'গর্ভাবস্থা']):
            if 'pregnancy' in self.modules:
                try:
                    response = self.modules['pregnancy'].process_query(query, language_code)
                    return 'pregnancy', response
                except:
                    pass
        
        if any(word in query_lower for word in ['menstrual', 'मासिक', 'মাসিক']):
            if 'menstrual' in self.modules:
                try:
                    response = self.modules['menstrual'].process_query(query, language_code)
                    return 'menstrual', response
                except:
                    pass
        
        if any(word in query_lower for word in ['government', 'सरकार', 'সরকার']):
            if 'government' in self.modules:
                try:
                    response = self.modules['government'].process_query(query, language_code)
                    return 'government', response
                except:
                    pass
        
        # Default general response
        return 'general', self._get_general_response(query, language_code)

    
    def _get_fallback_message(self, language_code: str) -> str:
        """Get fallback message when voice processing fails."""
        messages = {
            'hi': 'मुझे आपकी आवाज़ समझने में कठिनाई हो रही है। कृपया फिर से कोशिश करें।',
            'en': 'I am having trouble understanding your voice. Please try again.',
            'bn': 'আমি আপনার কণ্ঠস্বর বুঝতে সমস্যা হচ্ছে। অনুগ্রহ করে আবার চেষ্টা করুন।'
        }
        return messages.get(language_code, messages['hi'])
    
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
    
    def get_fallback_options(self, language_code: str = 'hi') -> List[Dict[str, Any]]:
        """Get available fallback options for the user."""
        sorted_options = sorted(self._fallback_options, key=lambda x: x.priority)
        return [asdict(option) for option in sorted_options]
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get voice interaction statistics."""
        stats = self._interaction_stats.copy()
        
        if stats['total_interactions'] > 0:
            stats['success_rate'] = stats['successful_interactions'] / stats['total_interactions']
            stats['fallback_rate'] = stats['fallback_used'] / stats['total_interactions']
            stats['emergency_rate'] = stats['emergency_detected'] / stats['total_interactions']
        else:
            stats['success_rate'] = 0.0
            stats['fallback_rate'] = 0.0
            stats['emergency_rate'] = 0.0
        
        stats['available_modules'] = list(self.modules.keys())
        stats['fallback_options_count'] = len(self._fallback_options)
        
        return stats
    
    def _get_bedrock_response(self, query: str, language_code: str) -> Optional[str]:
        """Get response from Amazon Bedrock."""
        try:
            import boto3
            import json
            import os

            # Check if we're in mock mode
            if self.use_mock:
                self.logger.info("Using mock mode for Bedrock - returning simulated response")
                return self._get_mock_bedrock_response(query, language_code)

            aws_region = os.environ.get('AWS_REGION', 'us-east-1')

            # Reuse cached client to avoid re-auth overhead
            if not hasattr(self, '_bedrock_client') or self._bedrock_client is None:
                self._bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=aws_region
                )
                self.logger.info(f"Bedrock client initialized in region {aws_region}")
            
            # Language-specific system prompts
            system_prompts = {
                'hi': '''तुम AI सखी हो, एक महिला स्वास्थ्य सहायक। महिलाओं और लड़कियों को स्वास्थ्य शिक्षा प्रदान करो।

नियम:
1. कभी चिकित्सा निदान न दें
2. गंभीर लक्षणों के लिए डॉक्टर से परामर्श की सलाह दें
3. सरल भाषा का उपयोग करें
4. 2-3 वाक्यों में उत्तर दें''',
                
                'en': '''You are AI Sakhi, a women's health companion. Provide health education to women and girls.

Rules:
1. Never provide medical diagnosis
2. Recommend doctor for serious symptoms
3. Use simple language
4. Answer in 2-3 sentences''',
                
                'bn': '''তুমি AI সখী, মহিলা স্বাস্থ্য সহায়ক। মহিলা এবং মেয়েদের স্বাস্থ্য শিক্ষা দাও।

নিয়ম:
1. চিকিৎসা নির্ণয় দিও না
2. গুরুতর লক্ষণের জন্য ডাক্তারের পরামর্শ দাও
3. সহজ ভাষা ব্যবহার কর
4. ২-৩ বাক্যে উত্তর দাও'''
            }
            
            system_prompt = system_prompts.get(language_code, system_prompts['en'])
            
            # Use Claude 3 Haiku (fast and cost-effective)
            model_id = "anthropic.claude-3-haiku-20240307-v1:0"
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{system_prompt}\n\nप्रश्न: {query}\n\nउत्तर:"
                    }
                ]
            }
            
            response = self._bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                self.logger.info(f"Bedrock response received for language: {language_code}")
                return response_body['content'][0]['text'].strip()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Amazon Bedrock error (will NOT fall back to mock): {e}", exc_info=True)
            # Reset cached client so next call retries fresh
            self._bedrock_client = None
            return None
    
    def _get_mock_bedrock_response(self, query: str, language_code: str) -> str:
        """Generate mock Bedrock response for development."""
        mock_responses = {
            'hi': {
                'default': 'मैं AI सखी हूं। मैं आपकी मदद के लिए यहां हूं। आप स्वास्थ्य से जुड़े कोई भी सवाल पूछ सकते हैं।',
                'puberty': 'यौवन प्राकृतिक है। शरीर में बदलाव सामान्य हैं। स्वच्छता महत्वपूर्ण है।',
                'pregnancy': 'गर्भावस्था में पौष्टिक भोजन और नियमित जांच जरूरी है।',
                'menstrual': 'मासिक धर्म में स्वच्छता बनाए रखें। पैड या कप का उपयोग करें।',
                'safety': 'आपकी सुरक्षा महत्वपूर्ण है। खतरे में 112 या 181 पर कॉल करें।'
            },
            'en': {
                'default': 'I am AI Sakhi. I am here to help you with health questions.',
                'puberty': 'Puberty is natural. Body changes are normal. Hygiene is important.',
                'pregnancy': 'During pregnancy, eat nutritious food and get regular checkups.',
                'menstrual': 'Maintain hygiene during menstruation. Use pads or cups.',
                'safety': 'Your safety is important. In danger, call 112 or 181.'
            },
            'bn': {
                'default': 'আমি AI সখী। আমি আপনার স্বাস্থ্য প্রশ্নে সাহায্য করতে এখানে আছি।',
                'puberty': 'বয়ঃসন্ধি স্বাভাবিক। শরীরের পরিবর্তন স্বাভাবিক। পরিচ্ছন্নতা গুরুত্বপূর্ণ।',
                'pregnancy': 'গর্ভাবস্থায় পুষ্টিকর খাবার এবং নিয়মিত চেকআপ প্রয়োজন।',
                'menstrual': 'মাসিকের সময় পরিচ্ছন্নতা বজায় রাখুন। প্যাড বা কাপ ব্যবহার করুন।',
                'safety': 'আপনার নিরাপত্তা গুরুত্বপূর্ণ। বিপদে 112 বা 181 নম্বরে কল করুন।'
            },
            'ta': {
                'default': 'நான் AI சகி. உங்கள் சுகாதார கேள்விகளுக்கு உதவ இங்கே இருக்கிறேன்.',
                'puberty': 'பருவமடைதல் இயற்கையானது. உடல் மாற்றங்கள் சாதாரணமானவை. சுகாதாரம் முக்கியம்.',
                'pregnancy': 'கர்ப்ப காலத்தில் சத்தான உணவு மற்றும் வழக்கமான பரிசோதனை அவசியம்.',
                'menstrual': 'மாதவிடாய் நேரத்தில் சுகாதாரம் பராமரிக்கவும். பேட் அல்லது கப் பயன்படுத்தவும்.',
                'safety': 'உங்கள் பாதுகாப்பு முக்கியம். ஆபத்தில் 112 அல்லது 181 அழைக்கவும்.'
            },
            'te': {
                'default': 'నేను AI సఖి. మీ ఆరోగ్య ప్రశ్నలకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను.',
                'puberty': 'యుక్తవయస్సు సహజమైనది. శరీర మార్పులు సాధారణమైనవి. పరిశుభ్రత ముఖ్యం.',
                'pregnancy': 'గర్భధారణ సమయంలో పోషకాహారం మరియు క్రమం తప్పకుండా తనిఖీలు అవసరం.',
                'menstrual': 'మాసిక ధర్మ సమయంలో పరిశుభ్రత పాటించండి. ప్యాడ్ లేదా కప్ వాడండి.',
                'safety': 'మీ భద్రత ముఖ్యం. ప్రమాదంలో 112 లేదా 181 కి కాల్ చేయండి.'
            },
            'mr': {
                'default': 'मी AI सखी आहे. मी तुमच्या आरोग्य प्रश्नांसाठी मदत करण्यासाठी येथे आहे.',
                'puberty': 'तारुण्यावस्था नैसर्गिक आहे. शरीरातील बदल सामान्य आहेत. स्वच्छता महत्त्वाची आहे.',
                'pregnancy': 'गर्भधारणेदरम्यान पौष्टिक अन्न आणि नियमित तपासणी आवश्यक आहे.',
                'menstrual': 'मासिक पाळीत स्वच्छता राखा. पॅड किंवा कप वापरा.',
                'safety': 'तुमची सुरक्षा महत्त्वाची आहे. धोक्यात 112 किंवा 181 वर कॉल करा.'
            }
        }
        
        query_lower = query.lower()
        topic = 'default'
        
        if any(word in query_lower for word in ['puberty', 'यौवन', 'বয়ঃসন্ধি', 'பருவம்', 'యుక్తవయస్సు', 'तारुण्य']):
            topic = 'puberty'
        elif any(word in query_lower for word in ['pregnancy', 'गर्भ', 'গর্ভ', 'கர்ப்ப', 'గర్భ', 'गर्भधारण']):
            topic = 'pregnancy'
        elif any(word in query_lower for word in ['menstrual', 'मासिक', 'মাসিক', 'மாதவிடாய்', 'మాసిక', 'period']):
            topic = 'menstrual'
        elif any(word in query_lower for word in ['safety', 'सुरक्षा', 'নিরাপত্তা', 'பாதுகாப்பு', 'భద్రత', 'help', 'मदद']):
            topic = 'safety'
        
        responses = mock_responses.get(language_code, mock_responses['en'])
        return responses.get(topic, responses['default'])
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the voice interface system."""
        from datetime import datetime, timezone
        
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        try:
            # Check speech processor
            speech_health = self.speech_processor.health_check()
            health_status["checks"]["speech_processor"] = {
                "status": speech_health["status"],
                "details": f"Speech processing: {speech_health['status']}"
            }
            
            # Check modules
            healthy_modules = len([m for m in self.modules.values() if m])
            health_status["checks"]["health_modules"] = {
                "status": "healthy" if healthy_modules > 0 else "degraded",
                "details": f"{healthy_modules} modules available"
            }
            
            # Check fallback options
            health_status["checks"]["fallback_options"] = {
                "status": "healthy" if len(self._fallback_options) >= 3 else "degraded",
                "details": f"{len(self._fallback_options)} fallback options available"
            }
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Voice interface health check failed: {e}")
        
        return health_status


# Utility functions
def create_voice_interface(speech_processor: SpeechProcessor, content_manager: ContentManager,
                          session_manager: SessionManager, use_mock: bool = True) -> VoiceInterface:
    """Factory function to create a VoiceInterface instance."""
    return VoiceInterface(speech_processor, content_manager, session_manager, use_mock)


def validate_voice_input(audio_data: bytes) -> bool:
    """Validate voice input data."""
    try:
        if not audio_data or len(audio_data) < 10 or len(audio_data) > 10 * 1024 * 1024:
            return False
        return True
    except Exception:
        return False
