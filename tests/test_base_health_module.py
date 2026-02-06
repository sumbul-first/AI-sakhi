"""
Tests for BaseHealthModule abstract class.

This module tests the common functionality provided by the BaseHealthModule
abstract base class, including content safety validation, emergency detection,
and integration with ContentManager and SessionManager.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from modules.base_health_module import BaseHealthModule, validate_module_requirements, create_emergency_response
from models.data_models import ContentItem, EmergencyContact, UserSession
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class TestHealthModule(BaseHealthModule):
    """Concrete implementation of BaseHealthModule for testing."""
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: str = None) -> dict:
        """Test implementation of abstract method."""
        return {
            "content": [
                ContentItem(
                    module_name=self.module_name,
                    topic=topic,
                    content_type="text",
                    language_code=language_code,
                    transcript=f"Educational content about {topic}",
                    safety_validated=True
                )
            ],
            "language_used": language_code,
            "emergency_detected": False,
            "recommendations": [f"Learn more about {topic}"]
        }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: str = None) -> dict:
        """Test implementation of abstract method."""
        return {
            "response": f"Here's information about your query: {query}",
            "content_items": [],
            "emergency_detected": "emergency" in query.lower(),
            "safety_warnings": [],
            "next_actions": ["Continue learning"]
        }
    
    def get_module_topics(self, language_code: str) -> list:
        """Test implementation of abstract method."""
        return ["test_topic_1", "test_topic_2", "test_topic_3"]


class TestBaseHealthModule:
    """Test cases for BaseHealthModule functionality."""
    
    @pytest.fixture
    def mock_content_manager(self):
        """Create a mock ContentManager for testing."""
        mock_cm = Mock(spec=ContentManager)
        mock_cm.get_supported_languages.return_value = ["en", "hi", "bn"]
        mock_cm.health_check.return_value = {"status": "healthy"}
        return mock_cm
    
    @pytest.fixture
    def mock_session_manager(self):
        """Create a mock SessionManager for testing."""
        mock_sm = Mock(spec=SessionManager)
        mock_sm.get_session_count.return_value = 5
        mock_sm.update_session.return_value = True
        mock_sm.get_session.return_value = Mock(spec=UserSession)
        return mock_sm
    
    @pytest.fixture
    def health_module(self, mock_content_manager, mock_session_manager):
        """Create a test health module instance."""
        return TestHealthModule("test_module", mock_content_manager, mock_session_manager)
    
    def test_module_initialization(self, mock_content_manager, mock_session_manager):
        """Test proper initialization of BaseHealthModule."""
        module = TestHealthModule("test_module", mock_content_manager, mock_session_manager)
        
        assert module.module_name == "test_module"
        assert module.content_manager == mock_content_manager
        assert module.session_manager == mock_session_manager
        assert hasattr(module, 'logger')
    
    def test_initialization_validation(self, mock_content_manager, mock_session_manager):
        """Test validation during module initialization."""
        # Test invalid module name
        with pytest.raises(ValueError, match="Module name must be a non-empty string"):
            TestHealthModule("", mock_content_manager, mock_session_manager)
        
        # Test invalid content manager
        with pytest.raises(ValueError, match="content_manager must be a ContentManager instance"):
            TestHealthModule("test", "invalid", mock_session_manager)
        
        # Test invalid session manager
        with pytest.raises(ValueError, match="session_manager must be a SessionManager instance"):
            TestHealthModule("test", mock_content_manager, "invalid")
    
    def test_validate_content_safety_string(self, health_module):
        """Test content safety validation with string input."""
        # Safe educational content
        safe_content = "This is educational information about health topics"
        result = health_module.validate_content_safety(safe_content)
        
        assert result["is_safe"] is True
        assert len(result["medical_flags"]) == 0
        assert len(result["emergency_flags"]) == 0
        
        # Content with medical diagnosis keywords
        medical_content = "You need to diagnose this disease and get treatment"
        result = health_module.validate_content_safety(medical_content)
        
        assert result["is_safe"] is False
        assert "diagnose" in result["medical_flags"]
        assert "disease" in result["medical_flags"]
        assert "treatment" in result["medical_flags"]
        assert result["requires_medical_referral"] is True
        
        # Content with emergency keywords
        emergency_content = "This is an emergency situation with danger"
        result = health_module.validate_content_safety(emergency_content)
        
        assert "emergency" in result["emergency_flags"]
        assert "danger" in result["emergency_flags"]
    
    def test_validate_content_safety_content_item(self, health_module):
        """Test content safety validation with ContentItem input."""
        # Safe content item
        safe_item = ContentItem(
            module_name="test",
            topic="education",
            content_type="text",
            transcript="Educational information about health"
        )
        
        result = health_module.validate_content_safety(safe_item)
        assert result["is_safe"] is True
        
        # Unsafe content item
        unsafe_item = ContentItem(
            module_name="test",
            topic="medical",
            content_type="text",
            transcript="This will cure your disease with this medicine"
        )
        
        result = health_module.validate_content_safety(unsafe_item)
        assert result["is_safe"] is False
        assert "cure" in result["medical_flags"]
        assert "disease" in result["medical_flags"]
        assert "medicine" in result["medical_flags"]
    
    def test_validate_content_safety_list(self, health_module):
        """Test content safety validation with list of ContentItems."""
        content_items = [
            ContentItem(
                module_name="test",
                topic="safe",
                content_type="text",
                transcript="Safe educational content"
            ),
            ContentItem(
                module_name="test",
                topic="unsafe",
                content_type="text",
                transcript="Emergency help needed urgently"
            )
        ]
        
        result = health_module.validate_content_safety(content_items)
        assert "emergency" in result["emergency_flags"]
        assert "help" in result["emergency_flags"]
        assert "urgent" in result["emergency_flags"]  # "urgently" is detected as "urgent"
    
    def test_get_emergency_resources(self, health_module):
        """Test emergency resource retrieval."""
        # Test default parameters
        contacts = health_module.get_emergency_resources()
        assert len(contacts) > 0
        assert all(isinstance(contact, EmergencyContact) for contact in contacts)
        
        # Test with specific language
        hindi_contacts = health_module.get_emergency_resources(language_code="hi")
        assert len(hindi_contacts) > 0
        assert all("hi" in contact.language_support for contact in hindi_contacts)
        
        # Test caching
        cached_contacts = health_module.get_emergency_resources()
        assert len(cached_contacts) == len(contacts)
    
    def test_detect_emergency_situation(self, health_module):
        """Test emergency situation detection."""
        # Non-emergency input
        normal_input = "I want to learn about health topics"
        result = health_module.detect_emergency_situation(normal_input)
        assert result["is_emergency"] is False
        assert result["emergency_type"] is None
        assert result["confidence"] == 0.0
        
        # Emergency input - safety threat
        safety_threat = "I am being threatened and feel unsafe"
        result = health_module.detect_emergency_situation(safety_threat)
        assert result["is_emergency"] is True
        assert result["emergency_type"] == "safety_threat"
        assert result["confidence"] > 0.0
        assert len(result["recommended_contacts"]) > 0
        
        # Emergency input - medical emergency
        medical_emergency = "I have severe bleeding and need hospital"
        result = health_module.detect_emergency_situation(medical_emergency)
        assert result["is_emergency"] is True
        assert result["emergency_type"] == "medical_emergency"
        assert "Call 108 for medical emergency" in result["immediate_actions"]
        
        # Emergency input - mental health crisis
        mental_crisis = "I want to end my life, thinking about suicide"
        result = health_module.detect_emergency_situation(mental_crisis)
        assert result["is_emergency"] is True
        assert result["emergency_type"] == "mental_health_crisis"
        
        # Invalid input
        result = health_module.detect_emergency_situation("")
        assert result["is_emergency"] is False
    
    def test_get_content_with_safety_check(self, health_module):
        """Test content retrieval with integrated safety validation."""
        result = health_module.get_content_with_safety_check("test_topic", "en")
        
        assert "content" in result
        assert "safety_validated" in result
        assert "medical_flags" in result
        assert "emergency_flags" in result
        assert "safety_recommendations" in result
        assert len(result["content"]) > 0
    
    def test_update_session_context(self, health_module):
        """Test session context updating."""
        session_id = "test_session_123"
        interaction_data = {
            "query": "test query",
            "response": "test response",
            "topic": "test_topic"
        }
        
        result = health_module.update_session_context(session_id, interaction_data)
        assert result is True
        
        # Verify session manager was called
        health_module.session_manager.update_session.assert_called_once()
        health_module.session_manager.get_session.assert_called_once_with(session_id)
    
    def test_get_module_info(self, health_module):
        """Test module information retrieval."""
        info = health_module.get_module_info()
        
        assert info["module_name"] == "test_module"
        assert "description" in info
        assert "capabilities" in info
        assert "supported_languages" in info
        assert info["emergency_support"] is True
        assert info["safety_validation"] is True
        assert info["session_integration"] is True
    
    def test_health_check(self, health_module):
        """Test module health check functionality."""
        health_status = health_module.health_check()
        
        assert health_status["module_name"] == "test_module"
        assert "status" in health_status
        assert "timestamp" in health_status
        assert "checks" in health_status
        
        # Verify individual checks
        assert "content_manager" in health_status["checks"]
        assert "session_manager" in health_status["checks"]
        assert "emergency_resources" in health_status["checks"]


class TestUtilityFunctions:
    """Test utility functions for health modules."""
    
    def test_validate_module_requirements(self):
        """Test module requirements validation."""
        # Valid managers
        mock_cm = Mock(spec=ContentManager)
        mock_cm.get_supported_languages.return_value = ["en", "hi"]
        
        mock_sm = Mock(spec=SessionManager)
        mock_sm.get_session_count.return_value = 0
        
        assert validate_module_requirements(mock_cm, mock_sm) is True
        
        # Invalid content manager
        with pytest.raises(ValueError, match="content_manager must be a ContentManager instance"):
            validate_module_requirements("invalid", mock_sm)
        
        # Invalid session manager
        with pytest.raises(ValueError, match="session_manager must be a SessionManager instance"):
            validate_module_requirements(mock_cm, "invalid")
        
        # Content manager with no languages
        mock_cm.get_supported_languages.return_value = []
        with pytest.raises(ValueError, match="ContentManager has no supported languages"):
            validate_module_requirements(mock_cm, mock_sm)
    
    def test_create_emergency_response(self):
        """Test emergency response creation."""
        # English response
        response = create_emergency_response("medical_emergency", "en")
        assert response["emergency_type"] == "medical_emergency"
        assert response["language_code"] == "en"
        assert "108" in response["message"]
        assert response["immediate_action_required"] is True
        assert response["priority"] == "high"
        
        # Hindi response
        response = create_emergency_response("safety_threat", "hi")
        assert response["language_code"] == "hi"
        assert "112" in response["message"]
        
        # Unknown emergency type
        response = create_emergency_response("unknown_type", "en")
        assert "112" in response["message"]  # Should fall back to general emergency
        
        # Unsupported language
        response = create_emergency_response("general_emergency", "unsupported")
        assert response["language_code"] == "unsupported"
        # Should fall back to English message
        assert "112" in response["message"]


if __name__ == "__main__":
    pytest.main([__file__])