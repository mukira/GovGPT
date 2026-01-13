"""
Test YouTube API with user's API key
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

# Test YouTube API
API_KEY = "AIzaSyDCVCT6ZQtIa1uYHyw3kUeiqB5ri2RhObo"

from app.services.social_media.youtube_service import YouTubeService

print("📺 Testing YouTube API Key")
print("=" * 70)

# Initialize with API key
yt = YouTubeService(api_key=API_KEY)

# Test 1: Search Kenya government videos
print("\n1️⃣ Searching for 'Kenya government policy'...")
videos = yt.search_kenya_videos(query="Kenya government policy", max_results=5)
print(f"✅ Found {len(videos)} videos\n")

for i, video in enumerate(videos[:3], 1):
    print(f"{i}. {video['title'][:50]}...")
    print(f"   Channel: {video['channel']}")
    print(f"   URL: {video['url']}")
    print()

# Test 2: Get Citizen TV videos
print("\n2️⃣ Getting Citizen TV Kenya videos...")
citizen_videos = yt.get_channel_videos('citizen_tv', max_results=3)
print(f"✅ Found {len(citizen_videos)} Citizen TV videos\n")

for i, video in enumerate(citizen_videos, 1):
    print(f"{i}. {video['title'][:55]}...")

# Test 3: Get comments from first video
if videos:
    print(f"\n3️⃣ Fetching comments from first video...")
    comments = yt.get_video_comments(videos[0]['video_id'], max_results=5)
    print(f"✅ Found {len(comments)} comments\n")
    
    for i, comment in enumerate(comments[:3], 1):
        print(f"{i}. @{comment['author']}: {comment['content'][:50]}...")
        print(f"   👍 {comment['likes']} likes")

print("\n" + "=" * 70)
print("✅ YouTube API working!")
