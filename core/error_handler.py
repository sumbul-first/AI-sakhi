#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Error Handling and Recovery System for AI Sakhi.

This module provides graceful degradation for service failures,
user-friendly error messages, and recovery options.

Requirements: Error handling across all modules
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
from functools import wraps
import traceback


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors."""
    NETWORK = "network"
    AWS_SERVICE = "aws_service"
    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    CONTENT = "content"
    VOICE_PROCESSING = "voice_processing"
    SESSION = "session"
    UNKNOWN = "unknown"


@dataclass
class ErrorResponse:
    """Standardized error response structure."""
    error_code: str
    error_message: str
    user_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    recovery_options: List[str]
    fallback_available: bool
    technical_details: Optional[str] = None
    timestamp: Optional[str] = None


class ErrorHandler:
    """Comprehensive error handling and recovery system."""
    
    # Error messages in multiple languages
    ERROR_MESSAGES = {
        'hi': {
            'network_error': 'नेटवर्क कनेक्शन में समस्या है। कृपया अपना इंटरनेट कनेक्शन जांचें।',
            'voice_processing_error': 'आवाज़ प्रोसेसिंग में समस्या है। कृपया टेक्स्ट इनपुट का उपयोग करें।',
            'content_not_found': 'सामग्री उपलब्ध नहीं है। कृपया बाद में पुनः प्रयास करें।',
            'session_expired': 'आपका सत्र समाप्त हो गया है। कृपया फिर से लॉगिन करें।',
            'service_unavailable': 'सेवा अस्थायी रूप से अनुपलब्ध है। कृपया बाद में पुनः प्रयास करें।',
            'validation_error': 'अमान्य इनपुट। कृपया अपनी जानकारी जांचें।',
            'unknown_error': 'कुछ गलत हो गया। कृपया पुनः प्रयास करें।',
            'emergency_available': 'आपातकालीन संपर्क ऑफ़लाइन उपलब्ध हैं।'
        },
        'en': {
            'network_error': 'Network connection problem. Please check your internet connection.',
            'voice_processing_error': 'Voice processing issue. Please use text input.',
            'content_not_found': 'Content not available. Please try again later.',
            'session_expired': 'Your session has expired. Please log in again.',
            'service_unavailable': 'Service temporarily unavailable. Please try again later.',
            'validation_error': 'Invalid input. Please check your information.',
            'unknown_error': 'Something went wrong. Please try again.',
            'emergency_available': 'Emergency contacts available offline.'
        },
        'bn': {
            'network_error': 'নেটওয়ার্ক সংযোগ সমস্যা। অনুগ্রহ করে আপনার ইন্টারনেট সংযোগ পরীক্ষা করুন।',
            'voice_processing_error': 'ভয়েস প্রসেসিং সমস্যা। অনুগ্রহ করে টেক্সট ইনপুট ব্যবহার করুন।',
            'content_not_found': 'বিষয়বস্তু উপলব্ধ নেই। অনুগ্রহ করে পরে আবার চেষ্টা করুন।',
            'session_expired': 'আপনার সেশন মেয়াদ শেষ হয়ে গেছে। অনুগ্রহ করে আবার লগইন করুন।',
            'service_unavailable': 'সেবা সাময়িকভাবে অনুপলব্ধ। অনুগ্রহ করে পরে আবার চেষ্টা করুন।',
            'validation_error': 'অবৈধ ইনপুট। অনুগ্রহ করে আপনার তথ্য পরীক্ষা করুন।',
            'unknown_error': 'কিছু ভুল হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।',
            'emergency_available': 'জরুরি যোগাযোগ অফলাইনে উপলব্ধ।'
        }
    }
    
    # Recovery options
    RECOVERY_OPTIONS = {
        'hi': {
            'retry': 'पुनः प্রयास करें',
            'use_text': 'टेक्स्ट इनपुट का उपयोग करें',
            'use_voice': 'आवाज़ इनपुट का उपयोग करें',
            'go_home': 'होम पेज पर जाएं',
            'contact_support': 'सहायता से संपर्क करें',
            'view_offline_content': 'ऑफ़लाइन सामग्री देखें',
            'emergency_contacts': 'आपातकालीन संपर्क देखें'
        },
        'en': {
            'retry': 'Retry',
            'use_text': 'Use text input',
            'use_voice': 'Use voice input',
            'go_home': 'Go to home page',
            'contact_support': 'Contact support',
            'view_offline_content': 'View offline content',
            'emergency_contacts': 'View emergency contacts'
        },
        'bn': {
            'retry': 'আবার চেষ্টা করুন',
            'use_text': 'টেক্সট ইনপুট ব্যবহার করুন',
            'use_voice': 'ভয়েস ইনপুট ব্যবহার করুন',
            'go_home': 'হোম পেজে যান',
            'contact_support': 'সহায়তার সাথে যোগাযোগ করুন',
            'view_offline_content': 'অফলাইন বিষয়বস্তু দেখুন',
            'emergency_contacts': 'জরুরি যোগাযোগ দেখুন'
        }
    }
    
    def __init__(self):
        """Initialize the error handler."""
        self.logger = logging.getLogger(__name__)
        self._error_count = {}
        self._circuit_breakers = {}
    
    def handle_error(self, error: Exception, context: Dict[str, Any],
                    language_code: str = 'hi') -> ErrorResponse:
        """
        Handle an error and generate appropriate response.
        
        Args:
            error: The exception that occurred
            context: Context information about where error occurred
            language_code: Language for error messages
            
        Returns:
            ErrorResponse with user-friendly message and recovery options
        """
        try:
            # Categorize the error
            category = self._categorize_error(error)
            severity = self._determine_severity(error, category)
            
            # Get error messages
            error_code = self._generate_error_code(category, error)
            user_message = self._get_user_message(category, language_code)
            technical_message = str(error)
            
            # Get recovery options
            recovery_options = self._get_recovery_options(category, language_code)
            
            # Check if fallback is available
            fallback_available = self._check_fallback_availability(category, context)
            
            # Log the error
            self._log_error(error, category, severity, context)
            
            # Track error for circuit breaker
            self._track_error(category)
            
            return ErrorResponse(
                error_code=error_code,
                error_message=technical_message,
                user_message=user_message,
                severity=severity,
                category=category,
                recovery_options=recovery_options,
                fallback_available=fallback_available,
                technical_details=traceback.format_exc() if severity == ErrorSeverity.CRITICAL else None
            )
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return self._get_fallback_error_response(language_code)
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize the error based on exception type."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if 'network' in error_message or 'connection' in error_message:
            return ErrorCategory.NETWORK
        elif 'aws' in error_message or 's3' in error_message or 'polly' in error_message:
            return ErrorCategory.AWS_SERVICE
        elif 'voice' in error_message or 'audio' in error_message or 'speech' in error_message:
            return ErrorCategory.VOICE_PROCESSING
        elif 'session' in error_message or 'expired' in error_message:
            return ErrorCategory.SESSION
        elif 'validation' in error_message or 'invalid' in error_message:
            return ErrorCategory.VALIDATION
        elif 'content' in error_message or 'not found' in error_message:
            return ErrorCategory.CONTENT
        else:
            return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity."""
        # Critical errors
        if category == ErrorCategory.DATABASE:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [ErrorCategory.AWS_SERVICE, ErrorCategory.AUTHENTICATION]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.VOICE_PROCESSING, ErrorCategory.CONTENT]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _generate_error_code(self, category: ErrorCategory, error: Exception) -> str:
        """Generate a unique error code."""
        category_code = category.value.upper()[:3]
        error_hash = abs(hash(str(error))) % 10000
        return f"AI_SAKHI_{category_code}_{error_hash:04d}"
    
    def _get_user_message(self, category: ErrorCategory, language_code: str) -> str:
        """Get user-friendly error message."""
        messages = self.ERROR_MESSAGES.get(language_code, self.ERROR_MESSAGES['en'])
        
        category_map = {
            ErrorCategory.NETWORK: 'network_error',
            ErrorCategory.AWS_SERVICE: 'service_unavailable',
            ErrorCategory.VOICE_PROCESSING: 'voice_processing_error',
            ErrorCategory.SESSION: 'session_expired',
            ErrorCategory.VALIDATION: 'validation_error',
            ErrorCategory.CONTENT: 'content_not_found',
            ErrorCategory.UNKNOWN: 'unknown_error'
        }
        
        message_key = category_map.get(category, 'unknown_error')
        return messages.get(message_key, messages['unknown_error'])
    
    def _get_recovery_options(self, category: ErrorCategory, language_code: str) -> List[str]:
        """Get recovery options for the error."""
        options = self.RECOVERY_OPTIONS.get(language_code, self.RECOVERY_OPTIONS['en'])
        
        recovery_map = {
            ErrorCategory.NETWORK: ['retry', 'view_offline_content', 'emergency_contacts'],
            ErrorCategory.AWS_SERVICE: ['retry', 'use_text', 'go_home'],
            ErrorCategory.VOICE_PROCESSING: ['use_text', 'retry', 'go_home'],
            ErrorCategory.SESSION: ['go_home', 'retry'],
            ErrorCategory.VALIDATION: ['retry', 'go_home'],
            ErrorCategory.CONTENT: ['retry', 'go_home', 'view_offline_content'],
            ErrorCategory.UNKNOWN: ['retry', 'go_home', 'contact_support']
        }
        
        option_keys = recovery_map.get(category, ['retry', 'go_home'])
        return [options[key] for key in option_keys if key in options]
    
    def _check_fallback_availability(self, category: ErrorCategory, context: Dict[str, Any]) -> bool:
        """Check if fallback mechanism is available."""
        if category == ErrorCategory.VOICE_PROCESSING:
            return True  # Text input always available
        elif category == ErrorCategory.CONTENT:
            return context.get('offline_content_available', False)
        elif category == ErrorCategory.NETWORK:
            return True  # Emergency contacts available offline
        return False
    
    def _log_error(self, error: Exception, category: ErrorCategory,
                  severity: ErrorSeverity, context: Dict[str, Any]) -> None:
        """Log error with appropriate level."""
        log_message = f"Error [{category.value}] [{severity.value}]: {str(error)}"
        
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra=context)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra=context)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra=context)
        else:
            self.logger.info(log_message, extra=context)
    
    def _track_error(self, category: ErrorCategory) -> None:
        """Track error for circuit breaker pattern."""
        category_key = category.value
        self._error_count[category_key] = self._error_count.get(category_key, 0) + 1
        
        # Implement circuit breaker if too many errors
        if self._error_count[category_key] > 10:
            self._circuit_breakers[category_key] = True
            self.logger.warning(f"Circuit breaker activated for {category_key}")
    
    def is_circuit_open(self, category: ErrorCategory) -> bool:
        """Check if circuit breaker is open for a category."""
        return self._circuit_breakers.get(category.value, False)
    
    def reset_circuit(self, category: ErrorCategory) -> None:
        """Reset circuit breaker for a category."""
        category_key = category.value
        self._circuit_breakers[category_key] = False
        self._error_count[category_key] = 0
        self.logger.info(f"Circuit breaker reset for {category_key}")
    
    def _get_fallback_error_response(self, language_code: str) -> ErrorResponse:
        """Get fallback error response when error handler itself fails."""
        messages = self.ERROR_MESSAGES.get(language_code, self.ERROR_MESSAGES['en'])
        options = self.RECOVERY_OPTIONS.get(language_code, self.RECOVERY_OPTIONS['en'])
        
        return ErrorResponse(
            error_code="AI_SAKHI_UNKNOWN_0000",
            error_message="Error handler failure",
            user_message=messages['unknown_error'],
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.UNKNOWN,
            recovery_options=[options['retry'], options['go_home']],
            fallback_available=True
        )


# Decorator for automatic error handling
def handle_errors(language_code: str = 'hi', context: Optional[Dict[str, Any]] = None):
    """
    Decorator to automatically handle errors in functions.
    
    Args:
        language_code: Language for error messages
        context: Additional context information
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                error_context = context or {}
                error_context['function'] = func.__name__
                error_response = error_handler.handle_error(e, error_context, language_code)
                
                # Return error response in appropriate format
                return {
                    'status': 'error',
                    'error_code': error_response.error_code,
                    'message': error_response.user_message,
                    'recovery_options': error_response.recovery_options,
                    'fallback_available': error_response.fallback_available
                }
        return wrapper
    return decorator


# Graceful degradation helper
class GracefulDegradation:
    """Helper class for implementing graceful degradation."""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable,
                     error_handler: Optional[ErrorHandler] = None) -> Any:
        """
        Execute primary function with fallback on failure.
        
        Args:
            primary_func: Primary function to execute
            fallback_func: Fallback function if primary fails
            error_handler: Optional error handler
            
        Returns:
            Result from primary or fallback function
        """
        try:
            return primary_func()
        except Exception as e:
            if error_handler:
                error_handler.handle_error(e, {'function': primary_func.__name__})
            
            try:
                return fallback_func()
            except Exception as fallback_error:
                if error_handler:
                    error_handler.handle_error(
                        fallback_error,
                        {'function': fallback_func.__name__, 'is_fallback': True}
                    )
                raise
    
    @staticmethod
    def retry_with_backoff(func: Callable, max_retries: int = 3,
                          backoff_factor: float = 2.0) -> Any:
        """
        Retry function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            backoff_factor: Backoff multiplier
            
        Returns:
            Result from function
        """
        import time
        
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
        
        raise last_exception


# Offline emergency contacts helper
class OfflineEmergencyAccess:
    """Provide offline access to emergency contacts."""
    
    EMERGENCY_CONTACTS = {
        'hi': [
            {'name': 'राष्ट्रीय आपातकालीन', 'number': '112', 'type': 'सभी आपातकाल'},
            {'name': 'एम्बुलेंस', 'number': '108', 'type': 'चिकित्सा आपातकाल'},
            {'name': 'महिला हेल्पलाइन', 'number': '1091', 'type': 'महिला सुरक्षा'}
        ],
        'en': [
            {'name': 'National Emergency', 'number': '112', 'type': 'All emergencies'},
            {'name': 'Ambulance', 'number': '108', 'type': 'Medical emergency'},
            {'name': 'Women Helpline', 'number': '1091', 'type': 'Women safety'}
        ],
        'bn': [
            {'name': 'জাতীয় জরুরি', 'number': '112', 'type': 'সব জরুরি অবস্থা'},
            {'name': 'অ্যাম্বুলেন্স', 'number': '108', 'type': 'চিকিৎসা জরুরি'},
            {'name': 'মহিলা হেল্পলাইন', 'number': '1091', 'type': 'মহিলা নিরাপত্তা'}
        ]
    }
    
    @classmethod
    def get_contacts(cls, language_code: str = 'hi') -> List[Dict[str, str]]:
        """Get emergency contacts for offline access."""
        return cls.EMERGENCY_CONTACTS.get(language_code, cls.EMERGENCY_CONTACTS['en'])


# Create global error handler instance
error_handler = ErrorHandler()
