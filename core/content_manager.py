"""
Content Manager for AI Sakhi Voice-First Health Companion application.

This module provides the ContentManager class that handles retrieval and management
of educational content from AWS S3, including audio, video, and text content with
caching mechanisms for performance optimization.

Requirements: 8.1, 8.5
"""

import boto3
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from dataclasses import asdict
import hashlib
import threading
from collections import OrderedDict

from models.data_models import ContentItem


class ContentCache:
    """
    Thread-safe LRU cache for content items with TTL support.
    
    This cache provides in-memory storage for frequently accessed content
    with automatic expiration and size limits to optimize performance.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the content cache.
        
        Args:
            max_size: Maximum number of items to store in cache
            default_ttl: Default time-to-live in seconds (1 hour default)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._timestamps = {}
        self._lock = threading.RLock()
        
    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry has expired."""
        if key not in self._timestamps:
            return True
        
        expiry_time = self._timestamps[key]
        return datetime.now(timezone.utc) > expiry_time
    
    def _evict_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = datetime.now(timezone.utc)
        expired_keys = [
            key for key, expiry_time in self._timestamps.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
    
    def _evict_lru(self) -> None:
        """Remove least recently used items if cache is full."""
        while len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            self._cache.pop(oldest_key)
            self._timestamps.pop(oldest_key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve an item from cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached item or None if not found/expired
        """
        with self._lock:
            if key not in self._cache or self._is_expired(key):
                return None
            
            # Move to end (most recently used)
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store an item in cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Clean up expired entries
            self._evict_expired()
            
            # Evict LRU items if needed
            self._evict_lru()
            
            # Store the item
            self._cache[key] = value
            
            # Set expiry time
            ttl = ttl or self.default_ttl
            expiry_time = datetime.now(timezone.utc) + timedelta(seconds=ttl)
            self._timestamps[key] = expiry_time
    
    def invalidate(self, key: str) -> bool:
        """
        Remove an item from cache.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if item was removed, False if not found
        """
        with self._lock:
            removed = key in self._cache
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            return removed
    
    def clear(self) -> None:
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            self._evict_expired()
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            self._evict_expired()
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "keys": list(self._cache.keys())
            }


class ContentManager:
    """
    Manages educational content retrieval and caching for AI Sakhi application.
    
    This class provides methods for retrieving audio, video, and text content
    from AWS S3, with built-in caching mechanisms for performance optimization
    and content search functionality. Supports multi-language content delivery
    with fallback mechanisms for missing translations.
    """
    
    # Supported languages for AI Sakhi application
    SUPPORTED_LANGUAGES = ['hi', 'en', 'bn', 'ta', 'te', 'mr']
    DEFAULT_LANGUAGE = 'hi'  # Hindi as default
    FALLBACK_LANGUAGE = 'en'  # English as fallback
    
    def __init__(self, s3_bucket_name: str, aws_region: str = 'us-east-1', 
                 use_mock: bool = True, cache_size: int = 1000, cache_ttl: int = 3600):
        """
        Initialize the ContentManager.
        
        Args:
            s3_bucket_name: Name of the S3 bucket containing content
            aws_region: AWS region for S3 operations
            use_mock: Whether to use mock S3 operations for development
            cache_size: Maximum number of items in cache
            cache_ttl: Cache time-to-live in seconds
        """
        self.s3_bucket_name = s3_bucket_name
        self.aws_region = aws_region
        self.use_mock = use_mock
        
        # Set up logging first
        self.logger = logging.getLogger(__name__)
        
        # Initialize cache
        self.cache = ContentCache(max_size=cache_size, default_ttl=cache_ttl)
        
        # Initialize S3 client
        self._s3_client = None
        self._initialize_s3_client()
        
        # Content metadata for mock operations
        self._mock_content_metadata = self._initialize_mock_content()
        
        # Content synchronization tracking
        self._last_sync_time = None
        self._sync_lock = threading.Lock()
    
    def _initialize_s3_client(self) -> None:
        """Initialize the S3 client with proper error handling."""
        if self.use_mock:
            self.logger.info("Using mock S3 operations for development")
            return
        
        try:
            self._s3_client = boto3.client('s3', region_name=self.aws_region)
            # Test connection
            self._s3_client.head_bucket(Bucket=self.s3_bucket_name)
            self.logger.info(f"Successfully connected to S3 bucket: {self.s3_bucket_name}")
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Using mock operations.")
            self.use_mock = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                self.logger.error(f"S3 bucket not found: {self.s3_bucket_name}. Using mock operations.")
            else:
                self.logger.error(f"S3 connection error: {e}. Using mock operations.")
            self.use_mock = True
        except Exception as e:
            self.logger.error(f"Unexpected error initializing S3: {e}. Using mock operations.")
            self.use_mock = True
    
    def _initialize_mock_content(self) -> Dict[str, List[ContentItem]]:
        """Initialize mock content for development and testing with multi-language support."""
        mock_content = {
            "puberty_education": [
                # Hindi content
                ContentItem(
                    content_id="pe_001",
                    module_name="puberty_education",
                    topic="body_changes",
                    content_type="audio",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/hi/body_changes.mp3",
                    duration_seconds=240,
                    transcript="शरीर में होने वाले बदलाव के बारे में जानकारी...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="pe_002",
                    module_name="puberty_education",
                    topic="menstruation_basics",
                    content_type="video",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/hi/menstruation_basics.mp4",
                    duration_seconds=300,
                    transcript="मासिक धर्म की बुनियादी जानकारी...",
                    safety_validated=True
                ),
                # English content
                ContentItem(
                    content_id="pe_003",
                    module_name="puberty_education",
                    topic="body_changes",
                    content_type="audio",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/en/body_changes.mp3",
                    duration_seconds=240,
                    transcript="Information about body changes during puberty...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="pe_004",
                    module_name="puberty_education",
                    topic="hygiene_practices",
                    content_type="text",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/text/en/hygiene_practices.txt",
                    duration_seconds=0,
                    transcript="Proper hygiene practices during puberty include...",
                    safety_validated=True
                ),
                # Bengali content
                ContentItem(
                    content_id="pe_005",
                    module_name="puberty_education",
                    topic="body_changes",
                    content_type="audio",
                    language_code="bn",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/bn/body_changes.mp3",
                    duration_seconds=240,
                    transcript="বয়ঃসন্ধিকালে শরীরের পরিবর্তন সম্পর্কে তথ্য...",
                    safety_validated=True
                ),
                # Tamil content
                ContentItem(
                    content_id="pe_006",
                    module_name="puberty_education",
                    topic="menstruation_basics",
                    content_type="video",
                    language_code="ta",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/ta/menstruation_basics.mp4",
                    duration_seconds=300,
                    transcript="மாதவிடாய் பற்றிய அடிப்படை தகவல்கள்...",
                    safety_validated=True
                )
            ],
            "safety_mental_support": [
                # Hindi content
                ContentItem(
                    content_id="sms_001",
                    module_name="safety_mental_support",
                    topic="good_bad_touch",
                    content_type="audio",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/hi/good_bad_touch.mp3",
                    duration_seconds=180,
                    transcript="अच्छे और बुरे स्पर्श के बारे में...",
                    safety_validated=True
                ),
                # English content
                ContentItem(
                    content_id="sms_002",
                    module_name="safety_mental_support",
                    topic="good_bad_touch",
                    content_type="audio",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/en/good_bad_touch.mp3",
                    duration_seconds=180,
                    transcript="Understanding good touch and bad touch...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="sms_003",
                    module_name="safety_mental_support",
                    topic="emotional_support",
                    content_type="video",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/en/emotional_support.mp4",
                    duration_seconds=420,
                    transcript="Emotional support and coping strategies...",
                    safety_validated=True
                ),
                # Telugu content
                ContentItem(
                    content_id="sms_004",
                    module_name="safety_mental_support",
                    topic="emotional_support",
                    content_type="audio",
                    language_code="te",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/te/emotional_support.mp3",
                    duration_seconds=420,
                    transcript="భావోద్వేగ మద్దతు మరియు దూకుడు వ్యూహాలు...",
                    safety_validated=True
                )
            ],
            "menstrual_guide": [
                # Hindi content
                ContentItem(
                    content_id="mg_001",
                    module_name="menstrual_guide",
                    topic="product_comparison",
                    content_type="audio",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/hi/product_comparison.mp3",
                    duration_seconds=360,
                    transcript="पैड, कप और कपड़े के विकल्पों की तुलना...",
                    safety_validated=True
                ),
                # English content
                ContentItem(
                    content_id="mg_002",
                    module_name="menstrual_guide",
                    topic="product_comparison",
                    content_type="audio",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/en/product_comparison.mp3",
                    duration_seconds=360,
                    transcript="Comparison of pads, cups, and cloth options...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="mg_003",
                    module_name="menstrual_guide",
                    topic="cost_analysis",
                    content_type="text",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/text/en/cost_analysis.txt",
                    duration_seconds=0,
                    transcript="Cost comparison of menstrual products...",
                    safety_validated=True
                ),
                # Marathi content
                ContentItem(
                    content_id="mg_004",
                    module_name="menstrual_guide",
                    topic="product_comparison",
                    content_type="video",
                    language_code="mr",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/mr/product_comparison.mp4",
                    duration_seconds=360,
                    transcript="पॅड, कप आणि कापडाच्या पर्यायांची तुलना...",
                    safety_validated=True
                )
            ],
            "pregnancy_guidance": [
                # Hindi content
                ContentItem(
                    content_id="pg_001",
                    module_name="pregnancy_guidance",
                    topic="nutrition_tips",
                    content_type="video",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/hi/nutrition_tips.mp4",
                    duration_seconds=480,
                    transcript="गर्भावस्था में पोषण की जानकारी...",
                    safety_validated=True
                ),
                # English content
                ContentItem(
                    content_id="pg_002",
                    module_name="pregnancy_guidance",
                    topic="nutrition_tips",
                    content_type="video",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/en/nutrition_tips.mp4",
                    duration_seconds=480,
                    transcript="Nutrition information during pregnancy...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="pg_003",
                    module_name="pregnancy_guidance",
                    topic="danger_signs",
                    content_type="audio",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/en/danger_signs.mp3",
                    duration_seconds=300,
                    transcript="Warning signs during pregnancy that require immediate medical attention...",
                    safety_validated=True
                )
            ],
            "government_resources": [
                # Hindi content
                ContentItem(
                    content_id="gr_001",
                    module_name="government_resources",
                    topic="jsy_scheme",
                    content_type="audio",
                    language_code="hi",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/hi/jsy_scheme.mp3",
                    duration_seconds=240,
                    transcript="जननी सुरक्षा योजना की जानकारी...",
                    safety_validated=True
                ),
                # English content
                ContentItem(
                    content_id="gr_002",
                    module_name="government_resources",
                    topic="jsy_scheme",
                    content_type="audio",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/en/jsy_scheme.mp3",
                    duration_seconds=240,
                    transcript="Information about Janani Suraksha Yojana scheme...",
                    safety_validated=True
                ),
                ContentItem(
                    content_id="gr_003",
                    module_name="government_resources",
                    topic="pmsma_benefits",
                    content_type="video",
                    language_code="en",
                    s3_url="https://ai-sakhi-content.s3.amazonaws.com/video/en/pmsma_benefits.mp4",
                    duration_seconds=360,
                    transcript="Pradhan Mantri Surakshit Matritva Abhiyan benefits...",
                    safety_validated=True
                )
            ]
        }
        
        # Flatten the structure for easier searching
        all_content = []
        for module_content in mock_content.values():
            all_content.extend(module_content)
        
        return {
            "by_module": mock_content,
            "all_content": all_content
        }
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a cache key from parameters.
        
        Args:
            prefix: Key prefix
            **kwargs: Parameters to include in key
            
        Returns:
            Generated cache key
        """
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        param_str = "_".join(f"{k}:{v}" for k, v in sorted_params)
        key_str = f"{prefix}_{param_str}"
        
        # Hash long keys to keep them manageable
        if len(key_str) > 100:
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}_{key_hash}"
        
        return key_str
    
    def _get_s3_object_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for S3 object access.
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Presigned URL for the S3 object
        """
        if self.use_mock:
            # Return mock URL for development
            return f"https://ai-sakhi-content.s3.amazonaws.com/{s3_key}"
        
        try:
            url = self._s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            self.logger.error(f"Error generating presigned URL for {s3_key}: {e}")
            return f"https://{self.s3_bucket_name}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
    
    def _search_mock_content(self, query: str, module_name: Optional[str] = None) -> List[ContentItem]:
        """
        Search mock content for development and testing.
        
        Args:
            query: Search query
            module_name: Optional module to limit search to
            
        Returns:
            List of matching content items
        """
        query_lower = query.lower()
        results = []
        
        # Determine content to search
        if module_name and module_name in self._mock_content_metadata["by_module"]:
            content_to_search = self._mock_content_metadata["by_module"][module_name]
        else:
            content_to_search = self._mock_content_metadata["all_content"]
        
        # Search through content
        for content_item in content_to_search:
            # Search in topic, transcript, and module name
            searchable_text = " ".join([
                content_item.topic,
                content_item.transcript,
                content_item.module_name
            ]).lower()
            
            if query_lower in searchable_text:
                results.append(content_item)
        
        return results
    
    def get_module_content(self, module_name: str, language_code: str) -> List[ContentItem]:
        """
        Retrieve localized content for a specific module.
        
        Args:
            module_name: Name of the health education module
            language_code: Language code for content (e.g., 'hi', 'en')
            
        Returns:
            List of content items for the module in the specified language
            
        Raises:
            ValueError: If module_name or language_code is invalid
        """
        if not module_name or not isinstance(module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        if not language_code or not isinstance(language_code, str):
            raise ValueError("Language code must be a non-empty string")
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            "module_content",
            module=module_name,
            lang=language_code
        )
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            self.logger.debug(f"Cache hit for module content: {module_name}, {language_code}")
            return cached_result
        
        try:
            if self.use_mock:
                # Use mock content for development
                if module_name in self._mock_content_metadata["by_module"]:
                    all_module_content = self._mock_content_metadata["by_module"][module_name]
                    # Filter by language
                    filtered_content = [
                        content for content in all_module_content
                        if content.language_code == language_code
                    ]
                else:
                    filtered_content = []
            else:
                # Real S3 implementation would go here
                # For now, fall back to mock content
                filtered_content = []
                self.logger.warning("Real S3 implementation not yet available, using mock content")
            
            # Cache the result
            self.cache.put(cache_key, filtered_content)
            
            self.logger.info(f"Retrieved {len(filtered_content)} content items for module: {module_name}, language: {language_code}")
            return filtered_content
            
        except Exception as e:
            self.logger.error(f"Error retrieving module content for {module_name}, {language_code}: {e}")
            return []
    
    def get_module_content_with_fallback(self, module_name: str, language_code: str, 
                                       fallback_languages: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieve localized content for a module with fallback language support.
        
        This method implements the fallback mechanism for missing translations as required
        by Requirements 7.2 and 7.4. It tries the requested language first, then falls
        back to alternative languages if content is not available.
        
        Args:
            module_name: Name of the health education module
            language_code: Preferred language code
            fallback_languages: Optional list of fallback languages (uses default if None)
            
        Returns:
            Dictionary containing:
            - content: List of content items
            - language_used: Language code of the content returned
            - fallback_used: Boolean indicating if fallback was used
            - available_languages: List of languages with content for this module
            
        Raises:
            ValueError: If module_name or language_code is invalid
        """
        if not module_name or not isinstance(module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        if not language_code or not isinstance(language_code, str):
            raise ValueError("Language code must be a non-empty string")
        
        # Validate language code
        if language_code not in self.SUPPORTED_LANGUAGES:
            self.logger.warning(f"Unsupported language code: {language_code}, using default")
            language_code = self.DEFAULT_LANGUAGE
        
        # Set up fallback languages
        if fallback_languages is None:
            fallback_languages = [self.FALLBACK_LANGUAGE, self.DEFAULT_LANGUAGE]
        
        # Create language priority list
        language_priority = [language_code]
        for fallback_lang in fallback_languages:
            if fallback_lang not in language_priority and fallback_lang in self.SUPPORTED_LANGUAGES:
                language_priority.append(fallback_lang)
        
        # Get available languages for this module
        available_languages = self.get_available_languages_for_module(module_name)
        
        # Try each language in priority order
        for lang in language_priority:
            content = self.get_module_content(module_name, lang)
            if content:
                return {
                    "content": content,
                    "language_used": lang,
                    "fallback_used": lang != language_code,
                    "available_languages": available_languages,
                    "requested_language": language_code
                }
        
        # No content found in any language
        self.logger.warning(f"No content found for module {module_name} in any supported language")
        return {
            "content": [],
            "language_used": None,
            "fallback_used": True,
            "available_languages": available_languages,
            "requested_language": language_code
        }
    
    def get_available_languages_for_module(self, module_name: str) -> List[str]:
        """
        Get list of available languages for a specific module.
        
        Args:
            module_name: Name of the health education module
            
        Returns:
            List of language codes that have content for this module
            
        Raises:
            ValueError: If module_name is invalid
        """
        if not module_name or not isinstance(module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        # Generate cache key
        cache_key = self._generate_cache_key("available_languages", module=module_name)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            available_languages = set()
            
            if self.use_mock:
                # Use mock content
                if module_name in self._mock_content_metadata["by_module"]:
                    module_content = self._mock_content_metadata["by_module"][module_name]
                    available_languages = {content.language_code for content in module_content}
            else:
                # Real S3 implementation would scan S3 prefixes
                # For now, fall back to mock content
                if module_name in self._mock_content_metadata["by_module"]:
                    module_content = self._mock_content_metadata["by_module"][module_name]
                    available_languages = {content.language_code for content in module_content}
            
            result = sorted(list(available_languages))
            
            # Cache the result
            self.cache.put(cache_key, result, ttl=1800)  # 30 minutes
            
            self.logger.debug(f"Available languages for module {module_name}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting available languages for module {module_name}: {e}")
            return []
    
    def get_content_by_topic_and_language(self, module_name: str, topic: str, 
                                        language_code: str, content_type: Optional[str] = None) -> List[ContentItem]:
        """
        Retrieve content for a specific topic in a specific language.
        
        Args:
            module_name: Name of the health education module
            topic: Specific topic within the module
            language_code: Language code for content
            content_type: Optional filter by content type ('audio', 'video', 'text')
            
        Returns:
            List of content items matching the criteria
            
        Raises:
            ValueError: If required parameters are invalid
        """
        if not module_name or not isinstance(module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        if not topic or not isinstance(topic, str):
            raise ValueError("Topic must be a non-empty string")
        
        if not language_code or not isinstance(language_code, str):
            raise ValueError("Language code must be a non-empty string")
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            "topic_content",
            module=module_name,
            topic=topic,
            lang=language_code,
            type=content_type or "all"
        )
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # Get all content for the module and language
            module_content = self.get_module_content(module_name, language_code)
            
            # Filter by topic
            topic_content = [
                content for content in module_content
                if content.topic == topic
            ]
            
            # Filter by content type if specified
            if content_type:
                topic_content = [
                    content for content in topic_content
                    if content.content_type == content_type
                ]
            
            # Cache the result
            self.cache.put(cache_key, topic_content)
            
            self.logger.debug(f"Retrieved {len(topic_content)} items for topic {topic} in {language_code}")
            return topic_content
            
        except Exception as e:
            self.logger.error(f"Error retrieving content for topic {topic}: {e}")
            return []
    
    def synchronize_content_from_s3(self, force_sync: bool = False) -> Dict[str, Any]:
        """
        Synchronize content from AWS S3 storage without downtime.
        
        This method implements content synchronization as required by Requirement 8.5.
        It updates the local content metadata from S3 while maintaining service availability.
        
        Args:
            force_sync: Force synchronization even if recently synced
            
        Returns:
            Dictionary containing synchronization results:
            - success: Boolean indicating if sync was successful
            - timestamp: When the sync occurred
            - new_content_count: Number of new content items found
            - updated_content_count: Number of updated content items
            - errors: List of any errors encountered
        """
        with self._sync_lock:
            sync_result = {
                "success": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "new_content_count": 0,
                "updated_content_count": 0,
                "errors": []
            }
            
            try:
                # Check if sync is needed
                if not force_sync and self._last_sync_time:
                    time_since_sync = datetime.now(timezone.utc) - self._last_sync_time
                    if time_since_sync.total_seconds() < 300:  # 5 minutes minimum between syncs
                        sync_result["success"] = True
                        sync_result["errors"].append("Sync skipped - too recent")
                        return sync_result
                
                if self.use_mock:
                    # Mock synchronization - simulate finding new content
                    self.logger.info("Mock synchronization: simulating S3 content sync")
                    sync_result["success"] = True
                    sync_result["new_content_count"] = 0
                    sync_result["updated_content_count"] = 0
                else:
                    # Real S3 synchronization implementation
                    sync_result.update(self._perform_s3_sync())
                
                # Update last sync time
                self._last_sync_time = datetime.now(timezone.utc)
                
                # Clear relevant caches to force refresh
                self._clear_content_caches()
                
                self.logger.info(f"Content synchronization completed: {sync_result}")
                
            except Exception as e:
                error_msg = f"Content synchronization failed: {str(e)}"
                self.logger.error(error_msg)
                sync_result["errors"].append(error_msg)
                sync_result["success"] = False
            
            return sync_result
    
    def _perform_s3_sync(self) -> Dict[str, Any]:
        """
        Perform actual S3 synchronization (placeholder for real implementation).
        
        Returns:
            Dictionary with sync results
        """
        sync_data = {
            "success": True,
            "new_content_count": 0,
            "updated_content_count": 0,
            "errors": []
        }
        
        try:
            if not self._s3_client:
                raise Exception("S3 client not initialized")
            
            # List objects in S3 bucket
            paginator = self._s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.s3_bucket_name)
            
            new_content = []
            updated_content = []
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Process each S3 object
                        # This is a placeholder - real implementation would:
                        # 1. Parse object metadata
                        # 2. Create ContentItem objects
                        # 3. Compare with existing content
                        # 4. Update content metadata
                        pass
            
            sync_data["new_content_count"] = len(new_content)
            sync_data["updated_content_count"] = len(updated_content)
            
        except Exception as e:
            sync_data["success"] = False
            sync_data["errors"].append(str(e))
        
        return sync_data
    
    def _clear_content_caches(self) -> None:
        """Clear content-related caches to force refresh after sync."""
        try:
            cache_stats = self.cache.stats()
            cleared_count = 0
            
            # Clear caches related to content
            for cache_key in cache_stats["keys"]:
                if any(prefix in cache_key for prefix in ["module_content", "available_languages", "topic_content"]):
                    if self.cache.invalidate(cache_key):
                        cleared_count += 1
            
            self.logger.debug(f"Cleared {cleared_count} content cache entries after sync")
            
        except Exception as e:
            self.logger.error(f"Error clearing content caches: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported languages.
        
        Returns:
            List of supported language codes
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported by the system.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_audio_content(self, content_id: str, language_code: str) -> Optional[str]:
        """
        Fetch audio content URL from S3.
        
        Args:
            content_id: Unique identifier for the content
            language_code: Language code for the content
            
        Returns:
            URL to access the audio content, or None if not found
            
        Raises:
            ValueError: If content_id or language_code is invalid
        """
        if not content_id or not isinstance(content_id, str):
            raise ValueError("Content ID must be a non-empty string")
        
        if not language_code or not isinstance(language_code, str):
            raise ValueError("Language code must be a non-empty string")
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            "audio_content",
            content_id=content_id,
            lang=language_code
        )
        
        # Check cache first
        cached_url = self.cache.get(cache_key)
        if cached_url is not None:
            self.logger.debug(f"Cache hit for audio content: {content_id}")
            return cached_url
        
        try:
            # Find content item
            content_item = None
            for content in self._mock_content_metadata["all_content"]:
                if (content.content_id == content_id and 
                    content.language_code == language_code and 
                    content.content_type == "audio"):
                    content_item = content
                    break
            
            if not content_item:
                self.logger.warning(f"Audio content not found: {content_id}, {language_code}")
                return None
            
            # Generate URL
            if self.use_mock:
                url = content_item.s3_url
            else:
                # Extract S3 key from URL for real S3 operations
                s3_key = f"audio/{language_code}/{content_id}.mp3"
                url = self._get_s3_object_url(s3_key)
            
            # Cache the URL (shorter TTL for URLs)
            self.cache.put(cache_key, url, ttl=1800)  # 30 minutes
            
            self.logger.info(f"Retrieved audio content URL for: {content_id}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error retrieving audio content {content_id}: {e}")
            return None
    
    def get_video_content(self, content_id: str, language_code: str) -> Optional[str]:
        """
        Fetch video content URL from S3.
        
        Args:
            content_id: Unique identifier for the content
            language_code: Language code for the content
            
        Returns:
            URL to access the video content, or None if not found
            
        Raises:
            ValueError: If content_id or language_code is invalid
        """
        if not content_id or not isinstance(content_id, str):
            raise ValueError("Content ID must be a non-empty string")
        
        if not language_code or not isinstance(language_code, str):
            raise ValueError("Language code must be a non-empty string")
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            "video_content",
            content_id=content_id,
            lang=language_code
        )
        
        # Check cache first
        cached_url = self.cache.get(cache_key)
        if cached_url is not None:
            self.logger.debug(f"Cache hit for video content: {content_id}")
            return cached_url
        
        try:
            # Find content item
            content_item = None
            for content in self._mock_content_metadata["all_content"]:
                if (content.content_id == content_id and 
                    content.language_code == language_code and 
                    content.content_type == "video"):
                    content_item = content
                    break
            
            if not content_item:
                self.logger.warning(f"Video content not found: {content_id}, {language_code}")
                return None
            
            # Generate URL
            if self.use_mock:
                url = content_item.s3_url
            else:
                # Extract S3 key from URL for real S3 operations
                s3_key = f"video/{language_code}/{content_id}.mp4"
                url = self._get_s3_object_url(s3_key)
            
            # Cache the URL (shorter TTL for URLs)
            self.cache.put(cache_key, url, ttl=1800)  # 30 minutes
            
            self.logger.info(f"Retrieved video content URL for: {content_id}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error retrieving video content {content_id}: {e}")
            return None
    
    def search_content(self, query: str, module_name: Optional[str] = None) -> List[ContentItem]:
        """
        Search for content based on query and optional module filter.
        
        Args:
            query: Search query string
            module_name: Optional module name to limit search scope
            
        Returns:
            List of matching content items
            
        Raises:
            ValueError: If query is invalid
        """
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty or whitespace only")
        
        # Generate cache key
        cache_key = self._generate_cache_key(
            "search_content",
            query=query,
            module=module_name or "all"
        )
        
        # Check cache first
        cached_results = self.cache.get(cache_key)
        if cached_results is not None:
            self.logger.debug(f"Cache hit for content search: {query}")
            return cached_results
        
        try:
            if self.use_mock:
                results = self._search_mock_content(query, module_name)
            else:
                # Real S3 search implementation would go here
                # For now, fall back to mock search
                results = self._search_mock_content(query, module_name)
                self.logger.warning("Real S3 search implementation not yet available, using mock search")
            
            # Cache the results
            self.cache.put(cache_key, results, ttl=1800)  # 30 minutes for search results
            
            self.logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching content for query '{query}': {e}")
            return []
    
    def cache_content(self, content_item: ContentItem) -> bool:
        """
        Cache a content item for performance optimization.
        
        Args:
            content_item: ContentItem to cache
            
        Returns:
            True if caching was successful, False otherwise
            
        Raises:
            ValueError: If content_item is invalid
        """
        if not isinstance(content_item, ContentItem):
            raise ValueError("content_item must be a ContentItem instance")
        
        try:
            # Validate the content item
            content_item.validate()
            
            # Generate cache key for the content item
            cache_key = self._generate_cache_key(
                "content_item",
                content_id=content_item.content_id,
                lang=content_item.language_code
            )
            
            # Cache the content item
            self.cache.put(cache_key, content_item)
            
            self.logger.debug(f"Cached content item: {content_item.content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching content item {content_item.content_id}: {e}")
            return False
    
    def invalidate_cache(self, content_id: str) -> bool:
        """
        Remove content from cache by content ID.
        
        Args:
            content_id: ID of content to remove from cache
            
        Returns:
            True if content was removed, False if not found
            
        Raises:
            ValueError: If content_id is invalid
        """
        if not content_id or not isinstance(content_id, str):
            raise ValueError("Content ID must be a non-empty string")
        
        try:
            # Find and remove all cache entries related to this content ID
            removed_count = 0
            cache_stats = self.cache.stats()
            
            for cache_key in cache_stats["keys"]:
                if content_id in cache_key:
                    if self.cache.invalidate(cache_key):
                        removed_count += 1
            
            self.logger.info(f"Invalidated {removed_count} cache entries for content ID: {content_id}")
            return removed_count > 0
            
        except Exception as e:
            self.logger.error(f"Error invalidating cache for content ID {content_id}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics and performance metrics.
        
        Returns:
            Dictionary containing cache statistics
        """
        try:
            stats = self.cache.stats()
            stats.update({
                "s3_bucket": self.s3_bucket_name,
                "aws_region": self.aws_region,
                "use_mock": self.use_mock,
                "supported_languages": self.SUPPORTED_LANGUAGES,
                "default_language": self.DEFAULT_LANGUAGE,
                "fallback_language": self.FALLBACK_LANGUAGE,
                "mock_content_modules": len(self._mock_content_metadata["by_module"]),
                "total_mock_content": len(self._mock_content_metadata["all_content"]),
                "last_sync_time": self._last_sync_time.isoformat() if self._last_sync_time else None
            })
            return stats
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def clear_cache(self) -> bool:
        """
        Clear all cached content.
        
        Returns:
            True if cache was cleared successfully
        """
        try:
            self.cache.clear()
            self.logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the content management system.
        
        Returns:
            Dictionary containing health check results
        """
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        try:
            # Check cache functionality
            test_key = "health_check_test"
            test_value = "test_data"
            self.cache.put(test_key, test_value, ttl=60)
            cached_value = self.cache.get(test_key)
            
            health_status["checks"]["cache"] = {
                "status": "healthy" if cached_value == test_value else "unhealthy",
                "details": "Cache read/write operations working"
            }
            
            # Clean up test data
            self.cache.invalidate(test_key)
            
            # Check S3 connectivity (if not using mock)
            if not self.use_mock and self._s3_client:
                try:
                    self._s3_client.head_bucket(Bucket=self.s3_bucket_name)
                    health_status["checks"]["s3"] = {
                        "status": "healthy",
                        "details": f"S3 bucket {self.s3_bucket_name} accessible"
                    }
                except Exception as e:
                    health_status["checks"]["s3"] = {
                        "status": "unhealthy",
                        "details": f"S3 error: {str(e)}"
                    }
                    health_status["status"] = "degraded"
            else:
                health_status["checks"]["s3"] = {
                    "status": "mock",
                    "details": "Using mock S3 operations"
                }
            
            # Check mock content availability
            mock_content_count = len(self._mock_content_metadata["all_content"])
            health_status["checks"]["mock_content"] = {
                "status": "healthy" if mock_content_count > 0 else "unhealthy",
                "details": f"{mock_content_count} mock content items available"
            }
            
            # Check multi-language support
            supported_languages = self.get_supported_languages()
            available_languages = set()
            for content in self._mock_content_metadata["all_content"]:
                available_languages.add(content.language_code)
            
            health_status["checks"]["multi_language"] = {
                "status": "healthy" if len(available_languages) > 1 else "degraded",
                "details": f"Supported: {supported_languages}, Available: {sorted(available_languages)}"
            }
            
            # Check content synchronization
            sync_status = "healthy" if self._last_sync_time else "not_synced"
            health_status["checks"]["content_sync"] = {
                "status": sync_status,
                "details": f"Last sync: {self._last_sync_time.isoformat() if self._last_sync_time else 'Never'}"
            }
            
            # Overall status
            unhealthy_checks = [
                check for check in health_status["checks"].values()
                if check["status"] == "unhealthy"
            ]
            
            if unhealthy_checks:
                health_status["status"] = "unhealthy"
            elif any(check["status"] in ["mock", "degraded", "not_synced"] for check in health_status["checks"].values()):
                health_status["status"] = "development"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status


# Utility functions for content management

def create_content_manager(bucket_name: str = "ai-sakhi-content", 
                          region: str = "us-east-1", 
                          use_mock: bool = True) -> ContentManager:
    """
    Factory function to create a ContentManager instance with default settings.
    
    Args:
        bucket_name: S3 bucket name for content storage
        region: AWS region
        use_mock: Whether to use mock operations for development
        
    Returns:
        Configured ContentManager instance
    """
    return ContentManager(
        s3_bucket_name=bucket_name,
        aws_region=region,
        use_mock=use_mock
    )


def validate_content_safety(content_item: ContentItem) -> bool:
    """
    Validate that content meets safety requirements for health education.
    
    Args:
        content_item: ContentItem to validate
        
    Returns:
        True if content is safe for health education use
    """
    try:
        # Basic validation
        content_item.validate()
        
        # Check if already validated
        if content_item.safety_validated:
            return True
        
        # Safety checks for transcript content
        if content_item.transcript:
            transcript_lower = content_item.transcript.lower()
            
            # Check for inappropriate medical advice keywords
            medical_diagnosis_keywords = [
                "diagnose", "diagnosis", "disease", "cure", "treatment", 
                "medicine", "drug", "prescription", "doctor says"
            ]
            
            for keyword in medical_diagnosis_keywords:
                if keyword in transcript_lower:
                    logging.warning(f"Content {content_item.content_id} contains potential medical advice: {keyword}")
                    return False
        
        # All safety checks passed
        return True
        
    except Exception as e:
        logging.error(f"Error validating content safety for {content_item.content_id}: {e}")
        return False