"""
Test all social media platforms
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

print("🌍 Testing Social Media Platforms for Kenya")
print("=" * 70)

# Test 1: Telegram
print("\n📱 Test 1: Telegram Public Channels")
print("-" * 70)
from app.services.social_media.telegram_service import telegram_service

try:
    telegram_posts = telegram_service.get_channel_messages('kenyans_ke', limit=3)
    print(f"✅ Telegram: {len(telegram_posts)} posts fetched")
    for post in telegram_posts[:2]:
        print(f"   • {post['content'][:60]}...")
except Exception as e:
    print(f"❌ Telegram: {e}")

# Test 2: Mastodon
print("\n🐘 Test 2: Mastodon/Fediverse")
print("-" * 70)
from app.services.social_media.mastodon_service import mastodon_service

try:
    mastodon_posts = mastodon_service.search_kenya_posts("Kenya", limit=5)
    print(f"✅ Mastodon: {len(mastodon_posts)} posts fetched")
    for post in mastodon_posts[:2]:
        print(f"   • @{post['username']}: {post['content'][:50]}...")
except Exception as e:
    print(f"❌ Mastodon: {e}")

# Test 3: Sentiment Analysis
print("\n🧠 Test 3: Sentiment Analysis")
print("-" * 70)
from app.services.social_media.sentiment_service import sentiment_analyzer

test_texts = [
    "Kenya's new agricultural policy is excellent for farmers!",
    "The government budget cuts are disappointing.",
    "Parliament met today to discuss the new bill."
]

for text in test_texts:
    result = sentiment_analyzer.analyze(text)
    print(f"   • \"{text[:40]}...\"")
    print(f"     → {result['sentiment'].upper()} (polarity: {result['polarity']})")

print("\n" + "=" * 70)
print("✅ Social media platform tests complete!")
