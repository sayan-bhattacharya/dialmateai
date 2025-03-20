# src/core/analyzer/integrated_analyzer.py
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import numpy as np
from dataclasses import dataclass, field

@dataclass
class AnalysisContext:
    user_id: int
    conversation_id: str
    timestamp: datetime
    participants: List[int]
    metrics: Dict = field(default_factory=dict)
    relationship_updates: Dict = field(default_factory=dict)

class IntegratedAnalyzer:
    def __init__(
        self,
        relationship_tracker,
        iq_assessment,
        conversation_analyzer,
        relationship_visualizer
    ):
        self.relationship_tracker = relationship_tracker
        self.iq_assessment = iq_assessment
        self.conversation_analyzer = conversation_analyzer
        self.visualizer = relationship_visualizer
        self.analysis_cache = {}

    async def process_conversation(
        self,
        conversation_data: Dict,
        user_context: Dict
    ) -> Dict:
        """Process conversation and update all relevant metrics"""
        context = AnalysisContext(
            user_id=user_context['user_id'],
            conversation_id=conversation_data['conversation_id'],
            timestamp=datetime.now(),
            participants=conversation_data['participants']
        )

        # Parallel analysis of different aspects
        analysis_tasks = [
            self._analyze_conversation_metrics(conversation_data),
            self._update_relationship_metrics(conversation_data, context),
            self._analyze_cognitive_indicators(conversation_data, user_context)
        ]

        results = await asyncio.gather(*analysis_tasks)

        # Combine results
        combined_analysis = self._combine_analysis_results(results, context)

        # Cache results
        self.analysis_cache[context.conversation_id] = combined_analysis

        return combined_analysis

    async def _analyze_conversation_metrics(self, conversation_data: Dict) -> Dict:
        """Analyze conversation-level metrics"""
        messages = conversation_data['messages']

        metrics = {
            "message_count": len(messages),
            "avg_message_length": np.mean([len(m['text']) for m in messages]),
            "conversation_duration": (
                messages[-1]['timestamp'] - messages[0]['timestamp']
            ).total_seconds() if messages else 0,
            "participant_engagement": self._calculate_engagement_metrics(messages)
        }

        # Add sentiment analysis
        sentiment_metrics = await self.conversation_analyzer.analyze_sentiment_flow(messages)
        metrics.update(sentiment_metrics)

        return metrics

    async def _update_relationship_metrics(
        self,
        conversation_data: Dict,
        context: AnalysisContext
    ) -> Dict:
        """Update relationship metrics for all participants"""
        updates = {}
        primary_user = context.user_id

        for participant in context.participants:
            if participant != primary_user:
                interaction_data = self._extract_interaction_data(
                    conversation_data,
                    primary_user,
                    participant
                )

                updates[participant] = await self.relationship_tracker.track_interaction(
                    primary_user,
                    participant,
                    interaction_data
                )

        return updates

    async def _analyze_cognitive_indicators(
        self,
        conversation_data: Dict,
        user_context: Dict
    ) -> Dict:
        """Analyze cognitive indicators from conversation"""
        messages = conversation_data['messages']
        user_messages = [m for m in messages if m['user_id'] == user_context['user_id']]

        cognitive_metrics = {
            "vocabulary_complexity": self._analyze_vocabulary(user_messages),
            "logical_coherence": self._analyze_logical_flow(user_messages),
            "response_sophistication": self._analyze_responses(messages, user_messages)
        }

        return cognitive_metrics

    def _calculate_engagement_metrics(self, messages: List[Dict]) -> Dict:
        """Calculate detailed engagement metrics"""
        participant_metrics = {}

        for message in messages:
            user_id = message['user_id']
            if user_id not in participant_metrics:
                participant_metrics[user_id] = {
                    "message_count": 0,
                    "total_length": 0,
                    "response_times": []
                }

            participant_metrics[user_id]["message_count"] += 1
            participant_metrics[user_id]["total_length"] += len(message['text'])

        # Calculate average response times
        for i in range(1, len(messages)):
            current_msg = messages[i]
            prev_msg = messages[i-1]

            if current_msg['user_id'] != prev_msg['user_id']:
                response_time = (
                    current_msg['timestamp'] - prev_msg['timestamp']
                ).total_seconds()
                participant_metrics[current_msg['user_id']]["response_times"].append(
                    response_time
                )

        # Calculate final metrics
        for user_id in participant_metrics:
            metrics = participant_metrics[user_id]
            metrics["avg_message_length"] = (
                metrics["total_length"] / metrics["message_count"]
                if metrics["message_count"] > 0 else 0
            )
            metrics["avg_response_time"] = (
                np.mean(metrics["response_times"])
                if metrics["response_times"] else 0
            )

        return participant_metrics

    def _analyze_vocabulary(self, messages: List[Dict]) -> Dict:
        """Analyze vocabulary complexity"""
        from collections import Counter
        import nltk
        from nltk.corpus import wordnet

        # Combine all text
        all_text = " ".join([m['text'] for m in messages])
        words = nltk.word_tokenize(all_text.lower())

        # Calculate metrics
        unique_words = len(set(words))
        total_words = len(words)
        word_frequency = Counter(words)

        # Calculate average word complexity
        complexity_scores = []
        for word in set(words):
            synsets = wordnet.synsets(word)
            if synsets:
                # Use number of synsets as complexity indicator
                complexity_scores.append(len(synsets))

        avg_complexity = np.mean(complexity_scores) if complexity_scores else 0

        return {
            "vocabulary_size": unique_words,
            "lexical_diversity": unique_words / total_words if total_words > 0 else 0,
            "avg_word_complexity": avg_complexity
        }

    def _analyze_logical_flow(self, messages: List[Dict]) -> Dict:
        """Analyze logical coherence of messages"""
        from nltk.tokenize import sent_tokenize
        from nltk.corpus import stopwords

        coherence_metrics = {
            "topic_consistency": 0.0,
            "logical_transitions": 0.0,
            "idea_development": 0.0
        }

        if len(messages) < 2:
            return coherence_metrics

        # Analyze topic consistency
        previous_topics = set()
        topic_shifts = 0

        for message in messages:
            current_topics = self._extract_topics(message['text'])
            if previous_topics:
                topic_overlap = len(current_topics & previous_topics) / len(current_topics | previous_topics) if current_topics | previous_topics else 0
                topic_shifts += (1 - topic_overlap)
            previous_topics = current_topics

        coherence_metrics["topic_consistency"] = 1 - (topic_shifts / len(messages))

        return coherence_metrics

    async def generate_analysis_report(
        self,
        conversation_id: str,
        user_id: int
    ) -> Dict:
        """Generate comprehensive analysis report"""
        if conversation_id not in self.analysis_cache:
            return {"error": "Conversation analysis not found"}

        analysis = self.analysis_cache[conversation_id]

        # Generate visualizations
        visualization_buffer = await self.visualizer.create_relationship_dashboard(
            user_id,
            analysis['relationship_updates'],
            analysis['conversation_metrics']
        )

        report = {
            "summary": self._generate_summary(analysis),
            "detailed_metrics": analysis,
            "visualization": visualization_buffer,
            "recommendations": self._generate_recommendations(analysis)
        }

        return report

    def _generate_summary(self, analysis: Dict) -> Dict:
        """Generate human-readable summary of analysis"""
        return {
            "main_findings": self._extract_main_findings(analysis),
            "key_metrics": self._summarize_key_metrics(analysis),
            "relationship_insights": self._summarize_relationships(analysis)
        }

    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []

        # Analyze areas for improvement
        metrics = analysis['conversation_metrics']
        relationship_data = analysis['relationship_updates']

        # Add communication recommendations
        if metrics['avg_message_length'] < 10:
            recommendations.append({
                "category": "communication",
                "suggestion": "Try to provide more detailed responses",
                "reason": "Short messages may limit effective communication"
            })

        # Add relationship recommendations
        for participant_id, rel_metrics in relationship_data.items():
            if rel_metrics['trust_score'] < 0.5:
                recommendations.append({
                    "category": "relationship",
                    "participant_id": participant_id,
                    "suggestion": "Focus on building trust through consistent communication",
                    "reason": "Trust levels could be improved"
                })

        return recommendations