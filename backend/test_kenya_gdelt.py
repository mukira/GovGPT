"""
Test enhanced Kenya GDELT queries
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.news.gdelt_service import gdelt_service

print("🔍 Testing Enhanced Kenya Queries with GDELT")
print("=" * 70)

# Test 1: Default Kenya query (with auto policy keywords)
print("\n1️⃣ Default Kenya Query (auto-adds policy keywords):")
print("-" * 70)
articles = gdelt_service.fetch_kenya_news(lookback_days=7, max_results=5)
print(f"✅ Found {len(articles)} articles\n")
for i, article in enumerate(articles[:3], 1):
    print(f"{i}. [{article['domain'][:30]}] {article['title'][:60]}...")
    print(f"   Sentiment: {article['sentiment']} | Tone: {article['tone']}")

# Test 2: Specific policy keywords
print("\n\n2️⃣ Kenya + Specific Keywords (agriculture, budget):")
print("-" * 70)
articles = gdelt_service.fetch_kenya_news(
    lookback_days=7, 
    keywords=['agriculture', 'budget'],
    max_results=5
)
print(f"✅ Found {len(articles)} articles\n")
for i, article in enumerate(articles[:3], 1):
    print(f"{i}. [{article['domain'][:30]}] {article['title'][:60]}...")

# Test 3: Government legislation focus
print("\n\n3️⃣ Kenya + Government Legislation:")
print("-" * 70)
articles = gdelt_service.fetch_kenya_news(
    lookback_days=7,
    keywords=['government', 'legislation', 'parliament'],
    max_results=5
)
print(f"✅ Found {len(articles)} articles\n")
for i, article in enumerate(articles[:3], 1):
    print(f"{i}. [{article['domain'][:30]}] {article['title'][:60]}...")

print("\n" + "=" * 70)
print("✅ Enhanced Kenya GDELT queries working!")
