# src/models/user_profile.py
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

@dataclass
class UserProfile:
    user_id: int
    created_at: datetime
    big_five_traits: Dict[str, float] = field(default_factory=dict)
    iq_score: float = 100.0
    conversation_history: List[str] = field(default_factory=list)
    assessment_completed: bool = False

    def update_traits(self, new_traits: Dict[str, float]):
        self.big_five_traits.update(new_traits)

    def update_iq_score(self, new_score: float):
        # Rolling average with more weight to historical data
        self.iq_score = 0.8 * self.iq_score + 0.2 * new_score