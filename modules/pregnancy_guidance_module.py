"""
PregnancyGuidanceModule - Pregnancy guidance and maternal health education module.

This module provides comprehensive pregnancy guidance including nutrition advice,
danger sign education, appointment reminders, and emergency response for pregnancy-
related concerns. It implements Requirements 4.1, 4.2, 4.3, and 4.5.

Key Features:
- Trimester-specific nutrition guidance with locally available foods
- Danger sign detection and emergency response
- Prenatal appointment reminder system
- Medical emergency routing for pregnancy concerns
- Multi-language support for rural accessibility
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta

from modules.base_health_module import BaseHealthModule
from models.data_models import ContentItem, EmergencyContact
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class PregnancyGuidanceModule(BaseHealthModule):
    """
    Pregnancy guidance module providing maternal health education and support.
    
    This module extends BaseHealthModule to provide specialized pregnancy-related
    content including nutrition guidance, danger sign awareness, appointment
    reminders, and emergency response capabilities.
    """
    
    # Pregnancy danger signs that require immediate medical attention
    DANGER_SIGNS = [
        "severe_bleeding", "severe_headache", "blurred_vision", "high_fever",
        "severe_abdominal_pain", "persistent_vomiting", "reduced_fetal_movement",
        "water_breaking", "severe_swelling", "difficulty_breathing",
        "chest_pain", "seizures", "unconsciousness", "severe_back_pain"
    ]
    
    # Emergency pregnancy keywords
    PREGNANCY_EMERGENCY_KEYWORDS = [
        "bleeding", "blood", "pain", "contractions", "water broke", "baby not moving",
        "headache", "vision", "swelling", "fever", "vomiting", "dizzy", "faint"
    ]
    
    # Nutrition categories by trimester
    NUTRITION_CATEGORIES = {
        "first_trimester": [
            "folic_acid_foods", "iron_rich_foods", "calcium_sources", 
            "protein_foods", "hydration", "morning_sickness_foods"
        ],
        "second_trimester": [
            "iron_rich_foods", "calcium_sources", "protein_foods", 
            "fiber_foods", "healthy_weight_gain", "vitamin_d_sources"
        ],
        "third_trimester": [
            "iron_rich_foods", "calcium_sources", "protein_foods",
            "small_frequent_meals", "labor_preparation_foods", "breastfeeding_prep"
        ]
    }
    
    # Appointment types and schedules
    APPOINTMENT_SCHEDULE = {
        "first_trimester": [
            {"week": 6, "type": "initial_checkup", "priority": "high"},
            {"week": 10, "type": "routine_checkup", "priority": "medium"},
            {"week": 12, "type": "first_ultrasound", "priority": "high"}
        ],
        "second_trimester": [
            {"week": 16, "type": "routine_checkup", "priority": "medium"},
            {"week": 20, "type": "anatomy_scan", "priority": "high"},
            {"week": 24, "type": "glucose_screening", "priority": "high"}
        ],
        "third_trimester": [
            {"week": 28, "type": "routine_checkup", "priority": "medium"},
            {"week": 32, "type": "routine_checkup", "priority": "medium"},
            {"week": 36, "type": "weekly_checkups", "priority": "high"},
            {"week": 40, "type": "delivery_preparation", "priority": "high"}
        ]
    }
    
    def __init__(self, content_manager: ContentManager, session_manager: SessionManager):
        """
        Initialize the pregnancy guidance module.
        
        Args:
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
        """
        super().__init__(
            module_name="pregnancy_guidance",
            content_manager=content_manager,
            session_manager=session_manager
        )
        
        # Initialize reminder system cache
        self._reminder_cache = {}
        
        self.logger.info("PregnancyGuidanceModule initialized successfully")
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve pregnancy-related content for a specific topic.
        
        Args:
            topic: Specific pregnancy topic (e.g., 'nutrition_first_trimester', 'danger_signs')
            language_code: Language code for content localization
            session_id: Optional session ID for personalization
            
        Returns:
            Dictionary containing content and safety information
        """
        try:
            self.logger.info(f"Retrieving pregnancy content for topic: {topic}, language: {language_code}")
            
            # Get base content from content manager
            content_items = self.content_manager.get_module_content(
                module_name=self.module_name,
                language_code=language_code
            )
            
            # Filter content by topic
            topic_content = []
            for item in content_items.get("content", []):
                if isinstance(item, ContentItem) and topic.lower() in item.topic.lower():
                    topic_content.append(item)
            
            # If no direct match, try to find related content
            if not topic_content:
                topic_content = self._get_related_content(topic, content_items.get("content", []))
            
            # Validate content safety
            safety_result = self.validate_content_safety(topic_content)
            
            # Check for emergency situations
            emergency_detected = self._detect_pregnancy_emergency(topic)
            
            result = {
                "content": topic_content,
                "safety_validated": safety_result["is_safe"],
                "emergency_detected": emergency_detected,
                "language_used": language_code,
                "recommendations": self._get_topic_recommendations(topic, language_code),
                "medical_flags": safety_result.get("medical_flags", []),
                "emergency_flags": safety_result.get("emergency_flags", [])
            }
            
            # Add emergency contacts if emergency detected
            if emergency_detected:
                result["emergency_contacts"] = self.get_emergency_resources(language_code)
                result["immediate_actions"] = self._get_emergency_actions(topic, language_code)
            
            # Add personalized content if session provided
            if session_id:
                result.update(self._add_personalized_content(session_id, topic, language_code))
            
            self.logger.info(f"Retrieved {len(topic_content)} content items for topic: {topic}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error retrieving pregnancy content for topic {topic}: {e}")
            return {
                "content": [],
                "safety_validated": False,
                "emergency_detected": True,  # Err on side of caution
                "language_used": language_code,
                "recommendations": ["Please consult healthcare provider"],
                "error": str(e),
                "emergency_contacts": self.get_emergency_resources(language_code)
            }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to pregnancy-related user queries.
        
        Args:
            query: User's pregnancy-related question or concern
            language_code: Language code for response
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing response and relevant content
        """
        try:
            self.logger.info(f"Processing pregnancy query: {query[:50]}...")
            
            query_lower = query.lower()
            
            # Detect emergency situations first
            emergency_result = self.detect_emergency_situation(query)
            if emergency_result["is_emergency"]:
                return self._handle_emergency_query(query, language_code, emergency_result)
            
            # Detect pregnancy-specific emergencies
            pregnancy_emergency = self._detect_pregnancy_emergency_in_query(query)
            if pregnancy_emergency:
                return self._handle_pregnancy_emergency(query, language_code, pregnancy_emergency)
            
            # Categorize query type
            query_type = self._categorize_pregnancy_query(query)
            
            # Get relevant content based on query type
            relevant_content = []
            response_text = ""
            
            if query_type == "nutrition":
                relevant_content, response_text = self._handle_nutrition_query(query, language_code)
            elif query_type == "danger_signs":
                relevant_content, response_text = self._handle_danger_signs_query(query, language_code)
            elif query_type == "appointments":
                relevant_content, response_text = self._handle_appointment_query(query, language_code, session_id)
            elif query_type == "trimester_info":
                relevant_content, response_text = self._handle_trimester_query(query, language_code)
            else:
                # General pregnancy query
                relevant_content, response_text = self._handle_general_query(query, language_code)
            
            # Validate content safety
            safety_result = self.validate_content_safety(relevant_content)
            
            result = {
                "response": response_text,
                "content_items": relevant_content,
                "emergency_detected": False,
                "safety_warnings": safety_result.get("recommendations", []),
                "next_actions": self._get_next_actions(query_type, language_code),
                "query_type": query_type,
                "requires_medical_referral": safety_result.get("requires_medical_referral", False)
            }
            
            # Update session context if provided
            if session_id:
                self.update_session_context(session_id, {
                    "query": query,
                    "query_type": query_type,
                    "response": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            self.logger.info(f"Processed pregnancy query successfully, type: {query_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling pregnancy query: {e}")
            return {
                "response": "I'm sorry, I encountered an error. Please consult your healthcare provider for pregnancy concerns.",
                "content_items": [],
                "emergency_detected": True,
                "safety_warnings": ["System error occurred"],
                "next_actions": ["Contact healthcare provider"],
                "error": str(e),
                "emergency_contacts": self.get_emergency_resources(language_code)
            }
    
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available pregnancy guidance topics.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        try:
            # Base topics available in pregnancy guidance
            base_topics = [
                "nutrition_first_trimester",
                "nutrition_second_trimester", 
                "nutrition_third_trimester",
                "danger_signs",
                "prenatal_appointments",
                "emergency_situations",
                "healthy_weight_gain",
                "exercise_during_pregnancy",
                "common_discomforts",
                "labor_preparation",
                "breastfeeding_preparation",
                "postpartum_care"
            ]
            
            # Get localized topic names if available
            try:
                content_items = self.content_manager.get_module_content(
                    module_name=self.module_name,
                    language_code=language_code
                )
                
                # Extract unique topics from available content
                available_topics = set()
                for item in content_items.get("content", []):
                    if isinstance(item, ContentItem):
                        available_topics.add(item.topic)
                
                # Combine base topics with available content topics
                all_topics = list(set(base_topics + list(available_topics)))
                
            except Exception as e:
                self.logger.warning(f"Could not retrieve content topics: {e}")
                all_topics = base_topics
            
            self.logger.info(f"Retrieved {len(all_topics)} pregnancy topics for language: {language_code}")
            return sorted(all_topics)
            
        except Exception as e:
            self.logger.error(f"Error getting pregnancy module topics: {e}")
            return [
                "nutrition_guidance",
                "danger_signs", 
                "prenatal_appointments",
                "emergency_situations"
            ]
    
    def get_nutrition_guidance(self, trimester: str, language_code: str) -> Dict[str, Any]:
        """
        Get trimester-specific nutrition guidance.
        
        Args:
            trimester: Pregnancy trimester ('first', 'second', 'third')
            language_code: Language code for guidance
            
        Returns:
            Dictionary containing nutrition guidance and recommendations
        """
        try:
            trimester_key = f"{trimester}_trimester"
            
            if trimester_key not in self.NUTRITION_CATEGORIES:
                raise ValueError(f"Invalid trimester: {trimester}")
            
            # Get nutrition content for the trimester
            nutrition_content = self.get_content_by_topic(
                f"nutrition_{trimester_key}",
                language_code
            )
            
            # Add specific nutrition recommendations
            nutrition_categories = self.NUTRITION_CATEGORIES[trimester_key]
            
            guidance = {
                "trimester": trimester,
                "content": nutrition_content.get("content", []),
                "categories": nutrition_categories,
                "local_foods": self._get_local_food_recommendations(trimester, language_code),
                "daily_requirements": self._get_daily_requirements(trimester),
                "foods_to_avoid": self._get_foods_to_avoid(language_code),
                "meal_planning": self._get_meal_planning_tips(trimester, language_code)
            }
            
            self.logger.info(f"Generated nutrition guidance for {trimester} trimester")
            return guidance
            
        except Exception as e:
            self.logger.error(f"Error getting nutrition guidance for {trimester}: {e}")
            return {
                "trimester": trimester,
                "content": [],
                "error": str(e),
                "emergency_contacts": self.get_emergency_resources(language_code)
            }
    
    def create_appointment_reminder(self, session_id: str, appointment_type: str, 
                                  appointment_date: datetime, language_code: str) -> Dict[str, Any]:
        """
        Create a reminder for prenatal appointments.
        
        Args:
            session_id: User session ID
            appointment_type: Type of appointment (e.g., 'routine_checkup', 'ultrasound')
            appointment_date: Date and time of appointment
            language_code: Language for reminder messages
            
        Returns:
            Dictionary containing reminder information and status
        """
        try:
            # Generate unique reminder ID
            reminder_id = f"preg_reminder_{session_id}_{int(appointment_date.timestamp())}"
            
            # Calculate reminder times (1 day before, 2 hours before)
            reminder_times = [
                appointment_date - timedelta(days=1),
                appointment_date - timedelta(hours=2)
            ]
            
            # Create reminder data
            reminder_data = {
                "reminder_id": reminder_id,
                "session_id": session_id,
                "appointment_type": appointment_type,
                "appointment_date": appointment_date.isoformat(),
                "language_code": language_code,
                "reminder_times": [rt.isoformat() for rt in reminder_times],
                "status": "scheduled",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "messages": self._generate_reminder_messages(appointment_type, language_code)
            }
            
            # Store reminder in cache (in production, this would be stored in database)
            self._reminder_cache[reminder_id] = reminder_data
            
            # Update session with reminder information
            if session_id:
                self.update_session_context(session_id, {
                    "reminder_created": reminder_id,
                    "appointment_type": appointment_type,
                    "appointment_date": appointment_date.isoformat()
                })
            
            result = {
                "reminder_id": reminder_id,
                "status": "created",
                "appointment_date": appointment_date.isoformat(),
                "reminder_times": [rt.isoformat() for rt in reminder_times],
                "messages": reminder_data["messages"]
            }
            
            self.logger.info(f"Created appointment reminder: {reminder_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating appointment reminder: {e}")
            return {
                "status": "error",
                "error": str(e),
                "recommendation": "Please set a manual reminder for your appointment"
            }
    
    def get_danger_sign_guidance(self, language_code: str) -> Dict[str, Any]:
        """
        Get comprehensive danger sign education and guidance.
        
        Args:
            language_code: Language code for guidance
            
        Returns:
            Dictionary containing danger sign information and emergency actions
        """
        try:
            # Get danger signs content
            danger_content = self.get_content_by_topic("danger_signs", language_code)
            
            # Organize danger signs by severity
            danger_signs_info = {
                "immediate_emergency": [
                    "severe_bleeding", "seizures", "unconsciousness", 
                    "severe_difficulty_breathing", "chest_pain"
                ],
                "urgent_medical_attention": [
                    "severe_headache", "blurred_vision", "high_fever",
                    "severe_abdominal_pain", "water_breaking_early"
                ],
                "monitor_and_contact_provider": [
                    "reduced_fetal_movement", "persistent_vomiting",
                    "severe_swelling", "severe_back_pain"
                ]
            }
            
            guidance = {
                "content": danger_content.get("content", []),
                "danger_signs": danger_signs_info,
                "emergency_actions": self._get_danger_sign_actions(language_code),
                "emergency_contacts": self.get_emergency_resources(language_code),
                "when_to_call": self._get_when_to_call_guidance(language_code)
            }
            
            self.logger.info("Generated danger sign guidance")
            return guidance
            
        except Exception as e:
            self.logger.error(f"Error getting danger sign guidance: {e}")
            return {
                "content": [],
                "error": str(e),
                "emergency_contacts": self.get_emergency_resources(language_code),
                "immediate_action": "Contact healthcare provider immediately for any concerning symptoms"
            }
    
    def _get_related_content(self, topic: str, all_content: List[ContentItem]) -> List[ContentItem]:
        """Find content related to the requested topic."""
        related_content = []
        topic_keywords = topic.lower().split('_')
        
        for item in all_content:
            if isinstance(item, ContentItem):
                item_topic_lower = item.topic.lower()
                # Check if any topic keyword appears in the content topic
                if any(keyword in item_topic_lower for keyword in topic_keywords):
                    related_content.append(item)
        
        return related_content
    
    def _detect_pregnancy_emergency(self, topic: str) -> bool:
        """Detect if topic indicates a pregnancy emergency."""
        topic_lower = topic.lower()
        return any(keyword in topic_lower for keyword in self.PREGNANCY_EMERGENCY_KEYWORDS)
    
    def _detect_pregnancy_emergency_in_query(self, query: str) -> Optional[str]:
        """Detect pregnancy emergency in user query."""
        query_lower = query.lower()
        
        for keyword in self.PREGNANCY_EMERGENCY_KEYWORDS:
            if keyword in query_lower:
                return keyword
        
        return None
    
    def _categorize_pregnancy_query(self, query: str) -> str:
        """Categorize the type of pregnancy query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["nutrition", "food", "eat", "diet", "vitamin"]):
            return "nutrition"
        elif any(word in query_lower for word in ["danger", "warning", "emergency", "symptom"]):
            return "danger_signs"
        elif any(word in query_lower for word in ["appointment", "checkup", "visit", "doctor"]):
            return "appointments"
        elif any(word in query_lower for word in ["trimester", "month", "week", "stage"]):
            return "trimester_info"
        else:
            return "general"
    
    def _handle_nutrition_query(self, query: str, language_code: str) -> tuple:
        """Handle nutrition-related queries."""
        # Determine trimester if mentioned
        trimester = "general"
        if "first" in query.lower():
            trimester = "first"
        elif "second" in query.lower():
            trimester = "second"
        elif "third" in query.lower():
            trimester = "third"
        
        content = self.get_content_by_topic(f"nutrition_{trimester}_trimester", language_code)
        
        response = f"Here's nutrition guidance for pregnancy"
        if trimester != "general":
            response += f" during the {trimester} trimester"
        response += ". Focus on iron-rich foods, calcium sources, and adequate protein."
        
        return content.get("content", []), response
    
    def _handle_danger_signs_query(self, query: str, language_code: str) -> tuple:
        """Handle danger signs queries."""
        content = self.get_content_by_topic("danger_signs", language_code)
        
        response = ("Important pregnancy danger signs include severe bleeding, severe headache, "
                   "blurred vision, high fever, and reduced fetal movement. "
                   "Contact your healthcare provider immediately if you experience any of these.")
        
        return content.get("content", []), response
    
    def _handle_appointment_query(self, query: str, language_code: str, session_id: Optional[str]) -> tuple:
        """Handle appointment-related queries."""
        content = self.get_content_by_topic("prenatal_appointments", language_code)
        
        response = ("Regular prenatal appointments are crucial for monitoring your health and baby's development. "
                   "Schedule checkups as recommended by your healthcare provider.")
        
        return content.get("content", []), response
    
    def _handle_trimester_query(self, query: str, language_code: str) -> tuple:
        """Handle trimester-specific queries."""
        # Determine which trimester
        trimester = "first"
        if "second" in query.lower():
            trimester = "second"
        elif "third" in query.lower():
            trimester = "third"
        
        content = self.get_content_by_topic(f"{trimester}_trimester_info", language_code)
        
        response = f"Here's information about the {trimester} trimester of pregnancy."
        
        return content.get("content", []), response
    
    def _handle_general_query(self, query: str, language_code: str) -> tuple:
        """Handle general pregnancy queries."""
        content = self.get_content_by_topic("general_pregnancy_info", language_code)
        
        response = ("I'm here to help with pregnancy guidance. You can ask about nutrition, "
                   "danger signs, appointments, or general pregnancy information.")
        
        return content.get("content", []), response
    
    def _handle_emergency_query(self, query: str, language_code: str, emergency_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency pregnancy queries."""
        return {
            "response": "This appears to be an emergency situation. Please seek immediate medical attention.",
            "content_items": [],
            "emergency_detected": True,
            "safety_warnings": ["Emergency situation detected"],
            "next_actions": emergency_result.get("immediate_actions", []),
            "emergency_contacts": self.get_emergency_resources(language_code),
            "immediate_action_required": True
        }
    
    def _handle_pregnancy_emergency(self, query: str, language_code: str, emergency_keyword: str) -> Dict[str, Any]:
        """Handle pregnancy-specific emergencies."""
        emergency_actions = {
            "bleeding": "Call emergency services immediately. Do not drive yourself to hospital.",
            "pain": "Severe pain during pregnancy requires immediate medical attention.",
            "contractions": "If contractions are regular and strong, you may be in labor.",
            "water broke": "Your water breaking means labor may be starting. Contact your healthcare provider.",
            "baby not moving": "Reduced fetal movement requires immediate medical evaluation."
        }
        
        action = emergency_actions.get(emergency_keyword, "Contact healthcare provider immediately.")
        
        return {
            "response": f"Pregnancy emergency detected: {emergency_keyword}. {action}",
            "content_items": [],
            "emergency_detected": True,
            "safety_warnings": [f"Pregnancy emergency: {emergency_keyword}"],
            "next_actions": ["Call emergency services", "Contact healthcare provider"],
            "emergency_contacts": self.get_emergency_resources(language_code),
            "immediate_action_required": True
        }
    
    def _get_topic_recommendations(self, topic: str, language_code: str) -> List[str]:
        """Get recommendations based on topic."""
        recommendations = {
            "nutrition": [
                "Eat iron-rich foods like leafy greens and lentils",
                "Include calcium sources like dairy and sesame seeds",
                "Stay hydrated with plenty of water"
            ],
            "danger_signs": [
                "Learn to recognize warning signs",
                "Keep emergency contacts readily available",
                "Don't hesitate to contact healthcare provider"
            ],
            "appointments": [
                "Keep all scheduled appointments",
                "Prepare questions for your healthcare provider",
                "Bring your pregnancy records to appointments"
            ]
        }
        
        return recommendations.get(topic, ["Consult your healthcare provider for personalized guidance"])
    
    def _get_next_actions(self, query_type: str, language_code: str) -> List[str]:
        """Get suggested next actions based on query type."""
        actions = {
            "nutrition": [
                "Plan balanced meals with local foods",
                "Take prescribed prenatal vitamins",
                "Monitor weight gain"
            ],
            "danger_signs": [
                "Review danger signs regularly",
                "Keep emergency contacts handy",
                "Trust your instincts about symptoms"
            ],
            "appointments": [
                "Schedule next appointment",
                "Set appointment reminders",
                "Prepare questions for provider"
            ]
        }
        
        return actions.get(query_type, ["Continue regular prenatal care"])
    
    def _add_personalized_content(self, session_id: str, topic: str, language_code: str) -> Dict[str, Any]:
        """Add personalized content based on session history."""
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return {}
            
            # Add personalization based on session data
            personalization = {
                "personalized": True,
                "session_context": {
                    "language_preference": session.language_preference,
                    "previous_topics": [
                        interaction.get("data", {}).get("query_type", "")
                        for interaction in session.interaction_history[-5:]  # Last 5 interactions
                    ]
                }
            }
            
            return personalization
            
        except Exception as e:
            self.logger.warning(f"Could not add personalized content: {e}")
            return {}
    
    def _get_local_food_recommendations(self, trimester: str, language_code: str) -> List[str]:
        """Get locally available food recommendations."""
        local_foods = {
            "first": [
                "Green leafy vegetables (palak, methi)",
                "Lentils and pulses (dal, rajma)",
                "Citrus fruits (orange, lemon)",
                "Whole grains (brown rice, wheat)"
            ],
            "second": [
                "Milk and dairy products",
                "Sesame seeds (til)",
                "Fish (if non-vegetarian)",
                "Nuts and seeds"
            ],
            "third": [
                "Iron-rich foods (jaggery, dates)",
                "Small frequent meals",
                "Fiber-rich foods",
                "Adequate fluids"
            ]
        }
        
        return local_foods.get(trimester, local_foods["first"])
    
    def _get_daily_requirements(self, trimester: str) -> Dict[str, str]:
        """Get daily nutritional requirements by trimester."""
        requirements = {
            "first": {
                "calories": "Additional 150-200 calories",
                "protein": "60-70 grams",
                "iron": "27 mg",
                "folic_acid": "600 mcg",
                "calcium": "1000 mg"
            },
            "second": {
                "calories": "Additional 300-350 calories", 
                "protein": "70-80 grams",
                "iron": "27 mg",
                "calcium": "1000 mg",
                "vitamin_d": "600 IU"
            },
            "third": {
                "calories": "Additional 400-450 calories",
                "protein": "80-90 grams", 
                "iron": "27 mg",
                "calcium": "1000 mg",
                "fiber": "25-30 grams"
            }
        }
        
        return requirements.get(trimester, requirements["first"])
    
    def _get_foods_to_avoid(self, language_code: str) -> List[str]:
        """Get list of foods to avoid during pregnancy."""
        return [
            "Raw or undercooked meat and eggs",
            "Unpasteurized dairy products",
            "High mercury fish",
            "Excessive caffeine",
            "Alcohol",
            "Raw sprouts",
            "Unwashed fruits and vegetables"
        ]
    
    def _get_meal_planning_tips(self, trimester: str, language_code: str) -> List[str]:
        """Get meal planning tips for the trimester."""
        tips = {
            "first": [
                "Eat small, frequent meals to manage nausea",
                "Keep crackers handy for morning sickness",
                "Focus on foods you can tolerate"
            ],
            "second": [
                "Establish regular meal times",
                "Include variety in your diet",
                "Plan balanced meals with all food groups"
            ],
            "third": [
                "Eat smaller, more frequent meals",
                "Avoid lying down immediately after eating",
                "Stay hydrated throughout the day"
            ]
        }
        
        return tips.get(trimester, tips["first"])
    
    def _generate_reminder_messages(self, appointment_type: str, language_code: str) -> Dict[str, str]:
        """Generate reminder messages for appointments."""
        messages = {
            "en": {
                "routine_checkup": "Reminder: You have a routine prenatal checkup scheduled.",
                "ultrasound": "Reminder: You have an ultrasound appointment scheduled.",
                "glucose_screening": "Reminder: You have glucose screening scheduled. Follow fasting instructions.",
                "anatomy_scan": "Reminder: You have an anatomy scan scheduled."
            },
            "hi": {
                "routine_checkup": "अनुस्मारक: आपकी नियमित प्रसवपूर्व जांच निर्धारित है।",
                "ultrasound": "अनुस्मारक: आपका अल्ट्रासाउंड अपॉइंटमेंट निर्धारित है।",
                "glucose_screening": "अनुस्मारक: आपकी ग्लूकोज जांच निर्धारित है।",
                "anatomy_scan": "अनुस्मारक: आपका एनाटॉमी स्कैन निर्धारित है।"
            }
        }
        
        lang_messages = messages.get(language_code, messages["en"])
        return {
            "day_before": lang_messages.get(appointment_type, "You have a prenatal appointment tomorrow."),
            "two_hours_before": lang_messages.get(appointment_type, "Your prenatal appointment is in 2 hours.")
        }
    
    def _get_danger_sign_actions(self, language_code: str) -> Dict[str, List[str]]:
        """Get actions to take for different danger signs."""
        return {
            "severe_bleeding": [
                "Call emergency services immediately (108)",
                "Do not drive yourself",
                "Lie down and elevate legs if possible"
            ],
            "severe_headache": [
                "Contact healthcare provider immediately",
                "Monitor blood pressure if possible",
                "Rest in a quiet, dark room"
            ],
            "reduced_fetal_movement": [
                "Try drinking cold water and lying on left side",
                "Count fetal movements for 1 hour",
                "Contact provider if less than 10 movements in 2 hours"
            ]
        }
    
    def _get_when_to_call_guidance(self, language_code: str) -> Dict[str, str]:
        """Get guidance on when to call healthcare provider."""
        return {
            "immediately": "Severe bleeding, severe headache with vision changes, seizures, difficulty breathing",
            "same_day": "Persistent vomiting, high fever, severe abdominal pain, signs of infection",
            "within_24_hours": "Reduced fetal movement, unusual swelling, persistent back pain",
            "next_appointment": "Mild discomforts, general questions, routine concerns"
        }
    
    def _get_emergency_actions(self, topic: str, language_code: str) -> List[str]:
        """Get emergency actions based on topic."""
        if "bleeding" in topic.lower():
            return [
                "Call 108 immediately",
                "Do not drive yourself to hospital",
                "Lie down and elevate legs"
            ]
        elif "pain" in topic.lower():
            return [
                "Contact healthcare provider immediately",
                "Note pain location and intensity",
                "Avoid taking pain medication without consulting provider"
            ]
        else:
            return [
                "Contact healthcare provider immediately",
                "Call emergency services if severe",
                "Do not wait if symptoms worsen"
            ]