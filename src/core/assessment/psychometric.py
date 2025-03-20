# src/core/assessment/psychometric_test.py
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime

class PsychometricTest:
    def __init__(self):
        self.big_five_questions = self._initialize_big_five_questions()
        self.iq_questions = self._initialize_iq_questions()
        self.current_question_index = 0

    def _initialize_big_five_questions(self) -> List[Dict]:
        return [
            # Openness
            {
                "id": "O1",
                "text": "I enjoy trying new experiences and learning new things",
                "trait": "openness",
                "reverse_scored": False
            },
            {
                "id": "O2",
                "text": "I prefer routine and familiar experiences",
                "trait": "openness",
                "reverse_scored": True
            },
            # Conscientiousness
            {
                "id": "C1",
                "text": "I am always prepared and organized",
                "trait": "conscientiousness",
                "reverse_scored": False
            },
            # Add more questions for each trait...
        ]

    def _initialize_iq_questions(self) -> List[Dict]:
        return [
            {
                "id": "IQ1",
                "type": "pattern",
                "text": "Complete the sequence: 2, 6, 12, 20, __",
                "options": ["30", "28", "32", "36"],
                "correct": "30",
                "difficulty": 0.5
            },
            {
                "id": "IQ2",
                "type": "verbal",
                "text": "Which word is the opposite of 'ephemeral'?",
                "options": ["permanent", "temporary", "fleeting", "brief"],
                "correct": "permanent",
                "difficulty": 0.7
            },
            # Add more questions...
        ]

class PersonalityAssessment:
    def __init__(self):
        self.test = PsychometricTest()
        self.responses = {}

    async def get_next_question(self, user_id: int) -> Dict:
        """Get next question based on user's progress"""
        if len(self.responses.get(user_id, {})) < len(self.test.big_five_questions):
            return self.test.big_five_questions[len(self.responses.get(user_id, {}))]
        return None

    async def process_response(self, user_id: int, question_id: str, response: int) -> Dict:
        """Process a single response and update user's profile"""
        if user_id not in self.responses:
            self.responses[user_id] = {}

        self.responses[user_id][question_id] = response

        # Check if assessment is complete
        if len(self.responses[user_id]) == len(self.test.big_five_questions):
            return await self.calculate_personality_traits(user_id)

        return {"status": "in_progress", "completed": len(self.responses[user_id])}

    async def calculate_personality_traits(self, user_id: int) -> Dict[str, float]:
        """Calculate final personality traits"""
        traits = {
            "openness": [],
            "conscientiousness": [],
            "extraversion": [],
            "agreeableness": [],
            "neuroticism": []
        }

        # Process responses
        for q_id, response in self.responses[user_id].items():
            question = next(q for q in self.test.big_five_questions if q["id"] == q_id)
            score = response if not question["reverse_scored"] else (6 - response)
            traits[question["trait"]].append(score)

        # Calculate averages
        return {trait: np.mean(scores) for trait, scores in traits.items()}

class IQAssessment:
    def __init__(self):
        self.test = PsychometricTest()
        self.responses = {}

    async def calculate_iq_score(self, user_id: int) -> float:
        """Calculate IQ score based on responses and difficulty"""
        correct_count = 0
        total_difficulty = 0

        for q_id, response in self.responses.get(user_id, {}).items():
            question = next(q for q in self.test.iq_questions if q["id"] == q_id)
            if response == question["correct"]:
                correct_count += 1
                total_difficulty += question["difficulty"]

        # Basic IQ calculation (can be made more sophisticated)
        base_iq = 100
        difficulty_bonus = total_difficulty * 15
        accuracy_multiplier = correct_count / len(self.test.iq_questions)

        return base_iq + (difficulty_bonus * accuracy_multiplier)