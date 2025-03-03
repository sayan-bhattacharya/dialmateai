# src/services/text_analyzer.py
from transformers import pipeline
import spacy
import logging
from typing import Dict, List, Optional

class TextAnalyzer:
    def __init__(self):
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.nlp = spacy.load("en_core_web_sm")
            logging.info("Text Analyzer initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Text Analyzer: {str(e)}")
            raise

    async def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for various metrics based on Dialmate's presentation requirements
        """
        try:
            doc = self.nlp(text)

            analysis = {
                "basic_metrics": self._get_basic_metrics(doc),
                "sentiment": self._get_sentiment(text),
                "communication_patterns": self._analyze_communication_patterns(doc),
                "relationship_indicators": self._analyze_relationship_indicators(doc),
                "toxicity_analysis": self._analyze_toxicity(text),
                "suggestions": self._generate_suggestions(doc)
            }

            return analysis

        except Exception as e:
            logging.error(f"Error in text analysis: {str(e)}")
            return {"error": str(e)}

    def _get_basic_metrics(self, doc) -> Dict:
        """Extract basic text metrics"""
        return {
            "word_count": len(doc),
            "sentence_count": len(list(doc.sents)),
            "average_word_length": sum(len(token.text) for token in doc) / len(doc) if len(doc) > 0 else 0,
            "unique_words": len(set(token.text.lower() for token in doc))
        }

    def _get_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text"""
        try:
            result = self.sentiment_analyzer(text)[0]
            return {
                "label": result["label"],
                "score": result["score"]
            }
        except Exception as e:
            logging.error(f"Sentiment analysis error: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}

    def _analyze_communication_patterns(self, doc) -> Dict:
        """Analyze communication patterns"""
        questions = len([sent for sent in doc.sents if sent.text.strip().endswith('?')])
        exclamations = len([sent for sent in doc.sents if sent.text.strip().endswith('!')])

        return {
            "questions_asked": questions,
            "exclamations_used": exclamations,
            "dialogue_turns": self._count_dialogue_turns(doc),
            "interruption_indicators": self._detect_interruptions(doc)
        }

    def _analyze_relationship_indicators(self, doc) -> Dict:
        """Analyze relationship-specific indicators"""
        return {
            "positive_language": self._count_positive_words(doc),
            "negative_language": self._count_negative_words(doc),
            "collaborative_terms": self._count_collaborative_terms(doc),
            "empathy_indicators": self._detect_empathy(doc)
        }

    def _analyze_toxicity(self, text: str) -> Dict:
        """Analyze text for toxic patterns"""
        # This is a simplified version. Consider using specialized toxicity models
        toxic_words = ["hate", "stupid", "idiot", "fool", "terrible"]
        doc = self.nlp(text.lower())
        toxic_count = sum(1 for token in doc if token.text in toxic_words)

        return {
            "toxicity_score": toxic_count / len(doc) if len(doc) > 0 else 0,
            "toxic_phrases": self._identify_toxic_phrases(doc)
        }

    def _generate_suggestions(self, doc) -> List[str]:
        """Generate communication improvement suggestions"""
        suggestions = []

        # Example suggestion generation logic
        if len(list(doc.sents)) > 0:
            avg_sent_length = len(doc) / len(list(doc.sents))
            if avg_sent_length > 20:
                suggestions.append("Consider using shorter sentences for clearer communication")

        # Add more suggestion logic based on analysis

        return suggestions

    def _count_dialogue_turns(self, doc) -> int:
        """Count number of dialogue turns"""
        # Simplified version - could be enhanced with speaker detection
        return len([sent for sent in doc.sents if sent.text.strip().startswith('"')])

    def _detect_interruptions(self, doc) -> List[str]:
        """Detect potential interruptions in dialogue"""
        interruption_indicators = ["wait", "hold on", "let me finish", "excuse me"]
        return [sent.text for sent in doc.sents
                if any(indicator in sent.text.lower() for indicator in interruption_indicators)]

    def _count_positive_words(self, doc) -> int:
        """Count positive language indicators"""
        positive_words = ["good", "great", "excellent", "thank", "appreciate", "love"]
        return sum(1 for token in doc if token.text.lower() in positive_words)

    def _count_negative_words(self, doc) -> int:
        """Count negative language indicators"""
        negative_words = ["bad", "wrong", "terrible", "hate", "awful"]
        return sum(1 for token in doc if token.text.lower() in negative_words)

    def _count_collaborative_terms(self, doc) -> int:
        """Count collaborative language usage"""
        collaborative_terms = ["we", "us", "our", "together", "both"]
        return sum(1 for token in doc if token.text.lower() in collaborative_terms)

    def _detect_empathy(self, doc) -> List[str]:
        """Detect empathy indicators in text"""
        empathy_phrases = ["i understand", "i see", "that must be", "i feel", "you feel"]
        return [sent.text for sent in doc.sents
                if any(phrase in sent.text.lower() for phrase in empathy_phrases)]

    def _identify_toxic_phrases(self, doc) -> List[str]:
        """Identify potentially toxic phrases"""
        # This could be enhanced with more sophisticated toxic language detection
        toxic_phrases = []
        for sent in doc.sents:
            if any(toxic_word in sent.text.lower() for toxic_word in ["hate", "stupid", "idiot"]):
                toxic_phrases.append(sent.text)
        return toxic_phrases