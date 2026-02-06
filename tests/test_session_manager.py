"""
Test suite for SessionManager class.

This module contains comprehensive tests for the session management system,
including unit tests for core functionality and property-based tests for
universal correctness properties.
"""

import json
import pytest
import tempfile
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.session_manager import SessionManager, create_session_manager, get_default_session_manager
from models.data_models import UserSession


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.session_manager = SessionManager(timeout_minutes=1)  # Short timeout for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = Path(self.temp_dir) / "test_sessions.json"
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up any temporary files
        if self.temp_file.exists():
            self.temp_file.unlink()
    
    def test_create_session_default_language(self):
        """Test creating a session with default language."""
        session = self.session_manager.create_session()
        
        assert session is not None
        assert session.session_id is not None
        assert session.language_preference == 'en'
        assert session.current_module == ""
        assert len(session.interaction_history) == 0
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_active, datetime)
    
    def test_create_session_custom_language(self):
        """Test creating a session with custom language."""
        session = self.session_manager.create_session(language_preference='hi')
        
        assert session.language_preference == 'hi'
        assert session.session_id in self.session_manager.sessions
    
    def test_create_session_invalid_language(self):
        """Test creating a session with invalid language preference."""
        with pytest.raises(RuntimeError):
            self.session_manager.create_session(language_preference="")
        
        with pytest.raises(RuntimeError):
            self.session_manager.create_session(language_preference=None)
    
    def test_get_session_existing(self):
        """Test retrieving an existing session."""
        # Create a session
        created_session = self.session_manager.create_session('bn')
        session_id = created_session.session_id
        
        # Retrieve the session
        retrieved_session = self.session_manager.get_session(session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
        assert retrieved_session.language_preference == 'bn'
    
    def test_get_session_nonexistent(self):
        """Test retrieving a non-existent session."""
        result = self.session_manager.get_session("nonexistent-id")
        assert result is None
    
    def test_get_session_invalid_id(self):
        """Test retrieving session with invalid ID."""
        assert self.session_manager.get_session("") is None
        assert self.session_manager.get_session(None) is None
    
    def test_update_session_valid_fields(self):
        """Test updating session with valid fields."""
        session = self.session_manager.create_session()
        session_id = session.session_id
        
        # Update session
        result = self.session_manager.update_session(
            session_id,
            current_module="puberty_education",
            language_preference="hi"
        )
        
        assert result is True
        
        # Verify updates
        updated_session = self.session_manager.get_session(session_id)
        assert updated_session.current_module == "puberty_education"
        assert updated_session.language_preference == "hi"
    
    def test_update_session_invalid_fields(self):
        """Test updating session with invalid fields."""
        session = self.session_manager.create_session()
        session_id = session.session_id
        
        # Update with invalid field
        result = self.session_manager.update_session(
            session_id,
            invalid_field="value"
        )
        
        # Should return False but not crash
        assert result is False
    
    def test_update_session_nonexistent(self):
        """Test updating a non-existent session."""
        result = self.session_manager.update_session(
            "nonexistent-id",
            current_module="test"
        )
        assert result is False
    
    def test_delete_session_existing(self):
        """Test deleting an existing session."""
        session = self.session_manager.create_session()
        session_id = session.session_id
        
        # Verify session exists
        assert self.session_manager.get_session(session_id) is not None
        
        # Delete session
        result = self.session_manager.delete_session(session_id)
        assert result is True
        
        # Verify session is gone
        assert self.session_manager.get_session(session_id) is None
    
    def test_delete_session_nonexistent(self):
        """Test deleting a non-existent session."""
        result = self.session_manager.delete_session("nonexistent-id")
        assert result is False
    
    def test_session_expiration(self):
        """Test session expiration functionality."""
        # Create session manager with very short timeout
        manager = SessionManager(timeout_minutes=0.01)  # ~0.6 seconds
        
        session = manager.create_session()
        session_id = session.session_id
        
        # Session should exist initially
        assert manager.get_session(session_id) is not None
        
        # Wait for expiration
        time.sleep(1)
        
        # Session should be expired and removed
        assert manager.get_session(session_id) is None
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        # Create session manager with very short timeout
        manager = SessionManager(timeout_minutes=0.01)
        
        # Create multiple sessions
        session1 = manager.create_session()
        session2 = manager.create_session()
        session3 = manager.create_session()
        
        # Verify all sessions exist
        assert len(manager.sessions) == 3
        
        # Wait for expiration
        time.sleep(1)
        
        # Run cleanup
        cleaned_count = manager.cleanup_expired_sessions()
        
        assert cleaned_count == 3
        assert len(manager.sessions) == 0
    
    def test_get_active_sessions(self):
        """Test retrieving active sessions."""
        # Create sessions
        session1 = self.session_manager.create_session('en')
        session2 = self.session_manager.create_session('hi')
        
        active_sessions = self.session_manager.get_active_sessions()
        
        assert len(active_sessions) == 2
        session_ids = [s.session_id for s in active_sessions]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids
    
    def test_get_session_count(self):
        """Test getting total session count."""
        assert self.session_manager.get_session_count() == 0
        
        self.session_manager.create_session()
        assert self.session_manager.get_session_count() == 1
        
        self.session_manager.create_session()
        assert self.session_manager.get_session_count() == 2
    
    def test_get_active_session_count(self):
        """Test getting active session count."""
        assert self.session_manager.get_active_session_count() == 0
        
        self.session_manager.create_session()
        assert self.session_manager.get_active_session_count() == 1
        
        self.session_manager.create_session()
        assert self.session_manager.get_active_session_count() == 2
    
    def test_session_persistence_enabled(self):
        """Test session persistence to file."""
        manager = SessionManager(
            timeout_minutes=30,
            enable_persistence=True,
            persistence_file=str(self.temp_file)
        )
        
        # Create session
        session = manager.create_session('hi')
        session_id = session.session_id
        
        # Verify file was created
        assert self.temp_file.exists()
        
        # Create new manager instance (simulating restart)
        manager2 = SessionManager(
            timeout_minutes=30,
            enable_persistence=True,
            persistence_file=str(self.temp_file)
        )
        
        # Session should be loaded from file
        loaded_session = manager2.get_session(session_id)
        assert loaded_session is not None
        assert loaded_session.language_preference == 'hi'
    
    def test_session_persistence_disabled(self):
        """Test session manager without persistence."""
        manager = SessionManager(enable_persistence=False)
        
        session = manager.create_session()
        assert session is not None
        
        # No file should be created
        assert not Path("sessions.json").exists()
    
    def test_recover_session_valid_data(self):
        """Test recovering session from valid data."""
        session_data = {
            'session_id': 'test-session-id',
            'language_preference': 'hi',
            'current_module': 'puberty_education',
            'interaction_history': [],
            'emergency_contacts': {},
            'accessibility_preferences': {},
            'created_at': datetime.now(timezone.utc),
            'last_active': datetime.now(timezone.utc)
        }
        
        recovered_session = self.session_manager.recover_session(session_data)
        
        assert recovered_session is not None
        assert recovered_session.session_id == 'test-session-id'
        assert recovered_session.language_preference == 'hi'
        assert recovered_session.current_module == 'puberty_education'
    
    def test_recover_session_expired_data(self):
        """Test recovering session with expired data."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        session_data = {
            'session_id': 'expired-session-id',
            'language_preference': 'en',
            'current_module': '',
            'interaction_history': [],
            'emergency_contacts': {},
            'accessibility_preferences': {},
            'created_at': old_time,
            'last_active': old_time
        }
        
        recovered_session = self.session_manager.recover_session(session_data)
        assert recovered_session is None
    
    def test_recover_session_invalid_data(self):
        """Test recovering session with invalid data."""
        invalid_data = {
            'session_id': '',  # Invalid empty ID
            'language_preference': 'en'
        }
        
        recovered_session = self.session_manager.recover_session(invalid_data)
        assert recovered_session is None
    
    def test_thread_safety(self):
        """Test thread safety of session operations."""
        results = []
        errors = []
        
        def create_sessions():
            try:
                valid_languages = ['en', 'hi', 'bn']
                for i in range(10):
                    session = self.session_manager.create_session(valid_languages[i % 3])
                    results.append(session.session_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_sessions)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        
        # Verify all sessions were created
        assert len(results) == 50
        assert len(set(results)) == 50  # All unique session IDs
        assert self.session_manager.get_session_count() == 50
    
    def test_context_manager(self):
        """Test SessionManager as context manager."""
        temp_file = Path(self.temp_dir) / "context_test.json"
        
        with SessionManager(enable_persistence=True, persistence_file=str(temp_file)) as manager:
            session = manager.create_session('en')
            assert session is not None
        
        # File should be saved on exit
        assert temp_file.exists()
    
    def test_factory_functions(self):
        """Test factory functions for creating session managers."""
        # Test create_session_manager
        manager1 = create_session_manager(timeout_minutes=60, enable_persistence=True)
        assert manager1.timeout_minutes == 60
        assert manager1.enable_persistence is True
        
        # Test get_default_session_manager
        manager2 = get_default_session_manager()
        assert manager2.timeout_minutes == 30
        assert manager2.enable_persistence is True


class TestSessionManagerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_large_number_of_sessions(self):
        """Test handling large number of sessions."""
        manager = SessionManager()
        
        # Create many sessions
        session_ids = []
        for i in range(1000):
            session = manager.create_session()
            session_ids.append(session.session_id)
        
        assert manager.get_session_count() == 1000
        
        # Verify all sessions can be retrieved
        for session_id in session_ids[:10]:  # Test first 10
            session = manager.get_session(session_id)
            assert session is not None
    
    def test_concurrent_cleanup(self):
        """Test concurrent cleanup operations."""
        manager = SessionManager(timeout_minutes=0.01)
        
        # Create sessions
        for _ in range(100):
            manager.create_session()
        
        # Wait for expiration
        time.sleep(1)
        
        # Run concurrent cleanups
        results = []
        
        def cleanup():
            result = manager.cleanup_expired_sessions()
            results.append(result)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=cleanup)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify cleanup worked
        assert manager.get_session_count() == 0
        assert sum(results) == 100  # Total cleaned sessions
    
    def test_malformed_persistence_file(self):
        """Test handling malformed persistence file."""
        temp_file = Path(self.temp_dir) / "malformed.json"
        
        # Create malformed JSON file
        with open(temp_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Should not crash when loading
        manager = SessionManager(
            enable_persistence=True,
            persistence_file=str(temp_file)
        )
        
        assert manager.get_session_count() == 0
    
    def test_permission_error_persistence(self):
        """Test handling permission errors during persistence."""
        # Create read-only directory
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        
        readonly_file = readonly_dir / "sessions.json"
        
        # Should handle permission error gracefully
        manager = SessionManager(
            enable_persistence=True,
            persistence_file=str(readonly_file)
        )
        
        # Creating session should still work (just no persistence)
        session = manager.create_session()
        assert session is not None
        
        # Clean up
        readonly_dir.chmod(0o755)
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# Property-based tests would go here if using Hypothesis
# For now, we'll include some basic property-like tests

class TestSessionManagerProperties:
    """Test universal properties of session management."""
    
    def test_session_id_uniqueness_property(self):
        """Property: All created sessions should have unique IDs."""
        manager = SessionManager()
        session_ids = set()
        
        # Create many sessions
        for _ in range(100):
            session = manager.create_session()
            assert session.session_id not in session_ids
            session_ids.add(session.session_id)
    
    def test_session_retrieval_consistency_property(self):
        """Property: Retrieved sessions should match created sessions."""
        manager = SessionManager()
        
        # Create sessions with different languages
        languages = ['en', 'hi', 'bn', 'ta', 'te']
        created_sessions = {}
        
        for lang in languages:
            session = manager.create_session(lang)
            created_sessions[session.session_id] = session
        
        # Verify all sessions can be retrieved correctly
        for session_id, original_session in created_sessions.items():
            retrieved_session = manager.get_session(session_id)
            assert retrieved_session is not None
            assert retrieved_session.session_id == original_session.session_id
            assert retrieved_session.language_preference == original_session.language_preference
    
    def test_session_update_persistence_property(self):
        """Property: Session updates should persist across retrievals."""
        manager = SessionManager()
        
        session = manager.create_session()
        session_id = session.session_id
        
        # Update session multiple times
        updates = [
            {'current_module': 'puberty_education'},
            {'language_preference': 'hi'},
            {'current_module': 'safety_support'},
            {'language_preference': 'bn'}
        ]
        
        for update in updates:
            result = manager.update_session(session_id, **update)
            assert result is True
            
            # Verify update persisted
            retrieved_session = manager.get_session(session_id)
            for key, value in update.items():
                assert getattr(retrieved_session, key) == value
    
    def test_session_cleanup_completeness_property(self):
        """Property: Cleanup should remove all expired sessions."""
        manager = SessionManager(timeout_minutes=0.01)
        
        # Create sessions
        session_count = 50
        for _ in range(session_count):
            manager.create_session()
        
        assert manager.get_session_count() == session_count
        
        # Wait for expiration
        time.sleep(1)
        
        # Cleanup should remove all sessions
        cleaned_count = manager.cleanup_expired_sessions()
        assert cleaned_count == session_count
        assert manager.get_session_count() == 0
        assert manager.get_active_session_count() == 0


if __name__ == '__main__':
    pytest.main([__file__])