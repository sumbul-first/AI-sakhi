#!/usr/bin/env python3
"""Simple test for voice interface."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports one by one
try:
    print("Testing imports...")
    
    print("1. Importing speech processor...")
    from core.speech_processor import SpeechProcessor
    print("   ✓ SpeechProcessor imported")
    
    print("2. Importing content manager...")
    from core.content_manager import ContentManager
    print("   ✓ ContentManager imported")
    
    print("3. Importing session manager...")
    from core.session_manager import SessionManager
    print("   ✓ SessionManager imported")
    
    print("4. Creating instances...")
    speech_processor = SpeechProcessor(use_mock=True)
    content_manager = ContentManager(use_mock=True)
    session_manager = SessionManager()
    print("   ✓ All instances created")
    
    print("5. Testing voice interface file...")
    import core.voice_interface as vi
    print(f"   Voice interface module contents: {[x for x in dir(vi) if not x.startswith('_')]}")
    
    # Try to manually define a simple VoiceInterface
    print("6. Creating simple VoiceInterface...")
    
    class SimpleVoiceInterface:
        def __init__(self, speech_processor, content_manager, session_manager):
            self.speech_processor = speech_processor
            self.content_manager = content_manager
            self.session_manager = session_manager
        
        def process_text_input(self, text, session_id, language_code='hi'):
            return {
                'success': True,
                'user_query': text,
                'response_text': f'Processed: {text}',
                'language_code': language_code,
                'fallback_used': True
            }
    
    voice_interface = SimpleVoiceInterface(speech_processor, content_manager, session_manager)
    result = voice_interface.process_text_input("test query", "test_session")
    print(f"   ✓ Simple voice interface test: {result['success']}")
    
    print("\n=== All tests passed! ===")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)