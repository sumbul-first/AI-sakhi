#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Safety Validation System for AI Sakhi Voice-First Health Companion.

This module ensures medical boundary compliance by detecting and preventing
medical diagnoses while providing educational guidance.

Requirements: 10.1, 10.2, 10.4
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class SafetyLevel(Enum):
    """Safety levels for content validation."""
    SAFE = "safe"
    CAUTION = "caution"
    UNSAFE = "unsafe"
    MEDICAL_REFERRAL = "medical_referral"


class ContentType(Enum):
    """Types of content being validated."""
    USER_QUERY = "user_query"
    SYSTEM_RESPONSE = "system_response"
    MODULE_CONTENT = "module_content"


@dataclass
class SafetyValidationResult:
    """Result of content safety validation."""
    is_safe: bool
    safety_level: SafetyLevel
    content_type: ContentType
    detected_issues: List[str]
    recommendations: List[str]
    requires_medical_referral: bool
    confidence_score: float
    flagged_terms: List[str] = None
    
    def __post_init__(self):
        if self.flagged_terms is None:
            self.flagged_terms = []


class ContentSafetyValidator:
    """Validates content for medical boundary compliance."""
    
    # Medical diagnosis keywords that should trigger referral
    DIAGNOSIS_KEYWORDS = [
        # English - focus on diagnosis/prescription actions, not general terms
        r'\b(diagnose|diagnosis|prescribe|prescription)\b',
        r'\b(medication dosage|drug treatment)\b',
        r'\b(surgery|operation|medical procedure)\b',
        r'\b(test results|lab results|blood test results)\b',
        r'\b(you have (a |an )?(disease|cancer|tumor|syndrome))\b',
        
        # Hindi
        r'\b(निदान|दवा की खुराक|सर्जरी|ऑपरेशन)\b',
        r'\b(परीक्षण परिणाम|रक्त परीक्षण)\b',
        r'\b(आपको (रोग|कैंसर|ट्यूमर|संक्रमण) है)\b',
        
        # Bengali
        r'\b(রোগ নির্ণয়|ওষুধের ডোজ|অস্ত্রোপচার)\b',
        r'\b(আপনার (ক্যান্সার|টিউমার|সংক্রমণ) আছে)\b'
    ]
    
    # Symptoms that require medical attention
    SERIOUS_SYMPTOMS = [
        # English
        r'\b(severe pain|chest pain|difficulty breathing|heavy bleeding)\b',
        r'\b(unconscious|seizure|stroke|heart attack)\b',
        r'\b(high fever|persistent vomiting|severe headache)\b',
        
        # Hindi
        r'\b(गंभीर दर्द|सीने में दर्द|सांस लेने में कठिनाई|भारी रक्तस्राव)\b',
        r'\b(बेहोश|दौरा|स्ट्रोक|दिल का दौरा)\b',
        r'\b(तेज बुखार|लगातार उल्टी|गंभीर सिरदर्द)\b',
        
        # Bengali
        r'\b(গুরুতর ব্যথা|বুকে ব্যথা|শ্বাসকষ্ট|ভারী রক্তপাত)\b',
        r'\b(অজ্ঞান|খিঁচুনি|স্ট্রোক|হার্ট অ্যাটাক)\b'
    ]
    
    # Educational terms that are acceptable
    EDUCATIONAL_TERMS = [
        r'\b(information|education|awareness|knowledge|understanding)\b',
        r'\b(learn|know|understand|aware)\b',
        r'\b(जानकारी|शिक्षा|जागरूकता|समझ)\b',
        r'\b(তথ্য|শিক্ষা|সচেতনতা|জ্ঞান)\b'
    ]
    
    # Referral phrases
    REFERRAL_PHRASES = {
        'hi': [
            'कृपया डॉक्टर से परामर्श लें',
            'स्वास्थ्य पेशेवर से संपर्क करें',
            'चिकित्सा सलाह के लिए क्लिनिक जाएं'
        ],
        'en': [
            'Please consult a doctor',
            'Contact a healthcare professional',
            'Visit a clinic for medical advice'
        ],
        'bn': [
            'অনুগ্রহ করে একজন ডাক্তারের সাথে পরামর্শ করুন',
            'স্বাস্থ্যসেবা পেশাদারের সাথে যোগাযোগ করুন'
        ]
    }
    
    def __init__(self):
        """Initialize the ContentSafetyValidator."""
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.diagnosis_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.DIAGNOSIS_KEYWORDS
        ]
        self.symptom_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.SERIOUS_SYMPTOMS
        ]
        self.educational_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.EDUCATIONAL_TERMS
        ]
    
    def validate_content(self, content: str, 
                        content_type: ContentType = ContentType.SYSTEM_RESPONSE,
                        language_code: str = 'hi') -> SafetyValidationResult:
        """Validate content for medical boundary compliance."""
        try:
            detected_issues = []
            flagged_terms = []
            requires_referral = False
            
            # Check for diagnosis keywords
            diagnosis_found = self._check_diagnosis_keywords(content)
            if diagnosis_found:
                detected_issues.append("medical_diagnosis_detected")
                flagged_terms.extend(diagnosis_found)
                requires_referral = True
            
            # Check for serious symptoms
            symptoms_found = self._check_serious_symptoms(content)
            if symptoms_found:
                detected_issues.append("serious_symptoms_detected")
                flagged_terms.extend(symptoms_found)
                requires_referral = True
            
            # Check if content is educational
            is_educational = self._is_educational_content(content)
            
            # Determine safety level
            safety_level = self._determine_safety_level(
                detected_issues, is_educational, requires_referral
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                detected_issues, language_code
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                content, detected_issues, is_educational
            )
            
            is_safe = safety_level in [SafetyLevel.SAFE, SafetyLevel.CAUTION]
            
            return SafetyValidationResult(
                is_safe=is_safe,
                safety_level=safety_level,
                content_type=content_type,
                detected_issues=detected_issues,
                recommendations=recommendations,
                requires_medical_referral=requires_referral,
                confidence_score=confidence,
                flagged_terms=flagged_terms
            )
            
        except Exception as e:
            self.logger.error(f"Error validating content: {e}")
            # Fail safe - mark as unsafe if validation fails
            return SafetyValidationResult(
                is_safe=False,
                safety_level=SafetyLevel.UNSAFE,
                content_type=content_type,
                detected_issues=["validation_error"],
                recommendations=["Content validation failed - manual review required"],
                requires_medical_referral=True,
                confidence_score=0.0
            )
    
    def validate_user_query(self, query: str, 
                           language_code: str = 'hi') -> SafetyValidationResult:
        """Validate user query for medical concerns."""
        result = self.validate_content(
            query, ContentType.USER_QUERY, language_code
        )
        
        # Log queries that require medical referral
        if result.requires_medical_referral:
            self.logger.warning(
                f"User query requires medical referral: {query[:50]}..."
            )
        
        return result
    
    def validate_system_response(self, response: str,
                                 language_code: str = 'hi') -> SafetyValidationResult:
        """Validate system response for medical boundary compliance."""
        result = self.validate_content(
            response, ContentType.SYSTEM_RESPONSE, language_code
        )
        
        # System responses should never contain diagnosis
        if "medical_diagnosis_detected" in result.detected_issues:
            self.logger.error(
                f"System response contains medical diagnosis: {response[:50]}..."
            )
        
        return result
    
    def sanitize_response(self, response: str, 
                         language_code: str = 'hi') -> Tuple[str, bool]:
        """Sanitize response by removing medical diagnosis content."""
        validation = self.validate_system_response(response, language_code)
        
        if validation.is_safe:
            return response, False
        
        # Add medical referral if needed
        if validation.requires_medical_referral:
            referral = self._get_referral_message(language_code)
            sanitized = f"{response}\n\n{referral}"
            return sanitized, True
        
        return response, False
    
    def _check_diagnosis_keywords(self, content: str) -> List[str]:
        """Check for medical diagnosis keywords."""
        found_terms = []
        for pattern in self.diagnosis_patterns:
            matches = pattern.findall(content)
            found_terms.extend(matches)
        return found_terms
    
    def _check_serious_symptoms(self, content: str) -> List[str]:
        """Check for serious symptoms requiring medical attention."""
        found_terms = []
        for pattern in self.symptom_patterns:
            matches = pattern.findall(content)
            found_terms.extend(matches)
        return found_terms
    
    def _is_educational_content(self, content: str) -> bool:
        """Check if content is educational in nature."""
        for pattern in self.educational_patterns:
            if pattern.search(content):
                return True
        return False
    
    def _determine_safety_level(self, detected_issues: List[str],
                                is_educational: bool,
                                requires_referral: bool) -> SafetyLevel:
        """Determine overall safety level."""
        if requires_referral:
            return SafetyLevel.MEDICAL_REFERRAL
        
        if detected_issues:
            return SafetyLevel.CAUTION if is_educational else SafetyLevel.UNSAFE
        
        return SafetyLevel.SAFE
    
    def _generate_recommendations(self, detected_issues: List[str],
                                  language_code: str) -> List[str]:
        """Generate recommendations based on detected issues."""
        recommendations = []
        
        if "medical_diagnosis_detected" in detected_issues:
            recommendations.append(
                self._get_recommendation("diagnosis", language_code)
            )
        
        if "serious_symptoms_detected" in detected_issues:
            recommendations.append(
                self._get_recommendation("symptoms", language_code)
            )
        
        return recommendations
    
    def _get_recommendation(self, issue_type: str, 
                           language_code: str) -> str:
        """Get recommendation message for specific issue."""
        recommendations = {
            'diagnosis': {
                'hi': 'यह शैक्षिक जानकारी है। निदान के लिए डॉक्टर से मिलें।',
                'en': 'This is educational information. Consult a doctor for diagnosis.',
                'bn': 'এটি শিক্ষামূলক তথ্য। রোগ নির্ণয়ের জন্য ডাক্তারের সাথে পরামর্শ করুন।'
            },
            'symptoms': {
                'hi': 'गंभीर लक्षणों के लिए तुरंत चिकित्सा सहायता लें।',
                'en': 'Seek immediate medical help for serious symptoms.',
                'bn': 'গুরুতর লক্ষণের জন্য অবিলম্বে চিকিৎসা সহায়তা নিন।'
            }
        }
        
        return recommendations.get(issue_type, {}).get(
            language_code, recommendations[issue_type]['en']
        )
    
    def _get_referral_message(self, language_code: str) -> str:
        """Get medical referral message."""
        phrases = self.REFERRAL_PHRASES.get(language_code, self.REFERRAL_PHRASES['en'])
        return phrases[0]
    
    def _calculate_confidence(self, content: str, 
                             detected_issues: List[str],
                             is_educational: bool) -> float:
        """Calculate confidence score for validation."""
        base_confidence = 0.8
        
        # Reduce confidence if issues detected
        if detected_issues:
            base_confidence -= 0.2 * len(detected_issues)
        
        # Increase confidence if educational
        if is_educational:
            base_confidence += 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def get_safe_response_template(self, topic: str,
                                   language_code: str = 'hi') -> str:
        """Get a safe response template for a topic."""
        templates = {
            'general': {
                'hi': 'यह {topic} के बारे में शैक्षिक जानकारी है। विशिष्ट चिकित्सा सलाह के लिए, कृपया स्वास्थ्य पेशेवर से परामर्श लें।',
                'en': 'This is educational information about {topic}. For specific medical advice, please consult a healthcare professional.',
                'bn': 'এটি {topic} সম্পর্কে শিক্ষামূলক তথ্য। নির্দিষ্ট চিকিৎসা পরামর্শের জন্য, অনুগ্রহ করে একজন স্বাস্থ্যসেবা পেশাদারের সাথে পরামর্শ করুন।'
            }
        }
        
        template = templates['general'].get(language_code, templates['general']['en'])
        return template.format(topic=topic)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the content safety system."""
        return {
            "status": "healthy",
            "patterns_loaded": {
                "diagnosis": len(self.diagnosis_patterns),
                "symptoms": len(self.symptom_patterns),
                "educational": len(self.educational_patterns)
            },
            "supported_languages": list(self.REFERRAL_PHRASES.keys())
        }


# Utility functions
def create_content_safety_validator() -> ContentSafetyValidator:
    """Factory function to create a ContentSafetyValidator instance."""
    return ContentSafetyValidator()


def validate_content_safety(content: str, language_code: str = 'hi') -> bool:
    """Quick validation function."""
    validator = ContentSafetyValidator()
    result = validator.validate_content(content, language_code=language_code)
    return result.is_safe
