"""
SafetyMentalSupportModule - Specialized health education module for safety awareness and mental support.

This module provides comprehensive safety education covering good/bad touch awareness,
emotional support, and emergency response as required by Requirements 2.1, 2.3, and 2.5.
It implements crisis intervention capabilities and professional referrals.

Key Features:
- Good/bad touch education with age-appropriate content
- Emergency detection and routing functionality
- Emotional support mechanisms and coping strategies
- Crisis intervention with professional referrals
- Distress response mechanisms
- Multi-language support with cultural sensitivity
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from modules.base_health_module import BaseHealthModule
from models.data_models import ContentItem, UserSession, EmergencyContact
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class SafetyMentalSupportModule(BaseHealthModule):
    """
    Specialized health education module for safety awareness and mental support.
    
    This module provides comprehensive education about personal safety, good/bad touch
    awareness, emotional support, and crisis intervention as required by Requirements
    2.1, 2.3, and 2.5.
    
    Topics covered:
    - Good touch vs bad touch awareness
    - Personal safety and boundary setting
    - Emotional support and coping strategies
    - Crisis intervention and professional referrals
    - Distress response mechanisms
    - Emergency detection and routing
    """
    
    # Available topics in the safety and mental support module
    AVAILABLE_TOPICS = [
        "good_bad_touch",
        "personal_safety",
        "emotional_support",
        "coping_strategies",
        "crisis_intervention",
        "boundary_setting",
        "distress_response",
        "professional_help"
    ]
    
    # Age-appropriate content mapping for safety education
    AGE_APPROPRIATE_CONTENT = {
        "young_adolescent": ["good_bad_touch", "personal_safety", "emotional_support", "boundary_setting"],
        "adolescent": ["good_bad_touch", "personal_safety", "emotional_support", "coping_strategies", "boundary_setting", "distress_response"],
        "young_adult": ["personal_safety", "emotional_support", "coping_strategies", "crisis_intervention", "boundary_setting", "distress_response", "professional_help"],
        "adult": ["personal_safety", "emotional_support", "coping_strategies", "crisis_intervention", "boundary_setting", "distress_response", "professional_help"]
    }
    
    # Crisis keywords that require immediate intervention
    CRISIS_KEYWORDS = [
        "abuse", "violence", "hurt", "scared", "threatened", "unsafe", "touch", "inappropriate",
        "harassment", "assault", "rape", "molest", "suicide", "self-harm", "depression",
        "anxiety", "panic", "trauma", "ptsd", "flashback", "nightmare", "fear", "terror"
    ]
    
    # Emotional distress indicators
    DISTRESS_INDICATORS = [
        "sad", "crying", "hopeless", "worthless", "alone", "isolated", "angry", "frustrated",
        "confused", "overwhelmed", "stressed", "worried", "anxious", "nervous", "panic",
        "depressed", "down", "low", "empty", "numb", "tired", "exhausted", "sleepless"
    ]
    
    # Professional help categories
    PROFESSIONAL_HELP_CATEGORIES = {
        "counseling": ["therapist", "counselor", "psychologist", "mental health professional"],
        "medical": ["doctor", "physician", "psychiatrist", "medical professional"],
        "legal": ["lawyer", "legal aid", "police", "law enforcement"],
        "social": ["social worker", "case worker", "support group", "community support"]
    }

    def __init__(self, content_manager: ContentManager, session_manager: SessionManager):
        """
        Initialize the SafetyMentalSupportModule.
        
        Args:
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
            
        Raises:
            ValueError: If required parameters are invalid
        """
        super().__init__(
            module_name="safety_mental_support",
            content_manager=content_manager,
            session_manager=session_manager
        )
        
        # Enhanced emergency keywords for safety module
        self.EMERGENCY_KEYWORDS.extend(self.CRISIS_KEYWORDS)
        
        self.logger.info("SafetyMentalSupportModule initialized successfully")
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content for a specific safety and mental support topic.
        
        This method implements topic-specific content retrieval with age-appropriate
        filtering and crisis detection as required by Requirements 2.1 and 2.3.
        
        Args:
            topic: Specific topic to retrieve content for
            language_code: Language code for content localization
            session_id: Optional session ID for personalization and age filtering
            
        Returns:
            Dictionary containing:
            - content: List of ContentItem objects
            - safety_validated: Boolean indicating content safety
            - emergency_detected: Boolean indicating if emergency keywords found
            - crisis_level: String indicating crisis severity (low/medium/high)
            - language_used: Actual language code used (may differ due to fallback)
            - recommendations: List of next steps or related topics
            - age_appropriate: Boolean indicating if content is age-appropriate
            - professional_referrals: List of professional help recommendations
        """
        try:
            # Validate topic
            if topic not in self.AVAILABLE_TOPICS:
                self.logger.warning(f"Invalid topic requested: {topic}")
                return {
                    "content": [],
                    "safety_validated": False,
                    "emergency_detected": False,
                    "crisis_level": "none",
                    "language_used": language_code,
                    "recommendations": [f"Available topics: {', '.join(self.AVAILABLE_TOPICS)}"],
                    "age_appropriate": False,
                    "professional_referrals": [],
                    "error": f"Topic '{topic}' not available in safety and mental support module"
                }
            
            # Get user session for age-appropriate filtering
            user_age_group = "adolescent"  # Default age group
            if session_id:
                session = self.session_manager.get_session(session_id)
                if session and session.accessibility_preferences:
                    user_age_group = session.accessibility_preferences.get("age_group", "adolescent")
            
            # Check if topic is age-appropriate
            age_appropriate_topics = self.AGE_APPROPRIATE_CONTENT.get(user_age_group, self.AVAILABLE_TOPICS)
            is_age_appropriate = topic in age_appropriate_topics
            
            if not is_age_appropriate:
                self.logger.info(f"Topic {topic} filtered for age group {user_age_group}")
                return {
                    "content": [],
                    "safety_validated": True,
                    "emergency_detected": False,
                    "crisis_level": "none",
                    "language_used": language_code,
                    "recommendations": [f"Age-appropriate topics: {', '.join(age_appropriate_topics)}"],
                    "age_appropriate": False,
                    "professional_referrals": [],
                    "message": "This content is not suitable for your age group. Please explore age-appropriate topics."
                }
            
            # Retrieve content from ContentManager with fallback
            content_result = self.content_manager.get_module_content_with_fallback(
                module_name=self.module_name,
                language_code=language_code,
                fallback_languages=["en", "hi"]
            )
            
            # Filter content by topic
            topic_content = [
                content for content in content_result["content"]
                if content.topic == topic
            ]
            
            # Validate content safety and detect crisis situations
            safety_result = self.validate_content_safety(topic_content)
            crisis_assessment = self._assess_crisis_level(topic, topic_content)
            
            # Generate professional referrals based on topic and crisis level
            professional_referrals = self._generate_professional_referrals(topic, crisis_assessment["level"], language_code)
            
            # Generate recommendations for related topics
            recommendations = self._generate_topic_recommendations(topic, user_age_group)
            
            # Update session context if session provided
            if session_id:
                self.update_session_context(session_id, {
                    "topic": topic,
                    "language": language_code,
                    "content_count": len(topic_content),
                    "age_group": user_age_group,
                    "crisis_level": crisis_assessment["level"]
                })
            
            result = {
                "content": topic_content,
                "safety_validated": safety_result["is_safe"],
                "emergency_detected": bool(safety_result["emergency_flags"]),
                "crisis_level": crisis_assessment["level"],
                "language_used": content_result["language_used"],
                "recommendations": recommendations,
                "age_appropriate": is_age_appropriate,
                "professional_referrals": professional_referrals,
                "fallback_used": content_result["fallback_used"],
                "available_languages": content_result["available_languages"],
                "crisis_indicators": crisis_assessment["indicators"]
            }
            
            # Add emergency contacts if emergency or crisis detected
            if safety_result["emergency_flags"] or crisis_assessment["level"] in ["medium", "high"]:
                result["emergency_contacts"] = self.get_emergency_resources(language_code)
            
            self.logger.info(f"Retrieved {len(topic_content)} content items for topic: {topic}, crisis level: {crisis_assessment['level']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error retrieving content for topic {topic}: {e}")
            return {
                "content": [],
                "safety_validated": False,
                "emergency_detected": True,  # Err on the side of caution
                "crisis_level": "unknown",
                "language_used": language_code,
                "recommendations": ["Please contact emergency services if you need immediate help"],
                "age_appropriate": False,
                "professional_referrals": self._generate_professional_referrals("crisis_intervention", "high", language_code),
                "emergency_contacts": self.get_emergency_resources(language_code),
                "error": str(e)
            }
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to a user query about safety and mental support.
        
        This method implements natural language query processing for safety-related
        questions with crisis detection and immediate routing as required by Requirements 2.3 and 2.5.
        
        Args:
            query: User's question or request
            language_code: Language code for response
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing:
            - response: Text response to the user
            - content_items: List of relevant ContentItem objects
            - emergency_detected: Boolean indicating emergency situation
            - crisis_level: String indicating crisis severity
            - safety_warnings: List of safety-related warnings
            - next_actions: Suggested next steps for the user
            - professional_referrals: List of professional help recommendations
            - immediate_help_needed: Boolean indicating need for immediate intervention
        """
        try:
            if not query or not isinstance(query, str):
                return {
                    "response": "I'm here to help with safety and emotional support. Please tell me what's on your mind or ask about personal safety.",
                    "content_items": [],
                    "emergency_detected": False,
                    "crisis_level": "none",
                    "safety_warnings": [],
                    "next_actions": ["Ask about personal safety", "Share your concerns", "Learn about good and bad touch"],
                    "professional_referrals": [],
                    "immediate_help_needed": False
                }
            
            # Detect emergency situations and crisis level
            emergency_result = self.detect_emergency_situation(query)
            crisis_assessment = self._assess_query_crisis_level(query)
            distress_level = self._detect_emotional_distress(query)
            
            # Determine if immediate help is needed
            immediate_help_needed = (
                emergency_result["is_emergency"] or 
                crisis_assessment["level"] == "high" or 
                distress_level["severity"] == "severe"
            )
            
            if immediate_help_needed:
                return {
                    "response": self._generate_crisis_response(emergency_result, crisis_assessment, distress_level, language_code),
                    "content_items": [],
                    "emergency_detected": True,
                    "crisis_level": max(crisis_assessment["level"], distress_level["severity"], key=lambda x: ["none", "low", "medium", "high", "severe"].index(x)),
                    "safety_warnings": ["Immediate professional help recommended"],
                    "next_actions": emergency_result["immediate_actions"] + crisis_assessment.get("immediate_actions", []),
                    "professional_referrals": self._generate_professional_referrals("crisis_intervention", "high", language_code),
                    "emergency_contacts": emergency_result["recommended_contacts"],
                    "immediate_help_needed": True
                }
            
            # Analyze query to determine relevant topic
            detected_topic = self._analyze_query_for_topic(query)
            
            # Get user age group for appropriate response
            user_age_group = "adolescent"
            if session_id:
                session = self.session_manager.get_session(session_id)
                if session and session.accessibility_preferences:
                    user_age_group = session.accessibility_preferences.get("age_group", "adolescent")
            
            # Generate response based on detected topic
            if detected_topic:
                # Get content for the detected topic
                content_result = self.get_content_by_topic(detected_topic, language_code, session_id)
                
                # Generate contextual response
                response_text = self._generate_contextual_response(
                    query, detected_topic, language_code, user_age_group, distress_level
                )
                
                # Get related content items
                content_items = content_result.get("content", [])
                
                # Generate next actions
                next_actions = self._generate_next_actions(detected_topic, user_age_group, distress_level)
                
                # Get professional referrals
                professional_referrals = content_result.get("professional_referrals", [])
                
            else:
                # General response when topic cannot be determined
                response_text = self._generate_general_response(query, language_code, user_age_group, distress_level)
                content_items = []
                next_actions = ["Share more about your situation", "Ask about specific safety topics", "Tell me how you're feeling"]
                professional_referrals = []
            
            # Update session context
            if session_id:
                self.update_session_context(session_id, {
                    "query": query,
                    "detected_topic": detected_topic,
                    "crisis_level": crisis_assessment["level"],
                    "distress_level": distress_level["severity"],
                    "response_generated": True,
                    "language": language_code
                })
            
            result = {
                "response": response_text,
                "content_items": content_items,
                "emergency_detected": emergency_result["is_emergency"],
                "crisis_level": crisis_assessment["level"],
                "safety_warnings": crisis_assessment.get("warnings", []),
                "next_actions": next_actions,
                "professional_referrals": professional_referrals,
                "immediate_help_needed": False,
                "detected_topic": detected_topic,
                "user_age_group": user_age_group,
                "distress_indicators": distress_level["indicators"]
            }
            
            self.logger.info(f"Processed user query successfully, detected topic: {detected_topic}, crisis level: {crisis_assessment['level']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling user query: {e}")
            return {
                "response": "I'm concerned about you and want to help. Please reach out to emergency services or a trusted adult if you need immediate help.",
                "content_items": [],
                "emergency_detected": True,
                "crisis_level": "high",
                "safety_warnings": ["System error occurred - seek immediate help if needed"],
                "next_actions": ["Contact emergency services: 112", "Reach out to a trusted adult", "Call women's helpline: 1091"],
                "professional_referrals": self._generate_professional_referrals("crisis_intervention", "high", language_code),
                "emergency_contacts": self.get_emergency_resources(language_code),
                "immediate_help_needed": True,
                "error": str(e)
            }
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available topics for safety and mental support module.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        try:
            # Return localized topic names if available, otherwise return English names
            if language_code == "hi":
                return [
                    "अच्छा और बुरा स्पर्श",      # good_bad_touch
                    "व्यक्तिगत सुरक्षा",        # personal_safety
                    "भावनात्मक सहारा",         # emotional_support
                    "तनाव से निपटने के तरीके",   # coping_strategies
                    "संकट में हस्तक्षेप",       # crisis_intervention
                    "सीमा निर्धारण",          # boundary_setting
                    "परेशानी का जवाब",        # distress_response
                    "पेशेवर मदद"             # professional_help
                ]
            elif language_code == "bn":
                return [
                    "ভাল এবং খারাপ স্পর্শ",      # good_bad_touch
                    "ব্যক্তিগত নিরাপত্তা",      # personal_safety
                    "আবেগিক সহায়তা",         # emotional_support
                    "মোকাবেলার কৌশল",        # coping_strategies
                    "সংকট হস্তক্ষেপ",         # crisis_intervention
                    "সীমানা নির্ধারণ",        # boundary_setting
                    "দুর্দশার প্রতিক্রিয়া",     # distress_response
                    "পেশাদার সাহায্য"        # professional_help
                ]
            else:
                # Default English topic names
                return [
                    "Good and Bad Touch",
                    "Personal Safety",
                    "Emotional Support",
                    "Coping Strategies",
                    "Crisis Intervention",
                    "Boundary Setting",
                    "Distress Response",
                    "Professional Help"
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting module topics for language {language_code}: {e}")
            return self.AVAILABLE_TOPICS  # Fallback to English topic keys

    def _assess_crisis_level(self, topic: str, content_items: List[ContentItem]) -> Dict[str, Any]:
        """
        Assess the crisis level based on topic and content.
        
        Args:
            topic: Current topic being accessed
            content_items: Content items being viewed
            
        Returns:
            Dictionary containing crisis assessment information
        """
        try:
            crisis_assessment = {
                "level": "none",
                "indicators": [],
                "immediate_actions": [],
                "warnings": []
            }
            
            # High-risk topics that indicate potential crisis
            high_risk_topics = ["crisis_intervention", "distress_response", "professional_help"]
            medium_risk_topics = ["good_bad_touch", "emotional_support", "coping_strategies"]
            
            if topic in high_risk_topics:
                crisis_assessment["level"] = "high"
                crisis_assessment["indicators"].append(f"Accessing high-risk topic: {topic}")
                crisis_assessment["immediate_actions"].extend([
                    "Consider contacting professional help immediately",
                    "Reach out to trusted adults or counselors",
                    "Call emergency services if in immediate danger"
                ])
                crisis_assessment["warnings"].append("This topic indicates potential crisis situation")
                
            elif topic in medium_risk_topics:
                crisis_assessment["level"] = "medium"
                crisis_assessment["indicators"].append(f"Accessing medium-risk topic: {topic}")
                crisis_assessment["immediate_actions"].extend([
                    "Consider talking to a trusted adult",
                    "Explore professional support options",
                    "Learn about available help resources"
                ])
            else:
                crisis_assessment["level"] = "low"
            
            # Analyze content for crisis indicators
            for content in content_items:
                if content.transcript:
                    crisis_keywords_found = [
                        keyword for keyword in self.CRISIS_KEYWORDS
                        if keyword in content.transcript.lower()
                    ]
                    if crisis_keywords_found:
                        crisis_assessment["indicators"].extend(crisis_keywords_found)
                        if crisis_assessment["level"] == "none":
                            crisis_assessment["level"] = "medium"
                        elif crisis_assessment["level"] == "low":
                            crisis_assessment["level"] = "medium"
            
            return crisis_assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing crisis level: {e}")
            return {
                "level": "high",  # Err on the side of caution
                "indicators": ["Assessment error occurred"],
                "immediate_actions": ["Seek immediate help if needed"],
                "warnings": ["Unable to assess crisis level properly"]
            }

    def _assess_query_crisis_level(self, query: str) -> Dict[str, Any]:
        """
        Assess crisis level based on user query content.
        
        Args:
            query: User's query text
            
        Returns:
            Dictionary containing crisis assessment
        """
        try:
            query_lower = query.lower()
            crisis_assessment = {
                "level": "none",
                "indicators": [],
                "immediate_actions": [],
                "warnings": []
            }
            
            # Check for crisis keywords
            crisis_matches = [keyword for keyword in self.CRISIS_KEYWORDS if keyword in query_lower]
            
            if crisis_matches:
                crisis_assessment["indicators"] = crisis_matches
                
                # Determine severity based on specific keywords
                severe_keywords = ["suicide", "kill", "die", "rape", "assault", "abuse", "violence"]
                high_keywords = ["hurt", "scared", "threatened", "unsafe", "harassment", "depression"]
                
                if any(keyword in crisis_matches for keyword in severe_keywords):
                    crisis_assessment["level"] = "high"
                    crisis_assessment["immediate_actions"] = [
                        "Call emergency services immediately: 112",
                        "Contact suicide prevention helpline if needed",
                        "Reach out to trusted adults or authorities"
                    ]
                    crisis_assessment["warnings"] = ["Severe crisis indicators detected"]
                    
                elif any(keyword in crisis_matches for keyword in high_keywords):
                    crisis_assessment["level"] = "medium"
                    crisis_assessment["immediate_actions"] = [
                        "Consider contacting helpline services",
                        "Talk to a trusted adult or counselor",
                        "Explore professional support options"
                    ]
                    crisis_assessment["warnings"] = ["Crisis indicators detected"]
                else:
                    crisis_assessment["level"] = "low"
                    crisis_assessment["immediate_actions"] = [
                        "Consider talking to someone you trust",
                        "Learn about available support resources"
                    ]
            
            return crisis_assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing query crisis level: {e}")
            return {
                "level": "medium",
                "indicators": ["Assessment error"],
                "immediate_actions": ["Seek help if needed"],
                "warnings": ["Unable to properly assess crisis level"]
            }
    def _detect_emotional_distress(self, query: str) -> Dict[str, Any]:
        """
        Detect emotional distress indicators in user query.
        
        Args:
            query: User's query text
            
        Returns:
            Dictionary containing distress assessment
        """
        try:
            query_lower = query.lower()
            distress_assessment = {
                "severity": "none",
                "indicators": [],
                "support_needed": False,
                "recommendations": []
            }
            
            # Check for distress indicators
            distress_matches = [indicator for indicator in self.DISTRESS_INDICATORS if indicator in query_lower]
            
            if distress_matches:
                distress_assessment["indicators"] = distress_matches
                distress_assessment["support_needed"] = True
                
                # Determine severity
                severe_indicators = ["hopeless", "worthless", "suicide", "self-harm", "empty", "numb"]
                moderate_indicators = ["sad", "crying", "depressed", "anxious", "overwhelmed", "panic"]
                
                if any(indicator in distress_matches for indicator in severe_indicators):
                    distress_assessment["severity"] = "severe"
                    distress_assessment["recommendations"] = [
                        "Immediate professional help recommended",
                        "Contact mental health crisis line",
                        "Reach out to trusted support person"
                    ]
                elif any(indicator in distress_matches for indicator in moderate_indicators):
                    distress_assessment["severity"] = "moderate"
                    distress_assessment["recommendations"] = [
                        "Consider talking to a counselor",
                        "Explore coping strategies",
                        "Connect with support resources"
                    ]
                else:
                    distress_assessment["severity"] = "mild"
                    distress_assessment["recommendations"] = [
                        "Practice self-care techniques",
                        "Talk to trusted friends or family",
                        "Consider stress management strategies"
                    ]
            
            return distress_assessment
            
        except Exception as e:
            self.logger.error(f"Error detecting emotional distress: {e}")
            return {
                "severity": "moderate",
                "indicators": ["Assessment error"],
                "support_needed": True,
                "recommendations": ["Seek support if needed"]
            }

    def _generate_professional_referrals(self, topic: str, crisis_level: str, language_code: str) -> List[Dict[str, Any]]:
        """
        Generate professional help referrals based on topic and crisis level.
        
        Args:
            topic: Current topic
            crisis_level: Assessed crisis level
            language_code: Language for referrals
            
        Returns:
            List of professional referral recommendations
        """
        try:
            referrals = []
            
            # Base referrals by crisis level
            if crisis_level in ["high", "severe"]:
                referrals.extend([
                    {
                        "type": "emergency",
                        "description": "Emergency Services" if language_code == "en" else "आपातकालीन सेवाएं",
                        "contact": "112",
                        "availability": "24/7",
                        "urgency": "immediate"
                    },
                    {
                        "type": "counseling",
                        "description": "Crisis Counseling" if language_code == "en" else "संकट परामर्श",
                        "contact": "9152987821",
                        "availability": "24/7",
                        "urgency": "immediate"
                    }
                ])
            
            if crisis_level in ["medium", "high", "severe"]:
                referrals.extend([
                    {
                        "type": "counseling",
                        "description": "Mental Health Professional" if language_code == "en" else "मानसिक स्वास्थ्य पेशेवर",
                        "contact": "Local counseling center",
                        "availability": "Business hours",
                        "urgency": "within 24-48 hours"
                    },
                    {
                        "type": "medical",
                        "description": "Healthcare Provider" if language_code == "en" else "स्वास्थ्य सेवा प्रदाता",
                        "contact": "104 (Health Helpline)",
                        "availability": "24/7",
                        "urgency": "as needed"
                    }
                ])
            
            # Topic-specific referrals
            if topic in ["good_bad_touch", "personal_safety"]:
                referrals.append({
                    "type": "legal",
                    "description": "Women's Helpline" if language_code == "en" else "महिला हेल्पलाइन",
                    "contact": "1091",
                    "availability": "24/7",
                    "urgency": "immediate if unsafe"
                })
            
            if topic in ["emotional_support", "coping_strategies"]:
                referrals.append({
                    "type": "social",
                    "description": "Support Groups" if language_code == "en" else "सहायता समूह",
                    "contact": "Local community centers",
                    "availability": "Varies",
                    "urgency": "ongoing support"
                })
            
            return referrals
            
        except Exception as e:
            self.logger.error(f"Error generating professional referrals: {e}")
            return [
                {
                    "type": "emergency",
                    "description": "Emergency Services",
                    "contact": "112",
                    "availability": "24/7",
                    "urgency": "immediate"
                }
            ]

    def _analyze_query_for_topic(self, query: str) -> Optional[str]:
        """
        Analyze user query to determine the most relevant safety/mental support topic.
        
        Args:
            query: User's query text
            
        Returns:
            Most relevant topic name or None if no clear match
        """
        query_lower = query.lower()
        
        # Topic keyword mapping
        topic_keywords = {
            "good_bad_touch": ["touch", "inappropriate", "uncomfortable", "private", "body", "parts", "स्पर्श", "छूना", "गलत"],
            "personal_safety": ["safety", "safe", "danger", "protect", "security", "सुरक्षा", "खतरा", "बचाव"],
            "emotional_support": ["sad", "upset", "emotional", "feelings", "support", "भावना", "दुखी", "सहारा"],
            "coping_strategies": ["cope", "deal", "manage", "stress", "handle", "निपटना", "तनाव", "संभालना"],
            "crisis_intervention": ["crisis", "emergency", "urgent", "help", "संकट", "आपातकाल", "मदद"],
            "boundary_setting": ["boundary", "limit", "say no", "refuse", "सीमा", "मना करना", "इनकार"],
            "distress_response": ["distress", "trouble", "problem", "worried", "परेशानी", "चिंता", "समस्या"],
            "professional_help": ["counselor", "therapist", "doctor", "help", "परामर्शदाता", "डॉक्टर", "सहायता"]
        }
        
        # Score each topic based on keyword matches
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Return topic with highest score
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return None
    def _generate_contextual_response(self, query: str, topic: str, language_code: str, 
                                    age_group: str, distress_level: Dict[str, Any]) -> str:
        """
        Generate a contextual response based on the query, topic, and user's emotional state.
        
        Args:
            query: Original user query
            topic: Detected topic
            language_code: Language for response
            age_group: User's age group for appropriate language
            distress_level: Emotional distress assessment
            
        Returns:
            Contextual response text
        """
        # Response templates by language, topic, and age group
        responses = {
            "en": {
                "good_bad_touch": {
                    "young_adolescent": "It's important to know the difference between good touch and bad touch. Good touch makes you feel safe and comfortable, while bad touch makes you feel uncomfortable or scared. You have the right to say no to any touch that makes you uncomfortable.",
                    "adolescent": "Understanding good and bad touch is crucial for your safety. Good touch is respectful and makes you feel safe, like hugs from family or medical exams with permission. Bad touch is inappropriate and makes you uncomfortable. Trust your feelings and speak up if someone touches you inappropriately.",
                    "young_adult": "Recognizing appropriate and inappropriate touch is essential for personal safety. You have the right to set boundaries about your body and to refuse any touch that makes you uncomfortable. Trust your instincts and seek help if someone violates your boundaries.",
                    "adult": "Understanding consent and appropriate touch helps you protect yourself and support others. Everyone has the right to bodily autonomy and to refuse unwanted touch. If you or someone you know experiences inappropriate touch, professional help and support are available."
                },
                "personal_safety": {
                    "young_adolescent": "Your safety is very important. Always trust your feelings when something doesn't feel right. Stay close to trusted adults and remember that you can always ask for help.",
                    "adolescent": "Personal safety involves being aware of your surroundings and trusting your instincts. Learn to recognize potentially dangerous situations and have a plan for getting help. Remember, your safety is more important than being polite.",
                    "young_adult": "Personal safety includes physical, emotional, and digital safety. Trust your instincts, set clear boundaries, and don't hesitate to remove yourself from uncomfortable situations. Having a safety plan and support network is important.",
                    "adult": "Personal safety involves awareness, preparation, and knowing your resources. Trust your instincts, maintain boundaries, and have emergency contacts readily available. Supporting others' safety is also part of community well-being."
                },
                "emotional_support": {
                    "young_adolescent": "It's okay to have big feelings, and it's important to talk about them with someone you trust. Your feelings matter, and there are people who want to help you feel better.",
                    "adolescent": "Having strong emotions is normal, especially during adolescence. It's important to express your feelings in healthy ways and seek support when you need it. Talking to trusted adults or friends can help.",
                    "young_adult": "Managing emotions is an ongoing process. It's healthy to acknowledge your feelings and seek support when needed. Professional counseling can provide valuable tools for emotional well-being.",
                    "adult": "Emotional support is important throughout life. Seeking help for mental health is a sign of strength, not weakness. Professional counselors and support groups can provide valuable assistance."
                }
            },
            "hi": {
                "good_bad_touch": {
                    "young_adolescent": "अच्छे और बुरे स्पर्श के बीच अंतर जानना जरूरी है। अच्छा स्पर्श आपको सुरक्षित महसूस कराता है, जबकि बुरा स्पर्श आपको असहज या डरा हुआ महसूस कराता है। आपको किसी भी असहज स्पर्श को मना करने का अधिकार है।",
                    "adolescent": "अच्छे और बुरे स्पर्श को समझना आपकी सुरक्षा के लिए जरूरी है। अच्छा स्पर्श सम्मानजनक होता है और आपको सुरक्षित महसूस कराता है। बुरा स्पर्श अनुचित होता है और आपको असहज महसूस कराता है। अपनी भावनाओं पर भरोसा करें।",
                    "young_adult": "उचित और अनुचित स्पर्श को पहचानना व्यक्तिगत सुरक्षा के लिए आवश्यक है। आपको अपने शरीर के बारे में सीमाएं तय करने और किसी भी असहज स्पर्श को मना करने का अधिकार है।",
                    "adult": "सहमति और उचित स्पर्श को समझना आपकी और दूसरों की सुरक्षा में मदद करता है। हर किसी को शारीरिक स्वायत्तता का अधिकार है। यदि आप या कोई और अनुचित स्पर्श का अनुभव करता है, तो पेशेवर मदद उपलब्ध है।"
                },
                "personal_safety": {
                    "young_adolescent": "आपकी सुरक्षा बहुत महत्वपूर्ण है। जब कुछ सही नहीं लगता तो हमेशा अपनी भावनाओं पर भरोसा करें। विश्वसनीय वयस्कों के पास रहें और याद रखें कि आप हमेशा मदद मांग सकती हैं।",
                    "adolescent": "व्यक्तिगत सुरक्षा में अपने आसपास के माहौल के बारे में जागरूक रहना और अपनी सहज बुद्धि पर भरोसा करना शामिल है। संभावित खतरनाक स्थितियों को पहचानना सीखें।",
                    "young_adult": "व्यक्तिगत सुरक्षा में शारीरिक, भावनात्मक और डिजिटल सुरक्षा शामिल है। अपनी सहज बुद्धि पर भरोसा करें, स्पष्ट सीमाएं तय करें।",
                    "adult": "व्यक्तिगत सुरक्षा में जागरूकता, तैयारी और अपने संसाधनों को जानना शामिल है। अपनी सहज बुद्धि पर भरोसा करें और आपातकालीन संपर्क तैयार रखें।"
                },
                "emotional_support": {
                    "young_adolescent": "बड़ी भावनाएं होना ठीक है, और किसी भरोसेमंद व्यक्ति से इनके बारे में बात करना जरूरी है। आपकी भावनाएं मायने रखती हैं।",
                    "adolescent": "तीव्र भावनाएं होना सामान्य है, खासकर किशोरावस्था में। अपनी भावनाओं को स्वस्थ तरीकों से व्यक्त करना और जरूरत पड़ने पर सहारा लेना जरूरी है।",
                    "young_adult": "भावनाओं का प्रबंधन एक निरंतर प्रक्रिया है। अपनी भावनाओं को स्वीकार करना और जरूरत पड़ने पर सहारा लेना स्वस्थ है।",
                    "adult": "भावनात्मक सहारा जीवन भर महत्वपूर्ण है। मानसिक स्वास्थ्य के लिए मदद लेना कमजोरी नहीं, बल्कि ताकत का संकेत है।"
                }
            }
        }
        
        # Adjust response based on distress level
        base_response = self._get_base_response(responses, language_code, topic, age_group)
        
        if distress_level["severity"] in ["moderate", "severe"]:
            support_message = (
                " I can see you might be going through a difficult time. Remember that you're not alone and help is available."
                if language_code == "en" else
                " मैं देख सकती हूं कि आप मुश्किल समय से गुजर रही हैं। याद रखें कि आप अकेली नहीं हैं और मदद उपलब्ध है।"
            )
            base_response += support_message
        
        return base_response

    def _get_base_response(self, responses: Dict, language_code: str, topic: str, age_group: str) -> str:
        """Get base response from response templates."""
        lang_responses = responses.get(language_code, responses["en"])
        topic_responses = lang_responses.get(topic, {})
        
        if age_group in topic_responses:
            return topic_responses[age_group]
        else:
            return topic_responses.get("adolescent", "I'm here to help you with safety and emotional support.")

    def _generate_general_response(self, query: str, language_code: str, age_group: str, 
                                 distress_level: Dict[str, Any]) -> str:
        """
        Generate a general response when specific topic cannot be determined.
        
        Args:
            query: Original user query
            language_code: Language for response
            age_group: User's age group
            distress_level: Emotional distress assessment
            
        Returns:
            General response text
        """
        general_responses = {
            "en": {
                "young_adolescent": "I'm here to help you stay safe and feel supported. You can talk to me about anything that's bothering you or ask about staying safe.",
                "adolescent": "I'm here to provide support and safety information. Whether you have questions about personal safety, need emotional support, or want to talk about your feelings, I'm here to listen and help.",
                "young_adult": "I can provide information and support about personal safety, emotional well-being, and crisis resources. What would you like to talk about today?",
                "adult": "I'm here to provide safety information, emotional support, and crisis resources. How can I help you today?"
            },
            "hi": {
                "young_adolescent": "मैं आपकी सुरक्षा और सहारे के लिए यहाँ हूँ। आप मुझसे किसी भी परेशानी के बारे में बात कर सकती हैं या सुरक्षित रहने के बारे में पूछ सकती हैं।",
                "adolescent": "मैं सहारा और सुरक्षा की जानकारी प्रदान करने के लिए यहाँ हूँ। चाहे आपके पास व्यक्तिगत सुरक्षा के बारे में सवाल हों, भावनात्मक सहारे की जरूरत हो, या अपनी भावनाओं के बारे में बात करना चाहती हों।",
                "young_adult": "मैं व्यक्तिगत सुरक्षा, भावनात्मक कल्याण और संकट संसाधनों के बारे में जानकारी और सहारा प्रदान कर सकती हूँ। आज आप किस बारे में बात करना चाहती हैं?",
                "adult": "मैं सुरक्षा जानकारी, भावनात्मक सहारा और संकट संसाधन प्रदान करने के लिए यहाँ हूँ। आज मैं आपकी कैसे मदद कर सकती हूँ?"
            }
        }
        
        lang_responses = general_responses.get(language_code, general_responses["en"])
        base_response = lang_responses.get(age_group, lang_responses["adolescent"])
        
        # Add supportive message if distress detected
        if distress_level["support_needed"]:
            support_message = (
                " I notice you might be going through something difficult. I'm here to listen and help you find the support you need."
                if language_code == "en" else
                " मुझे लगता है कि आप कुछ कठिन समय से गुजर रही हैं। मैं सुनने और आपको जरूरी सहारा दिलाने के लिए यहाँ हूँ।"
            )
            base_response += support_message
        
        return base_response
    def _generate_crisis_response(self, emergency_result: Dict[str, Any], crisis_assessment: Dict[str, Any], 
                                distress_level: Dict[str, Any], language_code: str) -> str:
        """
        Generate appropriate crisis response text for emergency situations.
        
        Args:
            emergency_result: Emergency detection result
            crisis_assessment: Crisis level assessment
            distress_level: Emotional distress assessment
            language_code: Language for response
            
        Returns:
            Crisis response text
        """
        crisis_responses = {
            "en": {
                "high": "I'm very concerned about your safety and well-being. Please reach out for immediate help. You are not alone, and there are people who want to help you. If you're in immediate danger, call 112. For emotional support, call 9152987821. Please don't hesitate to contact emergency services or a trusted adult.",
                "severe": "I'm deeply concerned about you. Your life and safety matter. Please reach out for immediate professional help. If you're having thoughts of suicide or self-harm, call emergency services (112) or a suicide prevention helpline (9152987821) right away. You don't have to go through this alone.",
                "medium": "I can see you're going through a difficult time. It's important to reach out for support. Consider talking to a trusted adult, counselor, or calling a helpline. Remember that seeking help is a sign of strength, not weakness.",
                "general": "I'm here to support you, but I'm concerned about your situation. Please consider reaching out to professional help or emergency services if you feel unsafe. You deserve support and care."
            },
            "hi": {
                "high": "मुझे आपकी सुरक्षा और कल्याण की बहुत चिंता है। कृपया तुरंत मदद के लिए संपर्क करें। आप अकेली नहीं हैं, और ऐसे लोग हैं जो आपकी मदद करना चाहते हैं। यदि आप तत्काल खतरे में हैं, तो 112 पर कॉल करें। भावनात्मक सहारे के लिए 9152987821 पर कॉल करें।",
                "severe": "मुझे आपकी गहरी चिंता है। आपका जीवन और सुरक्षा महत्वपूर्ण है। कृपया तुरंत पेशेवर मदद के लिए संपर्क करें। यदि आपके मन में आत्महत्या या आत्म-हानि के विचार आ रहे हैं, तो तुरंत आपातकालीन सेवाओं (112) या आत्महत्या रोकथाम हेल्पलाइन (9152987821) पर कॉल करें।",
                "medium": "मैं देख सकती हूं कि आप कठिन समय से गुजर रही हैं। सहारे के लिए संपर्क करना जरूरी है। किसी विश्वसनीय व्यक्ति, परामर्शदाता से बात करने या हेल्पलाइन पर कॉल करने पर विचार करें।",
                "general": "मैं आपका साथ देने के लिए यहाँ हूँ, लेकिन मुझे आपकी स्थिति की चिंता है। यदि आप असुरक्षित महसूस करती हैं तो कृपया पेशेवर मदद या आपातकालीन सेवाओं से संपर्क करने पर विचार करें।"
            }
        }
        
        # Determine response level based on assessments
        if distress_level["severity"] == "severe" or any(keyword in ["suicide", "kill", "die"] for keyword in crisis_assessment.get("indicators", [])):
            response_level = "severe"
        elif crisis_assessment["level"] == "high" or emergency_result["emergency_type"] in ["safety_threat", "mental_health_crisis"]:
            response_level = "high"
        elif crisis_assessment["level"] == "medium" or distress_level["severity"] == "moderate":
            response_level = "medium"
        else:
            response_level = "general"
        
        lang_responses = crisis_responses.get(language_code, crisis_responses["en"])
        return lang_responses.get(response_level, lang_responses["general"])

    def _generate_topic_recommendations(self, current_topic: str, age_group: str) -> List[str]:
        """
        Generate recommendations for related topics based on current topic and age group.
        
        Args:
            current_topic: Currently viewed topic
            age_group: User's age group
            
        Returns:
            List of recommended topic names
        """
        # Topic relationship mapping
        topic_relationships = {
            "good_bad_touch": ["personal_safety", "boundary_setting", "emotional_support"],
            "personal_safety": ["good_bad_touch", "boundary_setting", "coping_strategies"],
            "emotional_support": ["coping_strategies", "distress_response", "professional_help"],
            "coping_strategies": ["emotional_support", "distress_response", "professional_help"],
            "crisis_intervention": ["professional_help", "distress_response", "emotional_support"],
            "boundary_setting": ["personal_safety", "good_bad_touch", "emotional_support"],
            "distress_response": ["emotional_support", "coping_strategies", "crisis_intervention"],
            "professional_help": ["crisis_intervention", "emotional_support", "coping_strategies"]
        }
        
        # Get age-appropriate topics
        age_appropriate_topics = self.AGE_APPROPRIATE_CONTENT.get(age_group, self.AVAILABLE_TOPICS)
        
        # Get related topics
        related_topics = topic_relationships.get(current_topic, [])
        
        # Filter by age appropriateness and limit to 3 recommendations
        recommendations = [
            topic for topic in related_topics 
            if topic in age_appropriate_topics and topic != current_topic
        ][:3]
        
        return recommendations

    def _generate_next_actions(self, topic: str, age_group: str, distress_level: Dict[str, Any]) -> List[str]:
        """
        Generate suggested next actions based on topic, age group, and distress level.
        
        Args:
            topic: Current topic
            age_group: User's age group
            distress_level: Emotional distress assessment
            
        Returns:
            List of suggested next actions
        """
        next_actions = {
            "good_bad_touch": [
                "Learn about setting personal boundaries",
                "Practice saying 'no' to uncomfortable situations",
                "Talk to a trusted adult about any concerns"
            ],
            "personal_safety": [
                "Create a personal safety plan",
                "Identify trusted adults you can contact",
                "Learn about local emergency resources"
            ],
            "emotional_support": [
                "Practice self-care techniques",
                "Connect with supportive friends or family",
                "Consider talking to a counselor"
            ],
            "coping_strategies": [
                "Try relaxation techniques like deep breathing",
                "Engage in activities you enjoy",
                "Build a support network"
            ],
            "crisis_intervention": [
                "Contact professional help immediately",
                "Reach out to emergency services if needed",
                "Connect with crisis support resources"
            ],
            "boundary_setting": [
                "Practice assertive communication",
                "Learn to recognize your limits",
                "Seek support when boundaries are crossed"
            ],
            "distress_response": [
                "Use healthy coping mechanisms",
                "Reach out to support systems",
                "Consider professional counseling"
            ],
            "professional_help": [
                "Research local counseling services",
                "Ask trusted adults for referrals",
                "Contact mental health helplines"
            ]
        }
        
        base_actions = next_actions.get(topic, ["Explore related topics", "Ask specific questions", "Seek appropriate support"])
        
        # Add distress-specific actions if needed
        if distress_level["support_needed"]:
            if distress_level["severity"] in ["moderate", "severe"]:
                base_actions.insert(0, "Consider reaching out for professional support")
            if distress_level["severity"] == "severe":
                base_actions.insert(0, "Contact crisis support services immediately")
        
        return base_actions

    def get_crisis_resources(self, language_code: str = "en", crisis_type: str = "general") -> List[Dict[str, Any]]:
        """
        Get specialized crisis resources based on crisis type.
        
        Args:
            language_code: Language code for resource information
            crisis_type: Type of crisis (safety, mental_health, general)
            
        Returns:
            List of crisis resource information
        """
        try:
            crisis_resources = []
            
            # General crisis resources
            crisis_resources.extend([
                {
                    "name": "National Emergency Services" if language_code == "en" else "राष्ट्रीय आपातकालीन सेवाएं",
                    "phone": "112",
                    "type": "emergency",
                    "availability": "24/7",
                    "description": "Police, Fire, Medical Emergency" if language_code == "en" else "पुलिस, अग्निशमन, चिकित्सा आपातकाल"
                },
                {
                    "name": "Women's Helpline" if language_code == "en" else "महिला हेल्पलाइन",
                    "phone": "1091",
                    "type": "safety",
                    "availability": "24/7",
                    "description": "Domestic Violence, Harassment Support" if language_code == "en" else "घरेलू हिंसा, उत्पीड़न सहायता"
                }
            ])
            
            # Mental health specific resources
            if crisis_type in ["mental_health", "general"]:
                crisis_resources.extend([
                    {
                        "name": "AASRA Suicide Prevention" if language_code == "en" else "आसरा आत्महत्या रोकथाम",
                        "phone": "9152987821",
                        "type": "mental_health",
                        "availability": "24/7",
                        "description": "Suicide Prevention and Crisis Counseling" if language_code == "en" else "आत्महत्या रोकथाम और संकट परामर्श"
                    },
                    {
                        "name": "National Health Helpline" if language_code == "en" else "राष्ट्रीय स्वास्थ्य हेल्पलाइन",
                        "phone": "104",
                        "type": "medical",
                        "availability": "24/7",
                        "description": "Medical and Mental Health Consultation" if language_code == "en" else "चिकित्सा और मानसिक स्वास्थ्य परामर्श"
                    }
                ])
            
            # Safety specific resources
            if crisis_type in ["safety", "general"]:
                crisis_resources.append({
                    "name": "National Commission for Women" if language_code == "en" else "राष्ट्रीय महिला आयोग",
                    "phone": "011-26853846",
                    "type": "legal",
                    "availability": "9 AM - 6 PM",
                    "description": "Women's Rights and Legal Support" if language_code == "en" else "महिला अधिकार और कानूनी सहायता"
                })
            
            return crisis_resources
            
        except Exception as e:
            self.logger.error(f"Error getting crisis resources: {e}")
            return [
                {
                    "name": "Emergency Services",
                    "phone": "112",
                    "type": "emergency",
                    "availability": "24/7",
                    "description": "National Emergency Helpline"
                }
            ]

    def detect_safety_threat(self, user_input: str) -> Dict[str, Any]:
        """
        Detect potential safety threats in user input with immediate routing capability.
        
        This method implements Requirements 2.3 for emergency detection and routing.
        
        Args:
            user_input: User's text input to analyze
            
        Returns:
            Dictionary containing threat assessment and routing information
        """
        try:
            threat_assessment = {
                "threat_detected": False,
                "threat_level": "none",
                "threat_type": None,
                "immediate_action_required": False,
                "routing_recommendations": [],
                "safety_resources": []
            }
            
            if not user_input or not isinstance(user_input, str):
                return threat_assessment
            
            user_input_lower = user_input.lower()
            
            # Safety threat keywords
            safety_threats = {
                "physical_violence": ["hit", "beat", "hurt", "violence", "assault", "attack", "abuse"],
                "sexual_threat": ["rape", "molest", "inappropriate touch", "sexual assault", "harassment"],
                "emotional_abuse": ["threaten", "scare", "intimidate", "control", "isolate"],
                "immediate_danger": ["help", "emergency", "danger", "unsafe", "scared", "hiding"]
            }
            
            detected_threats = []
            for threat_type, keywords in safety_threats.items():
                if any(keyword in user_input_lower for keyword in keywords):
                    detected_threats.append(threat_type)
            
            if detected_threats:
                threat_assessment["threat_detected"] = True
                threat_assessment["threat_type"] = detected_threats[0]  # Primary threat
                
                # Determine threat level
                if "immediate_danger" in detected_threats or any(word in user_input_lower for word in ["help", "emergency", "now"]):
                    threat_assessment["threat_level"] = "high"
                    threat_assessment["immediate_action_required"] = True
                elif "physical_violence" in detected_threats or "sexual_threat" in detected_threats:
                    threat_assessment["threat_level"] = "high"
                    threat_assessment["immediate_action_required"] = True
                else:
                    threat_assessment["threat_level"] = "medium"
                
                # Generate routing recommendations
                threat_assessment["routing_recommendations"] = [
                    "Contact emergency services (112) if in immediate danger",
                    "Call women's helpline (1091) for support",
                    "Reach out to trusted adults or authorities",
                    "Consider contacting local police if crime occurred"
                ]
                
                # Get safety resources
                threat_assessment["safety_resources"] = self.get_crisis_resources(crisis_type="safety")
            
            return threat_assessment
            
        except Exception as e:
            self.logger.error(f"Error detecting safety threat: {e}")
            return {
                "threat_detected": True,  # Err on the side of caution
                "threat_level": "high",
                "threat_type": "unknown",
                "immediate_action_required": True,
                "routing_recommendations": ["Contact emergency services immediately"],
                "safety_resources": self.get_crisis_resources()
            }