# src/core/tracking/conversation_tracker.py
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import networkx as nx

@dataclass
class InteractionEvent:
    timestamp: datetime
    sender_id: int
    receiver_id: int
    message_type: str
    sentiment_score: float
    engagement_score: float
    response_time: float

class RelationshipTracker:
    def __init__(self):
        self.interaction_graph = nx.DiGraph()
        self.interaction_history: Dict[tuple, List[InteractionEvent]] = {}
        self.recent_window = timedelta(days=30)

    async def track_interaction(
        self,
        sender_id: int,
        receiver_id: int,
        message_content: dict
    ) -> Dict:
        """Track a single interaction between users"""
        event = InteractionEvent(
            timestamp=datetime.now(),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_content.get('type', 'text'),
            sentiment_score=message_content.get('sentiment', 0.0),
            engagement_score=message_content.get('engagement', 0.0),
            response_time=message_content.get('response_time', 0.0)
        )

        pair_key = (sender_id, receiver_id)
        if pair_key not in self.interaction_history:
            self.interaction_history[pair_key] = []

        self.interaction_history[pair_key].append(event)

        # Update interaction graph
        self._update_graph(event)

        # Calculate updated metrics
        return await self.calculate_relationship_metrics(sender_id, receiver_id)

    def _update_graph(self, event: InteractionEvent):
        """Update the interaction graph with new event"""
        if not self.interaction_graph.has_edge(event.sender_id, event.receiver_id):
            self.interaction_graph.add_edge(
                event.sender_id,
                event.receiver_id,
                interactions=0,
                avg_sentiment=0.0,
                avg_engagement=0.0
            )

        edge = self.interaction_graph[event.sender_id][event.receiver_id]
        n = edge['interactions']

        # Update rolling averages
        edge['avg_sentiment'] = (n * edge['avg_sentiment'] + event.sentiment_score) / (n + 1)
        edge['avg_engagement'] = (n * edge['avg_engagement'] + event.engagement_score) / (n + 1)
        edge['interactions'] += 1

    async def calculate_relationship_metrics(
        self,
        user1_id: int,
        user2_id: int
    ) -> Dict:
        """Calculate comprehensive relationship metrics"""
        recent_interactions = self._get_recent_interactions(user1_id, user2_id)

        if not recent_interactions:
            return {}

        metrics = {
            "interaction_frequency": len(recent_interactions) / 30,  # per day
            "sentiment_trend": self._calculate_sentiment_trend(recent_interactions),
            "engagement_quality": self._calculate_engagement_quality(recent_interactions),
            "response_patterns": self._analyze_response_patterns(recent_interactions),
            "relationship_strength": self._calculate_relationship_strength(user1_id, user2_id)
        }

        return metrics

    def _get_recent_interactions(
        self,
        user1_id: int,
        user2_id: int
    ) -> List[InteractionEvent]:
        """Get interactions within recent window"""
        cutoff_time = datetime.now() - self.recent_window

        all_interactions = (
            self.interaction_history.get((user1_id, user2_id), []) +
            self.interaction_history.get((user2_id, user1_id), [])
        )

        return [
            interaction for interaction in all_interactions
            if interaction.timestamp > cutoff_time
        ]

    def _calculate_sentiment_trend(
        self,
        interactions: List[InteractionEvent]
    ) -> Dict:
        """Calculate sentiment trends over time"""
        if not interactions:
            return {"trend": 0.0, "volatility": 0.0}

        sentiments = [i.sentiment_score for i in interactions]

        # Calculate trend using linear regression
        x = np.arange(len(sentiments))
        z = np.polyfit(x, sentiments, 1)
        trend = z[0]  # slope of the trend line

        # Calculate volatility
        volatility = np.std(sentiments)

        return {
            "trend": float(trend),
            "volatility": float(volatility),
            "current": float(sentiments[-1])
        }

    def _calculate_engagement_quality(
        self,
        interactions: List[InteractionEvent]
    ) -> float:
        """Calculate overall engagement quality"""
        if not interactions:
            return 0.0

        engagement_scores = [i.engagement_score for i in interactions]
        response_times = [i.response_time for i in interactions]

        # Normalize response times (inverse, since lower is better)
        max_response_time = max(response_times)
        norm_response_times = [
            1 - (rt / max_response_time) for rt in response_times
        ] if max_response_time > 0 else [1.0] * len(response_times)

        # Combine metrics with weights
        weights = {
            "engagement": 0.7,
            "response_time": 0.3
        }

        quality_score = (
            weights["engagement"] * np.mean(engagement_scores) +
            weights["response_time"] * np.mean(norm_response_times)
        )

        return float(quality_score)

    def _analyze_response_patterns(
        self,
        interactions: List[InteractionEvent]
    ) -> Dict:
        """Analyze patterns in responses"""
        if len(interactions) < 2:
            return {}

        # Calculate average response time
        response_times = []
        for i in range(1, len(interactions)):
            delta = (interactions[i].timestamp - interactions[i-1].timestamp).total_seconds()
            response_times.append(delta)

        return {
            "avg_response_time": float(np.mean(response_times)),
            "response_consistency": float(1 - np.std(response_times) / np.mean(response_times))
            if response_times else 0.0
        }

    def _calculate_relationship_strength(
        self,
        user1_id: int,
        user2_id: int
    ) -> float:
        """Calculate overall relationship strength"""
        if not self.interaction_graph.has_edge(user1_id, user2_id):
            return 0.0

        edge1 = self.interaction_graph[user1_id][user2_id]
        edge2 = self.interaction_graph[user2_id][user1_id] if self.interaction_graph.has_edge(user2_id, user1_id) else None

        # Calculate bidirectional metrics
        interaction_balance = min(edge1['interactions'], edge2['interactions'] if edge2 else 0) / \
                            max(edge1['interactions'], edge2['interactions'] if edge2 else 1)

        sentiment_harmony = 1 - abs(edge1['avg_sentiment'] - (edge2['avg_sentiment'] if edge2 else 0)) / 2
        engagement_harmony = 1 - abs(edge1['avg_engagement'] - (edge2['avg_engagement'] if edge2 else 0)) / 2

        # Weighted combination
        weights = {
            "interaction_balance": 0.3,
            "sentiment_harmony": 0.4,
            "engagement_harmony": 0.3
        }

        strength = (
            weights["interaction_balance"] * interaction_balance +
            weights["sentiment_harmony"] * sentiment_harmony +
            weights["engagement_harmony"] * engagement_harmony
        )

        return float(strength)