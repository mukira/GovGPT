"""
GDELT Service for fetching Kenyan news sources via REST API
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from urllib.parse import quote


class GDELTService:
    """Service for fetching news from GDELT focused on Kenya"""
    
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    def __init__(self):
        pass
        
    def fetch_kenya_news(
        self,
        lookback_days: int = 7,
        keywords: Optional[List[str]] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Fetch news articles about Kenya from GDELT
        
        Args:
            lookback_days: Number of days to look back
            keywords: Optional keywords to filter (e.g., ["policy", "government"])
            max_results: Maximum number of results to return
            
        Returns:
            List of article dictionaries with standardized format
        """
        try:
            # Build comprehensive Kenya search query
            query_parts = ["Kenya"]
            
            # Add policy-specific keywords if provided
            if keywords:
                # Filter out 'kenya' to avoid duplication
                topic_keywords = [k for k in keywords if k.lower() != 'kenya']
                if topic_keywords:
                    query_parts.extend(topic_keywords[:3])
            else:
                # Default: comprehensive Kenya policy coverage
                policy_keywords = [
                    "government", "policy", "legislation", "parliament",
                    "senate", "county", "ministry", "budget", "economy",
                    "agriculture", "education", "health", "infrastructure"
                ]
                query_parts.extend(policy_keywords[:3])  # Add top 3 for broader coverage
            
            query = " ".join(query_parts)
            print(f"📰 GDELT search: '{query}'")
            
            # Build API parameters
            params = {
                "query": query,
                "mode": "ArtList",  # Article list mode
                "maxrecords": max_results,
                "format": "json",
                "timespan": f"{lookback_days}d"  # Last N days
            }
            
            # Make request
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse articles
            articles = []
            if "articles" in data:
                for item in data["articles"]:
                    article = self._standardize_article(item)
                    if article and self._is_kenya_relevant(article):
                        articles.append(article)
            
            print(f"📰 GDELT: Found {len(articles)} Kenya-relevant articles")
            return articles[:max_results]
            
        except Exception as e:
            print(f"❌ Error fetching GDELT data: {e}")
            return []
    
    def _is_kenya_relevant(self, article: Dict) -> bool:
        """Check if article is actually about Kenya"""
        text = f"{article.get('title', '')} {article.get('url', '')} {article.get('domain', '')}".lower()
        
        # Must contain Kenya reference
        kenya_terms = ['kenya', 'kenyan', 'nairobi', '.ke']
        has_kenya = any(term in text for term in kenya_terms)
        
        # Exclude other African countries (unless Kenya is also mentioned)
        exclude_terms = ['sudan', 'botswana', 'somalia', 'ethiopia', 'uganda', 'tanzania']
        is_other_country = any(term in text for term in exclude_terms) and not has_kenya
        
        return has_kenya and not is_other_country
            
    def _standardize_article(self, item: Dict) -> Optional[Dict]:
        """Convert GDELT article to standardized format"""
        try:
            article = {
                'source': 'GDELT',
                'source_type': 'local',  # Kenyan sources
                'title': item.get('title', 'Untitled'),
                'url': item.get('url', ''),
                'published_at': item.get('seendate', datetime.now().isoformat()),
                'domain': item.get('domain', ''),
                'language': item.get('language', 'en'),
                'tone': float(item.get('tone', 0)),
                'sentiment': self._calculate_sentiment(float(item.get('tone', 0))),
                'image_url': item.get('socialimage', ''),
            }
            
            # Determine if it's Kenyan source
            domain = article['domain'].lower()
            kenyan_domains = ['nation.africa', 'standardmedia.co.ke', 'citizen.digital', 
                            'businessdailyafrica.com', 'the-star.co.ke', 'kbc.co.ke']
            
            if any(kd in domain for kd in kenyan_domains):
                article['source_type'] = 'kenyan_outlet'
            
            article['tone_positive'] = article['tone'] > 2
            article['tone_negative'] = article['tone'] < -2
            article['tone_neutral'] = abs(article['tone']) <= 2
            
            return article
            
        except Exception as e:
            print(f"Error standardizing article: {e}")
            return None
    
    def _calculate_sentiment(self, tone: float) -> str:
        """Calculate sentiment category from tone score"""
        if tone > 2:
            return "positive"
        elif tone < -2:
            return "negative"
        else:
            return "neutral"


# Singleton instance
gdelt_service = GDELTService()
