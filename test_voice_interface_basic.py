#!/usr/bin/env python3
"""
Basic test for VoiceInterface implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.voice_interface import VoiceInterface, VoiceInteractionResult, FallbackOption
from core.speech_processor import SpeechProcessor
from core.content_manager import ContentManager
from core.session_manager import SessionManager

def test_voice_interface_creation():
    """Test that VoiceInterface can be created successfully."""
    print("Testing VoiceInterface creation...")
    
    # Create dependencies
    speech_processor = SpeechProcessor(use_mock=True)
    content_manager = ContentManager(use_mock=True)
    session_manager = SessionManager()
    
    # Create voice interface
    voice_interface = VoiceInterface(
        speech_processor=speech_processor,
        content_manager=content_manager,
        session_manager=session_manager,
        use_mock=True
    )
    
    print("✓ VoiceInterface created successfully")
    return voice_interface

def test_voice_processing():
    """Test voice input processing."""
    print("Testing voice input processing...")
    
    voice_interface = test_voice_interface_creation()
    
    # Test voice input
    test_audio = b"test_audio_data_for_voice_processing"
    session_id = "test_session_123"
    
    result = voice_interface.process_voice_input(test_audio, session_id, 'hi')
    
    assert isinstance(result, VoiceInteractionResult)
    assert result.success or result.fallback_used  # Should succeed or use fallback
    
    print(f"✓ Voice processing result: success={result.success}, fallback={result.fallback_used}")
    print(f"  Response: {result.response_text[:100] if result.response_text else 'None'}...")
    
    return result

def test_text_fallback():
    """Test text input fallback."""
    print("Testing text input fallback...")
    
    voice_interface = test_voice_interface_creation()
    
    # Test text input
    test_text = "मुझे यौवनावस्था के बारे में जानकारी चाहिए"
    session_id = "test_session_456"
    
    result = voice_interface.process_text_input(test_text, session_id, 'hi')
    
    assert isinstance(result, VoiceInteractionResult)
    assert result.success
    assert result.fallback_used  # Text input is always a fallback
    
    print(f"✓ Text fallback result: success={result.success}")
    print(f"  Module used: {result.module_used}")
    print(f"  Response: {result.response_text[:100] if result.response_text else 'None'}...")
    
    return result

def test_emergency_detection():
    """Test emergency detection."""
    print("Testing emergency detection...")
    
    voice_interface = test_voice_interface_creation()
    
    # Test emergency text
    emergency_text = "help me please emergency"
    session_id = "test_session_emergency"
    
    result = voice_interface.process_text_input(emergency_text, session_id, 'en')
    
    assert isinstance(result, VoiceInteractionResult)
    assert result.success
    assert result.emergency_detected
    
    print(f"✓ Emergency detection result: emergency={result.emergency_detected}")
    print(f"  Module used: {result.module_used}")
    print(f"  Response: {result.response_text[:100] if result.response_text else 'None'}...")
    
    return result

def test_fallback_options():
    """Test fallback options."""
    print("Testing fallback options...")
    
    voice_interface = test_voice_interface_creation()
    
    fallback_options = voice_interface.get_fallback_options('hi')
    
    assert isinstance(fallback_options, list)
    assert len(fallback_options) > 0
    
    print(f"✓ Found {len(fallback_options)} fallback options")
    for option in fallback_options:
        print(f"  - {option['type']}: {option['title']}")
    
    return fallback_options

def test_health_check():
    """Test health check functionality."""
    print("Testing health check...")
    
    voice_interface = test_voice_interface_creation()
    
    health_status = voice_interface.health_check()
    
    assert isinstance(health_status, dict)
    assert 'status' in health_status
    assert 'checks' in health_status
    
    print(f"✓ Health check result: {health_status['status']}")
    for check_name, check_result in health_status['checks'].items():
        print(f"  - {check_name}: {check_result['status']}")
    
    return health_status

def test_statistics():
    """Test statistics functionality."""
    print("Testing statistics...")
    
    voice_interface = test_voice_interface_creation()
    
    # Process some interactions first
    test_voice_processing()
    test_text_fallback()
    
    stats = voice_interface.get_interaction_stats()
    
    assert isinstance(stats, dict)
    assert 'total_interactions' in stats
    assert 'success_rate' in stats
    
    print(f"✓ Statistics collected:")
    print(f"  - Total interactions: {stats['total_interactions']}")
    print(f"  - Success rate: {stats['success_rate']:.2%}")
    print(f"  - Fallback rate: {stats['fallback_rate']:.2%}")
    
    return stats

def main():
    """Run all tests."""
    print("=== VoiceInterface Basic Tests ===\n")
    
    try:
        test_voice_interface_creation()
        print()
        
        test_voice_processing()
        print()
        
        test_text_fallback()
        print()
        
        test_emergency_detection()
        print()
        
        test_fallback_options()
        print()
        
        test_health_check()
        print()
        
        test_statistics()
        print()
        
        print("=== All Tests Passed! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)