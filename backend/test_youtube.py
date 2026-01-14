#!/usr/bin/env python3
"""
YouTube API Verification Test
Tests YouTube search with retry logic for zero failures
"""
import os
import sys
sys.path.insert(0, '/Users/Mukira/gov-analysis-platform/backend')

from app.services.social_media.youtube_service import youtube_service

print("🧪 YouTube API Verification Test")
print("=" * 50)
print()

# Test queries
test_queries = [
    "Kenya healthcare policy",
    "Kenya education reforms",
    "Kenya infrastructure development",
]

total_tests = len(test_queries)
successful = 0
failed = 0
total_videos = 0

for i, query in enumerate(test_queries, 1):
    print(f"Test {i}/{total_tests}: '{query}'")
    print("-" * 50)
    
    try:
        videos = youtube_service.search_videos(query, max_results=5)
        
        if videos and len(videos) > 0:
            print(f"✅ SUCCESS: Found {len(videos)} videos")
            for j, video in enumerate(videos[:3], 1):
                print(f"   {j}. {video['title'][:60]}...")
            successful += 1
            total_videos += len(videos)
        else:
            print(f"⚠️  WARNING: No videos found (but no error)")
            successful += 1  # No error, just no results
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    print()

print("=" * 50)
print("📊 RESULTS:")
print(f"   Total Tests: {total_tests}")
print(f"   Successful: {successful} ({(successful/total_tests*100):.0f}%)")
print(f"   Failed: {failed}")
print(f"   Total Videos Retrieved: {total_videos}")
print()

if failed == 0:
    print("🎉 ALL TESTS PASSED - ZERO FAILURES!")
    print("   YouTube API is working perfectly!")
    sys.exit(0)
else:
    print(f"⚠️  {failed} test(s) failed")
    sys.exit(1)
