"""
Session Management System for AI Sakhi Voice-First Health Companion.

This module provides comprehensive session lifecycle management including creation,
retrieval, updates, cleanup, and recovery mechanisms. The SessionManager class
handles user sessions with configurable timeouts, thread-safe operations, and
graceful error handling.

Key Features:
- In-memory storage with JSON serialization support
- Configurable session timeout (default 30 minutes)
- Thread-safe operations for concurrent access
- Automatic cleanup of expired sessions
- Session recovery mechanisms
- Comprehensive error handling and logging
"""

import json
import logging
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from models.data_models import UserSession


class SessionManager:
    """
    Manages user session lifecycle with timeout, recovery, and cleanup mechanisms.
    
    This class provides thread-safe session management with in-memory storage,
    automatic cleanup of expired sessions, and comprehensive error handling.
    Sessions are stored in memory for fast access and can be persisted to JSON
    for recovery across application restarts.
    
    Attributes:
        timeout_minutes: Session timeout in minutes (default 30)
        sessions: In-memory storage for active sessions
        lock: Thread lock for concurrent access protection
        logger: Logger instance for session operations
        cleanup_interval: Interval between automatic cleanup runs (seconds)
        last_cleanup: Timestamp of last cleanup operation
    """
    
    def __init__(self, timeout_minutes: int = 30, enable_persistence: bool = False, 
                 persistence_file: str = "sessions.json"):
        """
        Initialize the SessionManager with configurable timeout and persistence.
        
        Args:
            timeout_minutes: Session timeout in minutes (default 30)
            enable_persistence: Whether to enable JSON file persistence
            persistence_file: Path to JSON file for session persistence
        """
        self.timeout_minutes = timeout_minutes
        self.enable_persistence = enable_persistence
        self.persistence_file = Path(persistence_file)
        
        # In-memory session storage
        self.sessions: Dict[str, UserSession] = {}
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Cleanup management
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = datetime.now(timezone.utc)
        
        # Load persisted sessions if enabled
        if self.enable_persistence:
            self._load_sessions_from_file()
        
        self.logger.info(f"SessionManager initialized with {timeout_minutes} minute timeout")
    
    def create_session(self, language_preference: str = 'en') -> UserSession:
        """
        Create a new user session with specified language preference.
        
        Args:
            language_preference: User's preferred language code (default 'en')
            
        Returns:
            UserSession: Newly created session object
            
        Raises:
            ValueError: If language_preference is invalid
            RuntimeError: If session creation fails
        """
        try:
            with self.lock:
                # Validate language preference
                if not language_preference or not isinstance(language_preference, str):
                    raise ValueError("Language preference must be a non-empty string")
                
                # Create new session
                session = UserSession(language_preference=language_preference)
                
                # Validate the session
                session.validate()
                
                # Store in memory
                self.sessions[session.session_id] = session
                
                # Persist if enabled
                if self.enable_persistence:
                    self._save_sessions_to_file()
                
                # Trigger cleanup if needed
                self._maybe_cleanup_expired_sessions()
                
                self.logger.info(f"Created new session {session.session_id} with language {language_preference}")
                return session
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            raise RuntimeError(f"Session creation failed: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Retrieve an existing session by ID.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Optional[UserSession]: Session object if found and valid, None otherwise
        """
        try:
            with self.lock:
                if not session_id or not isinstance(session_id, str):
                    self.logger.warning(f"Invalid session ID provided: {session_id}")
                    return None
                
                session = self.sessions.get(session_id)
                if not session:
                    self.logger.debug(f"Session not found: {session_id}")
                    return None
                
                # Check if session is expired
                if self._is_session_expired(session):
                    self.logger.info(f"Session {session_id} has expired, removing")
                    self._remove_session(session_id)
                    return None
                
                # Update last active time
                session.update_last_active()
                
                # Persist if enabled
                if self.enable_persistence:
                    self._save_sessions_to_file()
                
                self.logger.debug(f"Retrieved session {session_id}")
                return session
                
        except Exception as e:
            self.logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """
        Update session data with provided keyword arguments.
        
        Args:
            session_id: Unique session identifier
            **kwargs: Session attributes to update
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with self.lock:
                session = self.sessions.get(session_id)
                if not session:
                    self.logger.warning(f"Cannot update non-existent session: {session_id}")
                    return False
                
                # Check if session is expired
                if self._is_session_expired(session):
                    self.logger.info(f"Cannot update expired session: {session_id}")
                    self._remove_session(session_id)
                    return False
                
                # Update session attributes
                updated_fields = []
                for key, value in kwargs.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                        updated_fields.append(key)
                    else:
                        self.logger.warning(f"Invalid session attribute: {key}")
                
                if not updated_fields:
                    self.logger.warning(f"No valid fields to update for session {session_id}")
                    return False
                
                # Update last active time
                session.update_last_active()
                
                # Validate updated session
                session.validate()
                
                # Persist if enabled
                if self.enable_persistence:
                    self._save_sessions_to_file()
                
                self.logger.info(f"Updated session {session_id} fields: {updated_fields}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating session {session_id}: {str(e)}")
            return False
    
    def update_session_activity(self, session_id: str) -> bool:
        """
        Update the last active timestamp for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            with self.lock:
                session = self.sessions.get(session_id)
                if not session:
                    self.logger.debug(f"Cannot update activity for non-existent session: {session_id}")
                    return False
                
                # Check if session is expired
                if self._is_session_expired(session):
                    self.logger.info(f"Cannot update activity for expired session: {session_id}")
                    self._remove_session(session_id)
                    return False
                
                # Update last active time
                session.update_last_active()
                
                # Persist if enabled
                if self.enable_persistence:
                    self._save_sessions_to_file()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating session activity {session_id}: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Remove a session from storage.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            with self.lock:
                if session_id in self.sessions:
                    self._remove_session(session_id)
                    
                    # Persist if enabled
                    if self.enable_persistence:
                        self._save_sessions_to_file()
                    
                    self.logger.info(f"Deleted session {session_id}")
                    return True
                else:
                    self.logger.warning(f"Cannot delete non-existent session: {session_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions from storage.
        
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            with self.lock:
                expired_sessions = []
                current_time = datetime.now(timezone.utc)
                
                for session_id, session in self.sessions.items():
                    if self._is_session_expired(session, current_time):
                        expired_sessions.append(session_id)
                
                # Remove expired sessions
                for session_id in expired_sessions:
                    self._remove_session(session_id)
                
                # Update cleanup timestamp
                self.last_cleanup = current_time
                
                # Persist if enabled
                if self.enable_persistence and expired_sessions:
                    self._save_sessions_to_file()
                
                if expired_sessions:
                    self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                return len(expired_sessions)
                
        except Exception as e:
            self.logger.error(f"Error during session cleanup: {str(e)}")
            return 0
    
    def get_active_sessions(self) -> List[UserSession]:
        """
        Get list of all active (non-expired) sessions.
        
        Returns:
            List[UserSession]: List of active session objects
        """
        try:
            with self.lock:
                active_sessions = []
                current_time = datetime.now(timezone.utc)
                
                for session in self.sessions.values():
                    if not self._is_session_expired(session, current_time):
                        active_sessions.append(session)
                
                self.logger.debug(f"Retrieved {len(active_sessions)} active sessions")
                return active_sessions
                
        except Exception as e:
            self.logger.error(f"Error retrieving active sessions: {str(e)}")
            return []
    
    def get_session_count(self) -> int:
        """
        Get total number of sessions in storage.
        
        Returns:
            int: Total session count
        """
        with self.lock:
            return len(self.sessions)
    
    def get_active_session_count(self) -> int:
        """
        Get number of active (non-expired) sessions.
        
        Returns:
            int: Active session count
        """
        return len(self.get_active_sessions())
    
    def recover_session(self, session_data: Dict[str, Any]) -> Optional[UserSession]:
        """
        Recover a session from serialized data.
        
        Args:
            session_data: Dictionary containing session data
            
        Returns:
            Optional[UserSession]: Recovered session or None if recovery fails
        """
        try:
            with self.lock:
                # Create session from data
                session = UserSession(**session_data)
                session.validate()
                
                # Check if session is expired
                if self._is_session_expired(session):
                    self.logger.info(f"Cannot recover expired session: {session.session_id}")
                    return None
                
                # Store recovered session
                self.sessions[session.session_id] = session
                
                # Persist if enabled
                if self.enable_persistence:
                    self._save_sessions_to_file()
                
                self.logger.info(f"Recovered session {session.session_id}")
                return session
                
        except Exception as e:
            self.logger.error(f"Error recovering session: {str(e)}")
            return None
    
    def _is_session_expired(self, session: UserSession, 
                           current_time: Optional[datetime] = None) -> bool:
        """
        Check if a session has expired based on timeout.
        
        Args:
            session: Session to check
            current_time: Current time (defaults to now)
            
        Returns:
            bool: True if session is expired
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        timeout_delta = timedelta(minutes=self.timeout_minutes)
        return (current_time - session.last_active) > timeout_delta
    
    def _remove_session(self, session_id: str) -> None:
        """
        Remove a session from storage (internal method).
        
        Args:
            session_id: Session ID to remove
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _maybe_cleanup_expired_sessions(self) -> None:
        """
        Trigger cleanup if enough time has passed since last cleanup.
        """
        current_time = datetime.now(timezone.utc)
        time_since_cleanup = (current_time - self.last_cleanup).total_seconds()
        
        if time_since_cleanup >= self.cleanup_interval:
            self.cleanup_expired_sessions()
    
    def _save_sessions_to_file(self) -> None:
        """
        Save all sessions to JSON file for persistence.
        """
        try:
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = json.loads(session.to_json())
            
            with open(self.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"Saved {len(sessions_data)} sessions to {self.persistence_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving sessions to file: {str(e)}")
    
    def _load_sessions_from_file(self) -> None:
        """
        Load sessions from JSON file for persistence recovery.
        """
        try:
            if not self.persistence_file.exists():
                self.logger.info("No persistence file found, starting with empty sessions")
                return
            
            with open(self.persistence_file, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            loaded_count = 0
            for session_id, session_data in sessions_data.items():
                try:
                    # Convert datetime strings back to datetime objects
                    if 'created_at' in session_data:
                        session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                    if 'last_active' in session_data:
                        session_data['last_active'] = datetime.fromisoformat(session_data['last_active'])
                    
                    session = UserSession(**session_data)
                    
                    # Only load non-expired sessions
                    if not self._is_session_expired(session):
                        self.sessions[session_id] = session
                        loaded_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load session {session_id}: {str(e)}")
            
            self.logger.info(f"Loaded {loaded_count} sessions from {self.persistence_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading sessions from file: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self.enable_persistence:
            self._save_sessions_to_file()
        self.cleanup_expired_sessions()


# Utility functions for session management

def create_session_manager(timeout_minutes: int = 30, 
                          enable_persistence: bool = False) -> SessionManager:
    """
    Factory function to create a SessionManager instance.
    
    Args:
        timeout_minutes: Session timeout in minutes
        enable_persistence: Whether to enable file persistence
        
    Returns:
        SessionManager: Configured session manager instance
    """
    return SessionManager(
        timeout_minutes=timeout_minutes,
        enable_persistence=enable_persistence
    )


def get_default_session_manager() -> SessionManager:
    """
    Get a default SessionManager instance for the application.
    
    Returns:
        SessionManager: Default session manager with 30-minute timeout
    """
    return SessionManager(timeout_minutes=30, enable_persistence=True)