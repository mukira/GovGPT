"""
Test Sentiment Analysis with existing news sources (GDELT + RSS)
No extra API setup required!
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.news.gdelt_service import gdelt_service
from app.services.news.african_rss_service import african_rss_service
from app.services.social_media.sentiment_service import sentiment_analyzer

print("🔍 Kenya News Sentiment Analysis")
print("=" * 70)

# Step 1: Fetch Kenya news from GDELT
print("\n📰 Step 1: Fetching Kenya news from GDELT...")
gdelt_articles = gdelt_service.fetch_kenya_news(lookback_days=7, max_results=10)
print(f"✅ Fetched {len(gdelt_articles)} GDELT articles")

# Step 2: Analyze sentiment for GDELT articles
print("\n🧠 Step 2: Analyzing GDELT sentiment...")
print("-" * 70)

gdelt_sentiments = []
for i, article in enumerate(gdelt_articles[:5], 1):
    result = sentiment_analyzer.analyze(article['title'])
    gdelt_sentiments.append(result['sentiment'])
    
    print(f"{i}. {article['title'][:55]}...")
    print(f"   📊 Sentiment: {result['sentiment'].upper()} (polarity: {result['polarity']})")

# Step 3: Fetch East Africa RSS news
print("\n\n📱 Step 3: Fetching East Africa RSS news...")
rss_articles = african_rss_service.fetch_by_region('East Africa', max_per_feed=5)
print(f"✅ Fetched {len(rss_articles)} RSS articles")

# Step 4: Analyze sentiment for RSS articles
print("\n🧠 Step 4: Analyzing RSS sentiment...")
print("-" * 70)

rss_sentiments = []
for i, article in enumerate(rss_articles[:5], 1):
    text = f"{article['title']} {article.get('summary', '')}"
    result = sentiment_analyzer.analyze(text)
    rss_sentiments.append(result['sentiment'])
    
    print(f"{i}. [{article['country']}] {article['title'][:45]}...")
    print(f"   📊 Sentiment: {result['sentiment'].upper()} (polarity: {result['polarity']})")

# Step 5: Overall sentiment summary
print("\n\n📊 OVERALL KENYA/EAST AFRICA SENTIMENT")
print("=" * 70)

all_sentiments = gdelt_sentiments + rss_sentiments
if all_sentiments:
    pos = all_sentiments.count('positive')
    neg = all_sentiments.count('negative')
    neu = all_sentiments.count('neutral')
    total = len(all_sentiments)
    
    print(f"  ✅ Positive: {pos}/{total} ({pos/total*100:.0f}%)")
    print(f"  ❌ Negative: {neg}/{total} ({neg/total*100:.0f}%)")
    print(f"  ⚪ Neutral:  {neu}/{total} ({neu/total*100:.0f}%)")
    
    # Determine overall mood
    if pos > neg:
        mood = "📈 OPTIMISTIC"
    elif neg > pos:
        mood = "📉 CONCERNED"
    else:
        mood = "⚖️ BALANCED"
    
    print(f"\n  🎯 Overall Mood: {mood}")

print("\n" + "=" * 70)
print("✅ News sentiment analysis complete!")
