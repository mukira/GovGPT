"""
Test Reddit + Sentiment Analysis Integration
Fetch Kenya posts from Reddit and analyze sentiment
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.social_media.reddit_service import reddit_service
from app.services.social_media.sentiment_service import sentiment_analyzer

print("🔍 Testing Reddit + Sentiment Analysis for Kenya")
print("=" * 70)

# Step 1: Fetch Kenya posts
print("\n📱 Step 1: Fetching posts from Kenya subreddits...")
print("-" * 70)

posts = reddit_service.fetch_kenya_posts(
    keywords=['government', 'policy', 'president', 'parliament'],
    limit=10,
    time_filter='week'
)

print(f"✅ Fetched {len(posts)} Kenya posts\n")

# Step 2: Analyze sentiment for each post
print("\n🧠 Step 2: Analyzing sentiment...")
print("-" * 70)

for i, post in enumerate(posts[:5], 1):
    # Combine title and content for analysis
    text = f"{post['title']} {post['content']}"
    
    # Analyze sentiment
    sentiment = sentiment_analyzer.analyze(text)
    
    # Display results
    print(f"\n{i}. r/{post['subreddit']}: {post['title'][:50]}...")
    print(f"   👤 By: u/{post['author']}")
    print(f"   ⬆️  Score: {post['score']} | 💬 Comments: {post['num_comments']}")
    print(f"   😊 Sentiment: {sentiment['sentiment'].upper()} ({sentiment['confidence']} confidence, {sentiment['score']:.2f})")
    print(f"   🔗 {post['url']}")

# Step 3: Calculate overall sentiment
print("\n\n📊 Step 3: Overall Kenya Sentiment Analysis")
print("-" * 70)

sentiments = []
for post in posts:
    text = f"{post['title']} {post['content']}"
    result = sentiment_analyzer.analyze(text)
    sentiments.append(result['sentiment'])

positive_count = sentiments.count('positive')
negative_count = sentiments.count('negative')
neutral_count = sentiments.count('neutral')

total = len(sentiments)
print(f"\n📈 Overall Sentiment Distribution:")
print(f"   ✅ Positive: {positive_count}/{total} ({positive_count/total*100:.1f}%)")
print(f"   ❌ Negative: {negative_count}/{total} ({negative_count/total*100:.1f}%)")
print(f"   ⚪ Neutral:  {neutral_count}/{total} ({neutral_count/total*100:.1f}%)")

print("\n" + "=" * 70)
print("✅ Reddit sentiment analysis working!")
