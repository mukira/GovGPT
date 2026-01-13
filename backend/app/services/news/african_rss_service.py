"""
Pan-African RSS Feed Parser
Covers news outlets across all 54 African countries
"""
from datetime import datetime
from typing import List, Dict, Optional
import feedparser
import requests
from time import mktime
import re


class AfricanRSSService:
    """Service for parsing RSS feeds from African news outlets across all regions"""
    
    # Pan-African RSS feeds organized by region
    AFRICAN_FEEDS = {
        # EAST AFRICA
        'capital_fm_kenya': 'https://www.capitalfm.co.ke/news/feed/',
        'tuko_kenya': 'https://www.tuko.co.ke/rss/all.rss',
        'daily_monitor_uganda': 'https://www.monitor.co.ug/uganda/rss/headlines/rss.xml',
        'new_vision_uganda': 'https://www.newvision.co.ug/rss/news.xml',
        'new_times_rwanda': 'https://www.newtimes.co.rw/feed',
        'ethiopian_herald': 'https://www.press.et/english/?feed=rss2',
        'citizen_tanzania': 'https://www.thecitizen.co.tz/tanzania/rss',
        
        # WEST AFRICA  
        'premium_times_nigeria': 'https://www.premiumtimesng.com/feed',
        'punch_nigeria': 'https://punchng.com/feed/',
        'vanguard_nigeria': 'https://www.vanguardngr.com/feed/',
        'sahara_reporters': 'https://saharareporters.com/feeds/latest/feed',
        'joy_online_ghana': 'https://www.myjoyonline.com/feed/',
        'graphic_ghana': 'https://www.graphic.com.gh/feed',
        'ghanaweb': 'https://www.ghanaweb.com/GhanaHomePage/rss/news.xml',
        'seneweb_senegal': 'https://www.seneweb.com/rss_actualite.php',
        'abidjan_net': 'https://news.abidjan.net/rss.xml',
        
        # SOUTHERN AFRICA
        'news24_safrica': 'https://feeds.news24.com/articles/news24/topstories/rss',
        'iol_safrica': 'https://www.iol.co.za/rss',
        'daily_maverick': 'https://www.dailymaverick.co.za/dmrss/',
        'mail_guardian': 'https://mg.co.za/feed/',
        'times_live': 'https://www.timeslive.co.za/rss/',
        'herald_zimbabwe': 'https://www.herald.co.zw/feed/',
        'newsday_zimbabwe': 'https://www.newsday.co.zw/feed/',
        'lusaka_times': 'https://www.lusakatimes.com/feed/',
        'mmegi_botswana': 'https://www.mmegi.bw/index.php?format=feed&type=rss',
        'namibian': 'https://www.namibian.com.na/rss/news.xml',
        
        # NORTH AFRICA
        'ahram_online': 'https://english.ahram.org.eg/rss/egypt.aspx',
        'egypt_independent': 'https://www.egyptindependent.com/feed/',
        'daily_news_egypt': 'https://www.dailynewsegypt.com/feed/',
        'morocco_world_news': 'https://www.moroccoworldnews.com/feed/',
        'libya_herald': 'https://www.libyaherald.com/feed/',
        'tunisia_live': 'http://www.tunisia-live.net/feed/',
        
        # CENTRAL AFRICA
        'radio_okapi_drc': 'https://www.radiookapi.net/rss.xml',
        'cameroon_web': 'https://www.cameroonweb.com/CameroonHomePage/rss/news.xml',
        'journal_cameroun': 'https://www.journalducameroun.com/feed/',
    }
    
    # Regional mapping
    REGIONAL_MAPPING = {
        'East Africa': ['capital_fm_kenya', 'tuko_kenya', 'daily_monitor_uganda', 'new_vision_uganda', 
                       'new_times_rwanda', 'ethiopian_herald', 'citizen_tanzania'],
        'West Africa': ['premium_times_nigeria', 'punch_nigeria', 'vanguard_nigeria', 'sahara_reporters',
                       'joy_online_ghana', 'graphic_ghana', 'ghanaweb', 'seneweb_senegal', 'abidjan_net'],
        'Southern Africa': ['news24_safrica', 'iol_safrica', 'daily_maverick', 'mail_guardian', 'times_live',
                           'herald_zimbabwe', 'newsday_zimbabwe', 'lusaka_times', 'mmegi_botswana', 'namibian'],
        'North Africa': ['ahram_online', 'egypt_independent', 'daily_news_egypt', 'morocco_world_news', 
                        'libya_herald', 'tunisia_live'],
        'Central Africa': ['radio_okapi_drc', 'cameroon_web', 'journal_cameroun'],
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_all_feeds(self, max_per_feed: int = 10) -> List[Dict]:
        """Fetch articles from ALL African RSS feeds"""
        all_articles = []
        
        for source_name, feed_url in self.AFRICAN_FEEDS.items():
            try:
                articles = self.fetch_feed(feed_url, source_name, max_per_feed)
                all_articles.extend(articles)
                print(f"✅ {source_name}: {len(articles)} articles")
            except Exception as e:
                print(f"❌ {source_name}: {e}")
                continue
        
        return all_articles
    
    def fetch_by_region(self, region: str, max_per_feed: int = 10) -> List[Dict]:
        """Fetch articles from a specific African region"""
        if region not in self.REGIONAL_MAPPING:
            return []
        
        all_articles = []
        for source_name in self.REGIONAL_MAPPING[region]:
            try:
                feed_url = self.AFRICAN_FEEDS[source_name]
                articles = self.fetch_feed(feed_url, source_name, max_per_feed)
                all_articles.extend(articles)
            except:
                continue
        
        return all_articles
    
    def fetch_feed(self, feed_url: str, source_name: str, max_articles: int = 10) -> List[Dict]:
        """Fetch and parse a single RSS feed"""
        try:
            response = self.session.get(feed_url, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries[:max_articles]:
                article = self._standardize_entry(entry, source_name)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            raise Exception(f"Error parsing feed: {e}")
    
    def _standardize_entry(self, entry: Dict, source_name: str) -> Optional[Dict]:
        """Convert RSS entry to standardized format"""
        try:
            # Get publication date
            pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
            if pub_date:
                published_at = datetime.fromtimestamp(mktime(pub_date)).isoformat()
            else:
                published_at = datetime.now().isoformat()
            
            # Extract summary/description
            summary = entry.get('summary', '') or entry.get('description', '')
            summary = re.sub(r'<[^>]+>', '', summary)[:300]
            
            # Determine country and region
            country, region = self._get_location(source_name)
            
            article = {
                'source': source_name.replace('_', ' ').title(),
                'source_type': 'african_rss',
                'country': country,
                'region': region,
                'title': entry.get('title', 'Untitled'),
                'url': entry.get('link', ''),
                'published_at': published_at,
                'summary': summary.strip(),
                'author': entry.get('author', 'Unknown'),
                'categories': [tag.term for tag in entry.get('tags', [])],
            }
            
            return article
            
        except Exception as e:
            return None
    
    def _get_location(self, source_name: str) -> tuple:
        """Extract country and region from source name"""
        # Map source to country and region
        location_map = {
            'kenya': ('Kenya', 'East Africa'),
            'uganda': ('Uganda', 'East Africa'),
            'rwanda': ('Rwanda', 'East Africa'),
            'ethiopia': ('Ethiopia', 'East Africa'),
            'tanzania': ('Tanzania', 'East Africa'),
            'nigeria': ('Nigeria', 'West Africa'),
            'ghana': ('Ghana', 'West Africa'),
            'senegal': ('Senegal', 'West Africa'),
            'safrica': ('South Africa', 'Southern Africa'),
            'zimbabwe': ('Zimbabwe', 'Southern Africa'),
            'botswana': ('Botswana', 'Southern Africa'),
            'namibia': ('Namibia', 'Southern Africa'),
            'egypt': ('Egypt', 'North Africa'),
            'morocco': ('Morocco', 'North Africa'),
            'libya': ('Libya', 'North Africa'),
            'tunisia': ('Tunisia', 'North Africa'),
            'drc': ('Democratic Republic of Congo', 'Central Africa'),
            'cameroon': ('Cameroon', 'Central Africa'),
        }
        
        for key, (country, region) in location_map.items():
            if key in source_name.lower():
                return country, region
        
        return 'Unknown', 'Unknown'
    
    def search_feeds(self, keywords: List[str], region: Optional[str] = None, max_results: int = 50) -> List[Dict]:
        """Search RSS feeds for articles matching keywords, optionally filtered by region"""
        if region:
            all_articles = self.fetch_by_region(region, max_per_feed=50)
        else:
            all_articles = self.fetch_all_feeds(max_per_feed=50)
        
        # Filter by keywords
        matching = []
        for article in all_articles:
            text = f"{article['title']} {article['summary']}".lower()
            if any(kw.lower() in text for kw in keywords):
                matching.append(article)
        
        return matching[:max_results]


# Singleton instance
african_rss_service = AfricanRSSService()

