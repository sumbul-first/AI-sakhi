"""
GovernmentResourcesModule - Government health schemes and programs information module.

This module provides comprehensive information about Indian government health schemes
and programs for women and maternal health, including JSY, PMSMA, JSSK, RCH, and
Swasth Nari programs. It implements scheme eligibility checking, benefit explanation,
application process guidance, and regional variation handling.

Key Features:
- Information about 5 major government health schemes
- Eligibility checking functionality for each scheme
- Application process guidance with step-by-step instructions
- Regional variation handling for different Indian states
- Multi-language support for scheme information
- Integration with BaseHealthModule for safety and emergency features

Requirements Addressed:
- 5.1: Provide comprehensive information about JSY (Janani Suraksha Yojana)
- 5.2: Educate about PMSMA (Pradhan Mantri Surakshit Matritva Abhiyan)
- 5.3: Explain JSSK (Janani Shishu Suraksha Karyakram) benefits
- 5.4: Provide information about RCH (Reproductive and Child Health) programs
- 5.5: Guide users about Swasth Nari (Healthy Women) initiatives
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone

from modules.base_health_module import BaseHealthModule
from models.data_models import ContentItem, GovernmentScheme
from core.content_manager import ContentManager
from core.session_manager import SessionManager


class GovernmentResourcesModule(BaseHealthModule):
    """
    Government Resources Module for health schemes and programs information.
    
    This module extends BaseHealthModule to provide specialized functionality
    for government health schemes including eligibility checking, benefit
    explanation, and application guidance for Indian government programs.
    """
    
    # Government scheme identifiers
    SCHEME_JSY = "janani_suraksha_yojana"
    SCHEME_PMSMA = "pradhan_mantri_surakshit_matritva_abhiyan"
    SCHEME_JSSK = "janani_shishu_suraksha_karyakram"
    SCHEME_RCH = "reproductive_child_health"
    SCHEME_SWASTH_NARI = "swasth_nari"
    
    # Available topics for this module
    MODULE_TOPICS = [
        "government_schemes_overview",
        "jsy_information",
        "pmsma_information", 
        "jssk_information",
        "rch_programs",
        "swasth_nari_initiatives",
        "eligibility_checker",
        "application_process",
        "regional_variations",
        "scheme_benefits"
    ]
    
    # Indian states for regional variations
    INDIAN_STATES = [
        "andhra_pradesh", "arunachal_pradesh", "assam", "bihar", "chhattisgarh",
        "goa", "gujarat", "haryana", "himachal_pradesh", "jharkhand", "karnataka",
        "kerala", "madhya_pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
        "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil_nadu",
        "telangana", "tripura", "uttar_pradesh", "uttarakhand", "west_bengal",
        "delhi", "jammu_kashmir", "ladakh", "chandigarh", "dadra_nagar_haveli",
        "daman_diu", "lakshadweep", "puducherry"
    ]
    
    def __init__(self, content_manager: ContentManager, session_manager: SessionManager):
        """
        Initialize the Government Resources Module.
        
        Args:
            content_manager: ContentManager instance for content retrieval
            session_manager: SessionManager instance for session handling
        """
        super().__init__("government_resources", content_manager, session_manager)
        
        # Initialize government schemes data
        self._schemes_cache = {}
        self._regional_data_cache = {}
        
        # Load scheme data
        self._initialize_schemes_data()
        
        self.logger.info("Government Resources Module initialized successfully")
    
    def _initialize_schemes_data(self) -> None:
        """Initialize government schemes data with comprehensive information."""
        try:
            # JSY - Janani Suraksha Yojana
            jsy_scheme = GovernmentScheme(
                scheme_name="Janani Suraksha Yojana (JSY)",
                scheme_type="maternity",
                eligibility_criteria=[
                    "Pregnant women belonging to BPL (Below Poverty Line) families",
                    "All pregnant women in Low Performing States (LPS)",
                    "Women aged 19 years and above",
                    "Maximum of two live births for cash assistance"
                ],
                benefits=[
                    "Cash assistance of ₹1,400 for rural areas and ₹1,000 for urban areas",
                    "Free delivery care at government health facilities",
                    "ASHA (Accredited Social Health Activist) incentive of ₹600",
                    "Free transport to health facility",
                    "Free medicines and diagnostics"
                ],
                application_process="Register with ASHA worker during pregnancy. Complete ANC checkups. Deliver at government health facility or accredited private facility.",
                required_documents=[
                    "BPL card or income certificate",
                    "Pregnancy registration card (MCP card)",
                    "Aadhaar card",
                    "Bank account details",
                    "Age proof document"
                ],
                contact_details={
                    "helpline": "104",
                    "website": "nhm.gov.in",
                    "email": "jsyquery@nhm.gov.in"
                },
                regional_variations={
                    "uttar_pradesh": {
                        "additional_benefits": ["₹200 extra for completing 4 ANC visits"],
                        "special_conditions": ["Enhanced monitoring in high-risk districts"]
                    },
                    "bihar": {
                        "additional_benefits": ["Free nutritional supplements"],
                        "special_conditions": ["Mobile health units for remote areas"]
                    }
                },
                language_code="en"
            )
            
            # PMSMA - Pradhan Mantri Surakshit Matritva Abhiyan
            pmsma_scheme = GovernmentScheme(
                scheme_name="Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
                scheme_type="maternity",
                eligibility_criteria=[
                    "All pregnant women in their second and third trimester",
                    "Minimum 4 months of pregnancy",
                    "No income or caste restrictions"
                ],
                benefits=[
                    "Free comprehensive ANC checkup on 9th of every month",
                    "High-risk pregnancy identification and management",
                    "Free ultrasound and blood tests",
                    "Specialist doctor consultation",
                    "Referral services for complications"
                ],
                application_process="Visit nearest government health facility on 9th of any month. Register with ANM or doctor. Receive comprehensive checkup and follow-up care.",
                required_documents=[
                    "Pregnancy registration card",
                    "Any government ID proof",
                    "Previous medical records if available"
                ],
                contact_details={
                    "helpline": "104",
                    "website": "pmsma.nhp.gov.in",
                    "email": "pmsma@nhm.gov.in"
                },
                regional_variations={
                    "maharashtra": {
                        "additional_benefits": ["Telemedicine consultation available"],
                        "special_conditions": ["Extended hours on PMSMA day"]
                    },
                    "kerala": {
                        "additional_benefits": ["Home visit follow-up for high-risk cases"],
                        "special_conditions": ["Integration with state health insurance"]
                    }
                },
                language_code="en"
            )
            
            # JSSK - Janani Shishu Suraksha Karyakram
            jssk_scheme = GovernmentScheme(
                scheme_name="Janani Shishu Suraksha Karyakram (JSSK)",
                scheme_type="maternity",
                eligibility_criteria=[
                    "All pregnant women delivering in public health institutions",
                    "All sick newborns accessing public health institutions",
                    "No income or caste restrictions"
                ],
                benefits=[
                    "Free delivery including C-section",
                    "Free medicines and consumables",
                    "Free diagnostics and blood transfusion",
                    "Free transport from home to facility",
                    "Free food during stay in health facility",
                    "Free treatment of sick newborn up to 30 days"
                ],
                application_process="Visit government health facility during pregnancy for registration. Avail services during delivery and postpartum period. No separate application required.",
                required_documents=[
                    "Any government ID proof",
                    "Pregnancy registration if available",
                    "Residence proof"
                ],
                contact_details={
                    "helpline": "104",
                    "website": "nhm.gov.in/jssk",
                    "email": "jssk@nhm.gov.in"
                },
                regional_variations={
                    "rajasthan": {
                        "additional_benefits": ["Free transport up to ₹250 per trip"],
                        "special_conditions": ["108 ambulance service integration"]
                    },
                    "odisha": {
                        "additional_benefits": ["Extended postpartum care up to 42 days"],
                        "special_conditions": ["Tribal area special provisions"]
                    }
                },
                language_code="en"
            )
            
            # RCH - Reproductive and Child Health
            rch_scheme = GovernmentScheme(
                scheme_name="Reproductive and Child Health (RCH) Program",
                scheme_type="reproductive_health",
                eligibility_criteria=[
                    "All women of reproductive age (15-49 years)",
                    "All children under 6 years",
                    "Adolescent girls and boys",
                    "No income restrictions"
                ],
                benefits=[
                    "Family planning services and counseling",
                    "Contraceptive methods and supplies",
                    "Safe abortion services",
                    "Treatment of RTI/STI",
                    "Adolescent reproductive health services",
                    "Immunization services for children"
                ],
                application_process="Visit nearest government health facility or contact ASHA worker. Receive counseling and appropriate services based on needs.",
                required_documents=[
                    "Any government ID proof",
                    "Age proof for adolescent services",
                    "Medical history if available"
                ],
                contact_details={
                    "helpline": "104",
                    "website": "nhm.gov.in/rch",
                    "email": "rch@nhm.gov.in"
                },
                regional_variations={
                    "tamil_nadu": {
                        "additional_benefits": ["Comprehensive adolescent health clinics"],
                        "special_conditions": ["School health program integration"]
                    },
                    "andhra_pradesh": {
                        "additional_benefits": ["Mobile health units for remote areas"],
                        "special_conditions": ["Telemedicine support available"]
                    }
                },
                language_code="en"
            )
            
            # Swasth Nari - Healthy Women Initiative
            swasth_nari_scheme = GovernmentScheme(
                scheme_name="Swasth Nari (Healthy Women) Initiative",
                scheme_type="reproductive_health",
                eligibility_criteria=[
                    "All women aged 18 years and above",
                    "Focus on rural and marginalized women",
                    "No income restrictions"
                ],
                benefits=[
                    "Health education and awareness programs",
                    "Screening for common women's health issues",
                    "Nutrition counseling and support",
                    "Mental health support and counseling",
                    "Skill development and livelihood support",
                    "Community health worker training"
                ],
                application_process="Participate in community health programs. Contact local ASHA worker or visit health facility for enrollment in specific programs.",
                required_documents=[
                    "Any government ID proof",
                    "Residence proof",
                    "Bank account details for financial benefits"
                ],
                contact_details={
                    "helpline": "104",
                    "website": "nhm.gov.in/swasth-nari",
                    "email": "swasthnari@nhm.gov.in"
                },
                regional_variations={
                    "gujarat": {
                        "additional_benefits": ["Self-help group integration"],
                        "special_conditions": ["Microfinance linkage available"]
                    },
                    "madhya_pradesh": {
                        "additional_benefits": ["Nutrition supplementation program"],
                        "special_conditions": ["Focus on tribal women's health"]
                    }
                },
                language_code="en"
            )
            
            # Cache all schemes
            self._schemes_cache = {
                self.SCHEME_JSY: jsy_scheme,
                self.SCHEME_PMSMA: pmsma_scheme,
                self.SCHEME_JSSK: jssk_scheme,
                self.SCHEME_RCH: rch_scheme,
                self.SCHEME_SWASTH_NARI: swasth_nari_scheme
            }
            
            self.logger.info("Government schemes data initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing schemes data: {e}")
            self._schemes_cache = {}
    
    def get_content_by_topic(self, topic: str, language_code: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve content for a specific government resources topic.
        
        Args:
            topic: Specific topic to retrieve content for
            language_code: Language code for content localization
            session_id: Optional session ID for personalization
            
        Returns:
            Dictionary containing content and metadata
        """
        try:
            if topic not in self.MODULE_TOPICS:
                return {
                    "content": [],
                    "safety_validated": True,
                    "emergency_detected": False,
                    "language_used": language_code,
                    "recommendations": [f"Topic '{topic}' not found. Available topics: {', '.join(self.MODULE_TOPICS)}"],
                    "error": "Invalid topic"
                }
            
            content_items = []
            
            # Generate content based on topic
            if topic == "government_schemes_overview":
                content_items = self._get_schemes_overview_content(language_code)
            elif topic == "jsy_information":
                content_items = self._get_scheme_content(self.SCHEME_JSY, language_code)
            elif topic == "pmsma_information":
                content_items = self._get_scheme_content(self.SCHEME_PMSMA, language_code)
            elif topic == "jssk_information":
                content_items = self._get_scheme_content(self.SCHEME_JSSK, language_code)
            elif topic == "rch_programs":
                content_items = self._get_scheme_content(self.SCHEME_RCH, language_code)
            elif topic == "swasth_nari_initiatives":
                content_items = self._get_scheme_content(self.SCHEME_SWASTH_NARI, language_code)
            elif topic == "eligibility_checker":
                content_items = self._get_eligibility_checker_content(language_code)
            elif topic == "application_process":
                content_items = self._get_application_process_content(language_code)
            elif topic == "regional_variations":
                content_items = self._get_regional_variations_content(language_code)
            elif topic == "scheme_benefits":
                content_items = self._get_scheme_benefits_content(language_code)
            
            # Validate content safety
            safety_result = self.validate_content_safety(content_items)
            
            # Update session if provided
            if session_id:
                self.update_session_context(session_id, {
                    "topic": topic,
                    "language_code": language_code,
                    "content_count": len(content_items)
                })
            
            return {
                "content": content_items,
                "safety_validated": safety_result["is_safe"],
                "emergency_detected": bool(safety_result["emergency_flags"]),
                "language_used": language_code,
                "recommendations": self._get_topic_recommendations(topic),
                "safety_warnings": safety_result["recommendations"]
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving content for topic {topic}: {e}")
            return {
                "content": [],
                "safety_validated": False,
                "emergency_detected": False,
                "language_used": language_code,
                "recommendations": ["Error occurred while retrieving content"],
                "error": str(e)
            }
    
    def handle_user_query(self, query: str, language_code: str, 
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and respond to a user query about government resources.
        
        Args:
            query: User's question or request
            language_code: Language code for response
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing response and relevant content
        """
        try:
            query_lower = query.lower()
            
            # Detect emergency situations
            emergency_result = self.detect_emergency_situation(query)
            
            if emergency_result["is_emergency"]:
                return {
                    "response": "I understand you may need immediate help. Please contact emergency services or the helplines I'm providing.",
                    "content_items": [],
                    "emergency_detected": True,
                    "emergency_contacts": self.get_emergency_resources(language_code),
                    "safety_warnings": emergency_result["immediate_actions"],
                    "next_actions": ["Contact emergency services", "Seek immediate help"]
                }
            
            # Determine query intent and provide appropriate response
            response_data = self._process_government_query(query_lower, language_code)
            
            # Update session context
            if session_id:
                self.update_session_context(session_id, {
                    "query": query,
                    "response": response_data["response"],
                    "language_code": language_code
                })
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error handling user query: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your question. Please try asking again or contact the helpline at 104.",
                "content_items": [],
                "emergency_detected": False,
                "safety_warnings": ["Error occurred during query processing"],
                "next_actions": ["Try rephrasing your question", "Contact helpline 104"]
            }
    
    def get_module_topics(self, language_code: str) -> List[str]:
        """
        Get list of available topics for the government resources module.
        
        Args:
            language_code: Language code for topic names
            
        Returns:
            List of topic names available in this module
        """
        return self.MODULE_TOPICS.copy()
    
    def check_scheme_eligibility(self, scheme_name: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check eligibility for a specific government scheme.
        
        Args:
            scheme_name: Name of the scheme to check eligibility for
            user_profile: Dictionary containing user information
            
        Returns:
            Dictionary containing eligibility results and recommendations
        """
        try:
            if scheme_name not in self._schemes_cache:
                return {
                    "eligible": False,
                    "scheme_name": scheme_name,
                    "reason": "Scheme not found",
                    "recommendations": ["Please check the scheme name and try again"]
                }
            
            scheme = self._schemes_cache[scheme_name]
            eligibility_result = {
                "eligible": True,
                "scheme_name": scheme.scheme_name,
                "reason": "",
                "recommendations": [],
                "missing_criteria": [],
                "next_steps": []
            }
            
            # Check eligibility based on scheme type and criteria
            if scheme_name == self.SCHEME_JSY:
                eligibility_result = self._check_jsy_eligibility(user_profile, scheme)
            elif scheme_name == self.SCHEME_PMSMA:
                eligibility_result = self._check_pmsma_eligibility(user_profile, scheme)
            elif scheme_name == self.SCHEME_JSSK:
                eligibility_result = self._check_jssk_eligibility(user_profile, scheme)
            elif scheme_name == self.SCHEME_RCH:
                eligibility_result = self._check_rch_eligibility(user_profile, scheme)
            elif scheme_name == self.SCHEME_SWASTH_NARI:
                eligibility_result = self._check_swasth_nari_eligibility(user_profile, scheme)
            
            return eligibility_result
            
        except Exception as e:
            self.logger.error(f"Error checking eligibility for {scheme_name}: {e}")
            return {
                "eligible": False,
                "scheme_name": scheme_name,
                "reason": "Error occurred during eligibility check",
                "recommendations": ["Please try again or contact helpline 104"]
            }
    
    def get_regional_information(self, scheme_name: str, state: str, language_code: str = "en") -> Dict[str, Any]:
        """
        Get regional variation information for a scheme in a specific state.
        
        Args:
            scheme_name: Name of the scheme
            state: State name for regional information
            language_code: Language for the information
            
        Returns:
            Dictionary containing regional information and variations
        """
        try:
            if scheme_name not in self._schemes_cache:
                return {
                    "scheme_name": scheme_name,
                    "state": state,
                    "has_variations": False,
                    "message": "Scheme not found"
                }
            
            scheme = self._schemes_cache[scheme_name]
            state_key = state.lower().replace(" ", "_")
            
            regional_info = {
                "scheme_name": scheme.scheme_name,
                "state": state,
                "has_variations": state_key in scheme.regional_variations,
                "general_benefits": scheme.benefits,
                "general_eligibility": scheme.eligibility_criteria,
                "contact_details": scheme.contact_details
            }
            
            if regional_info["has_variations"]:
                variations = scheme.regional_variations[state_key]
                regional_info.update({
                    "additional_benefits": variations.get("additional_benefits", []),
                    "special_conditions": variations.get("special_conditions", []),
                    "state_specific_contacts": variations.get("contacts", {}),
                    "modified_eligibility": variations.get("eligibility_modifications", [])
                })
            else:
                regional_info.update({
                    "message": f"No specific regional variations found for {state}. General scheme benefits apply.",
                    "additional_benefits": [],
                    "special_conditions": []
                })
            
            return regional_info
            
        except Exception as e:
            self.logger.error(f"Error getting regional information: {e}")
            return {
                "scheme_name": scheme_name,
                "state": state,
                "has_variations": False,
                "message": "Error occurred while retrieving regional information"
            }
    
    def get_application_guidance(self, scheme_name: str, language_code: str = "en") -> Dict[str, Any]:
        """
        Get step-by-step application guidance for a specific scheme.
        
        Args:
            scheme_name: Name of the scheme
            language_code: Language for the guidance
            
        Returns:
            Dictionary containing detailed application guidance
        """
        try:
            if scheme_name not in self._schemes_cache:
                return {
                    "scheme_name": scheme_name,
                    "steps": [],
                    "documents": [],
                    "contacts": {},
                    "error": "Scheme not found"
                }
            
            scheme = self._schemes_cache[scheme_name]
            
            # Generate step-by-step guidance
            steps = self._generate_application_steps(scheme)
            
            return {
                "scheme_name": scheme.scheme_name,
                "steps": steps,
                "required_documents": scheme.required_documents,
                "contact_details": scheme.contact_details,
                "estimated_time": self._get_application_timeline(scheme_name),
                "tips": self._get_application_tips(scheme_name),
                "common_issues": self._get_common_application_issues(scheme_name)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting application guidance: {e}")
            return {
                "scheme_name": scheme_name,
                "steps": [],
                "documents": [],
                "contacts": {},
                "error": str(e)
            }
    
    def validate_content_safety(self, content: Union[str, ContentItem, List[ContentItem]]) -> Dict[str, Any]:
        """
        Validate content for safety boundaries with government scheme context.
        
        This method overrides the base class to provide more appropriate safety
        validation for government scheme information, which may contain medical
        terminology in an educational context.
        
        Args:
            content: Content to validate (string, ContentItem, or list of ContentItems)
            
        Returns:
            Dictionary containing safety validation results
        """
        try:
            # Get base validation result
            base_result = super().validate_content_safety(content)
            
            # For government schemes, certain medical terms are acceptable in educational context
            acceptable_medical_terms = [
                "medicine", "medicines", "medical", "telemedicine", "treatment",
                "therapy", "diagnostics", "consultation", "checkup", "care"
            ]
            
            # Filter out acceptable medical terms from flags
            filtered_medical_flags = [
                flag for flag in base_result["medical_flags"]
                if flag not in acceptable_medical_terms
            ]
            
            # Update result with filtered flags
            base_result["medical_flags"] = filtered_medical_flags
            base_result["requires_medical_referral"] = len(filtered_medical_flags) > 0
            
            # If no problematic medical flags remain, mark as safe
            if not filtered_medical_flags and not base_result["emergency_flags"]:
                base_result["is_safe"] = True
                base_result["recommendations"] = [
                    "Government scheme information appears safe for educational purposes."
                ]
            
            return base_result
            
        except Exception as e:
            self.logger.error(f"Error validating content safety: {e}")
            return {
                "is_safe": False,
                "medical_flags": [],
                "emergency_flags": [],
                "recommendations": ["Error occurred during safety validation"],
                "requires_medical_referral": True
            }
    
    def _get_schemes_overview_content(self, language_code: str) -> List[ContentItem]:
        """Generate overview content for all government schemes."""
        content_items = []
        
        overview_text = """
        Government Health Schemes for Women and Maternal Health:
        
        1. Janani Suraksha Yojana (JSY) - Cash assistance for safe delivery
        2. Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA) - Free ANC checkups
        3. Janani Shishu Suraksha Karyakram (JSSK) - Free delivery and newborn care
        4. Reproductive and Child Health (RCH) - Comprehensive reproductive health services
        5. Swasth Nari Initiative - Women's health education and empowerment
        
        These schemes provide financial assistance, free healthcare services, and support
        for women during pregnancy, delivery, and beyond. All schemes are available
        across India with some regional variations.
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic="government_schemes_overview",
            content_type="text",
            language_code=language_code,
            transcript=overview_text.strip(),
            safety_validated=True
        )
        
        content_items.append(content_item)
        return content_items
    
    def _get_scheme_content(self, scheme_key: str, language_code: str) -> List[ContentItem]:
        """Generate detailed content for a specific scheme."""
        if scheme_key not in self._schemes_cache:
            return []
        
        scheme = self._schemes_cache[scheme_key]
        content_items = []
        
        # Main scheme information
        scheme_text = f"""
        {scheme.scheme_name}
        
        Eligibility Criteria:
        {chr(10).join(f"• {criteria}" for criteria in scheme.eligibility_criteria)}
        
        Benefits:
        {chr(10).join(f"• {benefit}" for benefit in scheme.benefits)}
        
        Application Process:
        {scheme.application_process}
        
        Required Documents:
        {chr(10).join(f"• {doc}" for doc in scheme.required_documents)}
        
        Contact Information:
        Helpline: {scheme.contact_details.get('helpline', 'N/A')}
        Website: {scheme.contact_details.get('website', 'N/A')}
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic=scheme_key,
            content_type="text",
            language_code=language_code,
            transcript=scheme_text.strip(),
            safety_validated=True
        )
        
        content_items.append(content_item)
        return content_items
    
    def _get_eligibility_checker_content(self, language_code: str) -> List[ContentItem]:
        """Generate content for eligibility checking guidance."""
        eligibility_text = """
        Government Scheme Eligibility Checker
        
        To check your eligibility for government health schemes, please provide:
        
        1. Your age and pregnancy status
        2. Family income level (BPL card if available)
        3. State of residence
        4. Number of previous children (for some schemes)
        5. Current health facility registration status
        
        Based on this information, I can help you determine which schemes
        you are eligible for and guide you through the application process.
        
        Most schemes have no income restrictions, but some like JSY focus
        on BPL families and women in Low Performing States.
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic="eligibility_checker",
            content_type="text",
            language_code=language_code,
            transcript=eligibility_text.strip(),
            safety_validated=True
        )
        
        return [content_item]
    
    def _get_application_process_content(self, language_code: str) -> List[ContentItem]:
        """Generate content for general application process guidance."""
        process_text = """
        General Application Process for Government Health Schemes:
        
        Step 1: Identify Relevant Schemes
        - Determine which schemes apply to your situation
        - Check eligibility criteria for each scheme
        
        Step 2: Gather Required Documents
        - Government ID proof (Aadhaar preferred)
        - Income certificate or BPL card (if applicable)
        - Pregnancy registration card (for maternity schemes)
        - Bank account details
        - Residence proof
        
        Step 3: Visit Health Facility or Contact ASHA
        - Go to nearest government health center
        - Contact your local ASHA worker
        - Register for relevant schemes
        
        Step 4: Complete Required Procedures
        - Attend ANC checkups (for pregnancy schemes)
        - Follow scheme-specific requirements
        - Maintain all documentation
        
        Step 5: Receive Benefits
        - Cash benefits are usually transferred to bank account
        - Services are provided at registered health facilities
        - Keep all receipts and records
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic="application_process",
            content_type="text",
            language_code=language_code,
            transcript=process_text.strip(),
            safety_validated=True
        )
        
        return [content_item]
    
    def _get_regional_variations_content(self, language_code: str) -> List[ContentItem]:
        """Generate content about regional variations in schemes."""
        regional_text = """
        Regional Variations in Government Health Schemes:
        
        Many government health schemes have state-specific variations and
        additional benefits. Here are some examples:
        
        Enhanced Benefits in Some States:
        • Additional cash incentives for completing ANC visits
        • Extended postpartum care periods
        • Mobile health units for remote areas
        • Telemedicine consultation services
        • Integration with state health insurance schemes
        
        Special Focus Areas:
        • Tribal areas often have enhanced provisions
        • High-risk districts may have additional monitoring
        • Border areas may have special transport arrangements
        • Urban slums may have targeted outreach programs
        
        To get specific information about your state's variations:
        1. Contact your state health department
        2. Ask your local ASHA worker
        3. Visit the nearest government health facility
        4. Check your state's health department website
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic="regional_variations",
            content_type="text",
            language_code=language_code,
            transcript=regional_text.strip(),
            safety_validated=True
        )
        
        return [content_item]
    
    def _get_scheme_benefits_content(self, language_code: str) -> List[ContentItem]:
        """Generate comprehensive content about scheme benefits."""
        benefits_text = """
        Comprehensive Benefits from Government Health Schemes:
        
        Financial Benefits:
        • Cash assistance for institutional delivery (JSY)
        • Free delivery including C-section (JSSK)
        • Free transport to health facilities
        • ASHA worker incentives for support
        
        Healthcare Services:
        • Free ANC checkups and monitoring (PMSMA)
        • Free medicines and diagnostics
        • Blood transfusion services
        • Specialist consultation
        • Emergency obstetric care
        
        Newborn Care:
        • Free treatment for sick newborns up to 30 days
        • Immunization services
        • Growth monitoring
        • Nutritional support
        
        Additional Support:
        • Family planning counseling and services
        • Reproductive health education
        • Mental health support
        • Skill development opportunities (Swasth Nari)
        
        Long-term Benefits:
        • Improved maternal and child health outcomes
        • Reduced out-of-pocket healthcare expenses
        • Better access to quality healthcare services
        • Empowerment through health education
        """
        
        content_item = ContentItem(
            module_name=self.module_name,
            topic="scheme_benefits",
            content_type="text",
            language_code=language_code,
            transcript=benefits_text.strip(),
            safety_validated=True
        )
        
        return [content_item]
    
    def _process_government_query(self, query: str, language_code: str) -> Dict[str, Any]:
        """Process user query and provide appropriate government resources response."""
        
        # Query intent detection
        if any(word in query for word in ["jsy", "janani suraksha", "cash assistance", "delivery money"]):
            return self._handle_jsy_query(language_code)
        elif any(word in query for word in ["pmsma", "anc", "checkup", "9th"]):
            return self._handle_pmsma_query(language_code)
        elif any(word in query for word in ["jssk", "free delivery", "newborn care"]):
            return self._handle_jssk_query(language_code)
        elif any(word in query for word in ["rch", "family planning", "contraceptive"]):
            return self._handle_rch_query(language_code)
        elif any(word in query for word in ["swasth nari", "women health", "skill development"]):
            return self._handle_swasth_nari_query(language_code)
        elif any(word in query for word in ["eligible", "eligibility", "qualify"]):
            return self._handle_eligibility_query(language_code)
        elif any(word in query for word in ["apply", "application", "how to get"]):
            return self._handle_application_query(language_code)
        elif any(word in query for word in ["state", "regional", "variation"]):
            return self._handle_regional_query(language_code)
        else:
            return self._handle_general_query(language_code)
    
    def _handle_jsy_query(self, language_code: str) -> Dict[str, Any]:
        """Handle JSY-specific queries."""
        return {
            "response": "Janani Suraksha Yojana (JSY) provides cash assistance for safe delivery. You can get ₹1,400 in rural areas and ₹1,000 in urban areas for delivering at a government health facility.",
            "content_items": self._get_scheme_content(self.SCHEME_JSY, language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Check your eligibility", "Contact ASHA worker", "Register at health facility"]
        }
    
    def _handle_pmsma_query(self, language_code: str) -> Dict[str, Any]:
        """Handle PMSMA-specific queries."""
        return {
            "response": "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA) provides free comprehensive ANC checkups on the 9th of every month. Visit your nearest government health facility.",
            "content_items": self._get_scheme_content(self.SCHEME_PMSMA, language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Visit health facility on 9th", "Bring pregnancy card", "Get comprehensive checkup"]
        }
    
    def _handle_jssk_query(self, language_code: str) -> Dict[str, Any]:
        """Handle JSSK-specific queries."""
        return {
            "response": "Janani Shishu Suraksha Karyakram (JSSK) provides completely free delivery services including C-section, medicines, and newborn care up to 30 days at government facilities.",
            "content_items": self._get_scheme_content(self.SCHEME_JSSK, language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Register at government facility", "Plan delivery at registered facility", "Avail free services"]
        }
    
    def _handle_rch_query(self, language_code: str) -> Dict[str, Any]:
        """Handle RCH-specific queries."""
        return {
            "response": "Reproductive and Child Health (RCH) program provides family planning services, contraceptives, and reproductive health care for all women and children.",
            "content_items": self._get_scheme_content(self.SCHEME_RCH, language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Visit health facility", "Get counseling", "Choose appropriate services"]
        }
    
    def _handle_swasth_nari_query(self, language_code: str) -> Dict[str, Any]:
        """Handle Swasth Nari-specific queries."""
        return {
            "response": "Swasth Nari initiative focuses on women's health education, screening, nutrition support, and skill development. It empowers women through comprehensive health and livelihood programs.",
            "content_items": self._get_scheme_content(self.SCHEME_SWASTH_NARI, language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Join community programs", "Contact ASHA worker", "Participate in health education"]
        }
    
    def _handle_eligibility_query(self, language_code: str) -> Dict[str, Any]:
        """Handle eligibility-related queries."""
        return {
            "response": "I can help you check eligibility for government health schemes. Most schemes are available to all women, with some having specific criteria like pregnancy status or income level.",
            "content_items": self._get_eligibility_checker_content(language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Provide your details", "Check specific scheme eligibility", "Contact ASHA worker"]
        }
    
    def _handle_application_query(self, language_code: str) -> Dict[str, Any]:
        """Handle application process queries."""
        return {
            "response": "To apply for government health schemes, start by visiting your nearest government health facility or contacting your ASHA worker. Most schemes require basic documents like ID proof and pregnancy registration.",
            "content_items": self._get_application_process_content(language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Gather required documents", "Visit health facility", "Register for schemes"]
        }
    
    def _handle_regional_query(self, language_code: str) -> Dict[str, Any]:
        """Handle regional variation queries."""
        return {
            "response": "Government health schemes have regional variations with additional benefits in many states. Your state may offer enhanced services or additional cash incentives.",
            "content_items": self._get_regional_variations_content(language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Check state-specific benefits", "Contact state health department", "Ask local ASHA worker"]
        }
    
    def _handle_general_query(self, language_code: str) -> Dict[str, Any]:
        """Handle general government resources queries."""
        return {
            "response": "I can help you with information about government health schemes including JSY, PMSMA, JSSK, RCH, and Swasth Nari programs. These provide financial assistance and free healthcare services for women and children.",
            "content_items": self._get_schemes_overview_content(language_code),
            "emergency_detected": False,
            "safety_warnings": [],
            "next_actions": ["Ask about specific schemes", "Check eligibility", "Learn about application process"]
        }
    
    def _get_topic_recommendations(self, topic: str) -> List[str]:
        """Get recommendations for related topics based on current topic."""
        recommendations_map = {
            "government_schemes_overview": ["jsy_information", "eligibility_checker", "application_process"],
            "jsy_information": ["eligibility_checker", "application_process", "regional_variations"],
            "pmsma_information": ["jssk_information", "application_process", "scheme_benefits"],
            "jssk_information": ["jsy_information", "pmsma_information", "scheme_benefits"],
            "rch_programs": ["swasth_nari_initiatives", "eligibility_checker", "scheme_benefits"],
            "swasth_nari_initiatives": ["rch_programs", "eligibility_checker", "application_process"],
            "eligibility_checker": ["application_process", "regional_variations", "scheme_benefits"],
            "application_process": ["eligibility_checker", "regional_variations", "scheme_benefits"],
            "regional_variations": ["application_process", "eligibility_checker", "scheme_benefits"],
            "scheme_benefits": ["eligibility_checker", "application_process", "regional_variations"]
        }
        
        return recommendations_map.get(topic, ["government_schemes_overview", "eligibility_checker"])
    
    # Eligibility checking helper methods
    
    def _check_jsy_eligibility(self, user_profile: Dict[str, Any], scheme: GovernmentScheme) -> Dict[str, Any]:
        """Check JSY eligibility based on user profile."""
        result = {
            "eligible": True,
            "scheme_name": scheme.scheme_name,
            "reason": "",
            "recommendations": [],
            "missing_criteria": [],
            "next_steps": []
        }
        
        # Check age requirement
        age = user_profile.get("age", 0)
        if age < 19:
            result["eligible"] = False
            result["missing_criteria"].append("Must be 19 years or older")
        
        # Check pregnancy status
        is_pregnant = user_profile.get("is_pregnant", False)
        if not is_pregnant:
            result["eligible"] = False
            result["missing_criteria"].append("Must be pregnant")
        
        # Check BPL status or state
        is_bpl = user_profile.get("is_bpl", False)
        state = user_profile.get("state", "").lower()
        lps_states = ["uttar_pradesh", "bihar", "jharkhand", "madhya_pradesh", "chhattisgarh", "assam", "rajasthan", "odisha", "uttarakhand"]
        
        if not is_bpl and state not in lps_states:
            result["eligible"] = False
            result["missing_criteria"].append("Must have BPL card or be in Low Performing State")
        
        # Check number of children
        children_count = user_profile.get("children_count", 0)
        if children_count >= 2:
            result["eligible"] = False
            result["missing_criteria"].append("Cash assistance limited to first two live births")
        
        if result["eligible"]:
            result["reason"] = "You are eligible for JSY benefits"
            result["next_steps"] = [
                "Register with ASHA worker",
                "Complete ANC checkups",
                "Plan delivery at government facility"
            ]
        else:
            result["reason"] = "You do not meet all JSY eligibility criteria"
            result["recommendations"] = [
                "Check other schemes like JSSK (no eligibility restrictions)",
                "Contact ASHA worker for guidance"
            ]
        
        return result
    
    def _check_pmsma_eligibility(self, user_profile: Dict[str, Any], scheme: GovernmentScheme) -> Dict[str, Any]:
        """Check PMSMA eligibility based on user profile."""
        result = {
            "eligible": True,
            "scheme_name": scheme.scheme_name,
            "reason": "You are eligible for PMSMA services",
            "recommendations": [],
            "missing_criteria": [],
            "next_steps": [
                "Visit government health facility on 9th of any month",
                "Bring pregnancy registration card",
                "Get comprehensive ANC checkup"
            ]
        }
        
        # PMSMA has minimal eligibility criteria
        is_pregnant = user_profile.get("is_pregnant", False)
        pregnancy_months = user_profile.get("pregnancy_months", 0)
        
        if not is_pregnant:
            result["eligible"] = False
            result["missing_criteria"].append("Must be pregnant")
            result["reason"] = "PMSMA is for pregnant women only"
        elif pregnancy_months < 4:
            result["eligible"] = False
            result["missing_criteria"].append("Must be at least 4 months pregnant")
            result["reason"] = "PMSMA is for second and third trimester"
        
        if not result["eligible"]:
            result["recommendations"] = [
                "Wait until second trimester for PMSMA",
                "Continue regular ANC checkups",
                "Register for other schemes"
            ]
        
        return result
    
    def _check_jssk_eligibility(self, user_profile: Dict[str, Any], scheme: GovernmentScheme) -> Dict[str, Any]:
        """Check JSSK eligibility based on user profile."""
        # JSSK has no eligibility restrictions
        return {
            "eligible": True,
            "scheme_name": scheme.scheme_name,
            "reason": "JSSK is available to all pregnant women and newborns",
            "recommendations": [],
            "missing_criteria": [],
            "next_steps": [
                "Register at government health facility",
                "Plan delivery at registered facility",
                "Avail all free services"
            ]
        }
    
    def _check_rch_eligibility(self, user_profile: Dict[str, Any], scheme: GovernmentScheme) -> Dict[str, Any]:
        """Check RCH eligibility based on user profile."""
        result = {
            "eligible": True,
            "scheme_name": scheme.scheme_name,
            "reason": "You are eligible for RCH services",
            "recommendations": [],
            "missing_criteria": [],
            "next_steps": [
                "Visit government health facility",
                "Get counseling on family planning",
                "Choose appropriate services"
            ]
        }
        
        age = user_profile.get("age", 0)
        if age < 15 or age > 49:
            result["eligible"] = False
            result["missing_criteria"].append("Must be between 15-49 years for reproductive health services")
            result["reason"] = "RCH services are for reproductive age group (15-49 years)"
            result["recommendations"] = [
                "Check adolescent health services if under 15",
                "Consult healthcare provider for age-appropriate services"
            ]
        
        return result
    
    def _check_swasth_nari_eligibility(self, user_profile: Dict[str, Any], scheme: GovernmentScheme) -> Dict[str, Any]:
        """Check Swasth Nari eligibility based on user profile."""
        result = {
            "eligible": True,
            "scheme_name": scheme.scheme_name,
            "reason": "You are eligible for Swasth Nari programs",
            "recommendations": [],
            "missing_criteria": [],
            "next_steps": [
                "Join community health programs",
                "Contact ASHA worker for enrollment",
                "Participate in health education sessions"
            ]
        }
        
        age = user_profile.get("age", 0)
        if age < 18:
            result["eligible"] = False
            result["missing_criteria"].append("Must be 18 years or older")
            result["reason"] = "Swasth Nari is for adult women (18+ years)"
            result["recommendations"] = [
                "Wait until 18 years of age",
                "Participate in adolescent health programs"
            ]
        
        return result
    
    # Application guidance helper methods
    
    def _generate_application_steps(self, scheme: GovernmentScheme) -> List[str]:
        """Generate detailed application steps for a scheme."""
        base_steps = [
            "Gather all required documents",
            "Visit nearest government health facility or contact ASHA worker",
            "Complete registration process",
            "Follow scheme-specific procedures",
            "Maintain all documentation for future reference"
        ]
        
        # Customize steps based on scheme type
        if scheme.scheme_name.startswith("Janani Suraksha"):
            return [
                "Check eligibility (BPL status, age, pregnancy)",
                "Gather documents: BPL card, pregnancy card, Aadhaar, bank details",
                "Contact ASHA worker in your area",
                "Register for JSY during pregnancy",
                "Complete at least 3 ANC checkups",
                "Plan delivery at government health facility",
                "Receive cash assistance after delivery"
            ]
        elif "PMSMA" in scheme.scheme_name:
            return [
                "Confirm pregnancy (minimum 4 months)",
                "Bring pregnancy registration card and ID proof",
                "Visit government health facility on 9th of any month",
                "Register for PMSMA comprehensive checkup",
                "Receive thorough examination by specialist",
                "Follow up on any identified complications",
                "Continue regular ANC visits"
            ]
        elif "JSSK" in scheme.scheme_name:
            return [
                "Visit government health facility during pregnancy",
                "Register for JSSK services (no eligibility criteria)",
                "Plan delivery at registered government facility",
                "Avail free delivery services including C-section if needed",
                "Receive free medicines and diagnostics",
                "Get free newborn care up to 30 days",
                "Use free transport services as needed"
            ]
        
        return base_steps
    
    def _get_application_timeline(self, scheme_name: str) -> str:
        """Get estimated timeline for scheme application and benefits."""
        timelines = {
            self.SCHEME_JSY: "Registration during pregnancy, benefits after delivery (1-2 weeks for cash transfer)",
            self.SCHEME_PMSMA: "Immediate registration, services available on 9th of every month",
            self.SCHEME_JSSK: "Registration during pregnancy, services available immediately during delivery",
            self.SCHEME_RCH: "Immediate registration and services available",
            self.SCHEME_SWASTH_NARI: "Ongoing enrollment, programs run continuously"
        }
        return timelines.get(scheme_name, "Contact health facility for specific timeline")
    
    def _get_application_tips(self, scheme_name: str) -> List[str]:
        """Get helpful tips for scheme application."""
        general_tips = [
            "Keep multiple copies of all documents",
            "Maintain a file with all scheme-related papers",
            "Get receipt for every submission",
            "Note down contact numbers of ASHA worker and health facility",
            "Ask questions if anything is unclear"
        ]
        
        scheme_specific_tips = {
            self.SCHEME_JSY: [
                "Register early in pregnancy for better tracking",
                "Ensure bank account is active and linked to Aadhaar",
                "Complete all ANC visits for full benefits"
            ],
            self.SCHEME_PMSMA: [
                "Mark 9th of every month in calendar",
                "Arrive early at health facility on PMSMA day",
                "Bring previous medical reports if available"
            ],
            self.SCHEME_JSSK: [
                "Inform family about free services available",
                "Don't pay for any services covered under JSSK",
                "Report any demand for payment to authorities"
            ]
        }
        
        tips = general_tips.copy()
        if scheme_name in scheme_specific_tips:
            tips.extend(scheme_specific_tips[scheme_name])
        
        return tips
    
    def _get_common_application_issues(self, scheme_name: str) -> List[str]:
        """Get common issues and solutions for scheme applications."""
        common_issues = [
            "Document verification delays - Keep original and copies ready",
            "Bank account linking issues - Ensure Aadhaar is linked to bank account",
            "Communication barriers - Ask for translator or bring someone who speaks local language",
            "Long waiting times - Visit during less busy hours or make appointment",
            "Incomplete information - Ask ASHA worker to explain all requirements clearly"
        ]
        
        return common_issues