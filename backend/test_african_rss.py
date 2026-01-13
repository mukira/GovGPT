"""
Test script for Pan-African RSS service
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.news.african_rss_service import african_rss_service

print("🌍 Testing Pan-African RSS Feeds")
print("=" * 70)

# Test by region
regions = ['East Africa', 'West Africa', 'Southern Africa', 'North Africa', 'Central Africa']

for region in regions:
    print(f"\n📍 {region}:")
    print("-" * 70)
    articles = african_rss_service.fetch_by_region(region, max_per_feed=3)
    print(f"   Total articles: {len(articles)}")
    
    if articles:
        for i, article in enumerate(articles[:2], 1):
            print(f"   {i}. [{article['country']}] {article['title'][:50]}...")

print("\n" + "=" * 70)
print(f"\n✅ Pan-African RSS system operational!")
print(f"   Total feeds configured: {len(african_rss_service.AFRICAN_FEEDS)}")
print(f"   Regions covered: {len(african_rss_service.REGIONAL_MAPPING)}")
