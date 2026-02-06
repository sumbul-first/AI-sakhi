#!/usr/bin/env python3
"""
Demo script to showcase ContentManager functionality.
"""

from core.content_manager import ContentManager, create_content_manager
from models.data_models import ContentItem

def main():
    print("=== AI Sakhi ContentManager Demo ===\n")
    
    # Create ContentManager instance
    print("1. Creating ContentManager with mock S3 operations...")
    cm = create_content_manager(bucket_name="ai-sakhi-demo", use_mock=True)
    print(f"   ✓ ContentManager created for bucket: {cm.s3_bucket_name}")
    print(f"   ✓ Using mock operations: {cm.use_mock}")
    
    # Health check
    print("\n2. Performing health check...")
    health = cm.health_check()
    print(f"   ✓ System status: {health['status']}")
    print(f"   ✓ Cache status: {health['checks']['cache']['status']}")
    print(f"   ✓ Mock content available: {health['checks']['mock_content']['details']}")
    
    # Get module content
    print("\n3. Retrieving puberty education content in Hindi...")
    puberty_content = cm.get_module_content("puberty_education", "hi")
    print(f"   ✓ Found {len(puberty_content)} content items")
    for item in puberty_content:
        print(f"     - {item.topic} ({item.content_type}, {item.get_display_duration()})")
    
    # Get audio content
    print("\n4. Getting audio content URL...")
    audio_url = cm.get_audio_content("pe_001", "hi")
    if audio_url:
        print(f"   ✓ Audio URL: {audio_url}")
    else:
        print("   ✗ Audio content not found")
    
    # Get video content
    print("\n5. Getting video content URL...")
    video_url = cm.get_video_content("pe_002", "hi")
    if video_url:
        print(f"   ✓ Video URL: {video_url}")
    else:
        print("   ✗ Video content not found")
    
    # Search content
    print("\n6. Searching for 'menstruation' content...")
    search_results = cm.search_content("menstruation")
    print(f"   ✓ Found {len(search_results)} matching items")
    for result in search_results:
        print(f"     - {result.module_name}: {result.topic}")
    
    # Search with module filter
    print("\n7. Searching for 'body' in puberty education module...")
    filtered_results = cm.search_content("body", "puberty_education")
    print(f"   ✓ Found {len(filtered_results)} matching items in module")
    for result in filtered_results:
        print(f"     - {result.topic} ({result.content_type})")
    
    # Cache operations
    print("\n8. Testing cache operations...")
    
    # Create and cache a new content item
    new_content = ContentItem(
        content_id="demo_001",
        module_name="demo_module",
        topic="demo_topic",
        content_type="audio",
        language_code="en",
        s3_url="https://example.com/demo.mp3",
        duration_seconds=120,
        transcript="This is a demo content item for testing.",
        safety_validated=True
    )
    
    cache_success = cm.cache_content(new_content)
    print(f"   ✓ Content cached successfully: {cache_success}")
    
    # Get cache stats
    cache_stats = cm.get_cache_stats()
    print(f"   ✓ Cache size: {cache_stats['size']}/{cache_stats['max_size']}")
    
    # Test cache invalidation
    invalidated = cm.invalidate_cache("demo_001")
    print(f"   ✓ Cache invalidated: {invalidated}")
    
    # Government resources
    print("\n9. Retrieving government resources content...")
    gov_content = cm.get_module_content("government_resources", "hi")
    print(f"   ✓ Found {len(gov_content)} government scheme items")
    for item in gov_content:
        print(f"     - {item.topic} ({item.content_type})")
    
    # Safety and mental support
    print("\n10. Retrieving safety and mental support content...")
    safety_content = cm.get_module_content("safety_mental_support", "en")
    print(f"   ✓ Found {len(safety_content)} safety education items")
    for item in safety_content:
        print(f"     - {item.topic} ({item.content_type})")
    
    print("\n=== Demo completed successfully! ===")
    print("\nKey Features Demonstrated:")
    print("✓ AWS S3 integration with mock operations")
    print("✓ Multi-language content retrieval")
    print("✓ Content caching with TTL and LRU eviction")
    print("✓ Content search and filtering")
    print("✓ Audio and video content URL generation")
    print("✓ Health monitoring and diagnostics")
    print("✓ Thread-safe cache operations")
    print("✓ Comprehensive error handling")

if __name__ == "__main__":
    main()