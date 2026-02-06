#!/usr/bin/env python3
"""
Demo script for BaseHealthModule functionality.

This script demonstrates the BaseHealthModule abstract class working with
real ContentManager and SessionManager instances, showing content safety
validation, emergency detection, and integration capabilities.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.base_health_module import BaseHealthModule, create_emergency_response
from core.content_manager import ContentManager
from core.session_manager import SessionManager
from models.data_models import ContentItem


class DemoHealthModule(BaseHealthModule):
    """Demo implementation of BaseHealthModule for testing."""
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: str = None) -> dict:
        """Demo implementation that uses real ContentManager."""
        try:
            # Get content from ContentManager
            content_items = self.content_manager.get_content_by_topic_and_language(
                self.module_name, topic, language_code
            )
            
            if not content_items:
                # Create demo content if none found
                content_items = [
                    ContentItem(
                        module_name=self.module_name,
                        topic=topic,
                        content_type="text",
                        language_code=language_code,
                        transcript=f"Educational information about {topic} in {language_code}",
                        safety_validated=True
                    )
                ]
            
            return {
                "content": content_items,
                "language_used": language_code,
                "emergency_detected": False,
                "recommendations": [f"Continue learning about {topic}"]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting content for topic {topic}: {e}")
            return {
                "content": [],
                "language_used": language_code,
                "emergency_detected": False,
                "recommendations": [],
                "error": str(e)
            }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: str = None) -> dict:
        """Demo implementation of query handling."""
        try:
            # Detect emergency situations
            emergency_result = self.detect_emergency_situation(query)
            
            # Generate response based on query
            if emergency_result["is_emergency"]:
                response = f"I understand this may be urgent. {emergency_result['immediate_actions'][0] if emergency_result['immediate_actions'] else 'Please seek appropriate help.'}"
            else:
                response = f"Thank you for your question about: {query}. Let me provide some educational information."
            
            return {
                "response": response,
                "content_items": [],
                "emergency_detected": emergency_result["is_emergency"],
                "safety_warnings": [],
                "next_actions": emergency_result.get("immediate_actions", ["Continue learning"])
            }
            
        except Exception as e:
            self.logger.error(f"Error handling query: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your query.",
                "content_items": [],
                "emergency_detected": False,
                "safety_warnings": [str(e)],
                "next_actions": ["Please try again"]
            }
    
    def get_module_topics(self, language_code: str) -> list:
        """Demo implementation of topic listing."""
        return [
            "basic_information",
            "safety_guidelines", 
            "health_education",
            "emergency_resources"
        ]


def main():
    """Main demo function."""
    print("=== BaseHealthModule Demo ===\n")
    
    try:
        # Initialize ContentManager and SessionManager
        print("1. Initializing ContentManager and SessionManager...")
        content_manager = ContentManager(
            s3_bucket_name="ai-sakhi-demo",
            use_mock=True
        )
        session_manager = SessionManager(timeout_minutes=30)
        
        # Create demo health module
        print("2. Creating demo health module...")
        demo_module = DemoHealthModule(
            module_name="demo_health_education",
            content_manager=content_manager,
            session_manager=session_manager
        )
        
        # Test module info
        print("3. Getting module information...")
        module_info = demo_module.get_module_info()
        print(f"   Module: {module_info['module_name']}")
        print(f"   Capabilities: {len(module_info['capabilities'])} features")
        print(f"   Languages: {module_info['supported_languages']}")
        
        # Test content safety validation
        print("\n4. Testing content safety validation...")
        
        # Safe content
        safe_content = "This is educational information about health and wellness"
        safety_result = demo_module.validate_content_safety(safe_content)
        print(f"   Safe content validation: {safety_result['is_safe']}")
        
        # Unsafe content (medical diagnosis)
        unsafe_content = "You have a disease that needs immediate treatment with medicine"
        safety_result = demo_module.validate_content_safety(unsafe_content)
        print(f"   Unsafe content validation: {safety_result['is_safe']}")
        print(f"   Medical flags: {safety_result['medical_flags']}")
        print(f"   Requires medical referral: {safety_result['requires_medical_referral']}")
        
        # Test emergency detection
        print("\n5. Testing emergency situation detection...")
        
        # Normal query
        normal_query = "I want to learn about health topics"
        emergency_result = demo_module.detect_emergency_situation(normal_query)
        print(f"   Normal query emergency detection: {emergency_result['is_emergency']}")
        
        # Emergency query
        emergency_query = "I am in danger and need help urgently"
        emergency_result = demo_module.detect_emergency_situation(emergency_query)
        print(f"   Emergency query detection: {emergency_result['is_emergency']}")
        print(f"   Emergency type: {emergency_result['emergency_type']}")
        print(f"   Confidence: {emergency_result['confidence']:.2f}")
        
        # Test emergency resources
        print("\n6. Testing emergency resources...")
        emergency_contacts = demo_module.get_emergency_resources(language_code="en")
        print(f"   Found {len(emergency_contacts)} emergency contacts")
        for contact in emergency_contacts[:2]:  # Show first 2
            print(f"   - {contact.contact_type}: {contact.phone_number} ({contact.description})")
        
        # Test content retrieval with safety check
        print("\n7. Testing content retrieval with safety validation...")
        content_result = demo_module.get_content_with_safety_check(
            topic="basic_information",
            language_code="en"
        )
        print(f"   Content items retrieved: {len(content_result.get('content', []))}")
        print(f"   Safety validated: {content_result.get('safety_validated', False)}")
        
        # Test user query handling
        print("\n8. Testing user query handling...")
        
        # Normal query
        query_result = demo_module.handle_user_query(
            query="Tell me about health education",
            language_code="en"
        )
        print(f"   Normal query response: {query_result['response'][:50]}...")
        print(f"   Emergency detected: {query_result['emergency_detected']}")
        
        # Emergency query
        emergency_query_result = demo_module.handle_user_query(
            query="This is an emergency, I need help",
            language_code="en"
        )
        print(f"   Emergency query response: {emergency_query_result['response'][:50]}...")
        print(f"   Emergency detected: {emergency_query_result['emergency_detected']}")
        
        # Test session integration
        print("\n9. Testing session integration...")
        session = session_manager.create_session(language_preference="en")
        print(f"   Created session: {session.session_id}")
        
        interaction_data = {
            "query": "test query",
            "response": "test response",
            "topic": "health_education"
        }
        
        update_success = demo_module.update_session_context(session.session_id, interaction_data)
        print(f"   Session update successful: {update_success}")
        
        # Test health check
        print("\n10. Testing module health check...")
        health_status = demo_module.health_check()
        print(f"    Overall status: {health_status['status']}")
        print(f"    Checks performed: {len(health_status['checks'])}")
        
        for check_name, check_result in health_status['checks'].items():
            print(f"    - {check_name}: {check_result['status']}")
        
        # Test utility functions
        print("\n11. Testing utility functions...")
        emergency_response = create_emergency_response("medical_emergency", "en")
        print(f"    Emergency response type: {emergency_response['emergency_type']}")
        print(f"    Message: {emergency_response['message'][:50]}...")
        
        print("\n=== Demo completed successfully! ===")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)