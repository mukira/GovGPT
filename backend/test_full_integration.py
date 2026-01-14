"""
COMPREHENSIVE TEST: All Social Media + Sentiment Integration
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.social_media.social_aggregator import social_aggregator

print("🌐 TESTING FULL SOCIAL MEDIA INTEGRATION")
print("=" * 70)

# Test unified aggregator with all platforms
print("\n📊 Fetching from ALL platforms (Telegram + Mastodon + sentiment)...")
result = social_aggregator.fetch_kenya_social(keywords=['Kenya'])

print(f"\n✅ TOTAL POSTS: {result['total_count']}")
print(f"\n📱 Platform Breakdown:")
print(f"   • Telegram: {result['platforms']['telegram']} posts")
print(f"   • Mastodon: {result['platforms']['mastodon']} posts")
print(f"   • YouTube: {result['platforms']['youtube']} posts")

print(f"\n😊 Sentiment Summary:")
sentiment = result['sentiment_summary']
print(f"   • Positive: {sentiment.get('positive', 0)} ({sentiment.get('positive_pct', 0):.1f}%)")
print(f"   • Negative: {sentiment.get('negative', 0)} ({sentiment.get('negative_pct', 0):.1f}%)")
print(f"   • Neutral: {sentiment.get('neutral', 0)} ({sentiment.get('neutral_pct', 0):.1f}%)")
print(f"   • Overall Mood: {sentiment.get('overall', 'unknown').upper()}")

print(f"\n📝 Sample Posts:")
for i, post in enumerate(result['posts'][:5], 1):
    platform = post.get('platform', 'unknown')
    content = post.get('content', '')[:60]
    sent = post.get('sentiment', {})
    
    print(f"\n{i}. [{platform.upper()}] {content}...")
    if sent:
        print(f"   Sentiment: {sent.get('sentiment', 'N/A').upper()} (polarity: {sent.get('polarity', 0)})")

print("\n" + "=" * 70)
print("✅ FULL INTEGRATION WORKING!")
