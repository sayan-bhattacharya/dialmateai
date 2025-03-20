# src/core/analyzer/conversation_processor.py
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import asyncio
class ConversationProcessor:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.active_conversations = {}

    async def process_message(self, message: Dict) -> Dict:
        """
        Process a new message and update conversation analysis

        Args:
            message (Dict): Message data containing text, user_id, etc.

        Returns:
            Dict: Analysis results
        """
        conversation_id = message.get('conversation_id')

        # Initialize conversation if not exists
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = {
                'messages': [],
                'participants': set(),
                'start_time': datetime.now(),
                'last_update': datetime.now()
            }

        # Update conversation data
        conversation = self.active_conversations[conversation_id]
        conversation['messages'].append(message)
        conversation['participants'].add(message['user_id'])
        conversation['last_update'] = datetime.now()

        # Perform analysis
        analysis_result = await self.analyzer.analyze_message(
            message,
            conversation['messages'],
            list(conversation['participants'])
        )

        return analysis_result

    async def get_conversation_summary(self, conversation_id: str) -> Dict:
        """
        Get summary of conversation analysis

        Args:
            conversation_id (str): ID of the conversation

        Returns:
            Dict: Conversation summary
        """
        if conversation_id not in self.active_conversations:
            return {'error': 'Conversation not found'}

        conversation = self.active_conversations[conversation_id]

        return {
            'participant_count': len(conversation['participants']),
            'message_count': len(conversation['messages']),
            'duration': (conversation['last_update'] - conversation['start_time']).seconds,
            'active_participants': list(conversation['participants']),
            'last_update': conversation['last_update'].isoformat()
        }

    async def cleanup_old_conversations(self, max_age_hours: int = 24) -> None:
        """
        Remove conversations older than specified hours

        Args:
            max_age_hours (int): Maximum age of conversations to keep
        """
        current_time = datetime.now()
        conversations_to_remove = []

        for conv_id, conv_data in self.active_conversations.items():
            age = (current_time - conv_data['last_update']).total_seconds() / 3600
            if age > max_age_hours:
                conversations_to_remove.append(conv_id)

        for conv_id in conversations_to_remove:
            del self.active_conversations[conv_id]

    async def get_conversation_metrics(self, conversation_id: str) -> Dict:
        """
        Get detailed metrics for a conversation

        Args:
            conversation_id (str): ID of the conversation

        Returns:
            Dict: Conversation metrics
        """
        if conversation_id not in self.active_conversations:
            return {'error': 'Conversation not found'}

        conversation = self.active_conversations[conversation_id]

        # Calculate basic metrics
        total_messages = len(conversation['messages'])
        participants = list(conversation['participants'])
        duration = (conversation['last_update'] - conversation['start_time']).seconds

        # Calculate messages per participant
        messages_per_participant = {}
        for message in conversation['messages']:
            user_id = message['user_id']
            messages_per_participant[user_id] = messages_per_participant.get(user_id, 0) + 1

        return {
            'total_messages': total_messages,
            'participant_count': len(participants),
            'duration_seconds': duration,
            'messages_per_participant': messages_per_participant,
            'average_messages_per_participant': total_messages / len(participants) if participants else 0,
            'messages_per_minute': (total_messages * 60) / duration if duration > 0 else 0
        }

    async def export_conversation_data(self, conversation_id: str) -> Dict:
        """
        Export conversation data in a structured format

        Args:
            conversation_id (str): ID of the conversation

        Returns:
            Dict: Exported conversation data
        """
        if conversation_id not in self.active_conversations:
            return {'error': 'Conversation not found'}

        conversation = self.active_conversations[conversation_id]

        return {
            'conversation_id': conversation_id,
            'start_time': conversation['start_time'].isoformat(),
            'end_time': conversation['last_update'].isoformat(),
            'participants': list(conversation['participants']),
            'messages': [
                {
                    'user_id': msg['user_id'],
                    'text': msg['text'],
                    'timestamp': msg['timestamp'].isoformat(),
                    'type': msg['type']
                }
                for msg in conversation['messages']
            ],
            'metrics': await self.get_conversation_metrics(conversation_id)
        }