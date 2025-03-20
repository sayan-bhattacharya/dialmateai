# src/models/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class RelationType(Enum):
    FAMILY = "family"
    PROFESSIONAL = "professional"
    SOCIAL = "social"

class FamilyRole(Enum):
    MOTHER = "mother"
    FATHER = "father"
    SIBLING = "sibling"
    CHILD = "child"
    SPOUSE = "spouse"

class ProfessionalRole(Enum):
    BOSS = "boss"
    COLLEAGUE = "colleague"
    SUBORDINATE = "subordinate"
    CLIENT = "client"

@dataclass
class Relationship:
    related_user_id: int
    relation_type: RelationType
    specific_role: str
    start_date: datetime
    interaction_metrics: Dict = field(default_factory=lambda: {
        "conversation_count": 0,
        "average_sentiment": 0.0,
        "trust_score": 0.0,
        "communication_quality": 0.0,
        "response_time": 0.0
    })

@dataclass
class UserProfile:
    user_id: int
    created_at: datetime
    relationships: Dict[int, Relationship] = field(default_factory=dict)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    iq_score: Optional[float] = None
    assessment_status: Dict[str, bool] = field(default_factory=lambda: {
        "personality_complete": False,
        "iq_complete": False
    })