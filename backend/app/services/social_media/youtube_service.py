"""
YouTube Service for Kenya News Channel Comments
Fetches comments from Citizen TV, KTN, NTV and other Kenya news channels
"""
from datetime import datetime
from typing import List, Dict, Optional
from googleapiclient.discovery import build


class YouTubeService:
    """Service for fetching Kenya news channel comments from YouTube"""
    
    # ALL Kenya news channel IDs
    KENYA_CHANNELS = {
        # Major TV Stations
        'citizen_tv': 'UCr1ndHU7CP-Zd7tXoDsv9mA',      # Citizen TV Kenya
        'ktn_news': 'UCmulUe0S0-9MrXOIlNxfYjQ',         # KTN News Kenya
        'ntv_kenya': 'UCRnEELsRxmkNcJpU7RWHJ6Q',        # NTV Kenya
        'kbc_channel1': 'UCxQNqO8_8fxGCJxE0sZKXRg',     # KBC Channel 1
        'k24tv': 'UCuGikr9ckIw9Vsk9XdRxqlQ',            # K24 TV
        'tv47_kenya': 'UC7RQon_YwCNp_EbdmGHzDzQ',       # TV47 Kenya
        'switch_tv': 'UCWxLADMCMhGBlgGRmW-YBww',        # Switch TV
        
        # Newspapers & Digital
        'nation_africa': 'UCL_qhDIV47Yn8ouZvBCdVBg',    # Nation Africa (Daily Nation)
        'standard_digital': 'UCxIMmLAMnR0M8u1GzEKYGng', # Standard Digital
        'the_star_kenya': 'UCqQO8CRq1f0zSJB2h3e5pkg',   # The Star Kenya
        'business_daily': 'UCqA0j6V1L5ecV5KwfphU3_g',   # Business Daily Africa
        
        # Political/Analysis
        'trending_kenya': 'UCl4CG9BBPm1HUP4lWBfZl5g',   # Trending Kenya
        'kenya_citizen_tv': 'UCr1ndHU7CP-Zd7tXoDsv9mA', # Kenya Citizen TV (backup)
        'spice_fm': 'UCpPNO6P2-1NqqI0FfX6nVig',         # Spice FM
        
        # Radio Stations (with video)
        'radio_citizen': 'UCvN0y6pFg3GYOQy-b1WVd1Q',    # Radio Citizen
        'kiss100': 'UCJ7VRHI8hnr5I5fSXBx9vJQ',          # Kiss 100 Kenya
        'classic_105': 'UC1cIJr7B5Dy1g8ukWRWR8dQ',      # Classic 105
        
        # Regional & Vernacular
        'inooro_tv': 'UCQ8S5JDyM9Xp2vKSmF8A7wA',        # Inooro TV
        'ramogi_tv': 'UCgqzCWCl0K4BLpfzZwP7dHQ',        # Ramogi TV
        'kass_tv': 'UC4kcQR8O9kL4XHH2RMKZN3w',          # Kass TV
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize YouTube service
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.youtube = None
        
        if api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def search_kenya_videos(
        self,
        query: str = "Kenya government policy",
        max_results: int = 10,
        published_after: str = None
    ) -> List[Dict]:
        """
        Search for Kenya-related videos with retry logic
        
        Args:
            query: Search query
            max_results: Maximum videos to return
            published_after: ISO datetime string for filtering
            
        Returns:
            List of video dictionaries
        """
        if not self.youtube:
            return []
        
        # Retry configuration
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Build request with longer timeout
                request = self.youtube.search().list(
                    part='snippet',
                    q=query,
                    type='video',
                    maxResults=max_results,
                    regionCode='KE',  # Kenya region
                    relevanceLanguage='en',
                    order='date'
                )
                
                # Execute with explicit timeout (60 seconds)
                import socket
                original_timeout = socket.getdefaulttimeout()
                try:
                    socket.setdefaulttimeout(60)  # 60 second timeout
                    response = request.execute()
                finally:
                    socket.setdefaulttimeout(original_timeout)
                
                # Success - process results
                videos = []
                for item in response.get('items', []):
                    video = self._standardize_video(item)
                    videos.append(video)
                
                print(f"📺 Found {len(videos)} YouTube videos on '{query}'")
                return videos
                
            except socket.timeout:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️  YouTube timeout (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    import time
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ YouTube timeout after {max_retries} attempts")
                    return []
                    
            except Exception as e:
                error_str = str(e).lower()
                
                # Retry on network errors
                if any(x in error_str for x in ['timeout', 'timed out', 'ssl', 'connection']):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⚠️  YouTube error: {e} (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                        import time
                        time.sleep(delay)
                        continue
                
                # Don't retry on quota/auth errors
                print(f"❌ YouTube API error: {e}")
                return []
        
        return []
    
    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Fetch comments from a specific video
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum comments to return
            
        Returns:
            List of comment dictionaries
        """
        if not self.youtube:
            return []
        
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),
                order='relevance'
            )
            response = request.execute()
            
            comments = []
            for item in response.get('items', []):
                comment = self._standardize_comment(item)
                comments.append(comment)
            
            return comments
            
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []
    
    def get_channel_videos(
        self,
        channel_name: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Get recent videos from a Kenya news channel
        
        Args:
            channel_name: Channel key from KENYA_CHANNELS
            max_results: Maximum videos to return
            
        Returns:
            List of video dictionaries
        """
        channel_id = self.KENYA_CHANNELS.get(channel_name)
        if not channel_id or not self.youtube:
            return []
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=max_results,
                order='date',
                type='video'
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video = self._standardize_video(item)
                videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"Error fetching channel videos: {e}")
            return []
    
    def _standardize_video(self, item: Dict) -> Dict:
        """Convert YouTube video to standardized format"""
        snippet = item.get('snippet', {})
        return {
            'platform': 'youtube',
            'video_id': item.get('id', {}).get('videoId', ''),
            'title': snippet.get('title', ''),
            'description': snippet.get('description', '')[:300],
            'channel': snippet.get('channelTitle', ''),
            'channel_id': snippet.get('channelId', ''),
            'published_at': snippet.get('publishedAt', ''),
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'url': f"https://youtube.com/watch?v={item.get('id', {}).get('videoId', '')}"
        }
    
    def _standardize_comment(self, item: Dict) -> Dict:
        """Convert YouTube comment to standardized format"""
        snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
        return {
            'platform': 'youtube',
            'comment_id': item.get('id', ''),
            'video_id': snippet.get('videoId', ''),
            'author': snippet.get('authorDisplayName', 'Anonymous'),
            'content': snippet.get('textDisplay', ''),
            'likes': snippet.get('likeCount', 0),
            'published_at': snippet.get('publishedAt', ''),
            'reply_count': item.get('snippet', {}).get('totalReplyCount', 0)
        }


# Will be initialized with API key from environment
youtube_service = YouTubeService()
