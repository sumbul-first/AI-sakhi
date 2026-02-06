#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for AI Sakhi Content Safety Validation System
Tests medical boundary compliance and content safety
"""

import unittest
from core.content_safety import (
    ContentSafetyValidator, SafetyLevel, ContentType
)


class TestContentSafetyValidator(unittest.TestCase):
    """Test cases for ContentSafetyValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ContentSafetyValidator()
    
    def test_safe_educational_content(self):
        """Test that educational content is marked as safe"""
        content = "Learn about menstruation and hygiene practices"
        result = self.validator.validate_content(content)
        
        self.assertTrue(result.is_safe)
        self.assertEqual(result.safety_level, SafetyLevel.SAFE)
        self.assertEqual(len(result.detected_issues), 0)
    
    def test_diagnosis_detection_english(self):
        """Test detection of medical diagnosis in English"""
        content = "You have a disease that requires diagnosis"
        result = self.validator.validate_content(content)
        
        self.assertFalse(result.is_safe)
        self.assertIn("medical_diagnosis_detected", result.detected_issues)
        self.assertTrue(result.requires_medical_referral)
    
    def test_diagnosis_detection_hindi(self):
        """Test detection of medical diagnosis in Hindi"""
        content = "आपको एक रोग है जिसका निदान आवश्यक है"
        result = self.validator.validate_content(content, language_code='hi')
        
        self.assertFalse(result.is_safe)
        self.assertIn("medical_diagnosis_detected", result.detected_issues)
        self.assertTrue(result.requires_medical_referral)
    
    def test_serious_symptoms_detection(self):
        """Test detection of serious symptoms"""
        content = "I have severe chest pain and difficulty breathing"
        result = self.validator.validate_content(content)
        
        self.assertFalse(result.is_safe)
        self.assertIn("serious_symptoms_detected", result.detected_issues)
        self.assertTrue(result.requires_medical_referral)
    
    def test_educational_with_caution(self):
        """Test educational content with cautionary terms"""
        content = "Learn about symptoms of infection and when to seek help"
        result = self.validator.validate_content(content)
        
        # Should be safe because it's educational
        self.assertTrue(result.is_safe)
    
    def test_validate_user_query_safe(self):
        """Test validation of safe user query"""
        query = "Tell me about puberty and body changes"
        result = self.validator.validate_user_query(query)
        
        self.assertTrue(result.is_safe)
        self.assertEqual(result.content_type, ContentType.USER_QUERY)
    
    def test_validate_user_query_medical(self):
        """Test validation of medical user query"""
        query = "Can you diagnose my disease?"
        result = self.validator.validate_user_query(query)
        
        self.assertFalse(result.is_safe)
        self.assertTrue(result.requires_medical_referral)
    
    def test_validate_system_response_safe(self):
        """Test validation of safe system response"""
        response = "Here is educational information about menstrual health"
        result = self.validator.validate_system_response(response)
        
        self.assertTrue(result.is_safe)
        self.assertEqual(result.content_type, ContentType.SYSTEM_RESPONSE)
    
    def test_validate_system_response_unsafe(self):
        """Test validation of unsafe system response"""
        response = "You have a disease that needs prescription medication"
        result = self.validator.validate_system_response(response)
        
        self.assertFalse(result.is_safe)
        self.assertIn("medical_diagnosis_detected", result.detected_issues)
    
    def test_sanitize_response_safe(self):
        """Test sanitizing safe response"""
        response = "This is educational information about health"
        sanitized, was_modified = self.validator.sanitize_response(response)
        
        self.assertFalse(was_modified)
        self.assertEqual(sanitized, response)
    
    def test_sanitize_response_with_referral(self):
        """Test sanitizing response that needs referral"""
        response = "You have severe chest pain and need a diagnosis"
        sanitized, was_modified = self.validator.sanitize_response(response, 'en')
        
        self.assertTrue(was_modified)
        self.assertIn("consult", sanitized.lower())
    
    def test_multi_language_support(self):
        """Test multi-language content validation"""
        test_cases = [
            ('hi', 'यह स्वास्थ्य शिक्षा है'),
            ('en', 'This is health education'),
            ('bn', 'এটি স্বাস্থ্য শিক্ষা')
        ]
        
        for lang, content in test_cases:
            result = self.validator.validate_content(content, language_code=lang)
            self.assertTrue(result.is_safe)
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        # Safe content should have high confidence
        safe_result = self.validator.validate_content(
            "Educational information about health"
        )
        self.assertGreater(safe_result.confidence_score, 0.7)
        
        # Unsafe content should have lower confidence
        unsafe_result = self.validator.validate_content(
            "You have a disease requiring diagnosis"
        )
        self.assertLess(unsafe_result.confidence_score, 0.7)
    
    def test_flagged_terms_tracking(self):
        """Test that flagged terms are tracked"""
        content = "You need a diagnosis for this disease"
        result = self.validator.validate_content(content)
        
        self.assertGreater(len(result.flagged_terms), 0)
        self.assertTrue(any('diagnos' in term.lower() for term in result.flagged_terms))
    
    def test_recommendations_generation(self):
        """Test generation of recommendations"""
        content = "Severe symptoms requiring diagnosis"
        result = self.validator.validate_content(content)
        
        self.assertGreater(len(result.recommendations), 0)
    
    def test_get_safe_response_template(self):
        """Test getting safe response templates"""
        template = self.validator.get_safe_response_template(
            "pregnancy", language_code='en'
        )
        
        self.assertIn("educational", template.lower())
        self.assertIn("healthcare professional", template.lower())
    
    def test_health_check(self):
        """Test system health check"""
        health = self.validator.health_check()
        
        self.assertEqual(health['status'], 'healthy')
        self.assertIn('patterns_loaded', health)
        self.assertIn('supported_languages', health)
        self.assertGreater(health['patterns_loaded']['diagnosis'], 0)
    
    def test_empty_content(self):
        """Test validation of empty content"""
        result = self.validator.validate_content("")
        
        self.assertTrue(result.is_safe)
        self.assertEqual(len(result.detected_issues), 0)
    
    def test_mixed_safe_unsafe_content(self):
        """Test content with both safe and unsafe elements"""
        content = "Learn about health education but I need a diagnosis for my disease"
        result = self.validator.validate_content(content)
        
        # Should be flagged as unsafe due to diagnosis request
        self.assertFalse(result.is_safe)
        self.assertTrue(result.requires_medical_referral)


def run_content_safety_tests():
    """Run all content safety tests"""
    print("🧪 Running AI Sakhi Content Safety Tests...")
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(
        TestContentSafetyValidator
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        print("✅ All content safety tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"⚠️ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_content_safety_tests()
    exit(0 if success else 1)
