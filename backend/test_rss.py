"""
Test script for Kenyan RSS service
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.news.kenya_rss_service import kenyan_rss_service

# Test fetching from all RSS feeds
print("🔍 Fetching from Kenyan RSS feeds...")
print("=" * 60)

articles = kenyan_rss_service.fetch_all_feeds(max_per_feed=5)

print(f"\n✅ Found {len(articles)} articles from RSS feeds\n")

for i, article in enumerate(articles, 1):
    print(f"📰 Article {i}:")
    print(f"   Source: {article['source']}")
    print(f"   Title: {article['title'][:60]}...")
    print(f"   URL: {article['url'][:80]}...")
    print(f"   Published: {article['published_at']}")
    print(f"   Categories: {', '.join(article['categories'][:3]) if article['categories'] else 'None'}")
    print()

# Test searching
print("\n🔎 Searching for 'government' and 'policy'...")
print("=" * 60)

search_results = kenyan_rss_service.search_feeds(['government', 'policy'], max_results=3)

print(f"\n✅ Found {len(search_results)} matching articles\n")

for i, article in enumerate(search_results, 1):
    print(f"📰 Match {i}:")
    print(f"   Source: {article['source']}")
    print(f"   Title: {article['title']}")
    print(f"   Summary: {article['summary'][:100]}...")
    print()
