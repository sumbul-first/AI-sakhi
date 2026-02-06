"""
Speech Processor for AI Sakhi Voice-First Health Companion application.

This module provides the SpeechProcessor class that handles speech-to-text conversion
using AWS Transcribe, text-to-speech synthesis using AWS Polly, and language detection
for multi-language support in the voice-first interface.

Requirements: 6.1, 6.2, 8.3
"""

import boto3
import json
import logging
import time
import io
import base64
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
import threading
from dataclasses import dataclass, asdict


@dataclass
class VoiceProcessingResult:
    """
    Result of voice processing operations.
    
    This class encapsulates the results of speech-to-text or text-to-speech
    operations with metadata about the processing.
    """
    success: bool
    text: Optional[str] = None
    audio_url: Optional[str] = None
    audio_data: Optional[bytes] = None
    language_code: str = 'hi'
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    voice_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert bytes to base64 string for JSON serialization
        if result.get('audio_data') is not None:
            result['audio_data'] = base64.b64encode(result['audio_data']).decode('utf-8')
        return result


class SpeechProcessor:
    """
    Manages speech recognition and synthesis for AI Sakhi application.
    
    This class provides methods for converting speech to text using AWS Transcribe,
    synthesizing speech from text using AWS Polly, and detecting languages for
    multi-language support. Includes error handling and fallback mechanisms.
    """
    
    # Supported languages with their AWS service codes
    SUPPORTED_LANGUAGES = {
        'hi': {
            'transcribe_code': 'hi-IN',
            'polly_code': 'hi-IN',
            'voice_id': 'Aditi',
            'name': 'Hindi'
        },
        'en': {
            'transcribe_code': 'en-IN',
            'polly_code': 'en-IN',
            'voice_id': 'Raveena',
            'name': 'English (India)'
        },
        'bn': {
            'transcribe_code': 'bn-IN',
            'polly_code': 'hi-IN',  # Fallback to Hindi for Polly
            'voice_id': 'Aditi',
            'name': 'Bengali'
        },
        'ta': {
            'transcribe_code': 'ta-IN',
            'polly_code': 'hi-IN',  # Fallback to Hindi for Polly
            'voice_id': 'Aditi',
            'name': 'Tamil'
        },
        'te': {
            'transcribe_code': 'te-IN',
            'polly_code': 'hi-IN',  # Fallback to Hindi for Polly
            'voice_id': 'Aditi',
            'name': 'Telugu'
        },
        'mr': {
            'transcribe_code': 'hi-IN',  # Fallback to Hindi for Transcribe
            'polly_code': 'hi-IN',  # Fallback to Hindi for Polly
            'voice_id': 'Aditi',
            'name': 'Marathi'
        }
    }
    
    DEFAULT_LANGUAGE = 'hi'
    FALLBACK_LANGUAGE = 'en'
    
    def __init__(self, aws_region: str = 'us-east-1', use_mock: bool = True):
        """
        Initialize the SpeechProcessor.
        
        Args:
            aws_region: AWS region for Transcribe and Polly operations
            use_mock: Whether to use mock operations for development
        """
        self.aws_region = aws_region
        self.use_mock = use_mock
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize AWS clients
        self._transcribe_client = None
        self._polly_client = None
        self._initialize_aws_clients()
        
        # Processing statistics
        self._processing_stats = {
            'transcribe_requests': 0,
            'polly_requests': 0,
            'successful_transcriptions': 0,
            'successful_syntheses': 0,
            'errors': 0,
            'total_processing_time_ms': 0
        }
        self._stats_lock = threading.Lock()
        
        # Mock responses for development
        self._mock_transcriptions = self._initialize_mock_transcriptions()
        self._mock_audio_responses = self._initialize_mock_audio_responses()
    
    def _initialize_aws_clients(self) -> None:
        """Initialize AWS Transcribe and Polly clients with error handling."""
        if self.use_mock:
            self.logger.info("Using mock speech processing operations for development")
            return
        
        try:
            # Initialize Transcribe client
            self._transcribe_client = boto3.client('transcribe', region_name=self.aws_region)
            
            # Initialize Polly client
            self._polly_client = boto3.client('polly', region_name=self.aws_region)
            
            # Test connections
            self._polly_client.describe_voices(LanguageCode='hi-IN')
            
            self.logger.info("Successfully connected to AWS Transcribe and Polly services")
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Using mock operations.")
            self.use_mock = True
        except ClientError as e:
            self.logger.error(f"AWS service connection error: {e}. Using mock operations.")
            self.use_mock = True
        except Exception as e:
            self.logger.error(f"Unexpected error initializing AWS clients: {e}. Using mock operations.")
            self.use_mock = True
    
    def _initialize_mock_transcriptions(self) -> Dict[str, Dict[str, str]]:
        """Initialize mock transcription responses for development."""
        return {
            'hi': {
                'greeting': 'नमस्ते, मैं AI सखी हूं। मैं आपकी स्वास्थ्य संबंधी जानकारी में मदद कर सकती हूं।',
                'puberty_question': 'मुझे यौवनावस्था के बारे में जानकारी चाहिए।',
                'menstrual_question': 'मासिक धर्म के दौरान क्या सावधानियां बरतनी चाहिए?',
                'pregnancy_question': 'गर्भावस्था में पोषण के बारे में बताएं।',
                'safety_question': 'व्यक्तिगत सुरक्षा के बारे में जानकारी दें।',
                'government_question': 'सरकारी स्वास्थ्य योजनाओं के बारे में बताएं।'
            },
            'en': {
                'greeting': 'Hello, I am AI Sakhi. I can help you with health-related information.',
                'puberty_question': 'I need information about puberty.',
                'menstrual_question': 'What precautions should be taken during menstruation?',
                'pregnancy_question': 'Tell me about nutrition during pregnancy.',
                'safety_question': 'Give me information about personal safety.',
                'government_question': 'Tell me about government health schemes.'
            },
            'bn': {
                'greeting': 'নমস্কার, আমি AI সখী। আমি আপনার স্বাস্থ্য সংক্রান্ত তথ্যে সাহায্য করতে পারি।',
                'puberty_question': 'আমার বয়ঃসন্ধি সম্পর্কে তথ্য দরকার।',
                'menstrual_question': 'মাসিকের সময় কী সতর্কতা অবলম্বন করা উচিত?',
                'pregnancy_question': 'গর্ভাবস্থায় পুষ্টি সম্পর্কে বলুন।',
                'safety_question': 'ব্যক্তিগত নিরাপত্তা সম্পর্কে তথ্য দিন।',
                'government_question': 'সরকারি স্বাস্থ্য প্রকল্প সম্পর্কে বলুন।'
            },
            'ta': {
                'greeting': 'வணக்கம், நான் AI சகி. உங்கள் சுகாதார தகவல்களில் உதவ முடியும்.',
                'puberty_question': 'எனக்கு பருவமடைதல் பற்றிய தகவல் வேண்டும்.',
                'menstrual_question': 'மாதவிடாய் காலத்தில் என்ன முன்னெச்சரிக்கைகள் எடுக்க வேண்டும்?',
                'pregnancy_question': 'கர்ப்ப காலத்தில் ஊட்டச்சத்து பற்றி சொல்லுங்கள்.',
                'safety_question': 'தனிப்பட்ட பாதுகாப்பு பற்றிய தகவல் கொடுங்கள்.',
                'government_question': 'அரசு சுகாதார திட்டங்கள் பற்றி சொல்லுங்கள்.'
            },
            'te': {
                'greeting': 'నమస్కారం, నేను AI సఖి. మీ ఆరోగ్య సమాచారంలో సహాయం చేయగలను.',
                'puberty_question': 'నాకు యుక్తవయస్సు గురించి సమాచారం కావాలి.',
                'menstrual_question': 'మాసిక ధర్మ సమయంలో ఏ జాగ్రత్తలు తీసుకోవాలి?',
                'pregnancy_question': 'గర్భధారణ సమయంలో పోషణ గురించి చెప్పండి.',
                'safety_question': 'వ్యక్తిగత భద్రత గురించి సమాచారం ఇవ్వండి.',
                'government_question': 'ప్రభుత్వ ఆరోగ్య పథకాల గురించి చెప్పండి.'
            },
            'mr': {
                'greeting': 'नमस्कार, मी AI सखी आहे. मी तुमच्या आरोग्य माहितीत मदत करू शकते.',
                'puberty_question': 'मला तारुण्यावस्थेबद्दल माहिती हवी.',
                'menstrual_question': 'मासिक पाळीच्या वेळी कोणती काळजी घ्यावी?',
                'pregnancy_question': 'गर्भधारणेदरम्यान पोषणाबद्दल सांगा.',
                'safety_question': 'वैयक्तिक सुरक्षेबद्दल माहिती द्या.',
                'government_question': 'सरकारी आरोग्य योजनांबद्दल सांगा.'
            }
        }
    
    def _initialize_mock_audio_responses(self) -> Dict[str, str]:
        """Initialize mock audio response URLs for development."""
        return {
            'hi': 'https://ai-sakhi-content.s3.amazonaws.com/tts/hi/response.mp3',
            'en': 'https://ai-sakhi-content.s3.amazonaws.com/tts/en/response.mp3',
            'bn': 'https://ai-sakhi-content.s3.amazonaws.com/tts/bn/response.mp3',
            'ta': 'https://ai-sakhi-content.s3.amazonaws.com/tts/ta/response.mp3',
            'te': 'https://ai-sakhi-content.s3.amazonaws.com/tts/te/response.mp3',
            'mr': 'https://ai-sakhi-content.s3.amazonaws.com/tts/mr/response.mp3'
        }
    
    def _update_stats(self, operation: str, success: bool, processing_time_ms: int) -> None:
        """Update processing statistics."""
        with self._stats_lock:
            if operation == 'transcribe':
                self._processing_stats['transcribe_requests'] += 1
                if success:
                    self._processing_stats['successful_transcriptions'] += 1
            elif operation == 'polly':
                self._processing_stats['polly_requests'] += 1
                if success:
                    self._processing_stats['successful_syntheses'] += 1
            
            if not success:
                self._processing_stats['errors'] += 1
            
            self._processing_stats['total_processing_time_ms'] += processing_time_ms
    
    def detect_language(self, audio_data: bytes) -> str:
        """
        Detect the language of spoken audio.
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            Detected language code (defaults to Hindi if detection fails)
        """
        start_time = time.time()
        
        try:
            if self.use_mock:
                # Mock language detection - return default language
                detected_language = self.DEFAULT_LANGUAGE
                self.logger.info(f"Mock language detection: {detected_language}")
            else:
                # Real language detection would use AWS Transcribe with multiple language codes
                # For now, return default language
                detected_language = self.DEFAULT_LANGUAGE
                self.logger.warning("Real language detection not implemented, using default language")
            
            processing_time = int((time.time() - start_time) * 1000)
            self.logger.info(f"Language detection completed in {processing_time}ms: {detected_language}")
            
            return detected_language
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"Language detection failed: {e}")
            return self.DEFAULT_LANGUAGE
    
    def transcribe_audio(self, audio_data: bytes, language_code: str) -> VoiceProcessingResult:
        """
        Convert speech to text using AWS Transcribe.
        
        Args:
            audio_data: Raw audio data in bytes
            language_code: Language code for transcription
            
        Returns:
            VoiceProcessingResult with transcription results
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not audio_data:
                raise ValueError("Audio data cannot be empty")
            
            if language_code not in self.SUPPORTED_LANGUAGES:
                self.logger.warning(f"Unsupported language: {language_code}, using default")
                language_code = self.DEFAULT_LANGUAGE
            
            # Get AWS language code
            aws_language_code = self.SUPPORTED_LANGUAGES[language_code]['transcribe_code']
            
            if self.use_mock:
                # Mock transcription
                transcribed_text = self._get_mock_transcription(audio_data, language_code)
                confidence_score = 0.95
                
                result = VoiceProcessingResult(
                    success=True,
                    text=transcribed_text,
                    language_code=language_code,
                    confidence_score=confidence_score,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
                
                self.logger.info(f"Mock transcription completed: {language_code}")
                
            else:
                # Real AWS Transcribe implementation
                result = self._perform_real_transcription(audio_data, aws_language_code, language_code, start_time)
            
            # Update statistics
            self._update_stats('transcribe', result.success, result.processing_time_ms)
            
            return result
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_msg = f"Transcription failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Update statistics
            self._update_stats('transcribe', False, processing_time)
            
            return VoiceProcessingResult(
                success=False,
                language_code=language_code,
                processing_time_ms=processing_time,
                error_message=error_msg
            )
    
    def _get_mock_transcription(self, audio_data: bytes, language_code: str) -> str:
        """Get mock transcription based on audio data characteristics."""
        # Simple mock logic based on audio data length
        audio_length = len(audio_data)
        
        mock_responses = self._mock_transcriptions.get(language_code, self._mock_transcriptions['hi'])
        
        if audio_length < 1000:
            return mock_responses.get('greeting', 'नमस्ते')
        elif audio_length < 2000:
            return mock_responses.get('puberty_question', 'स्वास्थ्य की जानकारी चाहिए')
        elif audio_length < 3000:
            return mock_responses.get('menstrual_question', 'मासिक धर्म के बारे में बताएं')
        elif audio_length < 4000:
            return mock_responses.get('pregnancy_question', 'गर्भावस्था की जानकारी दें')
        elif audio_length < 5000:
            return mock_responses.get('safety_question', 'सुरक्षा के बारे में बताएं')
        else:
            return mock_responses.get('government_question', 'सरकारी योजनाओं के बारे में बताएं')
    
    def _perform_real_transcription(self, audio_data: bytes, aws_language_code: str, 
                                  language_code: str, start_time: float) -> VoiceProcessingResult:
        """Perform real AWS Transcribe operation."""
        try:
            # This is a placeholder for real AWS Transcribe implementation
            # Real implementation would:
            # 1. Upload audio to S3 or use streaming transcription
            # 2. Start transcription job or stream
            # 3. Wait for results
            # 4. Parse and return transcription
            
            # For now, return a placeholder result
            processing_time = int((time.time() - start_time) * 1000)
            
            return VoiceProcessingResult(
                success=False,
                language_code=language_code,
                processing_time_ms=processing_time,
                error_message="Real AWS Transcribe implementation not yet available"
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return VoiceProcessingResult(
                success=False,
                language_code=language_code,
                processing_time_ms=processing_time,
                error_message=f"AWS Transcribe error: {str(e)}"
            )
    
    def synthesize_speech(self, text: str, language_code: str, voice_id: Optional[str] = None) -> VoiceProcessingResult:
        """
        Convert text to speech using AWS Polly.
        
        Args:
            text: Text to convert to speech
            language_code: Language code for synthesis
            voice_id: Optional specific voice ID (uses default if None)
            
        Returns:
            VoiceProcessingResult with synthesis results
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            if language_code not in self.SUPPORTED_LANGUAGES:
                self.logger.warning(f"Unsupported language: {language_code}, using default")
                language_code = self.DEFAULT_LANGUAGE
            
            # Get voice configuration
            lang_config = self.SUPPORTED_LANGUAGES[language_code]
            aws_language_code = lang_config['polly_code']
            selected_voice_id = voice_id or lang_config['voice_id']
            
            if self.use_mock:
                # Mock synthesis
                result = self._get_mock_synthesis(text, language_code, selected_voice_id, start_time)
                self.logger.info(f"Mock synthesis completed: {language_code}")
                
            else:
                # Real AWS Polly implementation
                result = self._perform_real_synthesis(text, aws_language_code, selected_voice_id, language_code, start_time)
            
            # Update statistics
            self._update_stats('polly', result.success, result.processing_time_ms)
            
            return result
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_msg = f"Speech synthesis failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Update statistics
            self._update_stats('polly', False, processing_time)
            
            return VoiceProcessingResult(
                success=False,
                language_code=language_code,
                voice_id=voice_id,
                processing_time_ms=processing_time,
                error_message=error_msg
            )
    
    def _get_mock_synthesis(self, text: str, language_code: str, voice_id: str, start_time: float) -> VoiceProcessingResult:
        """Get mock synthesis result."""
        # Simulate processing time based on text length
        text_length = len(text)
        simulated_delay = min(text_length / 100, 2.0)  # Max 2 seconds
        time.sleep(simulated_delay)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Generate mock audio URL
        audio_url = self._mock_audio_responses.get(language_code, self._mock_audio_responses['hi'])
        
        # Generate mock audio data (placeholder)
        mock_audio_data = b"MOCK_AUDIO_DATA_" + text.encode('utf-8')[:50]
        
        return VoiceProcessingResult(
            success=True,
            text=text,
            audio_url=audio_url,
            audio_data=mock_audio_data,
            language_code=language_code,
            voice_id=voice_id,
            processing_time_ms=processing_time
        )
    
    def _perform_real_synthesis(self, text: str, aws_language_code: str, voice_id: str, 
                              language_code: str, start_time: float) -> VoiceProcessingResult:
        """Perform real AWS Polly synthesis."""
        try:
            if not self._polly_client:
                raise Exception("Polly client not initialized")
            
            # Synthesize speech
            response = self._polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                LanguageCode=aws_language_code
            )
            
            # Get audio data
            audio_data = response['AudioStream'].read()
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return VoiceProcessingResult(
                success=True,
                text=text,
                audio_data=audio_data,
                language_code=language_code,
                voice_id=voice_id,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return VoiceProcessingResult(
                success=False,
                text=text,
                language_code=language_code,
                voice_id=voice_id,
                processing_time_ms=processing_time,
                error_message=f"AWS Polly error: {str(e)}"
            )
    
    def process_voice_query(self, audio_data: bytes, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        End-to-end voice processing: transcribe audio and prepare for response.
        
        Args:
            audio_data: Raw audio data in bytes
            language_code: Optional language code (auto-detected if None)
            
        Returns:
            Dictionary containing processing results and metadata
        """
        start_time = time.time()
        
        try:
            # Detect language if not provided
            if not language_code:
                language_code = self.detect_language(audio_data)
            
            # Transcribe audio
            transcription_result = self.transcribe_audio(audio_data, language_code)
            
            if not transcription_result.success:
                return {
                    'success': False,
                    'error': transcription_result.error_message,
                    'language_code': language_code,
                    'processing_time_ms': int((time.time() - start_time) * 1000)
                }
            
            # Prepare response data
            total_processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'success': True,
                'transcribed_text': transcription_result.text,
                'language_code': language_code,
                'confidence_score': transcription_result.confidence_score,
                'processing_time_ms': total_processing_time,
                'transcription_time_ms': transcription_result.processing_time_ms
            }
            
            self.logger.info(f"Voice query processed successfully in {total_processing_time}ms")
            return result
            
        except Exception as e:
            total_processing_time = int((time.time() - start_time) * 1000)
            error_msg = f"Voice query processing failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'language_code': language_code or self.DEFAULT_LANGUAGE,
                'processing_time_ms': total_processing_time
            }
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages with their details.
        
        Returns:
            List of dictionaries containing language information
        """
        return [
            {
                'code': code,
                'name': config['name'],
                'transcribe_code': config['transcribe_code'],
                'polly_code': config['polly_code'],
                'voice_id': config['voice_id']
            }
            for code, config in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported for speech processing.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_available_voices(self, language_code: str) -> List[Dict[str, str]]:
        """
        Get available voices for a specific language.
        
        Args:
            language_code: Language code
            
        Returns:
            List of available voice configurations
        """
        if language_code not in self.SUPPORTED_LANGUAGES:
            return []
        
        config = self.SUPPORTED_LANGUAGES[language_code]
        return [{
            'voice_id': config['voice_id'],
            'language_code': config['polly_code'],
            'language_name': config['name']
        }]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get speech processing statistics.
        
        Returns:
            Dictionary containing processing statistics
        """
        with self._stats_lock:
            stats = self._processing_stats.copy()
            
            # Calculate derived metrics
            total_requests = stats['transcribe_requests'] + stats['polly_requests']
            if total_requests > 0:
                stats['success_rate'] = (stats['successful_transcriptions'] + stats['successful_syntheses']) / total_requests
                stats['average_processing_time_ms'] = stats['total_processing_time_ms'] / total_requests
            else:
                stats['success_rate'] = 0.0
                stats['average_processing_time_ms'] = 0.0
            
            stats.update({
                'supported_languages': len(self.SUPPORTED_LANGUAGES),
                'default_language': self.DEFAULT_LANGUAGE,
                'fallback_language': self.FALLBACK_LANGUAGE,
                'use_mock': self.use_mock,
                'aws_region': self.aws_region
            })
            
            return stats
    
    def clear_stats(self) -> None:
        """Clear processing statistics."""
        with self._stats_lock:
            self._processing_stats = {
                'transcribe_requests': 0,
                'polly_requests': 0,
                'successful_transcriptions': 0,
                'successful_syntheses': 0,
                'errors': 0,
                'total_processing_time_ms': 0
            }
        
        self.logger.info("Processing statistics cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the speech processing system.
        
        Returns:
            Dictionary containing health check results
        """
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        try:
            # Test language detection
            test_audio = b"test_audio_data"
            detected_lang = self.detect_language(test_audio)
            
            health_status["checks"]["language_detection"] = {
                "status": "healthy" if detected_lang in self.SUPPORTED_LANGUAGES else "degraded",
                "details": f"Detected language: {detected_lang}"
            }
            
            # Test transcription
            transcription_result = self.transcribe_audio(test_audio, self.DEFAULT_LANGUAGE)
            
            health_status["checks"]["transcription"] = {
                "status": "healthy" if transcription_result.success else "unhealthy",
                "details": f"Transcription test: {'passed' if transcription_result.success else 'failed'}"
            }
            
            # Test synthesis
            synthesis_result = self.synthesize_speech("Test message", self.DEFAULT_LANGUAGE)
            
            health_status["checks"]["synthesis"] = {
                "status": "healthy" if synthesis_result.success else "unhealthy",
                "details": f"Synthesis test: {'passed' if synthesis_result.success else 'failed'}"
            }
            
            # Check AWS connectivity (if not using mock)
            if not self.use_mock:
                if self._transcribe_client and self._polly_client:
                    health_status["checks"]["aws_connectivity"] = {
                        "status": "healthy",
                        "details": "AWS Transcribe and Polly clients initialized"
                    }
                else:
                    health_status["checks"]["aws_connectivity"] = {
                        "status": "unhealthy",
                        "details": "AWS clients not properly initialized"
                    }
                    health_status["status"] = "degraded"
            else:
                health_status["checks"]["aws_connectivity"] = {
                    "status": "mock",
                    "details": "Using mock speech processing operations"
                }
            
            # Check supported languages
            supported_count = len(self.SUPPORTED_LANGUAGES)
            health_status["checks"]["language_support"] = {
                "status": "healthy" if supported_count >= 6 else "degraded",
                "details": f"Supporting {supported_count} languages: {list(self.SUPPORTED_LANGUAGES.keys())}"
            }
            
            # Overall status
            unhealthy_checks = [
                check for check in health_status["checks"].values()
                if check["status"] == "unhealthy"
            ]
            
            if unhealthy_checks:
                health_status["status"] = "unhealthy"
            elif any(check["status"] in ["mock", "degraded"] for check in health_status["checks"].values()):
                health_status["status"] = "development"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status


# Utility functions for speech processing

def create_speech_processor(region: str = 'us-east-1', use_mock: bool = True) -> SpeechProcessor:
    """
    Factory function to create a SpeechProcessor instance with default settings.
    
    Args:
        region: AWS region for speech services
        use_mock: Whether to use mock operations for development
        
    Returns:
        Configured SpeechProcessor instance
    """
    return SpeechProcessor(aws_region=region, use_mock=use_mock)


def validate_audio_data(audio_data: bytes) -> bool:
    """
    Validate audio data for speech processing.
    
    Args:
        audio_data: Raw audio data to validate
        
    Returns:
        True if audio data is valid for processing
    """
    try:
        if not audio_data:
            return False
        
        # Basic validation - check minimum size (relaxed for demo)
        if len(audio_data) < 10:  # Minimum 10 bytes for demo
            return False
        
        # Check maximum size (10MB limit)
        if len(audio_data) > 10 * 1024 * 1024:
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error validating audio data: {e}")
        return False


def get_language_fallback_chain(language_code: str) -> List[str]:
    """
    Get fallback language chain for a given language.
    
    Args:
        language_code: Primary language code
        
    Returns:
        List of language codes in fallback order
    """
    fallback_chain = [language_code]
    
    # Add regional fallbacks
    if language_code in ['bn', 'ta', 'te', 'mr']:
        fallback_chain.append('hi')  # Hindi as regional fallback
    
    # Add English as universal fallback
    if 'en' not in fallback_chain:
        fallback_chain.append('en')
    
    # Add Hindi as final fallback if not already present
    if 'hi' not in fallback_chain:
        fallback_chain.append('hi')
    
    return fallback_chain