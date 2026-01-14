"""
Sentiment Analysis API Endpoints
"""
from fastapi import APIRouter, Body
from typing import List

from app.services.social_media.sentiment_service import sentiment_analyzer

router = APIRouter()


@router.post("/analyze")
async def analyze_sentiment(
    text: str = Body(..., embed=True)
):
    """Analyze sentiment of a single text"""
    result = sentiment_analyzer.analyze(text)
    return result


@router.post("/analyze/batch")
async def analyze_batch(
    texts: List[str] = Body(...)
):
    """Analyze sentiment of multiple texts"""
    results = sentiment_analyzer.analyze_batch(texts)
    return {
        "total": len(results),
        "results": results
    }
