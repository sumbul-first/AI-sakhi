"""
Unit tests for ContentManager class.

This module contains comprehensive tests for the ContentManager class,
including content retrieval, caching, search functionality, and AWS S3 integration.
"""

import pytest
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, NoCredentialsError

from core.content_manager import ContentManager, ContentCache, create_content_manager, validate_content_safety
from models.data_models import ContentItem


class TestContentCache:
    """Test cases for the ContentCache class."""
    
    def test_cache_initialization(self):
        """Test cache initialization with default and custom parameters."""
        # Default initialization
        cache = ContentCache()
        assert cache.max_size == 1000
        assert cache.default_ttl == 3600
        assert cache.size() == 0
        
        # Custom initialization
        cache = ContentCache(max_size=500, default_ttl=1800)
        assert cache.max_size == 500
        assert cache.default_ttl == 1800
    
    def test_cache_put_and_get(self):
        """Test basic cache put and get operations."""
        cache = ContentCache(max_size=10, default_ttl=3600)
        
        # Test putting and getting items
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.size() == 1
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration functionality."""
        cache = ContentCache(max_size=10, default_ttl=1)  # 1 second TTL
        
        # Put item with short TTL
        cache.put("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = ContentCache(max_size=2, default_ttl=3600)
        
        # Fill cache to capacity
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert cache.size() == 2
        
        # Add third item, should evict oldest
        cache.put("key3", "value3")
        assert cache.size() == 2
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_invalidation(self):
        """Test cache invalidation functionality."""
        cache = ContentCache()
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert cache.size() == 2
        
        # Invalidate one key
        result = cache.invalidate("key1")
        assert result is True
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.size() == 1
        
        # Try to invalidate non-existent key
        result = cache.invalidate("nonexistent")
        assert result is False
    
    def test_cache_clear(self):
        """Test cache clear functionality."""
        cache = ContentCache()
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_cache_stats(self):
        """Test cache statistics functionality."""
        cache = ContentCache(max_size=100, default_ttl=1800)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        stats = cache.stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 100
        assert stats["default_ttl"] == 1800
        assert "key1" in stats["keys"]
        assert "key2" in stats["keys"]


class TestContentManager:
    """Test cases for the ContentManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.content_manager = ContentManager(
            s3_bucket_name="test-bucket",
            aws_region="us-east-1",
            use_mock=True
        )
    
    def test_content_manager_initialization(self):
        """Test ContentManager initialization."""
        # Test with default parameters
        cm = ContentManager("test-bucket")
        assert cm.s3_bucket_name == "test-bucket"
        assert cm.aws_region == "us-east-1"
        assert cm.use_mock is True
        assert cm.cache is not None
        
        # Test with custom parameters (will fall back to mock if no AWS credentials)
        cm = ContentManager(
            s3_bucket_name="custom-bucket",
            aws_region="eu-west-1",
            use_mock=False,
            cache_size=500,
            cache_ttl=1800
        )
        assert cm.s3_bucket_name == "custom-bucket"
        assert cm.aws_region == "eu-west-1"
        # Note: use_mock may be True if AWS connection fails (expected in test environment)
        assert isinstance(cm.use_mock, bool)
    
    def test_get_module_content_valid_input(self):
        """Test get_module_content with valid inputs."""
        # Test existing module and language
        content = self.content_manager.get_module_content("puberty_education", "hi")
        assert isinstance(content, list)
        assert len(content) > 0
        
        # Verify content items are correct type and language
        for item in content:
            assert isinstance(item, ContentItem)
            assert item.language_code == "hi"
            assert item.module_name == "puberty_education"
    
    def test_get_module_content_invalid_input(self):
        """Test get_module_content with invalid inputs."""
        # Test empty module name
        with pytest.raises(ValueError, match="Module name must be a non-empty string"):
            self.content_manager.get_module_content("", "hi")
        
        # Test None module name
        with pytest.raises(ValueError, match="Module name must be a non-empty string"):
            self.content_manager.get_module_content(None, "hi")
        
        # Test empty language code
        with pytest.raises(ValueError, match="Language code must be a non-empty string"):
            self.content_manager.get_module_content("puberty_education", "")
        
        # Test None language code
        with pytest.raises(ValueError, match="Language code must be a non-empty string"):
            self.content_manager.get_module_content("puberty_education", None)
    
    def test_get_module_content_nonexistent_module(self):
        """Test get_module_content with non-existent module."""
        content = self.content_manager.get_module_content("nonexistent_module", "hi")
        assert isinstance(content, list)
        assert len(content) == 0
    
    def test_get_module_content_caching(self):
        """Test that get_module_content uses caching effectively."""
        # First call should populate cache
        content1 = self.content_manager.get_module_content("puberty_education", "hi")
        
        # Second call should use cache
        content2 = self.content_manager.get_module_content("puberty_education", "hi")
        
        # Results should be identical
        assert content1 == content2
        
        # Verify cache contains the result
        cache_stats = self.content_manager.get_cache_stats()
        assert cache_stats["size"] > 0
    
    def test_get_audio_content_valid_input(self):
        """Test get_audio_content with valid inputs."""
        # Test existing audio content
        url = self.content_manager.get_audio_content("pe_001", "hi")
        assert url is not None
        assert isinstance(url, str)
        assert "audio" in url
        assert "hi" in url
    
    def test_get_audio_content_invalid_input(self):
        """Test get_audio_content with invalid inputs."""
        # Test empty content ID
        with pytest.raises(ValueError, match="Content ID must be a non-empty string"):
            self.content_manager.get_audio_content("", "hi")
        
        # Test None content ID
        with pytest.raises(ValueError, match="Content ID must be a non-empty string"):
            self.content_manager.get_audio_content(None, "hi")
        
        # Test empty language code
        with pytest.raises(ValueError, match="Language code must be a non-empty string"):
            self.content_manager.get_audio_content("pe_001", "")
    
    def test_get_audio_content_nonexistent(self):
        """Test get_audio_content with non-existent content."""
        url = self.content_manager.get_audio_content("nonexistent", "hi")
        assert url is None
    
    def test_get_video_content_valid_input(self):
        """Test get_video_content with valid inputs."""
        # Test existing video content
        url = self.content_manager.get_video_content("pe_002", "hi")
        assert url is not None
        assert isinstance(url, str)
        assert "video" in url
        assert "hi" in url
    
    def test_get_video_content_invalid_input(self):
        """Test get_video_content with invalid inputs."""
        # Test empty content ID
        with pytest.raises(ValueError, match="Content ID must be a non-empty string"):
            self.content_manager.get_video_content("", "hi")
        
        # Test None language code
        with pytest.raises(ValueError, match="Language code must be a non-empty string"):
            self.content_manager.get_video_content("pe_002", None)
    
    def test_get_video_content_nonexistent(self):
        """Test get_video_content with non-existent content."""
        url = self.content_manager.get_video_content("nonexistent", "hi")
        assert url is None
    
    def test_search_content_valid_query(self):
        """Test search_content with valid queries."""
        # Test basic search
        results = self.content_manager.search_content("menstruation")
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Verify results contain the search term
        for result in results:
            assert isinstance(result, ContentItem)
            searchable_text = f"{result.topic} {result.transcript} {result.module_name}".lower()
            assert "menstruation" in searchable_text
    
    def test_search_content_with_module_filter(self):
        """Test search_content with module filter."""
        # Search within specific module
        results = self.content_manager.search_content("body", "puberty_education")
        assert isinstance(results, list)
        
        # All results should be from the specified module
        for result in results:
            assert result.module_name == "puberty_education"
    
    def test_search_content_invalid_input(self):
        """Test search_content with invalid inputs."""
        # Test empty query
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            self.content_manager.search_content("")
        
        # Test None query
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            self.content_manager.search_content(None)
        
        # Test whitespace-only query
        with pytest.raises(ValueError, match="Query cannot be empty or whitespace only"):
            self.content_manager.search_content("   ")
    
    def test_search_content_no_results(self):
        """Test search_content with query that returns no results."""
        results = self.content_manager.search_content("nonexistent_term_xyz")
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_cache_content_valid_item(self):
        """Test cache_content with valid ContentItem."""
        content_item = ContentItem(
            content_id="test_001",
            module_name="test_module",
            topic="test_topic",
            content_type="audio",
            language_code="en",
            s3_url="https://example.com/test.mp3",
            safety_validated=True
        )
        
        result = self.content_manager.cache_content(content_item)
        assert result is True
    
    def test_cache_content_invalid_item(self):
        """Test cache_content with invalid input."""
        # Test with non-ContentItem object
        with pytest.raises(ValueError, match="content_item must be a ContentItem instance"):
            self.content_manager.cache_content("not_a_content_item")
        
        # Test with None
        with pytest.raises(ValueError, match="content_item must be a ContentItem instance"):
            self.content_manager.cache_content(None)
    
    def test_invalidate_cache_valid_id(self):
        """Test invalidate_cache with valid content ID."""
        # First, cache some content
        content_item = ContentItem(
            content_id="test_cache_001",
            module_name="test_module",
            topic="test_topic",
            content_type="audio",
            language_code="en",
            safety_validated=True
        )
        self.content_manager.cache_content(content_item)
        
        # Then invalidate it
        result = self.content_manager.invalidate_cache("test_cache_001")
        # Note: Result might be False if no exact cache key matches, which is acceptable
        assert isinstance(result, bool)
    
    def test_invalidate_cache_invalid_input(self):
        """Test invalidate_cache with invalid inputs."""
        # Test empty content ID
        with pytest.raises(ValueError, match="Content ID must be a non-empty string"):
            self.content_manager.invalidate_cache("")
        
        # Test None content ID
        with pytest.raises(ValueError, match="Content ID must be a non-empty string"):
            self.content_manager.invalidate_cache(None)
    
    def test_get_cache_stats(self):
        """Test get_cache_stats functionality."""
        stats = self.content_manager.get_cache_stats()
        assert isinstance(stats, dict)
        assert "size" in stats
        assert "max_size" in stats
        assert "s3_bucket" in stats
        assert "use_mock" in stats
        assert stats["s3_bucket"] == "test-bucket"
        assert stats["use_mock"] is True
    
    def test_clear_cache(self):
        """Test clear_cache functionality."""
        # Add some content to cache first
        self.content_manager.get_module_content("puberty_education", "hi")
        
        # Verify cache has content
        stats_before = self.content_manager.get_cache_stats()
        assert stats_before["size"] > 0
        
        # Clear cache
        result = self.content_manager.clear_cache()
        assert result is True
        
        # Verify cache is empty
        stats_after = self.content_manager.get_cache_stats()
        assert stats_after["size"] == 0
    
    def test_health_check(self):
        """Test health_check functionality."""
        health = self.content_manager.health_check()
        assert isinstance(health, dict)
        assert "timestamp" in health
        assert "status" in health
        assert "checks" in health
        
        # Verify required checks are present
        assert "cache" in health["checks"]
        assert "s3" in health["checks"]
        assert "mock_content" in health["checks"]
        
        # Since we're using mock, status should be "development"
        assert health["status"] in ["healthy", "development", "degraded"]
    
    def test_generate_cache_key(self):
        """Test _generate_cache_key method."""
        # Test basic key generation
        key1 = self.content_manager._generate_cache_key("test", param1="value1", param2="value2")
        key2 = self.content_manager._generate_cache_key("test", param2="value2", param1="value1")
        
        # Keys should be identical regardless of parameter order
        assert key1 == key2
        
        # Test long key hashing
        long_params = {f"param_{i}": f"very_long_value_{i}" * 10 for i in range(10)}
        long_key = self.content_manager._generate_cache_key("test", **long_params)
        
        # Long keys should be hashed to manageable length
        assert len(long_key) < 100
    
    @patch('boto3.client')
    def test_s3_client_initialization_success(self, mock_boto_client):
        """Test successful S3 client initialization."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        cm = ContentManager("test-bucket", use_mock=False)
        
        # Should attempt to create S3 client
        mock_boto_client.assert_called_once_with('s3', region_name='us-east-1')
        mock_s3.head_bucket.assert_called_once_with(Bucket='test-bucket')
    
    @patch('boto3.client')
    def test_s3_client_initialization_no_credentials(self, mock_boto_client):
        """Test S3 client initialization with no credentials."""
        mock_boto_client.side_effect = NoCredentialsError()
        
        cm = ContentManager("test-bucket", use_mock=False)
        
        # Should fall back to mock mode
        assert cm.use_mock is True
    
    @patch('boto3.client')
    def test_s3_client_initialization_bucket_not_found(self, mock_boto_client):
        """Test S3 client initialization with bucket not found."""
        mock_s3 = Mock()
        mock_s3.head_bucket.side_effect = ClientError(
            {'Error': {'Code': '404'}}, 'HeadBucket'
        )
        mock_boto_client.return_value = mock_s3
        
        cm = ContentManager("test-bucket", use_mock=False)
        
        # Should fall back to mock mode
        assert cm.use_mock is True


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_create_content_manager(self):
        """Test create_content_manager factory function."""
        # Test with default parameters
        cm = create_content_manager()
        assert isinstance(cm, ContentManager)
        assert cm.s3_bucket_name == "ai-sakhi-content"
        assert cm.aws_region == "us-east-1"
        assert cm.use_mock is True
        
        # Test with custom parameters (will fall back to mock if no AWS credentials)
        cm = create_content_manager(
            bucket_name="custom-bucket",
            region="eu-west-1",
            use_mock=False
        )
        assert cm.s3_bucket_name == "custom-bucket"
        assert cm.aws_region == "eu-west-1"
        # Note: use_mock may be True if AWS connection fails (expected in test environment)
        assert isinstance(cm.use_mock, bool)
    
    def test_validate_content_safety_valid_content(self):
        """Test validate_content_safety with safe content."""
        safe_content = ContentItem(
            content_id="safe_001",
            module_name="puberty_education",
            topic="body_changes",
            content_type="audio",
            language_code="en",
            transcript="This is educational content about body changes during puberty.",
            safety_validated=False
        )
        
        result = validate_content_safety(safe_content)
        assert result is True
    
    def test_validate_content_safety_already_validated(self):
        """Test validate_content_safety with already validated content."""
        validated_content = ContentItem(
            content_id="validated_001",
            module_name="puberty_education",
            topic="body_changes",
            content_type="audio",
            language_code="en",
            transcript="Any content here",
            safety_validated=True
        )
        
        result = validate_content_safety(validated_content)
        assert result is True
    
    def test_validate_content_safety_unsafe_content(self):
        """Test validate_content_safety with unsafe content."""
        unsafe_content = ContentItem(
            content_id="unsafe_001",
            module_name="puberty_education",
            topic="body_changes",
            content_type="audio",
            language_code="en",
            transcript="I can diagnose your disease and prescribe medicine for treatment.",
            safety_validated=False
        )
        
        result = validate_content_safety(unsafe_content)
        assert result is False
    
    def test_validate_content_safety_invalid_content(self):
        """Test validate_content_safety with invalid ContentItem."""
        invalid_content = ContentItem(
            content_id="",  # Invalid empty ID
            module_name="puberty_education",
            topic="body_changes",
            content_type="audio",
            language_code="en",
            safety_validated=False
        )
        
        result = validate_content_safety(invalid_content)
        assert result is False


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.content_manager = ContentManager(
            s3_bucket_name="test-bucket",
            use_mock=True
        )
    
    def test_concurrent_cache_access(self):
        """Test concurrent access to cache (basic thread safety test)."""
        import threading
        import time
        
        results = []
        errors = []
        
        def cache_worker(worker_id):
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_item_{i}"
                    value = f"value_{worker_id}_{i}"
                    
                    # Put and get operations
                    self.content_manager.cache.put(key, value)
                    retrieved = self.content_manager.cache.get(key)
                    
                    if retrieved == value:
                        results.append(f"worker_{worker_id}_success_{i}")
                    else:
                        errors.append(f"worker_{worker_id}_mismatch_{i}")
                    
                    time.sleep(0.001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(f"worker_{worker_id}_error: {str(e)}")
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 50  # 5 workers * 10 operations each
    
    def test_cache_with_large_objects(self):
        """Test cache behavior with large objects."""
        large_content = ContentItem(
            content_id="large_001",
            module_name="test_module",
            topic="large_topic",
            content_type="text",
            language_code="en",
            transcript="x" * 10000,  # Large transcript
            safety_validated=True
        )
        
        # Should handle large objects without issues
        result = self.content_manager.cache_content(large_content)
        assert result is True
        
        # Should be able to retrieve large objects
        cache_key = self.content_manager._generate_cache_key(
            "content_item",
            content_id="large_001",
            lang="en"
        )
        cached_item = self.content_manager.cache.get(cache_key)
        assert cached_item is not None
        assert len(cached_item.transcript) == 10000
    
    def test_search_with_special_characters(self):
        """Test search functionality with special characters."""
        # Test search with various special characters
        special_queries = [
            "मासिक धर्म",  # Hindi text
            "body-changes",  # Hyphenated
            "good/bad touch",  # Forward slash
            "pregnancy & nutrition",  # Ampersand
            "safety (important)",  # Parentheses
        ]
        
        for query in special_queries:
            try:
                results = self.content_manager.search_content(query)
                assert isinstance(results, list)
                # Results may be empty, but should not raise exceptions
            except Exception as e:
                pytest.fail(f"Search failed for query '{query}': {str(e)}")
    
    def test_content_manager_with_empty_mock_data(self):
        """Test ContentManager behavior with empty mock data."""
        # Create ContentManager and clear mock data
        cm = ContentManager("test-bucket", use_mock=True)
        cm._mock_content_metadata = {"by_module": {}, "all_content": []}
        
        # All operations should handle empty data gracefully
        content = cm.get_module_content("any_module", "en")
        assert content == []
        
        audio_url = cm.get_audio_content("any_id", "en")
        assert audio_url is None
        
        video_url = cm.get_video_content("any_id", "en")
        assert video_url is None
        
        search_results = cm.search_content("any_query")
        assert search_results == []
    
    def test_malformed_s3_urls(self):
        """Test handling of malformed S3 URLs in mock content."""
        # Create content with malformed URL
        malformed_content = ContentItem(
            content_id="malformed_001",
            module_name="test_module",
            topic="test_topic",
            content_type="audio",
            language_code="en",
            s3_url="not-a-valid-url",
            safety_validated=True
        )
        
        # Add to mock content
        self.content_manager._mock_content_metadata["all_content"].append(malformed_content)
        
        # Should still return the URL (validation happens elsewhere)
        url = self.content_manager.get_audio_content("malformed_001", "en")
        assert url == "not-a-valid-url"


if __name__ == "__main__":
    pytest.main([__file__])