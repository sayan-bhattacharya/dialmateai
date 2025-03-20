# src/core/assessment/iq_assessment.py
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime
import random
from dataclasses import dataclass

@dataclass
class IQQuestion:
    id: str
    category: str
    difficulty: float
    question: str
    options: List[str]
    correct_answer: str
    time_limit: int  # seconds
    cognitive_areas: List[str]

class AdaptiveIQAssessment:
    def __init__(self):
        self.question_bank = self._initialize_question_bank()
        self.difficulty_levels = np.linspace(0.2, 0.95, 20)
        self.current_difficulty = 0.5
        self.response_history: Dict[int, List[Dict]] = {}

    def _initialize_question_bank(self) -> Dict[str, List[IQQuestion]]:
        """Initialize comprehensive question bank"""
        categories = {
            "logical_reasoning": [],
            "pattern_recognition": [],
            "spatial_reasoning": [],
            "numerical_reasoning": [],
            "verbal_reasoning": [],
            "memory": []
        }

        # Logical Reasoning Questions
        categories["logical_reasoning"] = [
            IQQuestion(
                id="L1",
                category="logical_reasoning",
                difficulty=0.5,
                question="If all A are B, and all B are C, what can we conclude?",
                options=["All A are C", "Some A are C", "No A are C", "Cannot determine"],
                correct_answer="All A are C",
                time_limit=60,
                cognitive_areas=["deductive_reasoning", "logical_inference"]
            ),
            # Add more questions...
        ]

        # Pattern Recognition Questions
        categories["pattern_recognition"] = [
            IQQuestion(
                id="P1",
                category="pattern_recognition",
                difficulty=0.6,
                question="What number comes next: 2, 6, 12, 20, 30, __?",
                options=["42", "40", "36", "44"],
                correct_answer="42",
                time_limit=45,
                cognitive_areas=["sequence_recognition", "mathematical_reasoning"]
            ),
            # Add more questions...
        ]

        return categories

    async def get_next_question(self, user_id: int) -> Optional[IQQuestion]:
        """Get next question based on user's performance"""
        if user_id not in self.response_history:
            self.response_history[user_id] = []

        # Select category based on performance gaps
        category = self._select_category(user_id)

        # Find question at current difficulty level
        questions = self.question_bank[category]
        suitable_questions = [
            q for q in questions
            if abs(q.difficulty - self.current_difficulty) < 0.1
            and q.id not in [r["question_id"] for r in self.response_history[user_id]]
        ]

        return random.choice(suitable_questions) if suitable_questions else None

    async def process_response(
        self,
        user_id: int,
        question_id: str,
        answer: str,
        response_time: float
    ) -> Dict:
        """Process user's response and update difficulty"""
        question = self._find_question(question_id)
        if not question:
            return {"error": "Question not found"}

        is_correct = answer == question.correct_answer
        time_factor = min(1.0, question.time_limit / response_time) if response_time > 0 else 0

        # Calculate performance score
        performance_score = self._calculate_performance_score(
            is_correct,
            time_factor,
            question.difficulty
        )

        # Update response history
        self.response_history[user_id].append({
            "question_id": question_id,
            "correct": is_correct,
            "time_factor": time_factor,
            "performance_score": performance_score
        })

        # Adjust difficulty
        self._adjust_difficulty(user_id)

        return {
            "score": performance_score,
            "complete": len(self.response_history[user_id]) >= 20
        }

    def _calculate_performance_score(
        self,
        is_correct: bool,
        time_factor: float,
        difficulty: float
    ) -> float:
        """Calculate performance score based on correctness, time, and difficulty"""
        base_score = 1.0 if is_correct else 0.0
        time_bonus = time_factor * 0.2
        difficulty_bonus = difficulty * 0.3

        return base_score + time_bonus + difficulty_bonus

    def _adjust_difficulty(self, user_id: int):
        """Adjust difficulty based on recent performance"""
        recent_responses = self.response_history[user_id][-3:]
        avg_performance = np.mean([r["performance_score"] for r in recent_responses])

        if avg_performance > 0.7:
            self.current_difficulty = min(0.95, self.current_difficulty + 0.1)
        elif avg_performance < 0.3:
            self.current_difficulty = max(0.2, self.current_difficulty - 0.1)

    async def calculate_final_iq(self, user_id: int) -> Dict:
        """Calculate final IQ score based on all responses"""
        if user_id not in self.response_history:
            return {"error": "No test data found"}

        responses = self.response_history[user_id]

        # Calculate base score
        performance_scores = [r["performance_score"] for r in responses]
        avg_performance = np.mean(performance_scores)

        # Calculate consistency
        consistency = 1 - np.std(performance_scores)

        # Calculate difficulty progression
        difficulty_progression = self._calculate_difficulty_progression(responses)

        # Calculate cognitive area scores
        cognitive_scores = self._calculate_cognitive_scores(user_id)

        # Final IQ calculation
        base_iq = 100
        performance_adjustment = avg_performance * 30
        consistency_bonus = consistency * 10
        progression_bonus = difficulty_progression * 10

        final_iq = base_iq + performance_adjustment + consistency_bonus + progression_bonus

        return {
            "iq_score": round(final_iq),
            "confidence": consistency,
            "cognitive_profile": cognitive_scores,
            "percentile": self._calculate_percentile(final_iq)
        }

    def _calculate_cognitive_scores(self, user_id: int) -> Dict[str, float]:
        """Calculate scores for different cognitive areas"""
        responses = self.response_history[user_id]
        cognitive_areas = {
            "logical_reasoning": [],
            "pattern_recognition": [],
            "spatial_reasoning": [],
            "numerical_reasoning": [],
            "verbal_reasoning": [],
            "memory": []
        }

        for response in responses:
            question = self._find_question(response["question_id"])
            for area in question.cognitive_areas:
                cognitive_areas[area].append(response["performance_score"])

        return {
            area: np.mean(scores) if scores else 0.0
            for area, scores in cognitive_areas.items()
        }

    def _calculate_percentile(self, iq_score: float) -> float:
        """Calculate percentile rank for IQ score"""
        # Using normal distribution with mean=100, std=15
        return float(norm.cdf((iq_score - 100) / 15) * 100)