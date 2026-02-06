#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reminder System for AI Sakhi Voice-First Health Companion application.

This module provides the ReminderSystem class for scheduling and managing
prenatal appointment reminders and other health-related notifications.

Requirements: 4.3
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from enum import Enum


class ReminderType(Enum):
    """Types of reminders supported by the system."""
    PRENATAL_APPOINTMENT = "prenatal_appointment"
    VACCINATION = "vaccination"
    MEDICATION = "medication"
    CHECKUP = "checkup"
    GENERAL = "general"


class ReminderStatus(Enum):
    """Status of a reminder."""
    SCHEDULED = "scheduled"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Reminder:
    """Represents a health reminder."""
    reminder_id: str
    user_id: str
    reminder_type: ReminderType
    title: str
    description: str
    scheduled_time: datetime
    language_code: str = 'hi'
    status: ReminderStatus = ReminderStatus.SCHEDULED
    notification_methods: List[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.notification_methods is None:
            self.notification_methods = ['voice', 'text']
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reminder to dictionary."""
        data = asdict(self)
        data['reminder_type'] = self.reminder_type.value
        data['status'] = self.status.value
        data['scheduled_time'] = self.scheduled_time.isoformat()
        data['created_at'] = self.created_at.isoformat()
        if self.sent_at:
            data['sent_at'] = self.sent_at.isoformat()
        if self.acknowledged_at:
            data['acknowledged_at'] = self.acknowledged_at.isoformat()
        return data


class ReminderSystem:
    """Manages health reminders and notifications."""
    
    def __init__(self, storage_backend=None):
        """Initialize the ReminderSystem."""
        self.logger = logging.getLogger(__name__)
        self.storage = storage_backend or {}  # In-memory storage for demo
        self.reminders: Dict[str, Reminder] = {}
        self._load_reminders()
    
    def create_reminder(self, user_id: str, reminder_type: ReminderType,
                       title: str, description: str, scheduled_time: datetime,
                       language_code: str = 'hi', 
                       notification_methods: List[str] = None,
                       metadata: Dict[str, Any] = None) -> Reminder:
        """Create a new reminder."""
        try:
            # Generate unique reminder ID
            reminder_id = self._generate_reminder_id(user_id, scheduled_time)
            
            # Create reminder object
            reminder = Reminder(
                reminder_id=reminder_id,
                user_id=user_id,
                reminder_type=reminder_type,
                title=title,
                description=description,
                scheduled_time=scheduled_time,
                language_code=language_code,
                notification_methods=notification_methods,
                metadata=metadata
            )
            
            # Store reminder
            self.reminders[reminder_id] = reminder
            self._save_reminder(reminder)
            
            self.logger.info(f"Created reminder {reminder_id} for user {user_id}")
            return reminder
            
        except Exception as e:
            self.logger.error(f"Error creating reminder: {e}")
            raise
    
    def create_prenatal_appointment_reminder(self, user_id: str, 
                                            appointment_date: datetime,
                                            doctor_name: str = None,
                                            clinic_name: str = None,
                                            language_code: str = 'hi') -> Reminder:
        """Create a prenatal appointment reminder."""
        # Schedule reminder 24 hours before appointment
        reminder_time = appointment_date - timedelta(hours=24)
        
        title = self._get_prenatal_title(language_code)
        description = self._get_prenatal_description(
            appointment_date, doctor_name, clinic_name, language_code
        )
        
        metadata = {
            'appointment_date': appointment_date.isoformat(),
            'doctor_name': doctor_name,
            'clinic_name': clinic_name,
            'appointment_type': 'prenatal'
        }
        
        return self.create_reminder(
            user_id=user_id,
            reminder_type=ReminderType.PRENATAL_APPOINTMENT,
            title=title,
            description=description,
            scheduled_time=reminder_time,
            language_code=language_code,
            metadata=metadata
        )
    
    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """Get a reminder by ID."""
        return self.reminders.get(reminder_id)
    
    def get_user_reminders(self, user_id: str, 
                          status: Optional[ReminderStatus] = None) -> List[Reminder]:
        """Get all reminders for a user."""
        user_reminders = [
            r for r in self.reminders.values() 
            if r.user_id == user_id
        ]
        
        if status:
            user_reminders = [r for r in user_reminders if r.status == status]
        
        return sorted(user_reminders, key=lambda r: r.scheduled_time)
    
    def get_upcoming_reminders(self, user_id: str, 
                              hours_ahead: int = 48) -> List[Reminder]:
        """Get upcoming reminders for a user."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(hours=hours_ahead)
        
        upcoming = [
            r for r in self.reminders.values()
            if r.user_id == user_id 
            and r.status == ReminderStatus.SCHEDULED
            and now <= r.scheduled_time <= cutoff
        ]
        
        return sorted(upcoming, key=lambda r: r.scheduled_time)
    
    def get_due_reminders(self) -> List[Reminder]:
        """Get all reminders that are due to be sent."""
        now = datetime.now(timezone.utc)
        
        due = [
            r for r in self.reminders.values()
            if r.status == ReminderStatus.SCHEDULED
            and r.scheduled_time <= now
        ]
        
        return sorted(due, key=lambda r: r.scheduled_time)
    
    def mark_reminder_sent(self, reminder_id: str) -> bool:
        """Mark a reminder as sent."""
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False
        
        reminder.status = ReminderStatus.SENT
        reminder.sent_at = datetime.now(timezone.utc)
        self._save_reminder(reminder)
        
        self.logger.info(f"Marked reminder {reminder_id} as sent")
        return True
    
    def acknowledge_reminder(self, reminder_id: str) -> bool:
        """Mark a reminder as acknowledged by the user."""
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False
        
        reminder.status = ReminderStatus.ACKNOWLEDGED
        reminder.acknowledged_at = datetime.now(timezone.utc)
        self._save_reminder(reminder)
        
        self.logger.info(f"Reminder {reminder_id} acknowledged")
        return True
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a reminder."""
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False
        
        reminder.status = ReminderStatus.CANCELLED
        self._save_reminder(reminder)
        
        self.logger.info(f"Cancelled reminder {reminder_id}")
        return True
    
    def reschedule_reminder(self, reminder_id: str, 
                           new_time: datetime) -> bool:
        """Reschedule a reminder to a new time."""
        reminder = self.get_reminder(reminder_id)
        if not reminder:
            return False
        
        old_time = reminder.scheduled_time
        reminder.scheduled_time = new_time
        reminder.status = ReminderStatus.SCHEDULED
        self._save_reminder(reminder)
        
        self.logger.info(f"Rescheduled reminder {reminder_id} from {old_time} to {new_time}")
        return True
    
    def process_due_reminders(self) -> List[Dict[str, Any]]:
        """Process all due reminders and return notification data."""
        due_reminders = self.get_due_reminders()
        notifications = []
        
        for reminder in due_reminders:
            try:
                notification = self._create_notification(reminder)
                notifications.append(notification)
                self.mark_reminder_sent(reminder.reminder_id)
            except Exception as e:
                self.logger.error(f"Error processing reminder {reminder.reminder_id}: {e}")
        
        return notifications
    
    def cleanup_expired_reminders(self, days_old: int = 30) -> int:
        """Clean up old reminders."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        expired_count = 0
        
        for reminder in list(self.reminders.values()):
            if reminder.scheduled_time < cutoff and reminder.status in [
                ReminderStatus.SENT, ReminderStatus.ACKNOWLEDGED, ReminderStatus.CANCELLED
            ]:
                reminder.status = ReminderStatus.EXPIRED
                self._save_reminder(reminder)
                expired_count += 1
        
        self.logger.info(f"Marked {expired_count} reminders as expired")
        return expired_count
    
    def get_reminder_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get reminder statistics."""
        reminders = self.reminders.values()
        if user_id:
            reminders = [r for r in reminders if r.user_id == user_id]
        
        stats = {
            'total_reminders': len(list(reminders)),
            'by_status': {},
            'by_type': {},
            'upcoming_count': 0,
            'overdue_count': 0
        }
        
        now = datetime.now(timezone.utc)
        
        for reminder in reminders:
            # Count by status
            status_key = reminder.status.value
            stats['by_status'][status_key] = stats['by_status'].get(status_key, 0) + 1
            
            # Count by type
            type_key = reminder.reminder_type.value
            stats['by_type'][type_key] = stats['by_type'].get(type_key, 0) + 1
            
            # Count upcoming and overdue
            if reminder.status == ReminderStatus.SCHEDULED:
                if reminder.scheduled_time > now:
                    stats['upcoming_count'] += 1
                else:
                    stats['overdue_count'] += 1
        
        return stats
    
    def _generate_reminder_id(self, user_id: str, scheduled_time: datetime) -> str:
        """Generate a unique reminder ID."""
        timestamp = scheduled_time.strftime('%Y%m%d%H%M%S')
        return f"reminder_{user_id}_{timestamp}"
    
    def _create_notification(self, reminder: Reminder) -> Dict[str, Any]:
        """Create notification data from a reminder."""
        return {
            'reminder_id': reminder.reminder_id,
            'user_id': reminder.user_id,
            'title': reminder.title,
            'description': reminder.description,
            'language_code': reminder.language_code,
            'notification_methods': reminder.notification_methods,
            'metadata': reminder.metadata,
            'scheduled_time': reminder.scheduled_time.isoformat()
        }
    
    def _get_prenatal_title(self, language_code: str) -> str:
        """Get prenatal appointment title in specified language."""
        titles = {
            'hi': 'प्रसवपूर्व जांच की याद',
            'en': 'Prenatal Appointment Reminder',
            'bn': 'প্রসবপূর্ব পরীক্ষার অনুস্মারক',
            'ta': 'பிரசவத்திற்கு முந்தைய சந்திப்பு நினைவூட்டல்',
            'te': 'ప్రసవ పూర్వ అపాయింట్‌మెంట్ రిమైండర్',
            'mr': 'प्रसूतीपूर्व तपासणी स्मरणपत्र'
        }
        return titles.get(language_code, titles['hi'])
    
    def _get_prenatal_description(self, appointment_date: datetime,
                                  doctor_name: Optional[str],
                                  clinic_name: Optional[str],
                                  language_code: str) -> str:
        """Get prenatal appointment description in specified language."""
        date_str = appointment_date.strftime('%d/%m/%Y %H:%M')
        
        templates = {
            'hi': f'आपकी प्रसवपूर्व जांच {date_str} को है।',
            'en': f'Your prenatal checkup is scheduled for {date_str}.',
            'bn': f'আপনার প্রসবপূর্ব পরীক্ষা {date_str} তারিখে নির্ধারিত।',
            'ta': f'உங்கள் பிரசவத்திற்கு முந்தைய பரிசோதனை {date_str} அன்று திட்டமிடப்பட்டுள்ளது.',
            'te': f'మీ ప్రసవ పూర్వ తనిఖీ {date_str}కి షెడ్యూల్ చేయబడింది.',
            'mr': f'तुमची प्रसूतीपूर्व तपासणी {date_str} रोजी आहे.'
        }
        
        description = templates.get(language_code, templates['hi'])
        
        if doctor_name:
            description += f" डॉक्टर: {doctor_name}।" if language_code == 'hi' else f" Doctor: {doctor_name}."
        if clinic_name:
            description += f" क्लिनिक: {clinic_name}।" if language_code == 'hi' else f" Clinic: {clinic_name}."
        
        return description
    
    def _save_reminder(self, reminder: Reminder) -> None:
        """Save reminder to storage."""
        try:
            self.storage[reminder.reminder_id] = reminder.to_dict()
        except Exception as e:
            self.logger.error(f"Error saving reminder: {e}")
    
    def _load_reminders(self) -> None:
        """Load reminders from storage."""
        try:
            for reminder_id, data in self.storage.items():
                # Reconstruct reminder from stored data
                # This is simplified - in production would use proper deserialization
                pass
        except Exception as e:
            self.logger.error(f"Error loading reminders: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the reminder system."""
        return {
            "status": "healthy",
            "total_reminders": len(self.reminders),
            "scheduled_reminders": len([r for r in self.reminders.values() 
                                       if r.status == ReminderStatus.SCHEDULED]),
            "due_reminders": len(self.get_due_reminders()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Utility functions
def create_reminder_system(storage_backend=None) -> ReminderSystem:
    """Factory function to create a ReminderSystem instance."""
    return ReminderSystem(storage_backend)
