#!/usr/bin/env python3
"""
Demo for VoiceInterface implementation.
"""

import sys
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class VoiceInteractionResult:
    """Result of a complete voice interaction cycle."""
    success: bool
    user_query: Optional[str] = None
    response_text: Optional[str] = None
    response_audio_url: Optional[str] = None
    language_code: str = 'hi'
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    module_used: Optional[str] = None
    fallback_used: bool = False
    error_message: Optional[str] = None
    emergency_detected: bool = False

class MockSpeechProcessor:
    """Mock speech processor for demo."""
    
    def __init__(self, use_mock=True):
        self.use_mock = use_mock
    
    def process_voice_query(self, audio_data: bytes, language_code: Optional[str] = None):
        """Mock voice query processing."""
        return {
            'success': True,
            'transcribed_text': 'मुझे यौवनावस्था के बारे में जानकारी चाहिए',
            'language_code': language_code or 'hi',
            'confidence_score': 0.95
        }
    
    def synthesize_speech(self, text: str, language_code: str):
        """Mock speech synthesis."""
        class MockResult:
            def __init__(self):
                self.success = True
                self.audio_url = f'https://ai-sakhi-content.s3.amazonaws.com/tts/{language_code}/response.mp3'
                self.audio_data = b'MOCK_AUDIO_DATA'
        
        return MockResult()
    
    def health_check(self):
        """Mock health check."""
        return {"status": "development"}

class MockContentManager:
    """Mock content manager for demo."""
    
    def __init__(self, use_mock=True):
        self.use_mock = use_mock
    
    def health_check(self):
        """Mock health check."""
        return {"status": "healthy"}

class MockSessionManager:
    """Mock session manager for demo."""
    
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id: str):
        """Get session."""
        return self.sessions.get(session_id)
    
    def create_session(self, session_id: str, language_code: str):
        """Create session."""
        class MockSession:
            def __init__(self, session_id, language_code):
                self.session_id = session_id
                self.language = language_code
        
        session = MockSession(session_id, language_code)
        self.sessions[session_id] = session
        return session
    
    def update_session_activity(self, session_id: str):
        """Update session activity."""
        pass
    
    def health_check(self):
        """Mock health check."""
        return {"status": "healthy"}

class MockHealthModule:
    """Mock health module for demo."""
    
    def __init__(self, content_manager):
        self.content_manager = content_manager
    
    def process_query(self, query: str, language_code: str) -> str:
        """Process query and return response."""
        responses = {
            'hi': 'यह यौवनावस्था के बारे में जानकारी है। यह एक प्राकृतिक प्रक्रिया है।',
            'en': 'This is information about puberty. It is a natural process.',
            'bn': 'এটি বয়ঃসন্ধি সম্পর্কে তথ্য। এটি একটি প্রাকৃতিক প্রক্রিয়া।'
        }
        return responses.get(language_code, responses['hi'])

class DemoVoiceInterface:
    """Demo voice interface implementation."""
    
    def __init__(self, speech_processor, content_manager, session_manager, use_mock=True):
        """Initialize the VoiceInterface."""
        self.speech_processor = speech_processor
        self.content_manager = content_manager
        self.session_manager = session_manager
        self.use_mock = use_mock
        
        # Initialize mock modules
        self.modules = {
            'puberty': MockHealthModule(content_manager),
            'safety': MockHealthModule(content_manager),
            'menstrual': MockHealthModule(content_manager),
            'pregnancy': MockHealthModule(content_manager),
            'government': MockHealthModule(content_manager)
        }
        
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
    
    def process_voice_input(self, audio_data: bytes, session_id: str, 
                          language_code: Optional[str] = None) -> VoiceInteractionResult:
        """Process voice input through the complete pipeline."""
        start_time = time.time()
        
        try:
            self._interaction_stats['total_interactions'] += 1
            
            # Get or create session
            session = self.session_manager.get_session(session_id)
            if not session:
                session = self.session_manager.create_session(session_id, language_code or 'hi')
            
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
                session = self.session_manager.create_session(session_id, language_code)
            
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
            language_code=language_code,
            processing_time_ms=processing_time,
            fallback_used=True,
            error_message=f"Voice processing failed: {error}"
        )
    
    def _detect_emergency(self, query: str) -> bool:
        """Detect if the query indicates an emergency situation."""
        if not query:
            return False
        
        emergency_keywords = ['help', 'emergency', 'danger', 'मदद', 'आपातकाल', 'खतरा']
        query_lower = query.lower()
        
        return any(keyword in query_lower for keyword in emergency_keywords)
    
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
            language_code=language_code,
            processing_time_ms=processing_time,
            module_used='safety',
            emergency_detected=True
        )
    
    def _route_to_module(self, query: str, language_code: str, session):
        """Route user query to the appropriate health module."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['puberty', 'यौवन', 'বয়ঃসন্ধি']):
            return 'puberty', self.modules['puberty'].process_query(query, language_code)
        elif any(word in query_lower for word in ['pregnancy', 'गर्भावस्था', 'গর্ভাবস্থা']):
            return 'pregnancy', self.modules['pregnancy'].process_query(query, language_code)
        elif any(word in query_lower for word in ['menstrual', 'मासिक', 'মাসিক']):
            return 'menstrual', self.modules['menstrual'].process_query(query, language_code)
        elif any(word in query_lower for word in ['government', 'सरकार', 'সরকার']):
            return 'government', self.modules['government'].process_query(query, language_code)
        else:
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
            'hi': 'यह एक आपातकालीन स्থिति लगती है। कृपया तुरंत 112 पर कॉल करें।',
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
            stats['fallback_rate'] = stats['fallback_used'] / stats['total_interactions']
            stats['emergency_rate'] = stats['emergency_detected'] / stats['total_interactions']
        else:
            stats['success_rate'] = 0.0
            stats['fallback_rate'] = 0.0
            stats['emergency_rate'] = 0.0
        
        stats['available_modules'] = list(self.modules.keys())
        
        return stats

def main():
    """Demo the voice interface functionality."""
    print("=== AI Sakhi Voice Interface Demo ===\n")
    
    try:
        # Create mock dependencies
        print("1. Creating mock dependencies...")
        speech_processor = MockSpeechProcessor(use_mock=True)
        content_manager = MockContentManager(use_mock=True)
        session_manager = MockSessionManager()
        print("   ✓ Mock dependencies created")
        
        # Create voice interface
        print("2. Creating voice interface...")
        voice_interface = DemoVoiceInterface(
            speech_processor=speech_processor,
            content_manager=content_manager,
            session_manager=session_manager,
            use_mock=True
        )
        print("   ✓ Voice interface created")
        
        # Test voice input processing
        print("3. Testing voice input processing...")
        test_audio = b"test_audio_data_for_voice_processing"
        session_id = "demo_session_123"
        
        result = voice_interface.process_voice_input(test_audio, session_id, 'hi')
        print(f"   ✓ Voice processing result: success={result.success}")
        print(f"   Query: {result.user_query}")
        print(f"   Response: {result.response_text[:100]}...")
        print(f"   Module: {result.module_used}")
        print(f"   Processing time: {result.processing_time_ms}ms")
        
        # Test text input fallback
        print("4. Testing text input fallback...")
        test_text = "मुझे गर्भावस्था के बारे में जानकारी चाहिए"
        
        result = voice_interface.process_text_input(test_text, session_id, 'hi')
        print(f"   ✓ Text processing result: success={result.success}")
        print(f"   Query: {result.user_query}")
        print(f"   Response: {result.response_text[:100]}...")
        print(f"   Module: {result.module_used}")
        print(f"   Fallback used: {result.fallback_used}")
        
        # Test emergency detection
        print("5. Testing emergency detection...")
        emergency_text = "help me please emergency"
        
        result = voice_interface.process_text_input(emergency_text, session_id, 'en')
        print(f"   ✓ Emergency detection result: emergency={result.emergency_detected}")
        print(f"   Response: {result.response_text[:100]}...")
        print(f"   Module: {result.module_used}")
        
        # Test statistics
        print("6. Testing statistics...")
        stats = voice_interface.get_interaction_stats()
        print(f"   ✓ Statistics collected:")
        print(f"   - Total interactions: {stats['total_interactions']}")
        print(f"   - Success rate: {stats['success_rate']:.2%}")
        print(f"   - Fallback rate: {stats['fallback_rate']:.2%}")
        print(f"   - Emergency rate: {stats['emergency_rate']:.2%}")
        print(f"   - Available modules: {stats['available_modules']}")
        
        print("\n=== Demo completed successfully! ===")
        print("\nThe voice interface implementation includes:")
        print("- Voice input processing with fallback mechanisms")
        print("- Multi-language support (Hindi, English, Bengali)")
        print("- Emergency detection and routing")
        print("- Module-based query routing")
        print("- Comprehensive error handling")
        print("- Statistics tracking")
        print("- Health check functionality")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)