"""
Data models for AI Sakhi Voice-First Health Companion application.

This module defines the core data structures used throughout the system,
including user sessions, content items, voice interactions, emergency contacts,
and government schemes. All models include validation methods and serialization
support for JSON storage and transmission.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json
import uuid
import re


@dataclass
class UserSession:
    """
    Represents a user session with language preferences, module state, and interaction history.
    
    Attributes:
        session_id: Unique identifier for the session
        language_preference: User's selected language code (e.g., 'hi', 'en', 'bn')
        current_module: Currently active health education module
        interaction_history: List of user interactions and system responses
        emergency_contacts: Dictionary of emergency contact information
        accessibility_preferences: User accessibility settings and preferences
        created_at: Session creation timestamp
        last_active: Last activity timestamp for session timeout management
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    language_preference: str = "en"
    current_module: str = ""
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    emergency_contacts: Dict[str, Any] = field(default_factory=dict)
    accessibility_preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> bool:
        """
        Validates the user session data for integrity.
        
        Returns:
            bool: True if all validation checks pass
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        if not self.session_id or not isinstance(self.session_id, str):
            raise ValueError("Session ID must be a non-empty string")
        
        # Validate language preference is a valid language code
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', self.language_preference):
            raise ValueError("Language preference must be a valid language code (e.g., 'en', 'hi', 'bn-IN')")
        
        # Validate timestamps
        if not isinstance(self.created_at, datetime) or not isinstance(self.last_active, datetime):
            raise ValueError("Timestamps must be datetime objects")
        
        if self.last_active < self.created_at:
            raise ValueError("Last active time cannot be before creation time")
        
        # Validate interaction history structure
        if not isinstance(self.interaction_history, list):
            raise ValueError("Interaction history must be a list")
        
        for interaction in self.interaction_history:
            if not isinstance(interaction, dict):
                raise ValueError("Each interaction must be a dictionary")
        
        return True

    def update_last_active(self) -> None:
        """Updates the last active timestamp to current time."""
        self.last_active = datetime.now(timezone.utc)

    def add_interaction(self, interaction_type: str, content: str, response: str = "") -> None:
        """
        Adds a new interaction to the session history.
        
        Args:
            interaction_type: Type of interaction (e.g., 'voice_query', 'module_access')
            content: User input or interaction content
            response: System response to the interaction
        """
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": interaction_type,
            "content": content,
            "response": response
        }
        self.interaction_history.append(interaction)
        self.update_last_active()

    def to_json(self) -> str:
        """
        Serializes the session to JSON string.
        
        Returns:
            str: JSON representation of the session
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'UserSession':
        """
        Creates a UserSession instance from JSON string.
        
        Args:
            json_str: JSON string representation of the session
            
        Returns:
            UserSession: Deserialized session object
        """
        data = json.loads(json_str)
        # Convert ISO format strings back to datetime objects
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        return cls(**data)


@dataclass
class ContentItem:
    """
    Represents a piece of educational content (audio, video, or text).
    
    Attributes:
        content_id: Unique identifier for the content item
        module_name: Health education module this content belongs to
        topic: Specific topic within the module
        content_type: Type of content ('audio', 'video', 'text')
        language_code: Language of the content
        s3_url: AWS S3 URL for the content file
        duration_seconds: Duration for audio/video content
        transcript: Text transcript of audio/video content
        safety_validated: Whether content has been validated for safety
        created_at: Content creation timestamp
    """
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module_name: str = ""
    topic: str = ""
    content_type: str = ""
    language_code: str = "en"
    s3_url: str = ""
    duration_seconds: int = 0
    transcript: str = ""
    safety_validated: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> bool:
        """
        Validates the content item data for integrity.
        
        Returns:
            bool: True if all validation checks pass
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        if not self.content_id or not isinstance(self.content_id, str):
            raise ValueError("Content ID must be a non-empty string")
        
        if not self.module_name or not isinstance(self.module_name, str):
            raise ValueError("Module name must be a non-empty string")
        
        if not self.topic or not isinstance(self.topic, str):
            raise ValueError("Topic must be a non-empty string")
        
        # Validate content type
        valid_content_types = ['audio', 'video', 'text']
        if self.content_type not in valid_content_types:
            raise ValueError(f"Content type must be one of: {valid_content_types}")
        
        # Validate language code
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', self.language_code):
            raise ValueError("Language code must be valid (e.g., 'en', 'hi', 'bn-IN')")
        
        # Validate S3 URL format
        if self.s3_url and not (self.s3_url.startswith('https://') or self.s3_url.startswith('s3://')):
            raise ValueError("S3 URL must start with 'https://' or 's3://'")
        
        # Validate duration for audio/video content
        if self.content_type in ['audio', 'video'] and self.duration_seconds < 0:
            raise ValueError("Duration must be non-negative for audio/video content")
        
        return True

    def is_multimedia(self) -> bool:
        """Returns True if content is audio or video."""
        return self.content_type in ['audio', 'video']

    def get_display_duration(self) -> str:
        """
        Returns human-readable duration string.
        
        Returns:
            str: Duration in MM:SS format
        """
        if not self.is_multimedia() or self.duration_seconds <= 0:
            return "N/A"
        
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def to_json(self) -> str:
        """
        Serializes the content item to JSON string.
        
        Returns:
            str: JSON representation of the content item
        """
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'ContentItem':
        """
        Creates a ContentItem instance from JSON string.
        
        Args:
            json_str: JSON string representation of the content item
            
        Returns:
            ContentItem: Deserialized content item object
        """
        data = json.loads(json_str)
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class VoiceInteraction:
    """
    Represents a voice interaction between user and system.
    
    Attributes:
        interaction_id: Unique identifier for the interaction
        session_id: Associated user session ID
        user_audio_transcript: Transcribed text from user's audio input
        system_response_text: System's text response
        system_audio_url: URL to system's audio response file
        language_code: Language used in the interaction
        confidence_score: Speech recognition confidence (0.0 to 1.0)
        processing_time_ms: Time taken to process the interaction
        timestamp: When the interaction occurred
    """
    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_audio_transcript: str = ""
    system_response_text: str = ""
    system_audio_url: str = ""
    language_code: str = "en"
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> bool:
        """
        Validates the voice interaction data for integrity.
        
        Returns:
            bool: True if all validation checks pass
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        if not self.interaction_id or not isinstance(self.interaction_id, str):
            raise ValueError("Interaction ID must be a non-empty string")
        
        if not self.session_id or not isinstance(self.session_id, str):
            raise ValueError("Session ID must be a non-empty string")
        
        # Validate language code
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', self.language_code):
            raise ValueError("Language code must be valid (e.g., 'en', 'hi', 'bn-IN')")
        
        # Validate confidence score range
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        # Validate processing time
        if self.processing_time_ms < 0:
            raise ValueError("Processing time must be non-negative")
        
        # Validate audio URL format if provided
        if self.system_audio_url and not (self.system_audio_url.startswith('https://') or self.system_audio_url.startswith('s3://')):
            raise ValueError("System audio URL must start with 'https://' or 's3://'")
        
        return True

    def is_high_confidence(self) -> bool:
        """Returns True if confidence score is above 0.8."""
        return self.confidence_score > 0.8

    def get_processing_time_display(self) -> str:
        """
        Returns human-readable processing time.
        
        Returns:
            str: Processing time with appropriate units
        """
        if self.processing_time_ms < 1000:
            return f"{self.processing_time_ms}ms"
        else:
            seconds = self.processing_time_ms / 1000
            return f"{seconds:.1f}s"

    def to_json(self) -> str:
        """
        Serializes the voice interaction to JSON string.
        
        Returns:
            str: JSON representation of the voice interaction
        """
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'VoiceInteraction':
        """
        Creates a VoiceInteraction instance from JSON string.
        
        Args:
            json_str: JSON string representation of the voice interaction
            
        Returns:
            VoiceInteraction: Deserialized voice interaction object
        """
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class EmergencyContact:
    """
    Represents an emergency contact resource.
    
    Attributes:
        contact_id: Unique identifier for the contact
        contact_type: Type of contact ('helpline', 'medical', 'counseling')
        phone_number: Contact phone number
        region: Geographic region served
        language_support: List of supported languages
        availability_hours: Hours when contact is available
        description: Description of services provided
    """
    contact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_type: str = ""
    phone_number: str = ""
    region: str = ""
    language_support: List[str] = field(default_factory=list)
    availability_hours: str = ""
    description: str = ""

    def validate(self) -> bool:
        """
        Validates the emergency contact data for integrity.
        
        Returns:
            bool: True if all validation checks pass
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        if not self.contact_id or not isinstance(self.contact_id, str):
            raise ValueError("Contact ID must be a non-empty string")
        
        # Validate contact type
        valid_contact_types = ['helpline', 'medical', 'counseling']
        if self.contact_type not in valid_contact_types:
            raise ValueError(f"Contact type must be one of: {valid_contact_types}")
        
        # Validate phone number format (basic validation)
        if not re.match(r'^[\+]?[\d\s\-\(\)]{7,15}$', self.phone_number):
            raise ValueError("Phone number must be a valid format (7-15 digits with optional formatting)")
        
        if not self.region or not isinstance(self.region, str):
            raise ValueError("Region must be a non-empty string")
        
        # Validate language support list
        if not isinstance(self.language_support, list):
            raise ValueError("Language support must be a list")
        
        for lang in self.language_support:
            if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', lang):
                raise ValueError(f"Invalid language code in support list: {lang}")
        
        return True

    def supports_language(self, language_code: str) -> bool:
        """
        Checks if this contact supports a specific language.
        
        Args:
            language_code: Language code to check
            
        Returns:
            bool: True if language is supported
        """
        return language_code in self.language_support

    def is_available_24_7(self) -> bool:
        """Returns True if contact is available 24/7."""
        return "24/7" in self.availability_hours or "24 hours" in self.availability_hours.lower()

    def to_json(self) -> str:
        """
        Serializes the emergency contact to JSON string.
        
        Returns:
            str: JSON representation of the emergency contact
        """
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'EmergencyContact':
        """
        Creates an EmergencyContact instance from JSON string.
        
        Args:
            json_str: JSON string representation of the emergency contact
            
        Returns:
            EmergencyContact: Deserialized emergency contact object
        """
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class GovernmentScheme:
    """
    Represents a government health scheme or program.
    
    Attributes:
        scheme_id: Unique identifier for the scheme
        scheme_name: Name of the scheme (e.g., 'JSY', 'PMSMA', 'JSSK')
        scheme_type: Type of scheme ('maternity', 'child_health', 'reproductive_health')
        eligibility_criteria: List of eligibility requirements
        benefits: List of benefits provided by the scheme
        application_process: Description of how to apply
        required_documents: List of required documents
        contact_details: Dictionary of contact information
        regional_variations: Dictionary of state-specific variations
        language_code: Language of the scheme information
        last_updated: When the scheme information was last updated
    """
    scheme_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scheme_name: str = ""
    scheme_type: str = ""
    eligibility_criteria: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    application_process: str = ""
    required_documents: List[str] = field(default_factory=list)
    contact_details: Dict[str, Any] = field(default_factory=dict)
    regional_variations: Dict[str, Any] = field(default_factory=dict)
    language_code: str = "en"
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> bool:
        """
        Validates the government scheme data for integrity.
        
        Returns:
            bool: True if all validation checks pass
            
        Raises:
            ValueError: If validation fails with specific error message
        """
        if not self.scheme_id or not isinstance(self.scheme_id, str):
            raise ValueError("Scheme ID must be a non-empty string")
        
        if not self.scheme_name or not isinstance(self.scheme_name, str):
            raise ValueError("Scheme name must be a non-empty string")
        
        # Validate scheme type
        valid_scheme_types = ['maternity', 'child_health', 'reproductive_health']
        if self.scheme_type not in valid_scheme_types:
            raise ValueError(f"Scheme type must be one of: {valid_scheme_types}")
        
        # Validate language code
        if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', self.language_code):
            raise ValueError("Language code must be valid (e.g., 'en', 'hi', 'bn-IN')")
        
        # Validate list fields
        for field_name, field_value in [
            ('eligibility_criteria', self.eligibility_criteria),
            ('benefits', self.benefits),
            ('required_documents', self.required_documents)
        ]:
            if not isinstance(field_value, list):
                raise ValueError(f"{field_name} must be a list")
        
        # Validate dictionary fields
        for field_name, field_value in [
            ('contact_details', self.contact_details),
            ('regional_variations', self.regional_variations)
        ]:
            if not isinstance(field_value, dict):
                raise ValueError(f"{field_name} must be a dictionary")
        
        return True

    def is_maternity_scheme(self) -> bool:
        """Returns True if this is a maternity-related scheme."""
        return self.scheme_type == 'maternity'

    def has_regional_variations(self) -> bool:
        """Returns True if scheme has regional variations."""
        return bool(self.regional_variations)

    def get_benefits_for_region(self, region: str) -> List[str]:
        """
        Gets benefits for a specific region, including regional variations.
        
        Args:
            region: Region to get benefits for
            
        Returns:
            List[str]: Combined list of general and regional benefits
        """
        benefits = self.benefits.copy()
        
        if region in self.regional_variations:
            regional_benefits = self.regional_variations[region].get('additional_benefits', [])
            benefits.extend(regional_benefits)
        
        return benefits

    def to_json(self) -> str:
        """
        Serializes the government scheme to JSON string.
        
        Returns:
            str: JSON representation of the government scheme
        """
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'GovernmentScheme':
        """
        Creates a GovernmentScheme instance from JSON string.
        
        Args:
            json_str: JSON string representation of the government scheme
            
        Returns:
            GovernmentScheme: Deserialized government scheme object
        """
        data = json.loads(json_str)
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


# Utility functions for data model operations

def validate_all_models(*models) -> bool:
    """
    Validates multiple model instances.
    
    Args:
        *models: Variable number of model instances to validate
        
    Returns:
        bool: True if all models are valid
        
    Raises:
        ValueError: If any model validation fails
    """
    for model in models:
        if hasattr(model, 'validate'):
            model.validate()
    return True


def serialize_models(models: List[Any]) -> str:
    """
    Serializes a list of models to JSON string.
    
    Args:
        models: List of model instances to serialize
        
    Returns:
        str: JSON array representation of the models
    """
    serialized = []
    for model in models:
        if hasattr(model, 'to_json'):
            serialized.append(json.loads(model.to_json()))
        else:
            serialized.append(asdict(model))
    
    return json.dumps(serialized, ensure_ascii=False)


def create_sample_data() -> Dict[str, Any]:
    """
    Creates sample data for testing and development.
    
    Returns:
        Dict[str, Any]: Dictionary containing sample instances of all models
    """
    # Sample user session
    session = UserSession(
        language_preference="hi",
        current_module="puberty_education",
        accessibility_preferences={"audio_speed": "normal", "high_contrast": False}
    )
    
    # Sample content item
    content = ContentItem(
        module_name="puberty_education",
        topic="menstruation_basics",
        content_type="audio",
        language_code="hi",
        s3_url="https://ai-sakhi-content.s3.amazonaws.com/audio/hi/menstruation_basics.mp3",
        duration_seconds=180,
        transcript="मासिक धर्म एक प्राकृतिक प्रक्रिया है...",
        safety_validated=True
    )
    
    # Sample voice interaction
    interaction = VoiceInteraction(
        session_id=session.session_id,
        user_audio_transcript="मुझे मासिक धर्म के बारे में जानना है",
        system_response_text="मैं आपको मासिक धर्म के बारे में बताती हूं...",
        language_code="hi",
        confidence_score=0.92,
        processing_time_ms=1250
    )
    
    # Sample emergency contact
    emergency = EmergencyContact(
        contact_type="helpline",
        phone_number="+91-11-26853846",
        region="Delhi",
        language_support=["hi", "en", "ur"],
        availability_hours="24/7",
        description="National Commission for Women Helpline"
    )
    
    # Sample government scheme
    scheme = GovernmentScheme(
        scheme_name="Janani Suraksha Yojana (JSY)",
        scheme_type="maternity",
        eligibility_criteria=[
            "Pregnant women belonging to BPL families",
            "All pregnant women in low performing states"
        ],
        benefits=[
            "Cash assistance for institutional delivery",
            "Free delivery care"
        ],
        application_process="Register at nearest ASHA worker or health facility",
        required_documents=["BPL card", "Pregnancy registration card"],
        contact_details={"helpline": "104", "website": "nhm.gov.in"},
        language_code="hi"
    )
    
    return {
        "user_session": session,
        "content_item": content,
        "voice_interaction": interaction,
        "emergency_contact": emergency,
        "government_scheme": scheme
    }