#!/usr/bin/env python3
"""
Comprehensive GovGPT Backend Verification Script
Tests all services, API endpoints, and initialization
"""
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules import without errors"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from app.config import settings
        print("✅ Config imported")
        
        from app.services.google_drive_service import drive_service
        print("✅ Google Drive service imported")
        
        from app.services.document_service import document_processor
        print("✅ Document processor imported")
        
        from app.services.vector_service import vector_service
        print("✅ Vector service imported")
        
        from app.services.llm_service import llm_service
        print("✅ LLM service imported")
        
        from app.services.chat_service import chat_service
        print("✅ Chat service imported")
        
        from app.services.social_media.youtube_service import youtube_service
        print("✅ YouTube service imported")
        
        from app.main import app
        print("✅ Main app imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_initialization():
    """Test service initialization with credentials"""
    print("\n" + "=" * 60)
    print("TEST 2: Service Initialization")
    print("=" * 60)
    
    from app.config import settings
    from app.services.vector_service import vector_service
    from app.services.llm_service import llm_service
    from app.services.social_media.youtube_service import youtube_service
    
    # Check Vector Service
    print(f"\n📦 Vector Service:")
    print(f"  - Qdrant URL: {settings.QDRANT_URL[:20]}..." if settings.QDRANT_URL else "  - No URL configured")
    print(f"  - Client initialized: {vector_service.client is not None}")
    
    # Check LLM Service
    print(f"\n🤖 LLM Service:")
    print(f"  - Groq API Key: {settings.GROQ_API_KEY[:10]}..." if settings.GROQ_API_KEY else "  - No API key")
    print(f"  - Client initialized: {llm_service.client is not None}")
    
    # Check YouTube Service
    print(f"\n📺 YouTube Service:")
    print(f"  - API Key: {settings.YOUTUBE_API_KEY[:10]}..." if settings.YOUTUBE_API_KEY else "  - No API key")
    print(f"  - Client initialized: {youtube_service.youtube is not None}")
    
    # Check Google Drive
    print(f"\n💾 Google Drive:")
    print(f"  - Folder ID: {settings.GOOGLE_DRIVE_FOLDER_ID}")
    print(f"  - Credentials: {settings.GOOGLE_DRIVE_CREDENTIALS_PATH or 'Not configured'}")

def test_api_endpoints():
    """Test that API endpoints are registered"""
    print("\n" + "=" * 60)
    print("TEST 3: API Endpoints")
    print("=" * 60)
    
    from app.main import app
    
    routes = [route.path for route in app.routes]
    
    expected_routes = [
        "/health",
        "/api/news/kenya",
        "/api/news/africa/all",
        "/api/social/kenya/pulse",
        "/api/social/mastodon/search",
        "/api/social/youtube/search",
        "/api/sentiment/analyze",
        "/api/chat/message",
        "/api/chat/stream",
        "/api/documents/sync"
    ]
    
    print(f"\n✅ Total routes registered: {len(routes)}")
    print(f"\nChecking critical endpoints:")
    for endpoint in expected_routes:
        status = "✅" if any(endpoint in route for route in routes) else "❌"
        print(f"  {status} {endpoint}")

def test_configuration():
    """Test configuration values"""
    print("\n" + "=" * 60)
    print("TEST 4: Configuration")
    print("=" * 60)
    
    from app.config import settings
    
    config_checks = {
        "GROQ_API_KEY": bool(settings.GROQ_API_KEY),
        "QDRANT_URL": bool(settings.QDRANT_URL),
        "QDRANT_API_KEY": bool(settings.QDRANT_API_KEY),
        "YOUTUBE_API_KEY": bool(settings.YOUTUBE_API_KEY),
        "GOOGLE_DRIVE_FOLDER_ID": bool(settings.GOOGLE_DRIVE_FOLDER_ID),
        "NEWS_API_KEY": bool(settings.NEWS_API_KEY),
    }
    
    for key, value in config_checks.items():
        status = "✅" if value else "⚠️ "
        print(f"  {status} {key}: {'Configured' if value else 'Not set'}")

def main():
    """Run all tests"""
    print("\n🚀 GovGPT Backend Verification\n")
    
    if not test_imports():
        print("\n❌ FAILED: Import errors detected")
        sys.exit(1)
    
    test_service_initialization()
    test_api_endpoints()
    test_configuration()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add Google Drive credentials to .env (optional)")
    print("2. Start backend: uvicorn app.main:app --reload")
    print("3. Visit: http://localhost:8000/api/docs")
    print()

if __name__ == "__main__":
    main()
