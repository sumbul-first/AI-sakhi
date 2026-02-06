"""
BaseHealthModule - Abstract base class for all health education modules.

This module provides the common interface and functionality for all health education
modules in the AI Sakhi Voice-First Health Companion application. It implements
content safety validation methods and emergency resource access as required by
Requirements 10.1 and 10.4.

Key Features:
- Common interface for content retrieval across all modules
- Content safety validation to ensure educational vs medical boundaries
- Emergency resource access methods for crisis situations
- Integration with ContentManager and SessionManager
- Multi-language support with fallback mechanisms
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone

from models.data_models import ContentItem, EmergencyContact, UserSession
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class BaseHealthModule(ABC):
    """
    Abstract base class for all health education modules.
    
    This class defines the common interface and provides shared functionality
    for all health education modules including puberty education, safety & mental
    support, menstrual guide, pregnancy guidance, and government resources.
    
    All concrete modules must implement the abstract methods while inheriting
    the common functionality for content safety validation and emergency routing.
    """
    
    # Medical diagnosis keywords that should trigger safety warnings
    MEDICAL_DIAGNOSIS_KEYWORDS = [
        "diagnose", "diagnosis", "disease", "cure", "treatment", "medicine",
        "drug", "prescription", "medication", "therapy", "surgery", "operation",
        "infection", "bacteria", "virus", "cancer", "tumor", "disorder",
        "syndrome", "condition", "illness", "sickness", "pathology"
    ]
    
    # Emergency keywords that should trigger immediate help routing
    EMERGENCY_KEYWORDS = [
        "emergency", "urgent", "help", "danger", "crisis", "abuse", "violence",
        "bleeding", "pain", "hurt", "scared", "afraid", "threatened", "unsafe",
        "suicide", "death", "dying", "hospital", "ambulance", "police"
    ]
    
    def __init__(self, module_name: str, content_manager: ContentManager, 
                 session_manager: SessionManager):
        """
        Initialize the base health module.
        
        Args:
            module_name: Name of the specific health module
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
            
        Raises:
            ValueError: If required parameters are invalid
        """
        if not module_name or not isinstance(module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        if not isinstance(content_manager, ContentManager):
            raise ValueError("content_manager must be a ContentManager instance")
        
        if not isinstance(session_manager, SessionManager):
            raise ValueError("session_manager must be a SessionManager instance")
        
        self.module_name = module_name
        self.content_manager = content_manager
        self.session_manager = session_manager
        
        # Set up logging
        self.logger = logging.getLogger(f"{__name__}.{module_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Emergency contacts cache
        self._emergency_contacts_cache = {}
        
        self.logger.info(f"Initialized {module_name} health module")
    
    @abstractmethod
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content for a specific topic within this module.
        
        Args:
            topic: Specific topic to retrieve content for
            language_code: Language code for content localization
            session_id: Optional session ID for personalization
            
        Returns:
            Dictionary containing:
            - content: List of ContentItem objects
            - safety_validated: Boolean indicating content safety
            - emergency_detected: Boolean indicating if emergency keywords found
            - language_used: Actual language code used (may differ due to fallback)
            - recommendations: List of next steps or related topics
        """
        pass
    
    @abstractmethod
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to a user query within this module's domain.
        
        Args:
            query: User's question or request
            language_code: Language code for response
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing:
            - response: Text response to the user
            - content_items: List of relevant ContentItem objects
            - emergency_detected: Boolean indicating emergency situation
            - safety_warnings: List of safety-related warnings
            - next_actions: Suggested next steps for the user
        """
        pass
    
    @abstractmethod
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available topics for this module.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        pass
    
    def validate_content_safety(self, content: Union[str, ContentItem, List[ContentItem]]) -> Dict[str, Any]:
        """
        Validate content for safety boundaries as required by Requirement 10.1.
        
        This method ensures that educational content does not cross into medical
        diagnosis territory and identifies potential emergency situations.
        
        Args:
            content: Content to validate (string, ContentItem, or list of ContentItems)
            
        Returns:
            Dictionary containing:
            - is_safe: Boolean indicating if content is safe for educational use
            - medical_flags: List of detected medical diagnosis keywords
            - emergency_flags: List of detected emergency keywords
            - recommendations: List of safety recommendations
            - requires_medical_referral: Boolean indicating need for medical professional
        """
        try:
            validation_result = {
                "is_safe": True,
                "medical_flags": [],
                "emergency_flags": [],
                "recommendations": [],
                "requires_medical_referral": False
            }
            
            # Extract text content for analysis
            text_content = []
            
            if isinstance(content, str):
                text_content.append(content.lower())
            elif isinstance(content, ContentItem):
                if content.transcript:
                    text_content.append(content.transcript.lower())
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, ContentItem) and item.transcript:
                        text_content.append(item.transcript.lower())
            
            # Analyze each piece of text content
            for text in text_content:
                # Check for medical diagnosis keywords
                for keyword in self.MEDICAL_DIAGNOSIS_KEYWORDS:
                    if keyword in text:
                        validation_result["medical_flags"].append(keyword)
                        validation_result["requires_medical_referral"] = True
                
                # Check for emergency keywords
                for keyword in self.EMERGENCY_KEYWORDS:
                    if keyword in text:
                        validation_result["emergency_flags"].append(keyword)
            
            # Determine safety status
            if validation_result["medical_flags"]:
                validation_result["is_safe"] = False
                validation_result["recommendations"].append(
                    "Content contains medical terminology. Recommend consulting healthcare professional."
                )
            
            if validation_result["emergency_flags"]:
                validation_result["recommendations"].append(
                    "Emergency keywords detected. Immediate human assistance may be needed."
                )
            
            # Add general safety recommendations
            if not validation_result["medical_flags"] and not validation_result["emergency_flags"]:
                validation_result["recommendations"].append(
                    "Content appears safe for educational purposes."
                )
            
            self.logger.debug(f"Content safety validation completed: {validation_result}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating content safety: {e}")
            return {
                "is_safe": False,
                "medical_flags": [],
                "emergency_flags": [],
                "recommendations": ["Error occurred during safety validation"],
                "requires_medical_referral": True
            }
    
    def get_emergency_resources(self, language_code: str = "en", 
                              region: str = "national") -> List[EmergencyContact]:
        """
        Get emergency contact resources as required by Requirement 10.4.
        
        This method provides immediate access to emergency contacts and human
        help services when emergency situations are detected.
        
        Args:
            language_code: Language code for contact information
            region: Geographic region for localized contacts
            
        Returns:
            List of EmergencyContact objects with relevant help resources
        """
        try:
            # Check cache first
            cache_key = f"{language_code}_{region}"
            if cache_key in self._emergency_contacts_cache:
                self.logger.debug(f"Emergency contacts cache hit for {cache_key}")
                return self._emergency_contacts_cache[cache_key]
            
            # Create emergency contacts (in real implementation, this would come from database)
            emergency_contacts = []
            
            # National emergency contacts
            if region == "national" or region == "india":
                emergency_contacts.extend([
                    EmergencyContact(
                        contact_type="helpline",
                        phone_number="112",
                        region="India",
                        language_support=["hi", "en", "bn", "ta", "te", "mr"],
                        availability_hours="24/7",
                        description="National Emergency Helpline - Police, Fire, Medical"
                    ),
                    EmergencyContact(
                        contact_type="medical",
                        phone_number="108",
                        region="India",
                        language_support=["hi", "en", "bn", "ta", "te", "mr"],
                        availability_hours="24/7",
                        description="Emergency Medical Services - Ambulance"
                    ),
                    EmergencyContact(
                        contact_type="counseling",
                        phone_number="9152987821",
                        region="India",
                        language_support=["hi", "en"],
                        availability_hours="24/7",
                        description="AASRA - Suicide Prevention Helpline"
                    )
                ])
            
            # Women-specific emergency contacts
            emergency_contacts.extend([
                EmergencyContact(
                    contact_type="helpline",
                    phone_number="1091",
                    region="India",
                    language_support=["hi", "en", "bn", "ta", "te", "mr"],
                    availability_hours="24/7",
                    description="Women Helpline - Domestic Violence, Harassment"
                ),
                EmergencyContact(
                    contact_type="counseling",
                    phone_number="011-26853846",
                    region="Delhi",
                    language_support=["hi", "en", "ur"],
                    availability_hours="9:00 AM - 6:00 PM",
                    description="National Commission for Women"
                ),
                EmergencyContact(
                    contact_type="medical",
                    phone_number="104",
                    region="India",
                    language_support=["hi", "en", "bn", "ta", "te", "mr"],
                    availability_hours="24/7",
                    description="National Health Helpline - Medical Consultation"
                )
            ])
            
            # Filter by language support
            filtered_contacts = [
                contact for contact in emergency_contacts
                if language_code in contact.language_support
            ]
            
            # Cache the results
            self._emergency_contacts_cache[cache_key] = filtered_contacts
            
            self.logger.info(f"Retrieved {len(filtered_contacts)} emergency contacts for {language_code}, {region}")
            return filtered_contacts
            
        except Exception as e:
            self.logger.error(f"Error retrieving emergency resources: {e}")
            # Return basic emergency contact as fallback
            return [
                EmergencyContact(
                    contact_type="helpline",
                    phone_number="112",
                    region="India",
                    language_support=["hi", "en"],
                    availability_hours="24/7",
                    description="National Emergency Helpline"
                )
            ]
    
    def detect_emergency_situation(self, user_input: str) -> Dict[str, Any]:
        """
        Detect if user input indicates an emergency situation.
        
        Args:
            user_input: User's text input to analyze
            
        Returns:
            Dictionary containing:
            - is_emergency: Boolean indicating emergency detection
            - emergency_type: Type of emergency detected
            - confidence: Confidence score (0.0 to 1.0)
            - recommended_contacts: List of relevant emergency contacts
            - immediate_actions: List of immediate steps to take
        """
        try:
            if not user_input or not isinstance(user_input, str):
                return {
                    "is_emergency": False,
                    "emergency_type": None,
                    "confidence": 0.0,
                    "recommended_contacts": [],
                    "immediate_actions": []
                }
            
            user_input_lower = user_input.lower()
            emergency_result = {
                "is_emergency": False,
                "emergency_type": None,
                "confidence": 0.0,
                "recommended_contacts": [],
                "immediate_actions": []
            }
            
            # Check for emergency keywords
            emergency_matches = []
            for keyword in self.EMERGENCY_KEYWORDS:
                if keyword in user_input_lower:
                    emergency_matches.append(keyword)
            
            if emergency_matches:
                emergency_result["is_emergency"] = True
                emergency_result["confidence"] = min(len(emergency_matches) * 0.3, 1.0)
                
                # Determine emergency type based on keywords
                if any(word in emergency_matches for word in ["abuse", "violence", "threatened", "unsafe"]):
                    emergency_result["emergency_type"] = "safety_threat"
                elif any(word in emergency_matches for word in ["bleeding", "pain", "hospital", "ambulance"]):
                    emergency_result["emergency_type"] = "medical_emergency"
                elif any(word in emergency_matches for word in ["suicide", "death", "dying"]):
                    emergency_result["emergency_type"] = "mental_health_crisis"
                else:
                    emergency_result["emergency_type"] = "general_emergency"
                
                # Get appropriate emergency contacts
                emergency_result["recommended_contacts"] = self.get_emergency_resources()
                
                # Add immediate actions
                emergency_result["immediate_actions"] = [
                    "If in immediate danger, call 112 (National Emergency)",
                    "Seek help from trusted adults or authorities",
                    "Contact appropriate helpline from the provided list"
                ]
                
                if emergency_result["emergency_type"] == "medical_emergency":
                    emergency_result["immediate_actions"].insert(0, "Call 108 for medical emergency")
                elif emergency_result["emergency_type"] == "mental_health_crisis":
                    emergency_result["immediate_actions"].insert(0, "Call suicide prevention helpline immediately")
            
            self.logger.info(f"Emergency detection completed: {emergency_result['is_emergency']}, type: {emergency_result['emergency_type']}")
            return emergency_result
            
        except Exception as e:
            self.logger.error(f"Error detecting emergency situation: {e}")
            return {
                "is_emergency": True,  # Err on the side of caution
                "emergency_type": "unknown",
                "confidence": 0.5,
                "recommended_contacts": self.get_emergency_resources(),
                "immediate_actions": ["Contact emergency services if needed"]
            }
    
    def get_content_with_safety_check(self, topic: str, language_code: str, 
                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content with integrated safety validation.
        
        This method combines content retrieval with safety validation to ensure
        all returned content meets educational boundaries.
        
        Args:
            topic: Topic to retrieve content for
            language_code: Language code for content
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing content and safety information
        """
        try:
            # Get content from the specific module implementation
            content_result = self.get_content_by_topic(topic, language_code, session_id)
            
            # Validate content safety
            if "content" in content_result and content_result["content"]:
                safety_result = self.validate_content_safety(content_result["content"])
                
                # Merge safety information into content result
                content_result.update({
                    "safety_validated": safety_result["is_safe"],
                    "medical_flags": safety_result["medical_flags"],
                    "emergency_flags": safety_result["emergency_flags"],
                    "safety_recommendations": safety_result["recommendations"],
                    "requires_medical_referral": safety_result["requires_medical_referral"]
                })
                
                # Add emergency contacts if emergency flags detected
                if safety_result["emergency_flags"]:
                    content_result["emergency_contacts"] = self.get_emergency_resources(language_code)
            
            return content_result
            
        except Exception as e:
            self.logger.error(f"Error retrieving content with safety check: {e}")
            return {
                "content": [],
                "safety_validated": False,
                "error": str(e),
                "emergency_contacts": self.get_emergency_resources(language_code)
            }
    
    def update_session_context(self, session_id: str, interaction_data: Dict[str, Any]) -> bool:
        """
        Update session with module-specific interaction data.
        
        Args:
            session_id: Session ID to update
            interaction_data: Data about the user interaction
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Update session with current module and interaction
            update_data = {
                "current_module": self.module_name,
                "last_interaction": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "module": self.module_name,
                    "data": interaction_data
                }
            }
            
            success = self.session_manager.update_session(session_id, **update_data)
            
            if success:
                # Add interaction to history
                session = self.session_manager.get_session(session_id)
                if session:
                    session.add_interaction(
                        interaction_type=f"{self.module_name}_interaction",
                        content=str(interaction_data.get("query", "")),
                        response=str(interaction_data.get("response", ""))
                    )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating session context: {e}")
            return False
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get information about this health module.
        
        Returns:
            Dictionary containing module metadata and capabilities
        """
        return {
            "module_name": self.module_name,
            "description": f"Health education module: {self.module_name}",
            "capabilities": [
                "Content retrieval by topic",
                "User query handling",
                "Content safety validation",
                "Emergency situation detection",
                "Multi-language support"
            ],
            "supported_languages": self.content_manager.get_supported_languages(),
            "emergency_support": True,
            "safety_validation": True,
            "session_integration": True
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for this module.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            health_status = {
                "module_name": self.module_name,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": {}
            }
            
            # Check content manager integration
            try:
                content_health = self.content_manager.health_check()
                health_status["checks"]["content_manager"] = {
                    "status": content_health.get("status", "unknown"),
                    "details": "Content manager integration"
                }
            except Exception as e:
                health_status["checks"]["content_manager"] = {
                    "status": "unhealthy",
                    "details": f"Content manager error: {str(e)}"
                }
            
            # Check session manager integration
            try:
                session_count = self.session_manager.get_session_count()
                health_status["checks"]["session_manager"] = {
                    "status": "healthy",
                    "details": f"Session manager active with {session_count} sessions"
                }
            except Exception as e:
                health_status["checks"]["session_manager"] = {
                    "status": "unhealthy",
                    "details": f"Session manager error: {str(e)}"
                }
            
            # Check emergency resources
            try:
                emergency_contacts = self.get_emergency_resources()
                health_status["checks"]["emergency_resources"] = {
                    "status": "healthy" if emergency_contacts else "degraded",
                    "details": f"{len(emergency_contacts)} emergency contacts available"
                }
            except Exception as e:
                health_status["checks"]["emergency_resources"] = {
                    "status": "unhealthy",
                    "details": f"Emergency resources error: {str(e)}"
                }
            
            # Determine overall status
            unhealthy_checks = [
                check for check in health_status["checks"].values()
                if check["status"] == "unhealthy"
            ]
            
            if unhealthy_checks:
                health_status["status"] = "unhealthy"
            elif any(check["status"] == "degraded" for check in health_status["checks"].values()):
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "module_name": self.module_name,
                "status": "unhealthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }


# Utility functions for health module operations

def validate_module_requirements(content_manager: ContentManager, 
                               session_manager: SessionManager) -> bool:
    """
    Validate that required dependencies are properly configured.
    
    Args:
        content_manager: ContentManager instance to validate
        session_manager: SessionManager instance to validate
        
    Returns:
        True if all requirements are met
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(content_manager, ContentManager):
        raise ValueError("content_manager must be a ContentManager instance")
    
    if not isinstance(session_manager, SessionManager):
        raise ValueError("session_manager must be a SessionManager instance")
    
    # Test content manager functionality
    try:
        supported_languages = content_manager.get_supported_languages()
        if not supported_languages:
            raise ValueError("ContentManager has no supported languages")
    except Exception as e:
        raise ValueError(f"ContentManager validation failed: {e}")
    
    # Test session manager functionality
    try:
        session_count = session_manager.get_session_count()
        if session_count < 0:
            raise ValueError("SessionManager returned invalid session count")
    except Exception as e:
        raise ValueError(f"SessionManager validation failed: {e}")
    
    return True


def create_emergency_response(emergency_type: str, language_code: str = "en") -> Dict[str, Any]:
    """
    Create a standardized emergency response structure.
    
    Args:
        emergency_type: Type of emergency detected
        language_code: Language for response messages
        
    Returns:
        Dictionary containing emergency response information
    """
    emergency_messages = {
        "en": {
            "safety_threat": "If you are in immediate danger, please call 112 or contact local authorities.",
            "medical_emergency": "For medical emergencies, call 108 immediately or go to the nearest hospital.",
            "mental_health_crisis": "Please reach out for help. Call a suicide prevention helpline or trusted person.",
            "general_emergency": "If you need immediate help, call 112 or contact appropriate emergency services."
        },
        "hi": {
            "safety_threat": "यदि आप तत्काल खतरे में हैं, तो कृपया 112 पर कॉल करें या स्थानीय अधिकारियों से संपर्क करें।",
            "medical_emergency": "चिकित्सा आपातकाल के लिए, तुरंत 108 पर कॉल करें या निकटतम अस्पताल जाएं।",
            "mental_health_crisis": "कृपया मदद के लिए संपर्क करें। आत्महत्या रोकथाम हेल्पलाइन या विश्वसनीय व्यक्ति को कॉल करें।",
            "general_emergency": "यदि आपको तत्काल सहायता चाहिए, तो 112 पर कॉल करें या उपयुक्त आपातकालीन सेवाओं से संपर्क करें।"
        }
    }
    
    messages = emergency_messages.get(language_code, emergency_messages["en"])
    message = messages.get(emergency_type, messages["general_emergency"])
    
    return {
        "emergency_type": emergency_type,
        "language_code": language_code,
        "message": message,
        "immediate_action_required": True,
        "priority": "high"
    }