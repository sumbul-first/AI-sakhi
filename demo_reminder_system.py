#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo for AI Sakhi Reminder System
Tests prenatal appointment reminders and notification scheduling
"""

from datetime import datetime, timedelta, timezone
from core.reminder_system import ReminderSystem, ReminderType, ReminderStatus


def demo_reminder_system():
    """Demonstrate reminder system functionality."""
    print("🔔 AI Sakhi Reminder System Demo")
    print("=" * 50)
    
    # Create reminder system
    reminder_system = ReminderSystem()
    
    # Demo 1: Create prenatal appointment reminder
    print("\n1. Creating Prenatal Appointment Reminder")
    print("-" * 50)
    
    appointment_date = datetime.now(timezone.utc) + timedelta(days=1, hours=10)
    reminder = reminder_system.create_prenatal_appointment_reminder(
        user_id="user_123",
        appointment_date=appointment_date,
        doctor_name="Dr. Sharma",
        clinic_name="Community Health Center",
        language_code="hi"
    )
    
    print(f"✅ Created reminder: {reminder.reminder_id}")
    print(f"   Title: {reminder.title}")
    print(f"   Description: {reminder.description}")
    print(f"   Scheduled for: {reminder.scheduled_time}")
    print(f"   Status: {reminder.status.value}")
    
    # Demo 2: Create multiple reminders
    print("\n2. Creating Multiple Reminders")
    print("-" * 50)
    
    # Vaccination reminder
    vax_time = datetime.now(timezone.utc) + timedelta(days=7)
    vax_reminder = reminder_system.create_reminder(
        user_id="user_123",
        reminder_type=ReminderType.VACCINATION,
        title="Vaccination Reminder",
        description="Time for your tetanus vaccination",
        scheduled_time=vax_time,
        language_code="en"
    )
    print(f"✅ Created vaccination reminder: {vax_reminder.reminder_id}")
    
    # Checkup reminder
    checkup_time = datetime.now(timezone.utc) + timedelta(days=14)
    checkup_reminder = reminder_system.create_reminder(
        user_id="user_123",
        reminder_type=ReminderType.CHECKUP,
        title="Monthly Checkup",
        description="Time for your monthly health checkup",
        scheduled_time=checkup_time,
        language_code="hi"
    )
    print(f"✅ Created checkup reminder: {checkup_reminder.reminder_id}")
    
    # Demo 3: Get user reminders
    print("\n3. Getting User Reminders")
    print("-" * 50)
    
    user_reminders = reminder_system.get_user_reminders("user_123")
    print(f"Total reminders for user_123: {len(user_reminders)}")
    for r in user_reminders:
        print(f"   - {r.title} ({r.reminder_type.value}) - {r.scheduled_time}")
    
    # Demo 4: Get upcoming reminders
    print("\n4. Getting Upcoming Reminders (48 hours)")
    print("-" * 50)
    
    upcoming = reminder_system.get_upcoming_reminders("user_123", hours_ahead=48)
    print(f"Upcoming reminders: {len(upcoming)}")
    for r in upcoming:
        hours_until = (r.scheduled_time - datetime.now(timezone.utc)).total_seconds() / 3600
        print(f"   - {r.title} in {hours_until:.1f} hours")
    
    # Demo 5: Create a due reminder (for testing)
    print("\n5. Creating and Processing Due Reminder")
    print("-" * 50)
    
    due_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    due_reminder = reminder_system.create_reminder(
        user_id="user_123",
        reminder_type=ReminderType.MEDICATION,
        title="Medication Reminder",
        description="Time to take your iron supplement",
        scheduled_time=due_time,
        language_code="hi"
    )
    print(f"✅ Created due reminder: {due_reminder.reminder_id}")
    
    # Process due reminders
    notifications = reminder_system.process_due_reminders()
    print(f"\n📬 Processed {len(notifications)} due reminders:")
    for notif in notifications:
        print(f"   - {notif['title']}")
        print(f"     User: {notif['user_id']}")
        print(f"     Methods: {', '.join(notif['notification_methods'])}")
    
    # Demo 6: Acknowledge reminder
    print("\n6. Acknowledging Reminder")
    print("-" * 50)
    
    success = reminder_system.acknowledge_reminder(due_reminder.reminder_id)
    if success:
        updated = reminder_system.get_reminder(due_reminder.reminder_id)
        print(f"✅ Reminder acknowledged")
        print(f"   Status: {updated.status.value}")
        print(f"   Acknowledged at: {updated.acknowledged_at}")
    
    # Demo 7: Reschedule reminder
    print("\n7. Rescheduling Reminder")
    print("-" * 50)
    
    new_time = appointment_date + timedelta(days=1)
    success = reminder_system.reschedule_reminder(reminder.reminder_id, new_time)
    if success:
        updated = reminder_system.get_reminder(reminder.reminder_id)
        print(f"✅ Reminder rescheduled")
        print(f"   Old time: {appointment_date}")
        print(f"   New time: {updated.scheduled_time}")
    
    # Demo 8: Cancel reminder
    print("\n8. Cancelling Reminder")
    print("-" * 50)
    
    success = reminder_system.cancel_reminder(vax_reminder.reminder_id)
    if success:
        updated = reminder_system.get_reminder(vax_reminder.reminder_id)
        print(f"✅ Reminder cancelled")
        print(f"   Status: {updated.status.value}")
    
    # Demo 9: Get statistics
    print("\n9. Reminder Statistics")
    print("-" * 50)
    
    stats = reminder_system.get_reminder_statistics("user_123")
    print(f"Total reminders: {stats['total_reminders']}")
    print(f"Upcoming: {stats['upcoming_count']}")
    print(f"Overdue: {stats['overdue_count']}")
    print("\nBy Status:")
    for status, count in stats['by_status'].items():
        print(f"   {status}: {count}")
    print("\nBy Type:")
    for rtype, count in stats['by_type'].items():
        print(f"   {rtype}: {count}")
    
    # Demo 10: Health check
    print("\n10. System Health Check")
    print("-" * 50)
    
    health = reminder_system.health_check()
    print(f"Status: {health['status']}")
    print(f"Total reminders: {health['total_reminders']}")
    print(f"Scheduled: {health['scheduled_reminders']}")
    print(f"Due: {health['due_reminders']}")
    
    # Demo 11: Multi-language support
    print("\n11. Multi-Language Reminders")
    print("-" * 50)
    
    languages = ['hi', 'en', 'bn', 'ta', 'te', 'mr']
    for lang in languages:
        appt_date = datetime.now(timezone.utc) + timedelta(days=2)
        r = reminder_system.create_prenatal_appointment_reminder(
            user_id="user_456",
            appointment_date=appt_date,
            doctor_name="Dr. Patel",
            language_code=lang
        )
        print(f"{lang}: {r.title}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")


if __name__ == '__main__':
    demo_reminder_system()
