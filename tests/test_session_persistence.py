"""
Property-based tests for session state persistence in AI Sakhi system.

**Feature: sakhi-saathi-ai, Property 15: Session State Persistence**
**Validates: Requirements 8.5**

This module tests that session state persists correctly across all interactions
within a session, including serialization/deserialization, language switching,
module navigation, and emergency contact updates.
"""

import json
import pytest
import time
from datetime import datetime, timezone, timedelta
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite
from models.data_models import UserSession


# Test data generation strategies
@composite
def valid_language_codes(draw):
    """Generate valid language codes (ISO 639-1 format)."""
    base_codes = ['en', 'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml', 'or', 'pa', 'ur']
    return draw(st.sampled_from(base_codes))


@composite
def valid_module_names(draw):
    """Generate valid health education module names."""
    modules = [
        'puberty_education',
        'safety_mental_support', 
        'menstrual_guide',
        'pregnancy_guidance',
        'government_resources',
        ''  # Empty string for no current module
    ]
    return draw(st.sampled_from(modules))


@composite
def interaction_data(draw):
    """Generate realistic interaction data."""
    interaction_types = ['voice_query', 'module_access', 'content_request', 'language_switch', 'emergency_access']
    content_samples = [
        'मुझे मासिक धर्म के बारे में जानना है',
        'Tell me about pregnancy nutrition',
        'What government schemes are available?',
        'I need help with safety information',
        'Show me menstrual product options'
    ]
    response_samples = [
        'मैं आपको मासिक धर्म के बारे में बताती हूं...',
        'Here is information about pregnancy nutrition...',
        'Available government schemes include JSY, PMSMA...',
        'Safety information includes recognizing inappropriate behavior...',
        'Menstrual product options include pads, cups, and cloth...'
    ]
    
    return {
        'type': draw(st.sampled_from(interaction_types)),
        'content': draw(st.sampled_from(content_samples)),
        'response': draw(st.sampled_from(response_samples)),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }


@composite
def emergency_contact_data(draw):
    """Generate realistic emergency contact data."""
    contact_types = ['helpline', 'medical', 'counseling']
    phone_numbers = ['+91-11-26853846', '1091', '181', '+91-80-25497777']
    regions = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
    
    return {
        'type': draw(st.sampled_from(contact_types)),
        'phone': draw(st.sampled_from(phone_numbers)),
        'region': draw(st.sampled_from(regions)),
        'available_24_7': draw(st.booleans())
    }


@composite
def accessibility_preferences_data(draw):
    """Generate realistic accessibility preferences."""
    audio_speeds = ['slow', 'normal', 'fast']
    return {
        'audio_speed': draw(st.sampled_from(audio_speeds)),
        'high_contrast': draw(st.booleans()),
        'large_text': draw(st.booleans()),
        'voice_only_mode': draw(st.booleans())
    }


@composite
def user_session_data(draw):
    """Generate comprehensive user session data for testing."""
    # Generate base session data
    language = draw(valid_language_codes())
    module = draw(valid_module_names())
    
    # Generate interaction history (0-10 interactions)
    num_interactions = draw(st.integers(min_value=0, max_value=10))
    interactions = [draw(interaction_data()) for _ in range(num_interactions)]
    
    # Generate emergency contacts (0-3 contacts)
    num_contacts = draw(st.integers(min_value=0, max_value=3))
    emergency_contacts = {}
    for i in range(num_contacts):
        contact_key = f"contact_{i}"
        emergency_contacts[contact_key] = draw(emergency_contact_data())
    
    # Generate accessibility preferences
    accessibility_prefs = draw(accessibility_preferences_data())
    
    # Generate timestamps (created_at before last_active, both in the past)
    # Use naive datetimes for Hypothesis, then add timezone
    now_naive = datetime(2024, 12, 31)  # Fixed past date to avoid future dates
    created_at_naive = draw(st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2024, 6, 1)
    ))
    created_at = created_at_naive.replace(tzinfo=timezone.utc)
    
    last_active_naive = draw(st.datetimes(
        min_value=created_at_naive,
        max_value=now_naive
    ))
    last_active = last_active_naive.replace(tzinfo=timezone.utc)
    
    return {
        'language_preference': language,
        'current_module': module,
        'interaction_history': interactions,
        'emergency_contacts': emergency_contacts,
        'accessibility_preferences': accessibility_prefs,
        'created_at': created_at,
        'last_active': last_active
    }


class TestSessionStatePersistence:
    """Property-based tests for session state persistence."""
    
    @given(session_data=user_session_data())
    @settings(max_examples=100, deadline=1000)
    def test_session_state_persistence_property(self, session_data):
        """
        **Feature: sakhi-saathi-ai, Property 15: Session State Persistence**
        
        Property: For any user interaction sequence, the system should maintain 
        session state across all interactions within the session.
        
        This test verifies that:
        1. Session creation preserves all initial state
        2. Multiple interactions update session state correctly
        3. JSON serialization/deserialization preserves all data
        4. Session timeout handling maintains data integrity
        5. Language switching maintains session continuity
        6. Module navigation preserves interaction history
        7. Emergency contact updates persist in session
        8. Accessibility preference changes are maintained
        """
        # Create initial session with generated data
        session = UserSession(
            language_preference=session_data['language_preference'],
            current_module=session_data['current_module'],
            interaction_history=session_data['interaction_history'],
            emergency_contacts=session_data['emergency_contacts'],
            accessibility_preferences=session_data['accessibility_preferences'],
            created_at=session_data['created_at'],
            last_active=session_data['last_active']
        )
        
        # Validate initial session
        assert session.validate(), "Initial session should be valid"
        
        # Test 1: Session creation and basic state persistence
        original_session_id = session.session_id
        original_language = session.language_preference
        original_module = session.current_module
        original_history_count = len(session.interaction_history)
        original_contacts = session.emergency_contacts.copy()
        original_accessibility = session.accessibility_preferences.copy()
        
        # Session ID should remain constant
        assert session.session_id == original_session_id
        
        # Test 2: Multiple interactions updating session state
        # Add a new interaction
        session.add_interaction("voice_query", "Test query", "Test response")
        
        # Verify interaction was added and state updated
        assert len(session.interaction_history) == original_history_count + 1
        assert session.interaction_history[-1]['type'] == "voice_query"
        assert session.interaction_history[-1]['content'] == "Test query"
        assert session.interaction_history[-1]['response'] == "Test response"
        
        # Last active time should be updated (or at least not decreased)
        assert session.last_active >= session_data['last_active']
        
        # Other state should remain unchanged
        assert session.session_id == original_session_id
        assert session.language_preference == original_language
        assert session.current_module == original_module
        
        # Test 3: JSON serialization/deserialization preserving all data
        json_str = session.to_json()
        assert isinstance(json_str, str), "Serialization should return string"
        
        # Verify JSON is valid
        json_data = json.loads(json_str)
        assert 'session_id' in json_data
        assert 'language_preference' in json_data
        assert 'current_module' in json_data
        assert 'interaction_history' in json_data
        assert 'emergency_contacts' in json_data
        assert 'accessibility_preferences' in json_data
        
        # Deserialize and verify all data is preserved
        restored_session = UserSession.from_json(json_str)
        
        assert restored_session.session_id == session.session_id
        assert restored_session.language_preference == session.language_preference
        assert restored_session.current_module == session.current_module
        assert len(restored_session.interaction_history) == len(session.interaction_history)
        assert restored_session.emergency_contacts == session.emergency_contacts
        assert restored_session.accessibility_preferences == session.accessibility_preferences
        assert restored_session.created_at == session.created_at
        assert restored_session.last_active == session.last_active
        
        # Test 4: Session timeout handling without data loss
        # Simulate session timeout by updating last_active
        old_last_active = restored_session.last_active
        
        # Add a small delay to ensure time difference
        import time
        time.sleep(0.001)  # 1ms delay
        restored_session.update_last_active()
        
        # Verify data integrity after timeout handling
        assert restored_session.last_active >= old_last_active
        assert restored_session.session_id == original_session_id
        assert restored_session.language_preference == original_language
        assert len(restored_session.interaction_history) == original_history_count + 1
        
        # Test 5: Language switching maintaining session continuity
        new_language = 'hi' if original_language != 'hi' else 'en'
        restored_session.language_preference = new_language
        
        # Verify language change doesn't affect other state
        assert restored_session.language_preference == new_language
        assert restored_session.session_id == original_session_id
        assert restored_session.current_module == original_module
        assert len(restored_session.interaction_history) == original_history_count + 1
        assert restored_session.emergency_contacts == original_contacts
        
        # Test 6: Module navigation preserving interaction history
        new_module = 'pregnancy_guidance' if original_module != 'pregnancy_guidance' else 'safety_mental_support'
        restored_session.current_module = new_module
        
        # Verify module change preserves interaction history
        assert restored_session.current_module == new_module
        assert len(restored_session.interaction_history) == original_history_count + 1
        assert restored_session.interaction_history[-1]['type'] == "voice_query"
        
        # Test 7: Emergency contact updates persisting in session
        new_contact = {
            'type': 'medical',
            'phone': '+91-11-12345678',
            'region': 'Test Region',
            'available_24_7': True
        }
        restored_session.emergency_contacts['new_contact'] = new_contact
        
        # Verify emergency contact persists
        assert 'new_contact' in restored_session.emergency_contacts
        assert restored_session.emergency_contacts['new_contact'] == new_contact
        
        # Test 8: Accessibility preference changes being maintained
        restored_session.accessibility_preferences['audio_speed'] = 'fast'
        restored_session.accessibility_preferences['high_contrast'] = True
        
        # Verify accessibility changes persist
        assert restored_session.accessibility_preferences['audio_speed'] == 'fast'
        assert restored_session.accessibility_preferences['high_contrast'] == True
        
        # Final serialization test to ensure all changes persist
        final_json = restored_session.to_json()
        final_session = UserSession.from_json(final_json)
        
        # Verify all changes are preserved through serialization
        assert final_session.language_preference == new_language
        assert final_session.current_module == new_module
        assert len(final_session.interaction_history) == original_history_count + 1
        assert 'new_contact' in final_session.emergency_contacts
        assert final_session.accessibility_preferences['audio_speed'] == 'fast'
        assert final_session.accessibility_preferences['high_contrast'] == True
        
        # Validate final session
        assert final_session.validate(), "Final session should be valid"


    @given(
        language1=valid_language_codes(),
        language2=valid_language_codes(),
        module1=valid_module_names(),
        module2=valid_module_names()
    )
    @settings(max_examples=50, deadline=500)
    def test_session_state_consistency_across_changes(self, language1, language2, module1, module2):
        """
        Test that session state remains consistent when making multiple changes.
        
        This property ensures that changing language and module preferences
        doesn't corrupt other session data.
        """
        assume(language1 != language2 or module1 != module2)  # Ensure at least one change
        
        # Create initial session
        session = UserSession(
            language_preference=language1,
            current_module=module1
        )
        
        # Add some initial data
        session.add_interaction("initial", "Initial content", "Initial response")
        session.emergency_contacts['test'] = {'type': 'helpline', 'phone': '123'}
        session.accessibility_preferences['test_pref'] = True
        
        original_session_id = session.session_id
        original_created_at = session.created_at
        
        # Make changes
        session.language_preference = language2
        session.current_module = module2
        session.add_interaction("after_change", "Changed content", "Changed response")
        
        # Verify consistency
        assert session.session_id == original_session_id
        assert session.created_at == original_created_at
        assert session.language_preference == language2
        assert session.current_module == module2
        assert len(session.interaction_history) == 2
        assert session.emergency_contacts['test']['phone'] == '123'
        assert session.accessibility_preferences['test_pref'] == True
        
        # Test serialization preserves consistency
        json_str = session.to_json()
        restored = UserSession.from_json(json_str)
        
        assert restored.session_id == original_session_id
        assert restored.language_preference == language2
        assert restored.current_module == module2
        assert len(restored.interaction_history) == 2
        assert restored.validate()


    @given(num_interactions=st.integers(min_value=1, max_value=20))
    @settings(max_examples=30, deadline=500)
    def test_interaction_history_persistence(self, num_interactions):
        """
        Test that interaction history persists correctly across multiple interactions.
        
        This property ensures that adding many interactions doesn't corrupt
        the session state or interaction history.
        """
        session = UserSession()
        
        # Add multiple interactions
        for i in range(num_interactions):
            session.add_interaction(
                f"interaction_type_{i}",
                f"content_{i}",
                f"response_{i}"
            )
        
        # Verify all interactions are preserved
        assert len(session.interaction_history) == num_interactions
        
        # Check each interaction
        for i in range(num_interactions):
            interaction = session.interaction_history[i]
            assert interaction['type'] == f"interaction_type_{i}"
            assert interaction['content'] == f"content_{i}"
            assert interaction['response'] == f"response_{i}"
            assert 'timestamp' in interaction
        
        # Test serialization preserves all interactions
        json_str = session.to_json()
        restored = UserSession.from_json(json_str)
        
        assert len(restored.interaction_history) == num_interactions
        for i in range(num_interactions):
            assert restored.interaction_history[i]['type'] == f"interaction_type_{i}"
            assert restored.interaction_history[i]['content'] == f"content_{i}"
            assert restored.interaction_history[i]['response'] == f"response_{i}"
        
        assert restored.validate()


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v", "--tb=short"])