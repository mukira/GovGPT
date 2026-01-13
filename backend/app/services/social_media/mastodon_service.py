"""
Mastodon/Fediverse Service for Kenya discussions
Fetches posts from Mastodon instances with Kenya content
"""
from datetime import datetime
from typing import List, Dict, Optional
import requests


class MastodonService:
    """Service for fetching Kenya discussions from Mastodon/Fediverse"""
    
    # Major Mastodon instances that may have Kenya content
    MASTODON_INSTANCES = [
        'mastodon.social',
        'mastodon.cloud',
        'mstdn.social',
    ]
    
    def __init__(self, access_token: str = None, instance: str = 'mastodon.social'):
        """
        Initialize Mastodon service
        
        Args:
            access_token: Optional Mastodon access token
            instance: Mastodon instance domain
        """
        self.access_token = access_token
        self.instance = instance
        self.base_url = f"https://{instance}/api/v1"
        
        self.headers = {}
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
            print(f"✅ Mastodon connected to {instance}")
        else:
            print(f"⚠️ Mastodon using public timeline (no auth)")
    
    def search_kenya_posts(
        self,
        query: str = "Kenya",
        limit: int = 40
    ) -> List[Dict]:
        """
        Search for Kenya-related posts on Mastodon
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of post dictionaries
        """
        try:
            # Use public search API (available without auth)
            url = f"{self.base_url}/timelines/tag/{query.lower()}"
            params = {'limit': min(limit, 40)}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                # Try search endpoint
                return self._search_statuses(query, limit)
            
            posts = []
            for item in response.json():
                post = self._standardize_post(item)
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error fetching Mastodon posts: {e}")
            return []
    
    def _search_statuses(self, query: str, limit: int) -> List[Dict]:
        """Search statuses using search API"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'q': query,
                'type': 'statuses',
                'limit': min(limit, 40)
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = []
            for item in data.get('statuses', []):
                post = self._standardize_post(item)
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error searching Mastodon: {e}")
            return []
    
    def get_public_timeline(self, limit: int = 20) -> List[Dict]:
        """Get public timeline and filter for Kenya content"""
        try:
            url = f"{self.base_url}/timelines/public"
            params = {'limit': min(limit, 40)}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            posts = []
            for item in response.json():
                # Filter for Kenya-related content
                content = item.get('content', '').lower()
                if 'kenya' in content or 'nairobi' in content:
                    post = self._standardize_post(item)
                    posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error fetching public timeline: {e}")
            return []
    
    def _standardize_post(self, item: Dict) -> Dict:
        """Convert Mastodon status to standardized format"""
        # Strip HTML from content
        import re
        content = re.sub(r'<[^>]+>', '', item.get('content', ''))
        
        account = item.get('account', {})
        
        return {
            'platform': 'mastodon',
            'instance': self.instance,
            'post_id': item.get('id', ''),
            'content': content[:500],
            'author': account.get('display_name', 'Anonymous'),
            'username': account.get('acct', ''),
            'url': item.get('url', ''),
            'published_at': item.get('created_at', ''),
            'engagement': {
                'replies': item.get('replies_count', 0),
                'reblogs': item.get('reblogs_count', 0),
                'favorites': item.get('favourites_count', 0)
            },
            'language': item.get('language', 'en')
        }
    
    def fetch_from_multiple_instances(self, query: str = "Kenya", limit_per: int = 10) -> List[Dict]:
        """Search multiple Mastodon instances for Kenya content"""
        all_posts = []
        
        for instance in self.MASTODON_INSTANCES:
            try:
                temp_service = MastodonService(instance=instance)
                posts = temp_service.search_kenya_posts(query, limit_per)
                all_posts.extend(posts)
                print(f"✅ {instance}: {len(posts)} posts")
            except Exception as e:
                print(f"❌ {instance}: {e}")
                continue
        
        return all_posts


# Singleton instance
mastodon_service = MastodonService()
