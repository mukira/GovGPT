"""
News API Endpoints
Exposes GDELT and African RSS news services
"""
from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.news.gdelt_service import gdelt_service
from app.services.news.african_rss_service import african_rss_service

router = APIRouter()


@router.get("/kenya")
async def get_kenya_news(
    lookback_days: int = Query(7, ge=1, le=1000),
    keywords: Optional[str] = Query(None),
    max_results: int = Query(50, ge=1, le=100)
):
    """Get Kenya news from GDELT"""
    keyword_list = keywords.split(',') if keywords else None
    articles = gdelt_service.fetch_kenya_news(
        lookback_days=lookback_days,
        keywords=keyword_list,
        max_results=max_results
    )
    return {
        "source": "gdelt",
        "total": len(articles),
        "articles": articles
    }


@router.get("/africa/{region}")
async def get_africa_regional_news(
    region: str,
    max_per_feed: int = Query(10, ge=1, le=20)
):
    """Get regional African news from RSS feeds"""
    articles = african_rss_service.fetch_by_region(
        region.replace('-', ' ').title(),
        max_per_feed=max_per_feed
    )
    return {
        "source": "african_rss",
        "region": region,
        "total": len(articles),
        "articles": articles
    }


@router.get("/africa/all")
async def get_all_africa_news(
    max_per_feed: int = Query(5, ge=1, le=10)
):
    """Get news from all African regions"""
    articles = african_rss_service.fetch_all_feeds(max_per_feed=max_per_feed)
    return {
        "source": "african_rss",
        "total": len(articles),
        "feeds": len(african_rss_service.AFRICAN_FEEDS),
        "articles": articles
    }
