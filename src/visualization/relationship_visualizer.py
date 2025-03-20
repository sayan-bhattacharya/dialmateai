# src/visualization/relationship_visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import Dict, List
import io
import numpy as np
from datetime import datetime, timedelta

class RelationshipVisualizer:
    def __init__(self):
        plt.style.use('seaborn')
        self.colors = sns.color_palette("husl", 8)

    async def create_relationship_dashboard(
        self,
        user_id: int,
        relationship_data: Dict,
        interaction_history: List[Dict]
    ) -> io.BytesIO:
        """Create comprehensive relationship dashboard"""
        fig = plt.figure(figsize=(15, 10))

        # Create subplots
        gs = fig.add_gridspec(3, 3)

        # Network graph
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_relationship_network(ax1, relationship_data)

        # Interaction timeline
        ax2 = fig.add_subplot(gs[1, :2])
        self._plot_interaction_timeline(ax2, interaction_history)

        # Sentiment analysis
        ax3 = fig.add_subplot(gs[2, :2])
        self._plot_sentiment_analysis(ax3, interaction_history)

        # Relationship strength metrics
        ax4 = fig.add_subplot(gs[:, 2])
        self._plot_relationship_metrics(ax4, relationship_data)

        plt.tight_layout()

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return buf

    def _plot_relationship_network(self, ax, relationship_data: Dict):
        """Plot network graph of relationships"""
        G = nx.Graph()

        # Add nodes and edges
        for rel in relationship_data['relationships']:
            G.add_edge(
                rel['user1_id'],
                rel['user2_id'],
                weight=rel['strength']
            )

        # Layout
        pos = nx.spring_layout(G)

        # Draw network
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue')
        nx.draw_networkx_edges(
            G, pos,
            ax=ax,
            edge_color=[G[u][v]['weight'] for u, v in G.edges()],
            edge_cmap=plt.cm.YlOrRd
        )

        ax.set_title("Relationship Network")

    def _plot_interaction_timeline(self, ax, interaction_history: List[Dict]):
        """Plot interaction timeline"""
        dates = [i['timestamp'] for i in interaction_history]
        counts = range(len(dates))

        ax.plot(dates, counts, '-o', color=self.colors[0])
        ax.set_title("Interaction Timeline")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Interactions")

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45)

    def _plot_sentiment_analysis(self, ax, interaction_history: List[Dict]):
        """Plot sentiment analysis over time"""
        dates = [i['timestamp'] for i in interaction_history]
        sentiments = [i['sentiment'] for i in interaction_history]

        # Plot sentiment
        ax.plot(dates, sentiments, '-o', color=self.colors[2])

        # Add trend line
        z = np.polyfit(range(len(dates)), sentiments, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(range(len(dates))), '--', color='gray')

        ax.set_title("Sentiment Analysis")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sentiment Score")

        plt.setp(ax.get_xticklabels(), rotation=45)

    def _plot_relationship_metrics(self, ax, relationship_data: Dict):
        """Plot relationship strength metrics"""
        metrics = [
            'trust_score',
            'communication_quality',
            'emotional_alignment',
            'interaction_frequency'
        ]

        values = [relationship_data[m] for m in metrics]

        # Create radar chart
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the circle
        angles = np.concatenate((angles, [angles[0]]))  # complete the circle

        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title("Relationship Metrics")