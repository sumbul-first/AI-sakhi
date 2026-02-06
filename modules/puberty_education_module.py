"""
PubertyEducationModule - Specialized health education module for puberty, menstruation, and hygiene.

This module provides comprehensive puberty education covering body changes, menstruation,
and hygiene practices as required by Requirements 1.1, 1.2, and 1.5. It implements
age-appropriate content filtering and culturally sensitive delivery mechanisms.

Key Features:
- Body changes education with age-appropriate content
- Menstruation basics and hygiene practices
- Multi-language support with cultural sensitivity
- Age-appropriate content filtering
- Integration with audio and video content
- Emergency support for distress situations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from modules.base_health_module import BaseHealthModule
from models.data_models import ContentItem, UserSession
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class PubertyEducationModule(BaseHealthModule):
    """
    Specialized health education module for puberty education.
    
    This module provides comprehensive education about body changes, menstruation,
    and hygiene practices for young girls and women. It implements age-appropriate
    content filtering and culturally sensitive delivery as required by Requirements
    1.1, 1.2, and 1.5.
    
    Topics covered:
    - Body changes during puberty
    - Menstruation basics and cycle understanding
    - Hygiene practices and product usage
    - Emotional changes and support
    - Myth-busting and factual information
    """
    
    # Available topics in the puberty education module
    AVAILABLE_TOPICS = [
        "body_changes",
        "menstruation_basics", 
        "hygiene_practices",
        "emotional_changes",
        "myth_busting",
        "product_usage",
        "cycle_tracking"
    ]
    
    # Age-appropriate content mapping
    AGE_APPROPRIATE_CONTENT = {
        "young_adolescent": ["body_changes", "emotional_changes", "hygiene_practices"],
        "adolescent": ["body_changes", "menstruation_basics", "hygiene_practices", "emotional_changes", "myth_busting"],
        "young_adult": ["menstruation_basics", "hygiene_practices", "product_usage", "cycle_tracking", "myth_busting"],
        "adult": ["menstruation_basics", "hygiene_practices", "product_usage", "cycle_tracking", "myth_busting"]
    }
    
    # Cultural sensitivity keywords for content filtering
    CULTURALLY_SENSITIVE_TERMS = [
        "periods", "menstruation", "body changes", "growing up", "adolescence",
        "hygiene", "cleanliness", "health", "normal development"
    ]
    
    def __init__(self, content_manager: ContentManager, session_manager: SessionManager):
        """
        Initialize the PubertyEducationModule.
        
        Args:
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
            
        Raises:
            ValueError: If required parameters are invalid
        """
        super().__init__(
            module_name="puberty_education",
            content_manager=content_manager,
            session_manager=session_manager
        )
        
        self.logger.info("PubertyEducationModule initialized successfully")
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content for a specific puberty education topic.
        
        This method implements topic-specific content retrieval with age-appropriate
        filtering as required by Requirements 1.1 and 1.2.
        
        Args:
            topic: Specific topic to retrieve content for
            language_code: Language code for content localization
            session_id: Optional session ID for personalization and age filtering
            
        Returns:
            Dictionary containing:
            - content: List of ContentItem objects
            - safety_validated: Boolean indicating content safety
            - emergency_detected: Boolean indicating if emergency keywords found
            - language_used: Actual language code used (may differ due to fallback)
            - recommendations: List of next steps or related topics
            - age_appropriate: Boolean indicating if content is age-appropriate
            - cultural_notes: List of cultural sensitivity notes
        """
        try:
            # Validate topic
            if topic not in self.AVAILABLE_TOPICS:
                self.logger.warning(f"Invalid topic requested: {topic}")
                return {
                    "content": [],
                    "safety_validated": False,
                    "emergency_detected": False,
                    "language_used": language_code,
                    "recommendations": [f"Available topics: {', '.join(self.AVAILABLE_TOPICS)}"],
                    "age_appropriate": False,
                    "cultural_notes": [],
                    "error": f"Topic '{topic}' not available in puberty education module"
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
                    "language_used": language_code,
                    "recommendations": [f"Age-appropriate topics: {', '.join(age_appropriate_topics)}"],
                    "age_appropriate": False,
                    "cultural_notes": ["Content filtered for age appropriateness"],
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
            
            # Validate content safety
            safety_result = self.validate_content_safety(topic_content)
            
            # Generate recommendations for related topics
            recommendations = self._generate_topic_recommendations(topic, user_age_group)
            
            # Add cultural sensitivity notes
            cultural_notes = self._generate_cultural_notes(topic, language_code)
            
            # Update session context if session provided
            if session_id:
                self.update_session_context(session_id, {
                    "topic": topic,
                    "language": language_code,
                    "content_count": len(topic_content),
                    "age_group": user_age_group
                })
            
            result = {
                "content": topic_content,
                "safety_validated": safety_result["is_safe"],
                "emergency_detected": bool(safety_result["emergency_flags"]),
                "language_used": content_result["language_used"],
                "recommendations": recommendations,
                "age_appropriate": is_age_appropriate,
                "cultural_notes": cultural_notes,
                "fallback_used": content_result["fallback_used"],
                "available_languages": content_result["available_languages"]
            }
            
            # Add emergency contacts if emergency detected
            if safety_result["emergency_flags"]:
                result["emergency_contacts"] = self.get_emergency_resources(language_code)
            
            self.logger.info(f"Retrieved {len(topic_content)} content items for topic: {topic}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error retrieving content for topic {topic}: {e}")
            return {
                "content": [],
                "safety_validated": False,
                "emergency_detected": False,
                "language_used": language_code,
                "recommendations": ["Please try again or contact support"],
                "age_appropriate": False,
                "cultural_notes": [],
                "error": str(e)
            }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to a user query about puberty education.
        
        This method implements natural language query processing for puberty-related
        questions with culturally sensitive responses as required by Requirements 1.1 and 1.2.
        
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
            - topic_suggestions: List of related topics to explore
        """
        try:
            if not query or not isinstance(query, str):
                return {
                    "response": "I didn't understand your question. Please ask about body changes, menstruation, or hygiene practices.",
                    "content_items": [],
                    "emergency_detected": False,
                    "safety_warnings": [],
                    "next_actions": ["Try asking about specific topics like 'body changes' or 'menstruation'"],
                    "topic_suggestions": self.AVAILABLE_TOPICS[:3]
                }
            
            # Detect emergency situations
            emergency_result = self.detect_emergency_situation(query)
            
            if emergency_result["is_emergency"]:
                return {
                    "response": self._generate_emergency_response(emergency_result, language_code),
                    "content_items": [],
                    "emergency_detected": True,
                    "safety_warnings": ["Emergency situation detected - immediate help recommended"],
                    "next_actions": emergency_result["immediate_actions"],
                    "emergency_contacts": emergency_result["recommended_contacts"],
                    "topic_suggestions": []
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
                    query, detected_topic, language_code, user_age_group
                )
                
                # Get related content items
                content_items = content_result.get("content", [])
                
                # Generate next actions
                next_actions = self._generate_next_actions(detected_topic, user_age_group)
                
                # Get topic suggestions
                topic_suggestions = self._generate_topic_recommendations(detected_topic, user_age_group)
                
            else:
                # General response when topic cannot be determined
                response_text = self._generate_general_response(query, language_code, user_age_group)
                content_items = []
                next_actions = ["Ask about specific topics like body changes, menstruation, or hygiene"]
                topic_suggestions = self.AVAILABLE_TOPICS[:3]
            
            # Update session context
            if session_id:
                self.update_session_context(session_id, {
                    "query": query,
                    "detected_topic": detected_topic,
                    "response_generated": True,
                    "language": language_code
                })
            
            result = {
                "response": response_text,
                "content_items": content_items,
                "emergency_detected": emergency_result["is_emergency"],
                "safety_warnings": [],
                "next_actions": next_actions,
                "topic_suggestions": topic_suggestions,
                "detected_topic": detected_topic,
                "user_age_group": user_age_group
            }
            
            self.logger.info(f"Processed user query successfully, detected topic: {detected_topic}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling user query: {e}")
            return {
                "response": "I'm sorry, I encountered an error. Please try asking your question again.",
                "content_items": [],
                "emergency_detected": False,
                "safety_warnings": ["System error occurred"],
                "next_actions": ["Try rephrasing your question", "Contact support if problem persists"],
                "topic_suggestions": [],
                "error": str(e)
            }
    
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available topics for puberty education module.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        try:
            # Return localized topic names if available, otherwise return English names
            if language_code == "hi":
                return [
                    "शरीर में बदलाव",      # body_changes
                    "मासिक धर्म की जानकारी",  # menstruation_basics
                    "स्वच्छता के तरीके",     # hygiene_practices
                    "भावनात्मक बदलाव",      # emotional_changes
                    "मिथकों का खंडन",       # myth_busting
                    "उत्पादों का उपयोग",     # product_usage
                    "चक्र की निगरानी"       # cycle_tracking
                ]
            elif language_code == "bn":
                return [
                    "শরীরের পরিবর্তন",        # body_changes
                    "মাসিকের তথ্য",          # menstruation_basics
                    "স্বচ্ছতার উপায়",        # hygiene_practices
                    "আবেগের পরিবর্তন",       # emotional_changes
                    "ভুল ধারণা দূরীকরণ",      # myth_busting
                    "পণ্যের ব্যবহার",        # product_usage
                    "চক্র পর্যবেক্ষণ"        # cycle_tracking
                ]
            else:
                # Default English topic names
                return [
                    "Body Changes",
                    "Menstruation Basics",
                    "Hygiene Practices", 
                    "Emotional Changes",
                    "Myth Busting",
                    "Product Usage",
                    "Cycle Tracking"
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting module topics for language {language_code}: {e}")
            return self.AVAILABLE_TOPICS  # Fallback to English topic keys
    
    def _analyze_query_for_topic(self, query: str) -> Optional[str]:
        """
        Analyze user query to determine the most relevant topic.
        
        Args:
            query: User's query text
            
        Returns:
            Most relevant topic name or None if no clear match
        """
        query_lower = query.lower()
        
        # Topic keyword mapping
        topic_keywords = {
            "body_changes": ["body", "changes", "growing", "development", "puberty", "adolescence", "शरीर", "बदलाव", "विकास"],
            "menstruation_basics": ["period", "menstruation", "monthly", "cycle", "bleeding", "मासिक", "धर्म", "पीरियड"],
            "hygiene_practices": ["hygiene", "clean", "wash", "care", "sanitation", "स्वच्छता", "सफाई", "धुलाई"],
            "emotional_changes": ["emotions", "feelings", "mood", "mental", "psychological", "भावना", "मूड", "मानसिक"],
            "myth_busting": ["myth", "misconception", "false", "truth", "fact", "मिथक", "गलत", "सच"],
            "product_usage": ["pad", "tampon", "cup", "product", "use", "पैड", "उत्पाद", "इस्तेमाल"],
            "cycle_tracking": ["track", "calendar", "date", "schedule", "record", "ट्रैक", "कैलेंडर", "तारीख"]
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
    
    def _generate_contextual_response(self, query: str, topic: str, language_code: str, age_group: str) -> str:
        """
        Generate a contextual response based on the query and detected topic.
        
        Args:
            query: Original user query
            topic: Detected topic
            language_code: Language for response
            age_group: User's age group for appropriate language
            
        Returns:
            Contextual response text
        """
        # Response templates by language and topic
        responses = {
            "en": {
                "body_changes": {
                    "young_adolescent": "Body changes during puberty are completely normal. Your body is growing and developing, which is a natural part of becoming a young woman.",
                    "adolescent": "During puberty, your body goes through many changes including growth spurts, breast development, and the start of menstruation. These changes are normal and healthy.",
                    "young_adult": "Understanding body changes helps you take better care of your health. Puberty brings physical and emotional changes that are part of normal development.",
                    "adult": "Body changes during puberty include physical development, hormonal changes, and the beginning of reproductive maturity. Understanding these changes helps in supporting young women."
                },
                "menstruation_basics": {
                    "young_adolescent": "Menstruation is a natural process that happens to girls as they grow up. It's nothing to be scared or ashamed about.",
                    "adolescent": "Menstruation is your body's natural monthly cycle. Understanding your period helps you manage it better and stay healthy.",
                    "young_adult": "Your menstrual cycle is an important part of your reproductive health. Learning about it helps you track your health and plan accordingly.",
                    "adult": "Understanding menstruation helps you manage your reproductive health and support other women in your family or community."
                },
                "hygiene_practices": {
                    "young_adolescent": "Keeping clean during your period is important for your health and comfort. Simple hygiene practices can help you feel confident.",
                    "adolescent": "Good hygiene during menstruation prevents infections and helps you feel comfortable. Regular washing and changing pads is important.",
                    "young_adult": "Proper menstrual hygiene includes regular changing of products, washing with clean water, and maintaining overall cleanliness.",
                    "adult": "Maintaining good menstrual hygiene prevents infections and promotes overall reproductive health. Clean practices are essential."
                }
            },
            "hi": {
                "body_changes": {
                    "young_adolescent": "बढ़ती उम्र में शरीर में होने वाले बदलाव बिल्कुल सामान्य हैं। यह एक प्राकृतिक प्रक्रिया है।",
                    "adolescent": "किशोरावस्था में शरीर में कई बदलाव होते हैं जैसे कि लंबाई बढ़ना और मासिक धर्म का शुरू होना। ये सभी बदलाव सामान्य हैं।",
                    "young_adult": "शरीर में होने वाले बदलावों को समझना आपकी सेहत के लिए जरूरी है। ये बदलाव प्राकृतिक विकास का हिस्सा हैं।",
                    "adult": "किशोरावस्था में होने वाले शारीरिक बदलाव प्राकृतिक विकास का हिस्सा हैं। इन्हें समझना युवा महिलाओं की मदद के लिए जरूरी है।"
                },
                "menstruation_basics": {
                    "young_adolescent": "मासिक धर्म एक प्राकृतिक प्रक्रिया है जो लड़कियों के बड़े होने पर होती है। इससे डरने या शर्म करने की कोई बात नहीं है।",
                    "adolescent": "मासिक धर्म आपके शरीर की प्राकृतिक मासिक प्रक्रिया है। इसे समझना आपको बेहतर तरीके से इसका सामना करने में मदद करता है।",
                    "young_adult": "आपका मासिक चक्र आपकी प्रजनन स्वास्थ्य का महत्वपूर्ण हिस्सा है। इसे समझना आपकी सेहत की निगरानी में मदद करता है।",
                    "adult": "मासिक धर्म को समझना आपकी प्रजनन स्वास्थ्य के लिए और परिवार की अन्य महिलाओं की मदद के लिए जरूरी है।"
                },
                "hygiene_practices": {
                    "young_adolescent": "मासिक धर्म के दौरान सफाई रखना आपकी सेहत और आराम के लिए जरूरी है। सरल स्वच्छता के तरीके आपको आत्मविश्वास दिलाते हैं।",
                    "adolescent": "मासिक धर्म के दौरान अच्छी सफाई संक्रमण से बचाती है और आपको आरामदायक महसूस कराती है। नियमित धुलाई और पैड बदलना जरूरी है।",
                    "young_adult": "उचित मासिक धर्म स्वच्छता में नियमित रूप से उत्पाद बदलना, साफ पानी से धोना और समग्र सफाई बनाए रखना शामिल है।",
                    "adult": "अच्छी मासिक धर्म स्वच्छता संक्रमण से बचाती है और समग्र प्रजनन स्वास्थ्य को बढ़ावा देती है। साफ-सुथरे तरीके जरूरी हैं।"
                }
            }
        }
        
        # Get appropriate response
        lang_responses = responses.get(language_code, responses["en"])
        topic_responses = lang_responses.get(topic, {})
        
        if age_group in topic_responses:
            return topic_responses[age_group]
        else:
            # Fallback to adolescent response
            return topic_responses.get("adolescent", "I can help you learn about this topic. Please explore the available content.")
    
    def _generate_general_response(self, query: str, language_code: str, age_group: str) -> str:
        """
        Generate a general response when specific topic cannot be determined.
        
        Args:
            query: Original user query
            language_code: Language for response
            age_group: User's age group
            
        Returns:
            General response text
        """
        general_responses = {
            "en": {
                "young_adolescent": "I'm here to help you learn about growing up and body changes. You can ask me about body changes, hygiene, or any concerns you have.",
                "adolescent": "I can help you understand puberty, menstruation, and hygiene practices. Feel free to ask about any topic you're curious about.",
                "young_adult": "I'm here to provide information about reproductive health, menstruation, and hygiene. What would you like to learn about?",
                "adult": "I can provide information about puberty education, menstrual health, and hygiene practices. How can I help you today?"
            },
            "hi": {
                "young_adolescent": "मैं आपको बढ़ती उम्र और शरीर में होने वाले बदलावों के बारे में सिखाने के लिए यहाँ हूँ। आप मुझसे शरीर के बदलाव, सफाई या किसी भी चिंता के बारे में पूछ सकती हैं।",
                "adolescent": "मैं आपको किशोरावस्था, मासिक धर्म और स्वच्छता के तरीकों के बारे में समझाने में मदद कर सकती हूँ। किसी भी विषय के बारे में बेझिझक पूछें।",
                "young_adult": "मैं प्रजनन स्वास्थ्य, मासिक धर्म और स्वच्छता के बारे में जानकारी प्रदान करने के लिए यहाँ हूँ। आप क्या जानना चाहती हैं?",
                "adult": "मैं किशोरावस्था शिक्षा, मासिक धर्म स्वास्थ्य और स्वच्छता प्रथाओं के बारे में जानकारी प्रदान कर सकती हूँ। आज मैं आपकी कैसे मदद कर सकती हूँ?"
            }
        }
        
        lang_responses = general_responses.get(language_code, general_responses["en"])
        return lang_responses.get(age_group, lang_responses["adolescent"])
    
    def _generate_emergency_response(self, emergency_result: Dict[str, Any], language_code: str) -> str:
        """
        Generate appropriate emergency response text.
        
        Args:
            emergency_result: Emergency detection result
            language_code: Language for response
            
        Returns:
            Emergency response text
        """
        emergency_responses = {
            "en": {
                "safety_threat": "I'm concerned about your safety. Please reach out to a trusted adult or call the helpline numbers I'm providing. You are not alone.",
                "medical_emergency": "This sounds like a medical concern. Please contact a healthcare provider or call emergency services immediately.",
                "mental_health_crisis": "I'm here to listen, but please reach out for professional help. Contact a counselor or call a mental health helpline.",
                "general_emergency": "If you need immediate help, please contact emergency services or a trusted adult. I'm providing helpline numbers for you."
            },
            "hi": {
                "safety_threat": "मुझे आपकी सुरक्षा की चिंता है। कृपया किसी विश्वसनीय व्यक्ति से संपर्क करें या हेल्पलाइन नंबर पर कॉल करें। आप अकेली नहीं हैं।",
                "medical_emergency": "यह एक चिकित्सा संबंधी चिंता लगती है। कृपया तुरंत किसी स्वास्थ्य सेवा प्रदाता से संपर्क करें या आपातकालीन सेवाओं को कॉल करें।",
                "mental_health_crisis": "मैं आपकी बात सुनने के लिए यहाँ हूँ, लेकिन कृपया पेशेवर मदद लें। किसी काउंसलर से संपर्क करें या मानसिक स्वास्थ्य हेल्पलाइन पर कॉल करें।",
                "general_emergency": "यदि आपको तत्काल सहायता चाहिए, तो कृपया आपातकालीन सेवाओं या किसी विश्वसनीय व्यक्ति से संपर्क करें। मैं आपके लिए हेल्पलाइन नंबर प्रदान कर रही हूँ।"
            }
        }
        
        emergency_type = emergency_result.get("emergency_type", "general_emergency")
        lang_responses = emergency_responses.get(language_code, emergency_responses["en"])
        
        return lang_responses.get(emergency_type, lang_responses["general_emergency"])
    
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
            "body_changes": ["emotional_changes", "hygiene_practices", "menstruation_basics"],
            "menstruation_basics": ["hygiene_practices", "product_usage", "cycle_tracking"],
            "hygiene_practices": ["product_usage", "menstruation_basics", "body_changes"],
            "emotional_changes": ["body_changes", "myth_busting"],
            "myth_busting": ["menstruation_basics", "emotional_changes"],
            "product_usage": ["hygiene_practices", "cycle_tracking"],
            "cycle_tracking": ["menstruation_basics", "product_usage"]
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
    
    def _generate_next_actions(self, topic: str, age_group: str) -> List[str]:
        """
        Generate suggested next actions based on topic and age group.
        
        Args:
            topic: Current topic
            age_group: User's age group
            
        Returns:
            List of suggested next actions
        """
        next_actions = {
            "body_changes": [
                "Listen to audio content about normal body development",
                "Learn about emotional changes during puberty",
                "Explore hygiene practices for growing bodies"
            ],
            "menstruation_basics": [
                "Watch video content about menstrual cycle",
                "Learn about different menstrual products",
                "Understand cycle tracking methods"
            ],
            "hygiene_practices": [
                "Learn about proper washing techniques",
                "Explore different hygiene products",
                "Understand infection prevention"
            ],
            "emotional_changes": [
                "Learn coping strategies for mood changes",
                "Understand normal emotional development",
                "Explore support resources"
            ],
            "myth_busting": [
                "Learn facts about menstruation",
                "Understand scientific explanations",
                "Share accurate information with others"
            ],
            "product_usage": [
                "Compare different menstrual products",
                "Learn proper usage techniques",
                "Understand cost and hygiene factors"
            ],
            "cycle_tracking": [
                "Learn to track your menstrual cycle",
                "Understand cycle patterns",
                "Identify when to seek medical advice"
            ]
        }
        
        return next_actions.get(topic, ["Explore related topics", "Ask specific questions", "Access multimedia content"])
    
    def _generate_cultural_notes(self, topic: str, language_code: str) -> List[str]:
        """
        Generate cultural sensitivity notes for the topic and language.
        
        Args:
            topic: Current topic
            language_code: Language code
            
        Returns:
            List of cultural sensitivity notes
        """
        cultural_notes = {
            "en": {
                "menstruation_basics": [
                    "Menstruation is a natural process, not something to be ashamed of",
                    "Cultural practices around menstruation vary, but health should always come first"
                ],
                "hygiene_practices": [
                    "Clean water and proper sanitation are essential for menstrual hygiene",
                    "Traditional practices should be evaluated for health and safety"
                ],
                "body_changes": [
                    "Body changes during puberty are normal and healthy",
                    "Every girl develops at her own pace"
                ]
            },
            "hi": {
                "menstruation_basics": [
                    "मासिक धर्म एक प्राकृतिक प्रक्रिया है, इससे शर्म करने की कोई बात नहीं",
                    "मासिक धर्म के बारे में सांस्कृतिक प्रथाएं अलग हो सकती हैं, लेकिन स्वास्थ्य हमेशा पहले आना चाहिए"
                ],
                "hygiene_practices": [
                    "मासिक धर्म स्वच्छता के लिए साफ पानी और उचित सफाई जरूरी है",
                    "पारंपरिक प्रथाओं का स्वास्थ्य और सुरक्षा के लिए मूल्यांकन करना चाहिए"
                ],
                "body_changes": [
                    "किशोरावस्था में शरीर के बदलाव सामान्य और स्वस्थ हैं",
                    "हर लड़की अपनी गति से विकसित होती है"
                ]
            }
        }
        
        lang_notes = cultural_notes.get(language_code, cultural_notes["en"])
        return lang_notes.get(topic, ["Content is culturally sensitive and health-focused"])
    
    def get_age_appropriate_topics(self, age_group: str) -> List[str]:
        """
        Get list of age-appropriate topics for a specific age group.
        
        Args:
            age_group: Age group identifier
            
        Returns:
            List of appropriate topic names for the age group
        """
        return self.AGE_APPROPRIATE_CONTENT.get(age_group, self.AVAILABLE_TOPICS)
    
    def filter_content_by_age(self, content_items: List[ContentItem], age_group: str) -> List[ContentItem]:
        """
        Filter content items based on age appropriateness.
        
        Args:
            content_items: List of content items to filter
            age_group: Age group for filtering
            
        Returns:
            List of age-appropriate content items
        """
        appropriate_topics = self.get_age_appropriate_topics(age_group)
        
        return [
            content for content in content_items
            if content.topic in appropriate_topics
        ]
    
    def get_multimedia_content(self, topic: str, language_code: str, 
                             content_type: str = "all") -> List[ContentItem]:
        """
        Get multimedia content (audio/video) for a specific topic as required by Requirement 1.5.
        
        Args:
            topic: Topic to get content for
            language_code: Language code for content
            content_type: Type of content ('audio', 'video', or 'all')
            
        Returns:
            List of multimedia content items
        """
        try:
            # Get all content for the topic
            content_result = self.get_content_by_topic(topic, language_code)
            all_content = content_result.get("content", [])
            
            # Filter by content type
            if content_type == "audio":
                multimedia_content = [c for c in all_content if c.content_type == "audio"]
            elif content_type == "video":
                multimedia_content = [c for c in all_content if c.content_type == "video"]
            else:
                multimedia_content = [c for c in all_content if c.content_type in ["audio", "video"]]
            
            self.logger.info(f"Retrieved {len(multimedia_content)} multimedia items for topic: {topic}")
            return multimedia_content
            
        except Exception as e:
            self.logger.error(f"Error retrieving multimedia content for topic {topic}: {e}")
            return []
    
    def validate_topic_safety(self, topic: str) -> Dict[str, Any]:
        """
        Validate that a topic is safe and appropriate for puberty education.
        
        Args:
            topic: Topic to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = {
                "is_safe": True,
                "is_appropriate": True,
                "warnings": [],
                "recommendations": []
            }
            
            # Check if topic is in available topics
            if topic not in self.AVAILABLE_TOPICS:
                validation_result["is_appropriate"] = False
                validation_result["warnings"].append(f"Topic '{topic}' is not available in puberty education")
                validation_result["recommendations"].append(f"Available topics: {', '.join(self.AVAILABLE_TOPICS)}")
            
            # Check for culturally sensitive terms
            topic_lower = topic.lower()
            sensitive_terms_found = [
                term for term in self.CULTURALLY_SENSITIVE_TERMS
                if term in topic_lower
            ]
            
            if sensitive_terms_found:
                validation_result["recommendations"].append(
                    "Topic contains culturally sensitive content - ensure appropriate delivery"
                )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating topic safety for {topic}: {e}")
            return {
                "is_safe": False,
                "is_appropriate": False,
                "warnings": [f"Validation error: {str(e)}"],
                "recommendations": ["Please try again or contact support"]
            }