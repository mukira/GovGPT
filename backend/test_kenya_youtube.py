"""
Test all Kenya news channels on YouTube
"""
import sys
sys.path.append('/Users/Mukira/gov-analysis-platform/backend')

from app.services.social_media.youtube_service import YouTubeService

API_KEY = "AIzaSyDCVCT6ZQtIa1uYHyw3kUeiqB5ri2RhObo"
yt = YouTubeService(api_key=API_KEY)

print("📺 All Kenya News Channels on YouTube")
print("=" * 70)
print(f"\nTotal channels configured: {len(yt.KENYA_CHANNELS)}\n")

# List all channels
print("📺 MAJOR TV STATIONS:")
print("   • Citizen TV, KTN News, NTV Kenya, KBC, K24, TV47, Switch TV")

print("\n📰 NEWSPAPERS & DIGITAL:")
print("   • Nation Africa, Standard Digital, The Star, Business Daily")

print("\n🎙️ RADIO STATIONS:")
print("   • Spice FM, Radio Citizen, Kiss 100, Classic 105")

print("\n🌍 REGIONAL & VERNACULAR:")
print("   • Inooro TV, Ramogi TV, Kass TV")

# Test search
print("\n" + "-" * 70)
print("Testing search: 'Kenya parliament budget'...")
videos = yt.search_kenya_videos("Kenya parliament budget", max_results=3)
print(f"✅ Found {len(videos)} videos\n")

for v in videos:
    print(f"   • {v['title'][:50]}... ({v['channel']})")

print("\n" + "=" * 70)
print(f"✅ {len(yt.KENYA_CHANNELS)} Kenya news channels ready!")
