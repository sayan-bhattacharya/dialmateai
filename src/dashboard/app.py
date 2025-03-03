# src/dashboard/app.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/conversation/{call_id}")
async def get_conversation_analysis(call_id: str):
    conversation = await Conversation.find_one({"call_id": call_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create visualization data
    speaking_time_fig = px.bar(
        x=list(conversation.speaker_stats.keys()),
        y=[stats.speaking_time for stats in conversation.speaker_stats.values()],
        title="Speaking Time Distribution"
    )

    sentiment_fig = px.line(
        x=list(conversation.speaker_stats.keys()),
        y=[stats.sentiment_score for stats in conversation.speaker_stats.values()],
        title="Sentiment Analysis"
    )

    return {
        "summary": conversation.summary,
        "visualizations": {
            "speaking_time": speaking_time_fig.to_json(),
            "sentiment": sentiment_fig.to_json()
        },
        "suggestions": conversation.suggestions
    }