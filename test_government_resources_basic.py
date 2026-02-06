#!/usr/bin/env python3
"""
Basic test for GovernmentResourcesModule to verify core functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.government_resources_module import GovernmentResourcesModule
from core.content_manager import ContentManager
from core.session_manager import SessionManager


def test_basic_functionality():
    """Test basic GovernmentResourcesModule functionality."""
    print("Testing GovernmentResourcesModule basic functionality...")
    
    # Initialize module
    content_manager = ContentManager(s3_bucket_name="test-bucket", use_mock=True)
    session_manager = SessionManager()
    gov_module = GovernmentResourcesModule(content_manager, session_manager)
    
    # Test 1: Module initialization
    assert gov_module.module_name == "government_resources"
    assert len(gov_module.get_module_topics("en")) == 10
    print("✓ Module initialization test passed")
    
    # Test 2: Get schemes overview
    overview = gov_module.get_content_by_topic("government_schemes_overview", "en")
    assert len(overview["content"]) > 0
    assert overview["language_used"] == "en"
    print("✓ Schemes overview test passed")
    
    # Test 3: JSY eligibility checking
    eligible_profile = {
        "age": 25,
        "is_pregnant": True,
        "pregnancy_months": 6,
        "is_bpl": True,
        "children_count": 0,
        "state": "uttar_pradesh"
    }
    
    jsy_eligibility = gov_module.check_scheme_eligibility(
        gov_module.SCHEME_JSY, 
        eligible_profile
    )
    assert jsy_eligibility["eligible"] == True
    print("✓ JSY eligibility test passed")
    
    # Test 4: JSSK eligibility (should always be eligible)
    jssk_eligibility = gov_module.check_scheme_eligibility(
        gov_module.SCHEME_JSSK,
        {"age": 30, "is_pregnant": False}
    )
    assert jssk_eligibility["eligible"] == True
    print("✓ JSSK eligibility test passed")
    
    # Test 5: Regional information
    regional_info = gov_module.get_regional_information(
        gov_module.SCHEME_JSY, 
        "Uttar Pradesh"
    )
    assert regional_info["has_variations"] == True
    print("✓ Regional information test passed")
    
    # Test 6: Application guidance
    app_guidance = gov_module.get_application_guidance(gov_module.SCHEME_JSY)
    assert len(app_guidance["steps"]) > 0
    assert len(app_guidance["required_documents"]) > 0
    print("✓ Application guidance test passed")
    
    # Test 7: User query handling
    response = gov_module.handle_user_query("Tell me about JSY scheme", "en")
    assert "JSY" in response["response"] or "Janani Suraksha" in response["response"]
    assert response["emergency_detected"] == False
    print("✓ User query handling test passed")
    
    # Test 8: Content safety validation
    safe_content = "Government health schemes provide financial assistance."
    safety_result = gov_module.validate_content_safety(safe_content)
    assert safety_result["is_safe"] == True
    print("✓ Content safety validation test passed")
    
    print("\n✅ All basic functionality tests passed!")
    print("GovernmentResourcesModule is working correctly.")


if __name__ == "__main__":
    test_basic_functionality()