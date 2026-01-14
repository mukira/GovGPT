"""
Telegram Service for Kenya Public Channels
Fetches messages from public Kenya news and politics channels
"""
from datetime import datetime
from typing import List, Dict, Optional
import requests


class TelegramService:
    """Service for fetching messages from public Kenya Telegram channels"""
    
    # Public Kenya Telegram channels (public, no auth needed to read)
    KENYA_CHANNELS = {
        'kenyans_ke': 'kenyans_ke',
        'kenya_news': 'kenya_news_today',
        'kenyan_politics': 'kenyanpolitics',
        'citizen_tv': 'citizentvkenya',
        'nation_africa': 'nationafrica',
    }
    
    BASE_URL = "https://api.telegram.org/bot{token}/"
    
    def __init__(self, bot_token: str = None, api_id: str = None, api_hash: str = None):
        """
        Initialize Telegram service
        
        Args:
            bot_token: Telegram Bot API token (optional)
            api_id: Telegram API ID from my.telegram.org
            api_hash: Telegram API Hash from my.telegram.org
        """
        self.bot_token = bot_token
        self.api_id = api_id
        self.api_hash = api_hash
        
        if api_id and api_hash:
            self.authenticated = True
        else:
            self.authenticated = False
    
    def get_channel_messages(
        self,
        channel_name: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch recent messages from a public Telegram channel
        
        Note: For public channels, we can use the public web interface
        or t.me preview which doesn't require bot token
        
        Args:
            channel_name: Channel username (without @)
            limit: Maximum messages to return
            
        Returns:
            List of message dictionaries
        """
        # For public channels, use web preview (no token needed)
        try:
            url = f"https://t.me/s/{channel_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            # Parse HTML for messages (basic extraction)
            messages = self._parse_telegram_web(response.text, channel_name, limit)
            return messages
            
        except Exception as e:
            print(f"Error fetching Telegram channel: {e}")
            return []
    
    def _parse_telegram_web(self, html: str, channel_name: str, limit: int) -> List[Dict]:
        """Parse Telegram web preview for messages"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        messages = []
        
        # Find message bubbles
        message_divs = soup.find_all('div', class_='tgme_widget_message_bubble')
        
        for div in message_divs[:limit]:
            try:
                # Extract text
                text_div = div.find('div', class_='tgme_widget_message_text')
                text = text_div.get_text(strip=True) if text_div else ''
                
                # Extract date
                date_div = div.find('time', class_='datetime')
                date_str = date_div.get('datetime', '') if date_div else ''
                
                # Extract views
                views_span = div.find('span', class_='tgme_widget_message_views')
                views = views_span.get_text(strip=True) if views_span else '0'
                
                if text:
                    messages.append({
                        'platform': 'telegram',
                        'channel': channel_name,
                        'content': text[:500],
                        'published_at': date_str,
                        'views': self._parse_views(views),
                        'url': f"https://t.me/{channel_name}"
                    })
                    
            except Exception:
                continue
        
        return messages
    
    def _parse_views(self, views_str: str) -> int:
        """Parse view count string (e.g., '1.2K' -> 1200)"""
        try:
            views_str = views_str.replace(' ', '').upper()
            if 'K' in views_str:
                return int(float(views_str.replace('K', '')) * 1000)
            elif 'M' in views_str:
                return int(float(views_str.replace('M', '')) * 1000000)
            return int(views_str.replace(',', ''))
        except:
            return 0
    
    def fetch_all_kenya_channels(self, limit_per_channel: int = 10) -> List[Dict]:
        """Fetch messages from all configured Kenya channels"""
        all_messages = []
        
        for name, username in self.KENYA_CHANNELS.items():
            try:
                messages = self.get_channel_messages(username, limit_per_channel)
                all_messages.extend(messages)
                print(f"✅ {name}: {len(messages)} messages")
            except Exception as e:
                print(f"❌ {name}: {e}")
                continue
        
        return all_messages
    
    def search_kenya_topics(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Search Kenya channels for specific topics"""
        all_messages = self.fetch_all_kenya_channels(limit_per_channel=20)
        
        # Filter by keywords
        matching = []
        for msg in all_messages:
            text = msg['content'].lower()
            if any(kw.lower() in text for kw in keywords):
                matching.append(msg)
        
        return matching[:limit]


# Initialize service with credentials from environment
from app.config import settings
import os

api_id = settings.TELEGRAM_API_ID or os.getenv('TELEGRAM_API_ID')
api_hash = settings.TELEGRAM_API_HASH or os.getenv('TELEGRAM_API_HASH')

if api_id and api_hash:
    print(f"✅ Telegram service initialized with API ID: {api_id}")
    telegram_service = TelegramService(bot_token=None, api_id=api_id, api_hash=api_hash)
else:
    print("⚠️  Telegram credentials not found - using public access only")
    telegram_service = TelegramService()
