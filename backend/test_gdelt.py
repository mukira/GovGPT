"""
Test script for GDELT service
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.news.gdelt_service import gdelt_service

# Test fetching Kenya news
print("🔍 Fetching Kenyan news from GDELT...")
print("=" * 60)

articles = gdelt_service.fetch_kenya_news(lookback_days=3, max_results=5)

print(f"\n✅ Found {len(articles)} articles\n")

for i, article in enumerate(articles, 1):
    print(f"📰 Article {i}:")
    print(f"   Title: {article['title'][:60]}...")
    print(f"   URL: {article['url'][:80]}...")
    print(f"   Domain: {article['domain']}")
    print(f"   Published: {article['published_at']}")
    print(f"   Sentiment: {article['sentiment']} (Tone: {article['tone']})")
    print(f"   Source Type: {article['source_type']}")
    print()
