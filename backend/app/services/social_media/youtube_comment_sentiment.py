"""
YouTube Comment Sentiment Service
Fetches and analyzes comments from Kenya news videos
"""
from typing import List, Dict
from app.services.social_media.youtube_service import youtube_service
from app.services.social_media.sentiment_service import sentiment_analyzer


class YouTubeCommentSentiment:
    """Fetch YouTube comments and analyze sentiment from Kenya news channels"""
    
    def __init__(self):
        self.youtube = youtube_service
    
    def get_sentiment_from_videos(
        self,
        query: str,
        max_videos: int = 3,
        comments_per_video: int = 20
    ) -> Dict:
        """
        Get sentiment from YouTube video comments
        
        Args:
            query: Search query for videos
            max_videos: Number of videos to analyze
            comments_per_video: Comments to fetch per video
            
        Returns:
            Dictionary with sentiment analysis and sample comments
        """
        # Search for Kenya-related videos
        videos = self.youtube.search_videos(query, max_results=max_videos)
        
        if not videos:
            return {
                'total_comments': 0,
                'sentiment_summary': {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                },
                'average_score': 0.0,
                'sample_comments': []
            }
        
        all_comments = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_score = 0.0
        
        print(f"💬 Fetching comments from {len(videos)} Kenya videos...")
        
        for video in videos:
            video_id = video['id']
            comments = self.youtube.get_video_comments(video_id, max_results=comments_per_video)
            
            # Analyze sentiment for each comment
            for comment in comments:
                text = comment.get('text', '')
                if not text or len(text.strip()) < 10:
                    continue
                
                # Get sentiment
                sentiment = sentiment_analyzer.analyze(text)
                
                comment['sentiment'] = sentiment['sentiment']
                comment['sentiment_score'] = sentiment['score']
                comment['polarity'] = sentiment['polarity']
                comment['video_title'] = video['title']
                
                # Track counts
                sentiment_counts[sentiment['sentiment']] += 1
                total_score += sentiment['score']
                
                all_comments.append(comment)
        
        # Calculate average
        avg_score = total_score / len(all_comments) if all_comments else 0.0
        
        # Sort by sentiment score (most polarized first)
        all_comments.sort(key=lambda x: abs(x.get('polarity', 0)), reverse=True)
        
        print(f"💬 Analyzed {len(all_comments)} YouTube comments")
        print(f"   Positive: {sentiment_counts['positive']}, Negative: {sentiment_counts['negative']}, Neutral: {sentiment_counts['neutral']}")
        
        return {
            'total_comments': len(all_comments),
            'sentiment_summary': sentiment_counts,
            'average_score': round(avg_score, 3),
            'sample_comments': all_comments[:10],  # Top 10 most polarized
            'videos_analyzed': len(videos)
        }
    
    def format_for_context(self, sentiment_data: Dict) -> str:
        """
        Format YouTube comment sentiment for LLM context
        
        Args:
            sentiment_data: Sentiment analysis results
            
        Returns:
            Formatted string for LLM
        """
        if sentiment_data['total_comments'] == 0:
            return "No YouTube comments available."
        
        summary = sentiment_data['sentiment_summary']
        total = sentiment_data['total_comments']
        
        # Calculate percentages
        pos_pct = (summary['positive'] / total * 100) if total > 0 else 0
        neg_pct = (summary['negative'] / total * 100) if total > 0 else 0
        neu_pct = (summary['neutral'] / total * 100) if total > 0 else 0
        
        context = f"""
### YouTube Public Sentiment ({total} comments from {sentiment_data['videos_analyzed']} Kenya news videos)

**Overall Sentiment:**
- Positive: {summary['positive']} ({pos_pct:.0f}%)
- Negative: {summary['negative']} ({neg_pct:.0f}%)
- Neutral: {summary['neutral']} ({neu_pct:.0f}%)
- Average Score: {sentiment_data['average_score']:.2f}

**Sample Public Comments:**
"""
        
        for i, comment in enumerate(sentiment_data['sample_comments'][:5], 1):
            sentiment_emoji = "😊" if comment['sentiment'] == 'positive' else "😟" if comment['sentiment'] == 'negative' else "😐"
            context += f"\n{i}. {sentiment_emoji} \"{comment['text'][:150]}...\""
            context += f"\n   (From: {comment['video_title'][:60]}...)"
        
        return context


# Global instance
youtube_comment_sentiment = YouTubeCommentSentiment()
