#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for AI Sakhi Reminder System
Tests reminder creation, scheduling, and notification delivery
"""

import unittest
from datetime import datetime, timedelta, timezone
from core.reminder_system import (
    ReminderSystem, ReminderType, ReminderStatus, Reminder
)


class TestReminderSystem(unittest.TestCase):
    """Test cases for ReminderSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reminder_system = ReminderSystem()
        self.test_user_id = "test_user_123"
    
    def test_create_reminder(self):
        """Test creating a basic reminder"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        reminder = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Test Reminder",
            description="This is a test reminder",
            scheduled_time=scheduled_time,
            language_code="en"
        )
        
        self.assertIsNotNone(reminder)
        self.assertEqual(reminder.user_id, self.test_user_id)
        self.assertEqual(reminder.title, "Test Reminder")
        self.assertEqual(reminder.status, ReminderStatus.SCHEDULED)
    
    def test_create_prenatal_appointment_reminder(self):
        """Test creating a prenatal appointment reminder"""
        appointment_date = datetime.now(timezone.utc) + timedelta(days=2)
        
        reminder = self.reminder_system.create_prenatal_appointment_reminder(
            user_id=self.test_user_id,
            appointment_date=appointment_date,
            doctor_name="Dr. Test",
            clinic_name="Test Clinic",
            language_code="hi"
        )
        
        self.assertIsNotNone(reminder)
        self.assertEqual(reminder.reminder_type, ReminderType.PRENATAL_APPOINTMENT)
        self.assertIn("प्रसवपूर्व", reminder.title)
        # Reminder should be 24 hours before appointment
        expected_time = appointment_date - timedelta(hours=24)
        self.assertAlmostEqual(
            reminder.scheduled_time.timestamp(),
            expected_time.timestamp(),
            delta=1
        )
    
    def test_get_reminder(self):
        """Test retrieving a reminder by ID"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        created = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.CHECKUP,
            title="Test Checkup",
            description="Test description",
            scheduled_time=scheduled_time
        )
        
        retrieved = self.reminder_system.get_reminder(created.reminder_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.reminder_id, created.reminder_id)
        self.assertEqual(retrieved.title, created.title)
    
    def test_get_user_reminders(self):
        """Test getting all reminders for a user"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        # Create multiple reminders
        for i in range(3):
            self.reminder_system.create_reminder(
                user_id=self.test_user_id,
                reminder_type=ReminderType.GENERAL,
                title=f"Reminder {i}",
                description=f"Description {i}",
                scheduled_time=scheduled_time + timedelta(hours=i)
            )
        
        reminders = self.reminder_system.get_user_reminders(self.test_user_id)
        
        self.assertEqual(len(reminders), 3)
        # Should be sorted by scheduled time
        for i in range(len(reminders) - 1):
            self.assertLessEqual(
                reminders[i].scheduled_time,
                reminders[i + 1].scheduled_time
            )
    
    def test_get_upcoming_reminders(self):
        """Test getting upcoming reminders within time window"""
        now = datetime.now(timezone.utc)
        
        # Create reminders at different times
        self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Soon",
            description="Within 48 hours",
            scheduled_time=now + timedelta(hours=24)
        )
        
        self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Later",
            description="Beyond 48 hours",
            scheduled_time=now + timedelta(hours=72)
        )
        
        upcoming = self.reminder_system.get_upcoming_reminders(
            self.test_user_id, hours_ahead=48
        )
        
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].title, "Soon")
    
    def test_get_due_reminders(self):
        """Test getting reminders that are due"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Create past reminder
        self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.MEDICATION,
            title="Due Reminder",
            description="Should be due",
            scheduled_time=past_time
        )
        
        # Create future reminder
        self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.MEDICATION,
            title="Future Reminder",
            description="Not due yet",
            scheduled_time=future_time
        )
        
        due = self.reminder_system.get_due_reminders()
        
        self.assertGreaterEqual(len(due), 1)
        self.assertTrue(all(r.scheduled_time <= datetime.now(timezone.utc) for r in due))
    
    def test_mark_reminder_sent(self):
        """Test marking a reminder as sent"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        reminder = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Test",
            description="Test",
            scheduled_time=scheduled_time
        )
        
        success = self.reminder_system.mark_reminder_sent(reminder.reminder_id)
        
        self.assertTrue(success)
        updated = self.reminder_system.get_reminder(reminder.reminder_id)
        self.assertEqual(updated.status, ReminderStatus.SENT)
        self.assertIsNotNone(updated.sent_at)
    
    def test_acknowledge_reminder(self):
        """Test acknowledging a reminder"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        reminder = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Test",
            description="Test",
            scheduled_time=scheduled_time
        )
        
        success = self.reminder_system.acknowledge_reminder(reminder.reminder_id)
        
        self.assertTrue(success)
        updated = self.reminder_system.get_reminder(reminder.reminder_id)
        self.assertEqual(updated.status, ReminderStatus.ACKNOWLEDGED)
        self.assertIsNotNone(updated.acknowledged_at)
    
    def test_cancel_reminder(self):
        """Test cancelling a reminder"""
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        reminder = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Test",
            description="Test",
            scheduled_time=scheduled_time
        )
        
        success = self.reminder_system.cancel_reminder(reminder.reminder_id)
        
        self.assertTrue(success)
        updated = self.reminder_system.get_reminder(reminder.reminder_id)
        self.assertEqual(updated.status, ReminderStatus.CANCELLED)
    
    def test_reschedule_reminder(self):
        """Test rescheduling a reminder"""
        old_time = datetime.now(timezone.utc) + timedelta(days=1)
        new_time = datetime.now(timezone.utc) + timedelta(days=2)
        
        reminder = self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.GENERAL,
            title="Test",
            description="Test",
            scheduled_time=old_time
        )
        
        success = self.reminder_system.reschedule_reminder(
            reminder.reminder_id, new_time
        )
        
        self.assertTrue(success)
        updated = self.reminder_system.get_reminder(reminder.reminder_id)
        self.assertEqual(updated.scheduled_time, new_time)
        self.assertEqual(updated.status, ReminderStatus.SCHEDULED)
    
    def test_process_due_reminders(self):
        """Test processing due reminders"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Create due reminder
        self.reminder_system.create_reminder(
            user_id=self.test_user_id,
            reminder_type=ReminderType.MEDICATION,
            title="Due Reminder",
            description="Should be processed",
            scheduled_time=past_time
        )
        
        notifications = self.reminder_system.process_due_reminders()
        
        self.assertGreaterEqual(len(notifications), 1)
        self.assertIn('title', notifications[0])
        self.assertIn('user_id', notifications[0])
    
    def test_get_reminder_statistics(self):
        """Test getting reminder statistics"""
        # Create fresh reminder system for this test
        test_system = ReminderSystem()
        test_user = "stats_test_user"
        scheduled_time = datetime.now(timezone.utc) + timedelta(days=1)
        
        # Create various reminders
        r1 = test_system.create_reminder(
            user_id=test_user,
            reminder_type=ReminderType.PRENATAL_APPOINTMENT,
            title="Test 1",
            description="Test",
            scheduled_time=scheduled_time
        )
        
        r2 = test_system.create_reminder(
            user_id=test_user,
            reminder_type=ReminderType.VACCINATION,
            title="Test 2",
            description="Test",
            scheduled_time=scheduled_time + timedelta(hours=1)
        )
        
        # Verify reminders were created
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        
        stats = test_system.get_reminder_statistics(test_user)
        
        self.assertIn('total_reminders', stats)
        self.assertIn('by_status', stats)
        self.assertIn('by_type', stats)
        self.assertGreaterEqual(stats['total_reminders'], 2)
    
    def test_multi_language_support(self):
        """Test multi-language reminder creation"""
        appointment_date = datetime.now(timezone.utc) + timedelta(days=1)
        languages = ['hi', 'en', 'bn', 'ta', 'te', 'mr']
        
        for lang in languages:
            reminder = self.reminder_system.create_prenatal_appointment_reminder(
                user_id=self.test_user_id,
                appointment_date=appointment_date,
                language_code=lang
            )
            
            self.assertEqual(reminder.language_code, lang)
            self.assertIsNotNone(reminder.title)
            self.assertIsNotNone(reminder.description)
    
    def test_health_check(self):
        """Test system health check"""
        health = self.reminder_system.health_check()
        
        self.assertIn('status', health)
        self.assertIn('total_reminders', health)
        self.assertIn('scheduled_reminders', health)
        self.assertEqual(health['status'], 'healthy')


def run_reminder_tests():
    """Run all reminder system tests"""
    print("🧪 Running AI Sakhi Reminder System Tests...")
    
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestReminderSystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        print("✅ All reminder system tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"⚠️ {len(result.errors)} error(s) occurred")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_reminder_tests()
    exit(0 if success else 1)
