"""
Test suite for AI Sakhi SpeechProcessor class.

This module contains comprehensive tests for the SpeechProcessor class,
including speech-to-text conversion, text-to-speech synthesis, language detection,
and AWS integration functionality.

Requirements: 6.1, 6.2, 8.3
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.speech_processor import (
    SpeechProcessor, 
    VoiceProcessingResult, 
    create_speech_processor,
    validate_audio_data,
    get_language_fallback_chain
)


class TestVoiceProcessingResult:
    """Test cases for VoiceProcessingResult dataclass."""
    
    def test_voice_processing_result_creation(self):
        """Test creating a VoiceProcessingResult instance."""
        result = VoiceProcessingResult(
            success=True,
            text="Test transcription",
            language_code="hi",
            confidence_score=0.95
        )
        
        assert result.success is True
        assert result.text == "Test transcription"
        assert result.language_code == "hi"
        assert result.confidence_score == 0.95
    
    def test_voice_processing_result_to_dict(self):
        """Test converting VoiceProcessingResult to dictionary."""
        audio_data = b"test_audio_data"
        result = VoiceProcessingResult(
            success=True,
            text="Test text",
            audio_data=audio_data,
            language_code="en"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['text'] == "Test text"
        assert result_dict['language_code'] == "en"
        # Audio data should be base64 encoded
        assert 'audio_data' in result_dict
        assert isinstance(result_dict['audio_data'], str)
    
    def test_voice_processing_result_to_dict_no_audio(self):
        """Test converting VoiceProcessingResult to dictionary without audio data."""
        result = VoiceProcessingResult(
            success=True,
            text="Test text",
            language_code="en"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['audio_data'] is None


class TestSpeechProcessor:
    """Test cases for SpeechProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = SpeechProcessor(use_mock=True)
    
    def test_speech_processor_initialization(self):
        """Test SpeechProcessor initialization."""
        processor = SpeechProcessor(aws_region='us-west-2', use_mock=True)
        
        assert processor.aws_region == 'us-west-2'
        assert processor.use_mock is True
        assert processor.DEFAULT_LANGUAGE == 'hi'
        assert processor.FALLBACK_LANGUAGE == 'en'
        assert len(processor.SUPPORTED_LANGUAGES) == 6
    
    def test_supported_languages(self):
        """Test supported languages configuration."""
        languages = self.processor.get_supported_languages()
        
        assert len(languages) == 6
        
        # Check that all expected languages are present
        language_codes = [lang['code'] for lang in languages]
        expected_codes = ['hi', 'en', 'bn', 'ta', 'te', 'mr']
        
        for code in expected_codes:
            assert code in language_codes
        
        # Check Hindi configuration
        hindi_config = next(lang for lang in languages if lang['code'] == 'hi')
        assert hindi_config['name'] == 'Hindi'
        assert hindi_config['voice_id'] == 'Aditi'
        assert hindi_config['transcribe_code'] == 'hi-IN'
        assert hindi_config['polly_code'] == 'hi-IN'
    
    def test_is_language_supported(self):
        """Test language support checking."""
        # Supported languages
        assert self.processor.is_language_supported('hi') is True
        assert self.processor.is_language_supported('en') is True
        assert self.processor.is_language_supported('bn') is True
        
        # Unsupported languages
        assert self.processor.is_language_supported('fr') is False
        assert self.processor.is_language_supported('de') is False
        assert self.processor.is_language_supported('invalid') is False
    
    def test_language_detection_mock(self):
        """Test language detection with mock data."""
        test_audio = b"test_audio_data"
        detected_language = self.processor.detect_language(test_audio)
        
        # Mock detection should return default language
        assert detected_language == self.processor.DEFAULT_LANGUAGE
    
    def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        test_audio = b"test_audio_data_for_transcription"
        language_code = "hi"
        
        result = self.processor.transcribe_audio(test_audio, language_code)
        
        assert result.success is True
        assert result.text is not None
        assert result.language_code == language_code
        assert result.confidence_score > 0
        assert result.error_message is None
    
    def test_transcribe_audio_empty_data(self):
        """Test transcription with empty audio data."""
        result = self.processor.transcribe_audio(b"", "hi")
        
        assert result.success is False
        assert result.error_message is not None
        assert "Audio data cannot be empty" in result.error_message
    
    def test_transcribe_audio_unsupported_language(self):
        """Test transcription with unsupported language."""
        test_audio = b"test_audio_data"
        
        result = self.processor.transcribe_audio(test_audio, "unsupported_lang")
        
        # Should fallback to default language and succeed
        assert result.success is True
        assert result.language_code == self.processor.DEFAULT_LANGUAGE
    
    def test_synthesize_speech_success(self):
        """Test successful speech synthesis."""
        test_text = "Hello, this is a test message."
        language_code = "en"
        
        result = self.processor.synthesize_speech(test_text, language_code)
        
        assert result.success is True
        assert result.text == test_text
        assert result.language_code == language_code
        assert result.audio_url is not None
        assert result.audio_data is not None
        assert result.voice_id is not None
        assert result.error_message is None
    
    def test_synthesize_speech_empty_text(self):
        """Test synthesis with empty text."""
        result = self.processor.synthesize_speech("", "hi")
        
        assert result.success is False
        assert result.error_message is not None
        assert "Text cannot be empty" in result.error_message
    
    def test_synthesize_speech_whitespace_only(self):
        """Test synthesis with whitespace-only text."""
        result = self.processor.synthesize_speech("   ", "hi")
        
        assert result.success is False
        assert result.error_message is not None
    
    def test_synthesize_speech_unsupported_language(self):
        """Test synthesis with unsupported language."""
        test_text = "Test message"
        
        result = self.processor.synthesize_speech(test_text, "unsupported_lang")
        
        # Should fallback to default language and succeed
        assert result.success is True
        assert result.language_code == self.processor.DEFAULT_LANGUAGE
    
    def test_synthesize_speech_custom_voice(self):
        """Test synthesis with custom voice ID."""
        test_text = "Test message with custom voice"
        custom_voice = "CustomVoice"
        
        result = self.processor.synthesize_speech(test_text, "hi", custom_voice)
        
        assert result.success is True
        assert result.voice_id == custom_voice
    
    def test_process_voice_query_success(self):
        """Test successful end-to-end voice query processing."""
        test_audio = b"test_voice_query_audio_data"
        
        result = self.processor.process_voice_query(test_audio)
        
        assert result['success'] is True
        assert 'transcribed_text' in result
        assert 'language_code' in result
        assert 'confidence_score' in result
        assert 'processing_time_ms' in result
    
    def test_process_voice_query_with_language(self):
        """Test voice query processing with specified language."""
        test_audio = b"test_voice_query_audio_data"
        language_code = "en"
        
        result = self.processor.process_voice_query(test_audio, language_code)
        
        assert result['success'] is True
        assert result['language_code'] == language_code
    
    def test_process_voice_query_invalid_audio(self):
        """Test voice query processing with invalid audio."""
        result = self.processor.process_voice_query(b"")
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_available_voices(self):
        """Test getting available voices for languages."""
        # Test supported language
        voices_hi = self.processor.get_available_voices('hi')
        assert len(voices_hi) == 1
        assert voices_hi[0]['voice_id'] == 'Aditi'
        assert voices_hi[0]['language_code'] == 'hi-IN'
        
        voices_en = self.processor.get_available_voices('en')
        assert len(voices_en) == 1
        assert voices_en[0]['voice_id'] == 'Raveena'
        assert voices_en[0]['language_code'] == 'en-IN'
        
        # Test unsupported language
        voices_unsupported = self.processor.get_available_voices('fr')
        assert len(voices_unsupported) == 0
    
    def test_processing_stats(self):
        """Test processing statistics tracking."""
        # Clear stats first
        self.processor.clear_stats()
        
        # Perform some operations
        test_audio = b"test_audio_for_stats"
        self.processor.transcribe_audio(test_audio, "hi")
        self.processor.synthesize_speech("Test text", "en")
        
        stats = self.processor.get_processing_stats()
        
        assert stats['transcribe_requests'] >= 1
        assert stats['polly_requests'] >= 1
        assert stats['successful_transcriptions'] >= 1
        assert stats['successful_syntheses'] >= 1
        assert 'success_rate' in stats
        assert 'average_processing_time_ms' in stats
    
    def test_clear_stats(self):
        """Test clearing processing statistics."""
        # Perform some operations first
        test_audio = b"test_audio_for_clear_stats"
        self.processor.transcribe_audio(test_audio, "hi")
        
        # Clear stats
        self.processor.clear_stats()
        
        stats = self.processor.get_processing_stats()
        assert stats['transcribe_requests'] == 0
        assert stats['polly_requests'] == 0
        assert stats['successful_transcriptions'] == 0
        assert stats['successful_syntheses'] == 0
        assert stats['errors'] == 0
    
    def test_health_check(self):
        """Test system health check."""
        health_status = self.processor.health_check()
        
        assert 'timestamp' in health_status
        assert 'status' in health_status
        assert 'checks' in health_status
        
        # Check individual health checks
        checks = health_status['checks']
        assert 'language_detection' in checks
        assert 'transcription' in checks
        assert 'synthesis' in checks
        assert 'aws_connectivity' in checks
        assert 'language_support' in checks
        
        # In mock mode, AWS connectivity should be 'mock'
        assert checks['aws_connectivity']['status'] == 'mock'


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_create_speech_processor(self):
        """Test speech processor factory function."""
        processor = create_speech_processor(region='eu-west-1', use_mock=False)
        
        assert isinstance(processor, SpeechProcessor)
        assert processor.aws_region == 'eu-west-1'
        # Note: use_mock might be True if AWS connection fails in test environment
    
    def test_validate_audio_data_valid(self):
        """Test audio data validation with valid data."""
        valid_audio = b"valid_audio_data_sample"
        assert validate_audio_data(valid_audio) is True
    
    def test_validate_audio_data_empty(self):
        """Test audio data validation with empty data."""
        assert validate_audio_data(b"") is False
        assert validate_audio_data(None) is False
    
    def test_validate_audio_data_too_small(self):
        """Test audio data validation with too small data."""
        small_audio = b"small"  # Less than 10 bytes
        assert validate_audio_data(small_audio) is False
    
    def test_validate_audio_data_too_large(self):
        """Test audio data validation with too large data."""
        # Create data larger than 10MB
        large_audio = b"x" * (11 * 1024 * 1024)
        assert validate_audio_data(large_audio) is False
    
    def test_get_language_fallback_chain(self):
        """Test language fallback chain generation."""
        # Test Hindi (should not add Hindi again)
        chain_hi = get_language_fallback_chain('hi')
        assert chain_hi[0] == 'hi'
        assert 'en' in chain_hi
        
        # Test Bengali (should add Hindi as regional fallback)
        chain_bn = get_language_fallback_chain('bn')
        assert chain_bn[0] == 'bn'
        assert 'hi' in chain_bn
        assert 'en' in chain_bn
        
        # Test English (should not add English again)
        chain_en = get_language_fallback_chain('en')
        assert chain_en[0] == 'en'
        assert 'hi' in chain_en
        
        # Test unsupported language
        chain_fr = get_language_fallback_chain('fr')
        assert chain_fr[0] == 'fr'
        assert 'hi' in chain_fr
        assert 'en' in chain_fr


class TestMultiLanguageSupport:
    """Test cases for multi-language support features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = SpeechProcessor(use_mock=True)
    
    def test_all_supported_languages_transcription(self):
        """Test transcription for all supported languages."""
        test_audio = b"test_audio_data_for_all_languages"
        
        for language_code in self.processor.SUPPORTED_LANGUAGES.keys():
            result = self.processor.transcribe_audio(test_audio, language_code)
            
            assert result.success is True, f"Transcription failed for language: {language_code}"
            assert result.language_code == language_code
            assert result.text is not None
    
    def test_all_supported_languages_synthesis(self):
        """Test synthesis for all supported languages."""
        test_text = "Test message for synthesis"
        
        for language_code in self.processor.SUPPORTED_LANGUAGES.keys():
            result = self.processor.synthesize_speech(test_text, language_code)
            
            assert result.success is True, f"Synthesis failed for language: {language_code}"
            assert result.language_code == language_code
            assert result.text == test_text
    
    def test_language_specific_voices(self):
        """Test that each language has appropriate voice configuration."""
        for lang_code, config in self.processor.SUPPORTED_LANGUAGES.items():
            voices = self.processor.get_available_voices(lang_code)
            
            assert len(voices) > 0, f"No voices available for language: {lang_code}"
            assert voices[0]['voice_id'] == config['voice_id']


class TestErrorHandling:
    """Test cases for error handling and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = SpeechProcessor(use_mock=True)
    
    def test_transcription_error_handling(self):
        """Test error handling in transcription."""
        # Test with None audio data - should return error result, not raise exception
        result = self.processor.transcribe_audio(None, "hi")
        assert result.success is False
        assert result.error_message is not None
        
        # Test with invalid language code (should fallback gracefully)
        result = self.processor.transcribe_audio(b"test", "invalid")
        assert result.success is True  # Should fallback to default language
    
    def test_synthesis_error_handling(self):
        """Test error handling in synthesis."""
        # Test with None text - should return error result, not raise exception
        result = self.processor.synthesize_speech(None, "hi")
        assert result.success is False
        assert result.error_message is not None
        
        # Test with invalid language code (should fallback gracefully)
        result = self.processor.synthesize_speech("test", "invalid")
        assert result.success is True  # Should fallback to default language
    
    def test_voice_query_error_handling(self):
        """Test error handling in voice query processing."""
        # Test with None audio data
        result = self.processor.process_voice_query(None)
        assert result['success'] is False
        assert 'error' in result
    
    def test_exception_handling_in_health_check(self):
        """Test that health check handles exceptions gracefully."""
        # Health check should not raise exceptions
        health_status = self.processor.health_check()
        assert isinstance(health_status, dict)
        assert 'status' in health_status


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])