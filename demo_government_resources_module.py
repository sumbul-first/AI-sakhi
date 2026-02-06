#!/usr/bin/env python3
"""
Demo script for GovernmentResourcesModule.

This script demonstrates the functionality of the GovernmentResourcesModule
including scheme information retrieval, eligibility checking, regional variations,
and application guidance.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.government_resources_module import GovernmentResourcesModule
from core.content_manager import ContentManager
from core.session_manager import SessionManager


def demo_government_resources():
    """Demonstrate GovernmentResourcesModule functionality."""
    print("=== AI Sakhi Government Resources Module Demo ===\n")
    
    try:
        # Initialize dependencies
        print("1. Initializing ContentManager and SessionManager...")
        content_manager = ContentManager(s3_bucket_name="ai-sakhi-content", use_mock=True)
        session_manager = SessionManager()
        
        # Initialize GovernmentResourcesModule
        print("2. Initializing GovernmentResourcesModule...")
        gov_module = GovernmentResourcesModule(content_manager, session_manager)
        
        print(f"✓ Module initialized: {gov_module.module_name}")
        print(f"✓ Available topics: {len(gov_module.get_module_topics('en'))}")
        print()
        
        # Demo 1: Get module topics
        print("3. Available Topics:")
        topics = gov_module.get_module_topics("en")
        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic}")
        print()
        
        # Demo 2: Get schemes overview
        print("4. Government Schemes Overview:")
        overview_result = gov_module.get_content_by_topic("government_schemes_overview", "en")
        if overview_result["content"]:
            content = overview_result["content"][0]
            print(f"   Content Type: {content.content_type}")
            print(f"   Safety Validated: {overview_result['safety_validated']}")
            print(f"   Language Used: {overview_result['language_used']}")
            print(f"   Content Preview: {content.transcript[:200]}...")
        print()
        
        # Demo 3: Get specific scheme information (JSY)
        print("5. JSY (Janani Suraksha Yojana) Information:")
        jsy_result = gov_module.get_content_by_topic("jsy_information", "en")
        if jsy_result["content"]:
            content = jsy_result["content"][0]
            print(f"   Content Length: {len(content.transcript)} characters")
            print(f"   Safety Validated: {jsy_result['safety_validated']}")
            print(f"   Recommendations: {jsy_result['recommendations']}")
        print()
        
        # Demo 4: Handle user queries
        print("6. User Query Handling:")
        queries = [
            "Tell me about JSY scheme",
            "How do I apply for government health schemes?",
            "What are the eligibility criteria for PMSMA?",
            "Are there regional variations in schemes?"
        ]
        
        for query in queries:
            print(f"   Query: '{query}'")
            response = gov_module.handle_user_query(query, "en")
            print(f"   Response: {response['response'][:100]}...")
            print(f"   Emergency Detected: {response['emergency_detected']}")
            print(f"   Next Actions: {response['next_actions'][:2]}")
            print()
        
        # Demo 5: Eligibility checking
        print("7. Eligibility Checking:")
        
        # Test user profiles
        test_profiles = [
            {
                "name": "Pregnant woman, BPL, first child",
                "profile": {
                    "age": 25,
                    "is_pregnant": True,
                    "pregnancy_months": 6,
                    "is_bpl": True,
                    "children_count": 0,
                    "state": "uttar_pradesh"
                }
            },
            {
                "name": "Non-pregnant woman, general category",
                "profile": {
                    "age": 30,
                    "is_pregnant": False,
                    "is_bpl": False,
                    "children_count": 1,
                    "state": "maharashtra"
                }
            }
        ]
        
        for test_case in test_profiles:
            print(f"   Testing: {test_case['name']}")
            
            # Check JSY eligibility
            jsy_eligibility = gov_module.check_scheme_eligibility(
                gov_module.SCHEME_JSY, 
                test_case["profile"]
            )
            print(f"   JSY Eligible: {jsy_eligibility['eligible']}")
            print(f"   Reason: {jsy_eligibility['reason']}")
            
            # Check JSSK eligibility (should always be eligible)
            jssk_eligibility = gov_module.check_scheme_eligibility(
                gov_module.SCHEME_JSSK,
                test_case["profile"]
            )
            print(f"   JSSK Eligible: {jssk_eligibility['eligible']}")
            print()
        
        # Demo 6: Regional information
        print("8. Regional Variations:")
        regional_info = gov_module.get_regional_information(
            gov_module.SCHEME_JSY, 
            "Uttar Pradesh", 
            "en"
        )
        print(f"   Scheme: {regional_info['scheme_name']}")
        print(f"   State: {regional_info['state']}")
        print(f"   Has Variations: {regional_info['has_variations']}")
        if regional_info['has_variations']:
            print(f"   Additional Benefits: {len(regional_info.get('additional_benefits', []))}")
            print(f"   Special Conditions: {len(regional_info.get('special_conditions', []))}")
        print()
        
        # Demo 7: Application guidance
        print("9. Application Guidance:")
        app_guidance = gov_module.get_application_guidance(gov_module.SCHEME_JSY, "en")
        print(f"   Scheme: {app_guidance['scheme_name']}")
        print(f"   Steps: {len(app_guidance['steps'])}")
        print(f"   Required Documents: {len(app_guidance['required_documents'])}")
        print(f"   Timeline: {app_guidance['estimated_time']}")
        print(f"   Tips: {len(app_guidance['tips'])}")
        print()
        
        # Demo 8: Module health check
        print("10. Module Health Check:")
        health_status = gov_module.health_check()
        print(f"   Module Status: {health_status['status']}")
        print(f"   Checks Performed: {len(health_status['checks'])}")
        for check_name, check_result in health_status['checks'].items():
            print(f"   {check_name}: {check_result['status']}")
        print()
        
        # Demo 9: Content safety validation
        print("11. Content Safety Validation:")
        test_content = "This is educational content about government health schemes for women."
        safety_result = gov_module.validate_content_safety(test_content)
        print(f"   Content Safe: {safety_result['is_safe']}")
        print(f"   Medical Flags: {len(safety_result['medical_flags'])}")
        print(f"   Emergency Flags: {len(safety_result['emergency_flags'])}")
        print(f"   Recommendations: {safety_result['recommendations']}")
        print()
        
        # Demo 10: Emergency resources
        print("12. Emergency Resources:")
        emergency_contacts = gov_module.get_emergency_resources("en", "india")
        print(f"   Emergency Contacts Available: {len(emergency_contacts)}")
        for contact in emergency_contacts[:3]:  # Show first 3
            print(f"   - {contact.contact_type}: {contact.phone_number} ({contact.description[:50]}...)")
        print()
        
        print("✓ Government Resources Module demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("- Comprehensive information about 5 government health schemes")
        print("- Eligibility checking for different user profiles")
        print("- Regional variation handling for different states")
        print("- Application process guidance with step-by-step instructions")
        print("- Multi-language support framework")
        print("- Content safety validation and emergency detection")
        print("- Integration with BaseHealthModule features")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_government_resources()