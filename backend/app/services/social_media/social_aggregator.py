"""
Unified Social Media Aggregator
Combines all social media sources with sentiment analysis
"""
from typing import List, Dict, Optional
from app.services.social_media.telegram_service import telegram_service
from app.services.social_media.mastodon_service import mastodon_service
from app.services.social_media.sentiment_service import sentiment_analyzer


class SocialAggregator:
    """Unified aggregator for all social media platforms"""
    
    def __init__(self):
        self.telegram = telegram_service
        self.mastodon = mastodon_service
        self.sentiment = sentiment_analyzer
    
    def fetch_kenya_social(
        self,
        keywords: Optional[List[str]] = None,
        include_sentiment: bool = True
    ) -> Dict:
        """
        Fetch all Kenya social media content with sentiment analysis
        
        Args:
            keywords: Optional keywords to filter content
            include_sentiment: Whether to analyze sentiment
            
        Returns:
            Dictionary with posts from all platforms and sentiment summary
        """
        all_posts = []
        
        # Fetch from Telegram
        try:
            telegram_posts = self.telegram.fetch_all_kenya_channels(limit_per_channel=5)
            for post in telegram_posts:
                if include_sentiment:
                    post['sentiment'] = self.sentiment.analyze(post['content'])
                all_posts.append(post)
        except Exception as e:
            print(f"Telegram error: {e}")
        
        # Fetch from Mastodon
        try:
            query = keywords[0] if keywords else "Kenya"
            mastodon_posts = self.mastodon.search_kenya_posts(query=query, limit=20)
            for post in mastodon_posts:
                if include_sentiment:
                    post['sentiment'] = self.sentiment.analyze(post['content'])
                all_posts.append(post)
        except Exception as e:
            print(f"Mastodon error: {e}")
        
        # Calculate overall sentiment
        sentiment_summary = self._calculate_sentiment_summary(all_posts)
        
        return {
            'posts': all_posts,
            'total_count': len(all_posts),
            'sentiment_summary': sentiment_summary,
            'platforms': {
                'telegram': len([p for p in all_posts if p.get('platform') == 'telegram']),
                'mastodon': len([p for p in all_posts if p.get('platform') == 'mastodon']),
                'youtube': len([p for p in all_posts if p.get('platform') == 'youtube']),
            }
        }
    
    def _calculate_sentiment_summary(self, posts: List[Dict]) -> Dict:
        """Calculate sentiment distribution across posts"""
        sentiments = []
        for post in posts:
            if 'sentiment' in post:
                sentiments.append(post['sentiment']['sentiment'])
        
        if not sentiments:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'overall': 'unknown'}
        
        total = len(sentiments)
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        
        # Determine overall mood
        if positive > negative:
            overall = 'optimistic'
        elif negative > positive:
            overall = 'concerned'
        else:
            overall = 'balanced'
        
        return {
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_pct': round(positive / total * 100, 1),
            'negative_pct': round(negative / total * 100, 1),
            'neutral_pct': round(neutral / total * 100, 1),
            'overall': overall
        }
    
    def get_kenya_pulse(self) -> Dict:
        """Get overall Kenya social media pulse"""
        return self.fetch_kenya_social(keywords=['Kenya', 'government', 'policy'])


# Singleton instance
social_aggregator = SocialAggregator()
