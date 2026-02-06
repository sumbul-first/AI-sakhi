#!/usr/bin/env python3
"""
Demo script for AI Sakhi SpeechProcessor class.

This script demonstrates the speech processing capabilities including:
- Speech-to-text conversion using AWS Transcribe
- Text-to-speech synthesis using AWS Polly
- Language detection and processing
- Multi-language support with fallback mechanisms
- Error handling and recovery

Requirements: 6.1, 6.2, 8.3
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.speech_processor import SpeechProcessor, create_speech_processor, validate_audio_data


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(result: Dict[str, Any], title: str = "Result") -> None:
    """Print formatted result."""
    print(f"\n{title}:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_language_detection():
    """Demonstrate language detection functionality."""
    print_header("Language Detection Demo")
    
    # Create speech processor
    processor = create_speech_processor(use_mock=True)
    
    # Test different audio samples (mock data)
    test_samples = [
        (b"short_audio_sample", "Short audio sample"),
        (b"medium_length_audio_sample_data", "Medium audio sample"),
        (b"longer_audio_sample_with_more_data_for_testing", "Long audio sample")
    ]
    
    for audio_data, description in test_samples:
        print(f"\nTesting {description}:")
        print(f"Audio data length: {len(audio_data)} bytes")
        
        detected_language = processor.detect_language(audio_data)
        print(f"Detected language: {detected_language}")
        
        # Check if language is supported
        is_supported = processor.is_language_supported(detected_language)
        print(f"Language supported: {is_supported}")


def demo_speech_transcription():
    """Demonstrate speech-to-text transcription."""
    print_header("Speech Transcription Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Test transcription in different languages
    test_cases = [
        (b"hello_audio_data", "hi", "Hindi greeting"),
        (b"puberty_question_audio", "en", "English puberty question"),
        (b"menstrual_health_query", "bn", "Bengali menstrual health query"),
        (b"pregnancy_nutrition_question", "ta", "Tamil pregnancy question"),
        (b"safety_information_request", "te", "Telugu safety question"),
        (b"government_schemes_query", "mr", "Marathi government schemes query")
    ]
    
    for audio_data, language_code, description in test_cases:
        print(f"\nTesting {description}:")
        print(f"Language: {language_code}")
        print(f"Audio data: {len(audio_data)} bytes")
        
        # Validate audio data
        is_valid = validate_audio_data(audio_data)
        print(f"Audio data valid: {is_valid}")
        
        if is_valid:
            # Perform transcription
            result = processor.transcribe_audio(audio_data, language_code)
            print_result(result.to_dict(), "Transcription Result")
        else:
            print("Skipping transcription due to invalid audio data")


def demo_text_to_speech():
    """Demonstrate text-to-speech synthesis."""
    print_header("Text-to-Speech Synthesis Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Test synthesis in different languages
    test_texts = [
        ("नमस्ते, मैं AI सखी हूं। मैं आपकी स्वास्थ्य संबंधी जानकारी में मदद कर सकती हूं।", "hi", "Hindi greeting"),
        ("Hello, I am AI Sakhi. I can help you with health-related information.", "en", "English greeting"),
        ("নমস্কার, আমি AI সখী। আমি আপনার স্বাস্থ্য সংক্রান্ত তথ্যে সাহায্য করতে পারি।", "bn", "Bengali greeting"),
        ("வணக்கம், நான் AI சகி. உங்கள் சுகாதார தகவல்களில் உதவ முடியும்.", "ta", "Tamil greeting"),
        ("నమస్కారం, నేను AI సఖి. మీ ఆరోగ్య సమాచారంలో సహాయం చేయగలను.", "te", "Telugu greeting"),
        ("नमस्कार, मी AI सखी आहे. मी तुमच्या आरोग्य माहितीत मदत करू शकते.", "mr", "Marathi greeting")
    ]
    
    for text, language_code, description in test_texts:
        print(f"\nTesting {description}:")
        print(f"Language: {language_code}")
        print(f"Text: {text}")
        
        # Get available voices for the language
        voices = processor.get_available_voices(language_code)
        print(f"Available voices: {voices}")
        
        # Perform synthesis
        result = processor.synthesize_speech(text, language_code)
        print_result(result.to_dict(), "Synthesis Result")


def demo_voice_query_processing():
    """Demonstrate end-to-end voice query processing."""
    print_header("Voice Query Processing Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Test complete voice processing workflow
    test_queries = [
        (b"puberty_education_query_audio", None, "Auto-detect language for puberty query"),
        (b"menstrual_health_question_audio", "hi", "Hindi menstrual health question"),
        (b"pregnancy_nutrition_query_audio", "en", "English pregnancy nutrition query"),
        (b"safety_awareness_question_audio", "bn", "Bengali safety awareness query"),
        (b"government_schemes_query_audio", "ta", "Tamil government schemes query")
    ]
    
    for audio_data, language_code, description in test_queries:
        print(f"\nTesting {description}:")
        print(f"Specified language: {language_code or 'Auto-detect'}")
        print(f"Audio data: {len(audio_data)} bytes")
        
        # Process voice query
        result = processor.process_voice_query(audio_data, language_code)
        print_result(result, "Voice Query Result")
        
        # If transcription was successful, demonstrate response synthesis
        if result.get('success') and result.get('transcribed_text'):
            print(f"\nGenerating response for: {result['transcribed_text']}")
            
            # Create a sample response
            response_text = f"आपका प्रश्न समझ में आया। मैं {result['transcribed_text']} के बारे में जानकारी दे सकती हूं।"
            
            # Synthesize response
            synthesis_result = processor.synthesize_speech(response_text, result['language_code'])
            print_result(synthesis_result.to_dict(), "Response Synthesis")


def demo_language_support():
    """Demonstrate language support features."""
    print_header("Language Support Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Show supported languages
    supported_languages = processor.get_supported_languages()
    print("\nSupported Languages:")
    for lang in supported_languages:
        print(f"  {lang['code']}: {lang['name']}")
        print(f"    Transcribe: {lang['transcribe_code']}")
        print(f"    Polly: {lang['polly_code']}")
        print(f"    Voice: {lang['voice_id']}")
        print()
    
    # Test language support checking
    test_languages = ['hi', 'en', 'bn', 'ta', 'te', 'mr', 'fr', 'de']
    
    print("Language Support Check:")
    for lang_code in test_languages:
        is_supported = processor.is_language_supported(lang_code)
        status = "✓ Supported" if is_supported else "✗ Not supported"
        print(f"  {lang_code}: {status}")


def demo_error_handling():
    """Demonstrate error handling and fallback mechanisms."""
    print_header("Error Handling Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Test with invalid inputs
    print("\nTesting error handling:")
    
    # Empty audio data
    print("\n1. Empty audio data:")
    result = processor.transcribe_audio(b"", "hi")
    print_result(result.to_dict(), "Empty Audio Result")
    
    # Invalid language code
    print("\n2. Invalid language code:")
    result = processor.transcribe_audio(b"test_audio", "invalid_lang")
    print_result(result.to_dict(), "Invalid Language Result")
    
    # Empty text for synthesis
    print("\n3. Empty text for synthesis:")
    result = processor.synthesize_speech("", "hi")
    print_result(result.to_dict(), "Empty Text Result")
    
    # Very long text
    print("\n4. Very long text:")
    long_text = "This is a very long text. " * 100
    result = processor.synthesize_speech(long_text, "en")
    print_result(result.to_dict(), "Long Text Result")


def demo_performance_stats():
    """Demonstrate performance statistics tracking."""
    print_header("Performance Statistics Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Perform several operations to generate stats
    print("Performing operations to generate statistics...")
    
    # Multiple transcriptions
    for i in range(5):
        audio_data = f"test_audio_sample_{i}".encode()
        processor.transcribe_audio(audio_data, "hi")
    
    # Multiple syntheses
    for i in range(3):
        text = f"Test message number {i}"
        processor.synthesize_speech(text, "en")
    
    # Get and display statistics
    stats = processor.get_processing_stats()
    print_result(stats, "Processing Statistics")


def demo_health_check():
    """Demonstrate system health check."""
    print_header("System Health Check Demo")
    
    processor = create_speech_processor(use_mock=True)
    
    # Perform health check
    health_status = processor.health_check()
    print_result(health_status, "Health Check Results")


def main():
    """Run all demonstrations."""
    print_header("AI Sakhi SpeechProcessor Demo")
    print("This demo showcases the speech processing capabilities of AI Sakhi")
    print("including multi-language support, error handling, and AWS integration.")
    
    try:
        # Run all demonstrations
        demo_language_detection()
        demo_speech_transcription()
        demo_text_to_speech()
        demo_voice_query_processing()
        demo_language_support()
        demo_error_handling()
        demo_performance_stats()
        demo_health_check()
        
        print_header("Demo Complete")
        print("All speech processing features demonstrated successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Multi-language speech recognition (Hindi, English, Bengali, Tamil, Telugu, Marathi)")
        print("✓ Text-to-speech synthesis with regional voices")
        print("✓ Language detection and fallback mechanisms")
        print("✓ End-to-end voice query processing")
        print("✓ Error handling and validation")
        print("✓ Performance monitoring and statistics")
        print("✓ System health checking")
        print("✓ AWS Transcribe and Polly integration (mock mode)")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)