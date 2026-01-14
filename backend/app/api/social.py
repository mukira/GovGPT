"""
Social Media API Endpoints
Exposes YouTube, Telegram, Mastodon services
"""
from fastapi import APIRouter, Query
from typing import Optional

from app.services.social_media.youtube_service import YouTubeService
from app.services.social_media.social_aggregator import social_aggregator

router = APIRouter()


@router.get("/kenya/pulse")
async def get_kenya_social_pulse(
    keywords: Optional[str] = Query(None)
):
    """Get overall Kenya social media sentiment pulse"""
    keyword_list = keywords.split(',') if keywords else ['Kenya']
    result = social_aggregator.fetch_kenya_social(keywords=keyword_list)
    return result


@router.get("/mastodon/search")
async def search_mastodon(
    query: str = Query("Kenya"),
    limit: int = Query(20, ge=1, le=40)
):
    """Search Mastodon for Kenya content"""
    from app.services.social_media.mastodon_service import mastodon_service
    posts = mastodon_service.search_kenya_posts(query=query, limit=limit)
    return {
        "platform": "mastodon",
        "query": query,
        "total": len(posts),
        "posts": posts
    }


@router.get("/youtube/search")
async def search_youtube(
    query: str = Query("Kenya government"),
    max_results: int = Query(10, ge=1, le=20)
):
    """Search YouTube for Kenya videos"""
    from app.config import settings
    yt = YouTubeService(api_key=getattr(settings, 'YOUTUBE_API_KEY', None))
    videos = yt.search_kenya_videos(query=query, max_results=max_results)
    return {
        "platform": "youtube",
        "query": query,
        "total": len(videos),
        "videos": videos
    }


@router.get("/youtube/comments/{video_id}")
async def get_youtube_comments(
    video_id: str,
    max_results: int = Query(50, ge=1, le=100)
):
    """Get comments from a YouTube video"""
    from app.config import settings
    yt = YouTubeService(api_key=getattr(settings, 'YOUTUBE_API_KEY', None))
    comments = yt.get_video_comments(video_id, max_results=max_results)
    return {
        "platform": "youtube",
        "video_id": video_id,
        "total": len(comments),
        "comments": comments
    }
