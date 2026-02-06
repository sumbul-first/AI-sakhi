"""
MenstrualGuideModule - Specialized health education module for menstrual product guidance and selection.

This module provides comprehensive menstrual product comparison and selection guidance
covering pads, cups, and cloth options with cost and hygiene information as required by
Requirements 3.1, 3.2, and 3.5. It implements personalized recommendation filtering
based on user preferences and circumstances.

Key Features:
- Product comparison system for pads, cups, and cloth options
- Cost analysis and hygiene information for each product type
- Personalized recommendation engine based on user preferences
- Multi-language support for product information
- Budget-based filtering and lifestyle considerations
- Safety and hygiene guidance for each product type
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from modules.base_health_module import BaseHealthModule
from models.data_models import ContentItem, UserSession
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class MenstrualGuideModule(BaseHealthModule):
    """
    Specialized health education module for menstrual product guidance and selection.
    
    This module provides comprehensive education about menstrual product options,
    cost analysis, and personalized recommendations as required by Requirements
    3.1, 3.2, and 3.5.
    
    Topics covered:
    - Product comparison (pads, cups, cloth options)
    - Cost analysis and budget considerations
    - Hygiene information for each product type
    - Personalized recommendations based on preferences
    - Product usage and care instructions
    - Environmental impact considerations
    """
    
    # Available topics in the menstrual guide module
    AVAILABLE_TOPICS = [
        "product_comparison",
        "cost_analysis",
        "hygiene_information",
        "personalized_recommendations",
        "product_usage",
        "environmental_impact",
        "budget_options",
        "product_care"
    ]
    
    # Menstrual product types with detailed information
    PRODUCT_TYPES = {
        "pads": {
            "name": "Sanitary Pads",
            "cost_range": {"low": 20, "high": 150},  # INR per month
            "duration": "4-6 hours",
            "pros": ["Easy to use", "Widely available", "No insertion required"],
            "cons": ["Monthly cost", "Environmental impact", "Bulk to carry"],
            "hygiene_score": 8,
            "comfort_score": 7,
            "convenience_score": 9
        },
        "cups": {
            "name": "Menstrual Cups",
            "cost_range": {"low": 300, "high": 2000},  # INR one-time cost
            "duration": "Up to 12 hours",
            "pros": ["Cost-effective long-term", "Eco-friendly", "Long wear time"],
            "cons": ["Learning curve", "Initial cost", "Requires sterilization"],
            "hygiene_score": 9,
            "comfort_score": 8,
            "convenience_score": 6
        },
        "cloth": {
            "name": "Cloth Pads",
            "cost_range": {"low": 100, "high": 800},  # INR one-time cost
            "duration": "4-6 hours",
            "pros": ["Reusable", "Natural materials", "Cost-effective"],
            "cons": ["Washing required", "Drying time", "Staining possible"],
            "hygiene_score": 7,
            "comfort_score": 8,
            "convenience_score": 5
        }
    }
    
    # User preference categories for recommendations
    PREFERENCE_CATEGORIES = {
        "budget": ["low", "medium", "high"],
        "lifestyle": ["active", "sedentary", "mixed"],
        "experience": ["beginner", "intermediate", "experienced"],
        "priorities": ["cost", "convenience", "environment", "comfort"],
        "flow": ["light", "medium", "heavy"],
        "age_group": ["young_adolescent", "adolescent", "young_adult", "adult"]
    }
    
    # Recommendation scoring weights
    SCORING_WEIGHTS = {
        "cost": 0.3,
        "hygiene": 0.25,
        "comfort": 0.2,
        "convenience": 0.15,
        "environmental": 0.1
    }

    def __init__(self, content_manager: ContentManager, session_manager: SessionManager):
        """
        Initialize the MenstrualGuideModule.
        
        Args:
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
            
        Raises:
            ValueError: If required parameters are invalid
        """
        super().__init__(
            module_name="menstrual_guide",
            content_manager=content_manager,
            session_manager=session_manager
        )
        
        self.logger.info("MenstrualGuideModule initialized successfully")
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content for a specific menstrual guide topic.
        
        This method implements topic-specific content retrieval with personalized
        filtering as required by Requirements 3.1, 3.2, and 3.5.
        
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
            - product_info: Detailed product information if applicable
            - cost_analysis: Cost comparison data if applicable
            - personalized_suggestions: User-specific recommendations
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
                    "product_info": {},
                    "cost_analysis": {},
                    "personalized_suggestions": [],
                    "error": f"Topic '{topic}' not available in menstrual guide module"
                }
            
            # Get user preferences for personalization
            user_preferences = {}
            if session_id:
                session = self.session_manager.get_session(session_id)
                if session and session.accessibility_preferences:
                    user_preferences = session.accessibility_preferences.get("menstrual_preferences", {})
            
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
            
            # Generate topic-specific information
            product_info = self._get_product_information(topic, language_code)
            cost_analysis = self._generate_cost_analysis(topic, user_preferences)
            personalized_suggestions = self._generate_personalized_suggestions(topic, user_preferences, language_code)
            
            # Generate recommendations for related topics
            recommendations = self._generate_topic_recommendations(topic, user_preferences)
            
            # Update session context if session provided
            if session_id:
                self.update_session_context(session_id, {
                    "topic": topic,
                    "language": language_code,
                    "content_count": len(topic_content),
                    "user_preferences": user_preferences
                })
            
            result = {
                "content": topic_content,
                "safety_validated": safety_result["is_safe"],
                "emergency_detected": bool(safety_result["emergency_flags"]),
                "language_used": content_result["language_used"],
                "recommendations": recommendations,
                "product_info": product_info,
                "cost_analysis": cost_analysis,
                "personalized_suggestions": personalized_suggestions,
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
                "product_info": {},
                "cost_analysis": {},
                "personalized_suggestions": [],
                "error": str(e)
            }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to a user query about menstrual products.
        
        This method implements natural language query processing for menstrual product
        questions with personalized recommendations as required by Requirements 3.1, 3.2, and 3.5.
        
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
            - product_recommendations: List of recommended products
            - cost_information: Cost analysis based on query
        """
        try:
            if not query or not isinstance(query, str):
                return {
                    "response": "I can help you choose the right menstrual products. Ask me about pads, cups, cloth options, or cost comparisons.",
                    "content_items": [],
                    "emergency_detected": False,
                    "safety_warnings": [],
                    "next_actions": ["Ask about product comparison", "Tell me your budget", "Share your preferences"],
                    "product_recommendations": [],
                    "cost_information": {}
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
                    "product_recommendations": [],
                    "cost_information": {}
                }
            
            # Analyze query to determine relevant topic and extract preferences
            detected_topic = self._analyze_query_for_topic(query)
            extracted_preferences = self._extract_preferences_from_query(query)
            
            # Get user preferences from session
            user_preferences = {}
            if session_id:
                session = self.session_manager.get_session(session_id)
                if session and session.accessibility_preferences:
                    user_preferences = session.accessibility_preferences.get("menstrual_preferences", {})
                
                # Update preferences with extracted information
                user_preferences.update(extracted_preferences)
                
                # Save updated preferences back to session
                if extracted_preferences:
                    self._update_user_preferences(session_id, user_preferences)
            
            # Generate response based on detected topic
            if detected_topic:
                # Get content for the detected topic
                content_result = self.get_content_by_topic(detected_topic, language_code, session_id)
                
                # Generate contextual response
                response_text = self._generate_contextual_response(
                    query, detected_topic, language_code, user_preferences
                )
                
                # Get related content items
                content_items = content_result.get("content", [])
                
                # Generate product recommendations
                product_recommendations = self._generate_product_recommendations(user_preferences, language_code)
                
                # Get cost information
                cost_information = content_result.get("cost_analysis", {})
                
                # Generate next actions
                next_actions = self._generate_next_actions(detected_topic, user_preferences)
                
            else:
                # General response when topic cannot be determined
                response_text = self._generate_general_response(query, language_code, user_preferences)
                content_items = []
                product_recommendations = self._generate_product_recommendations(user_preferences, language_code)
                cost_information = {}
                next_actions = ["Tell me about your budget", "Ask about specific products", "Share your lifestyle preferences"]
            
            # Update session context
            if session_id:
                self.update_session_context(session_id, {
                    "query": query,
                    "detected_topic": detected_topic,
                    "extracted_preferences": extracted_preferences,
                    "response_generated": True,
                    "language": language_code
                })
            
            result = {
                "response": response_text,
                "content_items": content_items,
                "emergency_detected": emergency_result["is_emergency"],
                "safety_warnings": [],
                "next_actions": next_actions,
                "product_recommendations": product_recommendations,
                "cost_information": cost_information,
                "detected_topic": detected_topic,
                "user_preferences": user_preferences
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
                "product_recommendations": [],
                "cost_information": {},
                "error": str(e)
            }
    
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available topics for menstrual guide module.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        try:
            # Return localized topic names if available, otherwise return English names
            if language_code == "hi":
                return [
                    "उत्पाद तुलना",           # product_comparison
                    "लागत विश्लेषण",         # cost_analysis
                    "स्वच्छता की जानकारी",    # hygiene_information
                    "व्यक्तिगत सुझाव",       # personalized_recommendations
                    "उत्पाद का उपयोग",       # product_usage
                    "पर्यावरणीय प्रभाव",      # environmental_impact
                    "बजट विकल्प",           # budget_options
                    "उत्पाद की देखभाल"       # product_care
                ]
            elif language_code == "bn":
                return [
                    "পণ্য তুলনা",            # product_comparison
                    "খরচ বিশ্লেষণ",          # cost_analysis
                    "স্বচ্ছতার তথ্য",        # hygiene_information
                    "ব্যক্তিগত সুপারিশ",      # personalized_recommendations
                    "পণ্যের ব্যবহার",        # product_usage
                    "পরিবেশগত প্রভাব",       # environmental_impact
                    "বাজেট বিকল্প",         # budget_options
                    "পণ্যের যত্ন"           # product_care
                ]
            else:
                # Default English topic names
                return [
                    "Product Comparison",
                    "Cost Analysis",
                    "Hygiene Information",
                    "Personalized Recommendations",
                    "Product Usage",
                    "Environmental Impact",
                    "Budget Options",
                    "Product Care"
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
            "product_comparison": ["compare", "difference", "which", "better", "pads", "cups", "cloth", "options", "तुलना", "विकल्प"],
            "cost_analysis": ["cost", "price", "expensive", "cheap", "budget", "money", "afford", "लागत", "कीमत", "बजट"],
            "hygiene_information": ["hygiene", "clean", "safe", "infection", "health", "स्वच्छता", "सफाई", "स्वास्थ्य"],
            "personalized_recommendations": ["recommend", "suggest", "best", "suitable", "right", "सुझाव", "सिफारिश", "उपयुक्त"],
            "product_usage": ["how", "use", "wear", "insert", "instructions", "कैसे", "उपयोग", "इस्तेमाल"],
            "environmental_impact": ["environment", "eco", "green", "sustainable", "waste", "पर्यावरण", "प्राकृतिक"],
            "budget_options": ["cheap", "affordable", "low cost", "budget", "सस्ता", "किफायती", "कम कीमत"],
            "product_care": ["care", "maintain", "wash", "clean", "store", "देखभाल", "धोना", "साफ करना"]
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
    
    def _extract_preferences_from_query(self, query: str) -> Dict[str, Any]:
        """
        Extract user preferences from query text.
        
        Args:
            query: User's query text
            
        Returns:
            Dictionary of extracted preferences
        """
        query_lower = query.lower()
        preferences = {}
        
        # Budget preferences
        if any(word in query_lower for word in ["cheap", "affordable", "low cost", "budget", "सस्ता", "किफायती"]):
            preferences["budget"] = "low"
        elif any(word in query_lower for word in ["expensive", "premium", "high quality", "महंगा", "उच्च गुणवत्ता"]):
            preferences["budget"] = "high"
        elif any(word in query_lower for word in ["medium", "moderate", "मध्यम"]):
            preferences["budget"] = "medium"
        
        # Lifestyle preferences
        if any(word in query_lower for word in ["active", "sports", "exercise", "gym", "सक्रिय", "खेल"]):
            preferences["lifestyle"] = "active"
        elif any(word in query_lower for word in ["office", "desk", "sitting", "कार्यालय", "बैठना"]):
            preferences["lifestyle"] = "sedentary"
        
        # Experience level
        if any(word in query_lower for word in ["first time", "new", "beginner", "पहली बार", "नया"]):
            preferences["experience"] = "beginner"
        elif any(word in query_lower for word in ["experienced", "used to", "अनुभवी", "आदी"]):
            preferences["experience"] = "experienced"
        
        # Flow preferences
        if any(word in query_lower for word in ["heavy", "lot", "much", "भारी", "ज्यादा"]):
            preferences["flow"] = "heavy"
        elif any(word in query_lower for word in ["light", "little", "कम", "हल्का"]):
            preferences["flow"] = "light"
        
        # Priority preferences
        if any(word in query_lower for word in ["environment", "eco", "green", "पर्यावरण"]):
            preferences["priorities"] = "environment"
        elif any(word in query_lower for word in ["comfort", "comfortable", "आराम", "सुविधा"]):
            preferences["priorities"] = "comfort"
        elif any(word in query_lower for word in ["convenient", "easy", "सुविधाजनक", "आसान"]):
            preferences["priorities"] = "convenience"
        
        return preferences
    
    def _get_product_information(self, topic: str, language_code: str) -> Dict[str, Any]:
        """
        Get detailed product information for the topic.
        
        Args:
            topic: Current topic
            language_code: Language for information
            
        Returns:
            Dictionary containing product information
        """
        if topic not in ["product_comparison", "cost_analysis", "hygiene_information"]:
            return {}
        
        # Localize product information
        if language_code == "hi":
            localized_products = {}
            for product_key, product_info in self.PRODUCT_TYPES.items():
                localized_products[product_key] = product_info.copy()
                if product_key == "pads":
                    localized_products[product_key]["name"] = "सैनिटरी पैड"
                elif product_key == "cups":
                    localized_products[product_key]["name"] = "मासिक धर्म कप"
                elif product_key == "cloth":
                    localized_products[product_key]["name"] = "कपड़े के पैड"
            return localized_products
        else:
            return self.PRODUCT_TYPES
    
    def _generate_cost_analysis(self, topic: str, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate cost analysis based on topic and user preferences.
        
        Args:
            topic: Current topic
            user_preferences: User's preferences
            
        Returns:
            Dictionary containing cost analysis
        """
        if topic != "cost_analysis" and "budget" not in user_preferences:
            return {}
        
        user_budget = user_preferences.get("budget", "medium")
        
        cost_analysis = {
            "monthly_costs": {},
            "annual_costs": {},
            "initial_investment": {},
            "long_term_savings": {},
            "budget_recommendation": user_budget
        }
        
        for product_key, product_info in self.PRODUCT_TYPES.items():
            cost_range = product_info["cost_range"]
            
            if product_key == "pads":
                # Monthly recurring cost
                monthly_cost = (cost_range["low"] + cost_range["high"]) / 2
                cost_analysis["monthly_costs"][product_key] = monthly_cost
                cost_analysis["annual_costs"][product_key] = monthly_cost * 12
                cost_analysis["initial_investment"][product_key] = monthly_cost
                
            else:  # cups and cloth - one-time investment
                initial_cost = (cost_range["low"] + cost_range["high"]) / 2
                cost_analysis["initial_investment"][product_key] = initial_cost
                cost_analysis["monthly_costs"][product_key] = 0  # After initial purchase
                cost_analysis["annual_costs"][product_key] = initial_cost / 3  # Amortized over 3 years
        
        # Calculate long-term savings
        pad_annual_cost = cost_analysis["annual_costs"]["pads"]
        for product_key in ["cups", "cloth"]:
            savings = pad_annual_cost - cost_analysis["annual_costs"][product_key]
            cost_analysis["long_term_savings"][product_key] = max(0, savings)
        
        return cost_analysis
    
    def _generate_personalized_suggestions(self, topic: str, user_preferences: Dict[str, Any], language_code: str) -> List[Dict[str, Any]]:
        """
        Generate personalized product suggestions based on user preferences.
        
        Args:
            topic: Current topic
            user_preferences: User's stated preferences
            language_code: Language for suggestions
            
        Returns:
            List of personalized suggestions with reasoning
        """
        if not user_preferences:
            return []
        
        suggestions = []
        
        # Score each product based on user preferences
        product_scores = {}
        for product_key, product_info in self.PRODUCT_TYPES.items():
            score = 0
            reasons = []
            
            # Budget scoring
            budget_pref = user_preferences.get("budget", "medium")
            if budget_pref == "low":
                if product_key == "pads":
                    score += 0.5  # Lower initial cost but higher long-term
                else:
                    score += 1.0  # Better long-term value
                    reasons.append("Cost-effective in the long run")
            elif budget_pref == "high":
                score += 1.0  # All products acceptable
                reasons.append("Fits your budget range")
            
            # Lifestyle scoring
            lifestyle_pref = user_preferences.get("lifestyle", "mixed")
            if lifestyle_pref == "active":
                if product_key == "cups":
                    score += 1.0
                    reasons.append("Great for active lifestyle - long wear time")
                elif product_key == "pads":
                    score += 0.7
                    reasons.append("Convenient for active days")
            
            # Experience scoring
            experience_pref = user_preferences.get("experience", "intermediate")
            if experience_pref == "beginner":
                if product_key == "pads":
                    score += 1.0
                    reasons.append("Easy to start with")
                elif product_key == "cloth":
                    score += 0.8
                    reasons.append("Natural and gentle option")
                else:  # cups
                    score += 0.3
                    reasons.append("May require learning curve")
            
            # Flow scoring
            flow_pref = user_preferences.get("flow", "medium")
            if flow_pref == "heavy":
                if product_key == "cups":
                    score += 1.0
                    reasons.append("Excellent capacity for heavy flow")
                elif product_key == "pads":
                    score += 0.8
                    reasons.append("Good absorption available")
            
            # Priority scoring
            priority_pref = user_preferences.get("priorities", "comfort")
            if priority_pref == "environment":
                if product_key in ["cups", "cloth"]:
                    score += 1.0
                    reasons.append("Environmentally friendly choice")
            elif priority_pref == "convenience":
                if product_key == "pads":
                    score += 1.0
                    reasons.append("Most convenient option")
            elif priority_pref == "comfort":
                if product_key == "cloth":
                    score += 1.0
                    reasons.append("Soft and comfortable material")
            
            product_scores[product_key] = {
                "score": score,
                "reasons": reasons,
                "product_info": product_info
            }
        
        # Sort products by score and create suggestions
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        for product_key, product_data in sorted_products[:3]:  # Top 3 recommendations
            if product_data["score"] > 0:
                suggestion = {
                    "product": product_key,
                    "name": product_data["product_info"]["name"],
                    "score": product_data["score"],
                    "reasons": product_data["reasons"],
                    "pros": product_data["product_info"]["pros"],
                    "cons": product_data["product_info"]["cons"],
                    "cost_range": product_data["product_info"]["cost_range"]
                }
                
                # Add localized recommendation text
                if language_code == "hi":
                    if product_key == "pads":
                        suggestion["recommendation"] = "आपकी प्राथमिकताओं के आधार पर सैनिटरी पैड एक अच्छा विकल्प है।"
                    elif product_key == "cups":
                        suggestion["recommendation"] = "मासिक धर्म कप आपके लिए उपयुक्त हो सकता है।"
                    elif product_key == "cloth":
                        suggestion["recommendation"] = "कपड़े के पैड आपकी आवश्यकताओं के अनुकूल हैं।"
                else:
                    suggestion["recommendation"] = f"Based on your preferences, {product_data['product_info']['name']} would be a good choice for you."
                
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_product_recommendations(self, user_preferences: Dict[str, Any], language_code: str) -> List[Dict[str, Any]]:
        """
        Generate general product recommendations based on user preferences.
        
        Args:
            user_preferences: User's preferences
            language_code: Language for recommendations
            
        Returns:
            List of product recommendations
        """
        return self._generate_personalized_suggestions("personalized_recommendations", user_preferences, language_code)
    
    def _generate_contextual_response(self, query: str, topic: str, language_code: str, user_preferences: Dict[str, Any]) -> str:
        """
        Generate a contextual response based on the query and detected topic.
        
        Args:
            query: Original user query
            topic: Detected topic
            language_code: Language for response
            user_preferences: User's preferences
            
        Returns:
            Contextual response text
        """
        # Response templates by language and topic
        responses = {
            "en": {
                "product_comparison": "I can help you compare different menstrual products. Pads are convenient and easy to use, cups are eco-friendly and cost-effective long-term, and cloth pads are natural and reusable.",
                "cost_analysis": "Let me break down the costs for you. Pads cost around ₹20-150 per month, cups are a one-time investment of ₹300-2000, and cloth pads cost ₹100-800 initially.",
                "hygiene_information": "Maintaining good hygiene is important with any menstrual product. Each option has specific care requirements to prevent infections and ensure comfort.",
                "personalized_recommendations": "Based on your preferences, I can suggest the best products for your needs. Tell me about your budget, lifestyle, and priorities.",
                "product_usage": "I'll guide you through how to use each product safely and effectively. Proper usage ensures comfort and prevents health issues.",
                "environmental_impact": "Menstrual cups and cloth pads are more environmentally friendly as they're reusable, while disposable pads create more waste but offer convenience.",
                "budget_options": "There are good options for every budget. Let me help you find products that fit your financial situation without compromising on quality.",
                "product_care": "Proper care extends the life of reusable products and maintains hygiene. I'll explain the best practices for each product type."
            },
            "hi": {
                "product_comparison": "मैं आपको विभिन्न मासिक धर्म उत्पादों की तुलना करने में मदद कर सकती हूं। पैड सुविधाजनक हैं, कप पर्यावरण-अनुकूल हैं, और कपड़े के पैड प्राकृतिक हैं।",
                "cost_analysis": "मैं आपके लिए लागत का विवरण देती हूं। पैड की मासिक लागत ₹20-150 है, कप एक बार का निवेश ₹300-2000 है, और कपड़े के पैड ₹100-800 में मिलते हैं।",
                "hygiene_information": "किसी भी मासिक धर्म उत्पाद के साथ अच्छी स्वच्छता बनाए रखना महत्वपूर्ण है। हर विकल्प की अपनी देखभाल की आवश्यकताएं हैं।",
                "personalized_recommendations": "आपकी प्राथमिकताओं के आधार पर, मैं आपकी आवश्यकताओं के लिए सबसे अच्छे उत्पाद सुझा सकती हूं।",
                "product_usage": "मैं आपको हर उत्पाद का सुरक्षित और प्रभावी उपयोग करने का तरीका बताऊंगी।",
                "environmental_impact": "मासिक धर्म कप और कपड़े के पैड अधिक पर्यावरण-अनुकूल हैं क्योंकि ये पुन: उपयोग योग्य हैं।",
                "budget_options": "हर बजट के लिए अच्छे विकल्प हैं। मैं आपकी वित्तीय स्थिति के अनुकूल उत्पाद खोजने में मदद करूंगी।",
                "product_care": "उचित देखभाल से पुन: उपयोग योग्य उत्पादों की आयु बढ़ती है और स्वच्छता बनी रहती है।"
            }
        }
        
        # Get appropriate response
        lang_responses = responses.get(language_code, responses["en"])
        base_response = lang_responses.get(topic, "I can help you with menstrual product guidance.")
        
        # Add personalized elements based on preferences
        if user_preferences:
            if user_preferences.get("budget") == "low":
                if language_code == "hi":
                    base_response += " आपके बजट को ध्यान में रखते हुए, मैं किफायती विकल्प सुझाऊंगी।"
                else:
                    base_response += " Considering your budget, I'll focus on cost-effective options."
            
            if user_preferences.get("experience") == "beginner":
                if language_code == "hi":
                    base_response += " चूंकि आप नई हैं, मैं आसान विकल्पों से शुरुआत करने का सुझाव दूंगी।"
                else:
                    base_response += " Since you're new to this, I'll suggest easy-to-use options to start with."
        
        return base_response
    
    def _generate_general_response(self, query: str, language_code: str, user_preferences: Dict[str, Any]) -> str:
        """
        Generate a general response when specific topic cannot be determined.
        
        Args:
            query: Original user query
            language_code: Language for response
            user_preferences: User's preferences
            
        Returns:
            General response text
        """
        general_responses = {
            "en": "I'm here to help you choose the right menstrual products. I can compare pads, cups, and cloth options, analyze costs, and provide personalized recommendations based on your needs and budget.",
            "hi": "मैं आपको सही मासिक धर्म उत्पाद चुनने में मदद करने के लिए यहां हूं। मैं पैड, कप और कपड़े के विकल्पों की तुलना कर सकती हूं और आपकी आवश्यकताओं के अनुसार सुझाव दे सकती हूं।"
        }
        
        base_response = general_responses.get(language_code, general_responses["en"])
        
        # Add context based on any extracted preferences
        if user_preferences:
            if language_code == "hi":
                base_response += " आपकी प्राथमिकताओं के आधार पर मैं बेहतर सुझाव दे सकूंगी।"
            else:
                base_response += " Based on your preferences, I can provide more targeted recommendations."
        
        return base_response
    
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
                "medical_emergency": "This sounds like a medical concern related to menstruation. Please contact a healthcare provider immediately for proper medical advice.",
                "general_emergency": "If you're experiencing severe menstrual problems or pain, please consult a doctor. I can provide product guidance, but medical issues need professional care."
            },
            "hi": {
                "medical_emergency": "यह मासिक धर्म से संबंधित चिकित्सा समस्या लगती है। कृपया तुरंत किसी स्वास्थ्य सेवा प्रदाता से संपर्क करें।",
                "general_emergency": "यदि आप गंभीर मासिक धर्म की समस्या या दर्द का अनुभव कर रही हैं, तो कृपया डॉक्टर से सलाह लें।"
            }
        }
        
        emergency_type = emergency_result.get("emergency_type", "general_emergency")
        lang_responses = emergency_responses.get(language_code, emergency_responses["en"])
        
        return lang_responses.get(emergency_type, lang_responses["general_emergency"])
    
    def _generate_topic_recommendations(self, current_topic: str, user_preferences: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for related topics based on current topic and preferences.
        
        Args:
            current_topic: Currently viewed topic
            user_preferences: User's preferences
            
        Returns:
            List of recommended topic names
        """
        # Topic relationship mapping
        topic_relationships = {
            "product_comparison": ["cost_analysis", "hygiene_information", "personalized_recommendations"],
            "cost_analysis": ["budget_options", "product_comparison", "personalized_recommendations"],
            "hygiene_information": ["product_care", "product_usage", "product_comparison"],
            "personalized_recommendations": ["product_comparison", "cost_analysis", "product_usage"],
            "product_usage": ["hygiene_information", "product_care", "product_comparison"],
            "environmental_impact": ["product_comparison", "cost_analysis"],
            "budget_options": ["cost_analysis", "product_comparison"],
            "product_care": ["hygiene_information", "product_usage"]
        }
        
        # Get related topics
        related_topics = topic_relationships.get(current_topic, ["product_comparison", "cost_analysis"])
        
        # Filter based on user preferences
        if user_preferences.get("budget") == "low":
            if "budget_options" not in related_topics:
                related_topics.insert(0, "budget_options")
        
        if user_preferences.get("priorities") == "environment":
            if "environmental_impact" not in related_topics:
                related_topics.insert(0, "environmental_impact")
        
        if user_preferences.get("experience") == "beginner":
            if "product_usage" not in related_topics:
                related_topics.append("product_usage")
        
        return related_topics[:3]  # Return top 3 recommendations
    
    def _generate_next_actions(self, topic: str, user_preferences: Dict[str, Any]) -> List[str]:
        """
        Generate suggested next actions based on topic and preferences.
        
        Args:
            topic: Current topic
            user_preferences: User's preferences
            
        Returns:
            List of suggested next actions
        """
        base_actions = {
            "product_comparison": ["Learn about costs", "Get personalized recommendations", "Understand hygiene requirements"],
            "cost_analysis": ["Compare long-term savings", "Explore budget options", "Get product recommendations"],
            "hygiene_information": ["Learn proper usage", "Understand care instructions", "Compare safety features"],
            "personalized_recommendations": ["Refine your preferences", "Learn about recommended products", "Compare costs"],
            "product_usage": ["Learn about hygiene", "Understand care requirements", "Get safety tips"],
            "environmental_impact": ["Compare eco-friendly options", "Learn about sustainability", "Calculate environmental savings"],
            "budget_options": ["Compare costs", "Learn about long-term savings", "Get affordable recommendations"],
            "product_care": ["Learn proper usage", "Understand hygiene requirements", "Get maintenance tips"]
        }
        
        actions = base_actions.get(topic, ["Ask specific questions", "Share your preferences", "Explore product options"])
        
        # Add preference-based actions
        if not user_preferences.get("budget"):
            actions.append("Tell me your budget range")
        
        if not user_preferences.get("experience"):
            actions.append("Share your experience level")
        
        if not user_preferences.get("lifestyle"):
            actions.append("Describe your lifestyle")
        
        return actions[:4]  # Return top 4 actions
    
    def _update_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences in session.
        
        Args:
            session_id: Session ID to update
            preferences: New preferences to save
            
        Returns:
            True if update was successful
        """
        try:
            session = self.session_manager.get_session(session_id)
            if session:
                if not session.accessibility_preferences:
                    session.accessibility_preferences = {}
                
                session.accessibility_preferences["menstrual_preferences"] = preferences
                return self.session_manager.update_session(session_id, accessibility_preferences=session.accessibility_preferences)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {e}")
            return False