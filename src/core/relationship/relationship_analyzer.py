# src/core/relationship/relationship_analyzer.py
from typing import Dict
import numpy as np
from datetime import datetime, timedelta

class RelationshipAnalyzer:
    def __init__(self):
        self.interaction_window = timedelta(days=30)  # Rolling window for metrics

    async def update_relationship_metrics(
        self,
        user_profile: 'UserProfile',
        related_user_id: int,
        interaction_data: Dict
    ) -> Dict:
        """Update relationship metrics based on new interaction"""
        relationship = user_profile.relationships.get(related_user_id)
        if not relationship:
            return {}

        # Update interaction metrics
        metrics = relationship.interaction_metrics
        metrics["conversation_count"] += 1

        # Update sentiment rolling average
        metrics["average_sentiment"] = (
            0.8 * metrics["average_sentiment"] +
            0.2 * interaction_data.get("sentiment", 0.0)
        )

        # Update trust score based on interaction patterns
        metrics["trust_score"] = self._calculate_trust_score(
            current_score=metrics["trust_score"],
            interaction_data=interaction_data
        )

        # Update communication quality
        metrics["communication_quality"] = self._calculate_communication_quality(
            interaction_data=interaction_data
        )

        return metrics

    def _calculate_trust_score(self, current_score: float, interaction_data: Dict) -> float:
        """Calculate trust score based on interaction patterns"""
        factors = {
            "response_time": 0.3,
            "sentiment_consistency": 0.3,
            "engagement_level": 0.4
        }

        new_score = (
            interaction_data.get("response_time_score", 0.0) * factors["response_time"] +
            interaction_data.get("sentiment_consistency", 0.0) * factors["sentiment_consistency"] +
            interaction_data.get("engagement_level", 0.0) * factors["engagement_level"]
        )

        # Rolling average with more weight to historical data
        return 0.9 * current_score + 0.1 * new_score

    def _calculate_communication_quality(self, interaction_data: Dict) -> float:
        """Calculate communication quality score"""
        weights = {
            "message_clarity": 0.3,
            "response_relevance": 0.3,
            "emotional_alignment": 0.4
        }

        return sum(
            interaction_data.get(metric, 0.0) * weight
            for metric, weight in weights.items()
        )