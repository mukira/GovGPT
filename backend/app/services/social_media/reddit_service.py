"""
Reddit Service for Kenya-focused discussions
Fetches posts and comments from Kenya subreddits with sentiment analysis
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import praw


class RedditService:
    """Service for fetching Kenya discussions from Reddit"""
    
    # Kenya-related subreddits
    KENYA_SUBREDDITS = [
        'Kenya',
        'Nairobi',
        'KenyanPolitics',
        'eastafrica',
    ]
    
    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = "GovGPT/1.0"):
        """
        Initialize Reddit service
        
        Args:
            client_id: Reddit app client ID (optional for read-only)
            client_secret: Reddit app secret (optional for read-only)
            user_agent: User agent string
        """
        if client_id and client_secret:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
        else:
            # Read-only mode (limited features but no auth required)
            self.reddit = praw.Reddit(
                client_id="",  # Empty for read-only
                client_secret="",
                user_agent=user_agent,
                check_for_updates=False,
                comment_kind="t1",
                message_kind="t4",
                redditor_kind="t2",
                submission_kind="t3",
                subreddit_kind="t5",
                trophy_kind="t6"
            )
    
    def fetch_kenya_posts(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 100,
        time_filter: str = 'week'
    ) -> List[Dict]:
        """
        Fetch Kenya-related posts from Reddit
        
        Args:
            keywords: Optional keywords to filter (e.g., ['policy', 'government'])
            limit: Number of posts to fetch per subreddit
            time_filter: 'hour', 'day', 'week', 'month', 'year', 'all'
            
        Returns:
            List of post dictionaries
        """
        all_posts = []
        
        for subreddit_name in self.KENYA_SUBREDDITS:
            try:
                posts = self._fetch_subreddit_posts(
                    subreddit_name, 
                    keywords, 
                    limit, 
                    time_filter
                )
                all_posts.extend(posts)
            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        # Sort by score (upvotes - downvotes)
        all_posts.sort(key=lambda x: x['score'], reverse=True)
        
        return all_posts
    
    def _fetch_subreddit_posts(
        self,
        subreddit_name: str,
        keywords: Optional[List[str]],
        limit: int,
        time_filter: str
    ) -> List[Dict]:
        """Fetch posts from a single subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        # Get hot posts
        for submission in subreddit.hot(limit=limit):
            # Filter by keywords if provided
            if keywords:
                text = f"{submission.title} {submission.selftext}".lower()
                if not any(kw.lower() in text for kw in keywords):
                    continue
            
            post = self._standardize_post(submission, subreddit_name)
            posts.append(post)
        
        return posts
    
    def _standardize_post(self, submission, subreddit_name: str) -> Dict:
        """Convert Reddit submission to standardized format"""
        return {
            'platform': 'reddit',
            'platform_type': 'social_media',
            'subreddit': subreddit_name,
            'post_id': submission.id,
            'title': submission.title,
            'content': submission.selftext,
            'author': str(submission.author) if submission.author else 'deleted',
            'url': f"https://reddit.com{submission.permalink}",
            'posted_at': datetime.fromtimestamp(submission.created_utc).isoformat(),
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'engagement': {
                'score': submission.score,
                'comments': submission.num_comments,
                'upvote_ratio': round(submission.upvote_ratio, 2)
            }
        }
    
    def fetch_top_comments(self, post_id: str, limit: int = 20) -> List[Dict]:
        """Fetch top comments from a Reddit post"""
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comment_sort = 'top'
            submission.comments.replace_more(limit=0)  # Don't fetch "load more" comments
            
            comments = []
            for comment in submission.comments[:limit]:
                if hasattr(comment, 'body'):
                    comments.append({
                        'comment_id': comment.id,
                        'author': str(comment.author) if comment.author else 'deleted',
                        'content': comment.body,
                        'score': comment.score,
                        'posted_at': datetime.fromtimestamp(comment.created_utc).isoformat()
                    })
            
            return comments
            
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []


# Singleton instance (no auth for now - read-only mode)
reddit_service = RedditService()
