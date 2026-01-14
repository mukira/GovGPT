"""
Integration Test Suite for GovGPT
Tests imports, services, and API endpoints to catch issues early
Run with: pytest backend/tests/test_integration.py -v
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestImports:
    """Test that all critical imports work"""
    
    def test_service_imports(self):
        """Test all service imports"""
        from app.services.llm_service import llm_service, SYSTEM_PROMPT, DECISION_REPORT_SYSTEM_PROMPT
        from app.services.vector_service import vector_service
        from app.services.chat_service import chat_service
        from app.services.news.gdelt_service import gdelt_service
        from app.services.social_media.social_aggregator import social_aggregator
        assert llm_service is not None
        assert vector_service is not None
        assert chat_service is not None
        
    def test_api_imports(self):
        """Test API endpoint imports"""
        from app.api import chat, news, social, sentiment, documents
        assert chat is not None
        
    def test_utility_imports(self):
        """Test utility imports"""
        from app.utils.query_classifier import classify_query, get_query_confidence
        assert classify_query is not None
        assert get_query_confidence is not None
    
    def test_main_app_import(self):
        """Test main FastAPI app imports"""
        from app.main import app
        assert app is not None


class TestQueryClassifier:
    """Test query classification logic"""
    
    def test_decision_queries(self):
        """Test that decision queries are classified correctly"""
        from app.utils.query_classifier import classify_query, get_query_confidence
        
        decision_queries = [
            "Should Kenya expand universal healthcare?",
            "Should we allocate 10% to rural schools?",
            "Recommend investment in infrastructure",
            "Approve the budget reallocation",
            "Should I increase funding for education?"
        ]
        
        for query in decision_queries:
            result = classify_query(query)
            assert result == "decision", f"Query '{query}' should be classified as decision, got {result}"
            
            detailed = get_query_confidence(query)
            assert detailed['type'] == "decision"
            assert detailed['confidence'] >= 0.60, f"Decision query confidence too low: {detailed['confidence']}"
    
    def test_exploratory_queries(self):
        """Test that exploratory queries are classified correctly"""
        from app.utils.query_classifier import classify_query
        
        exploratory_queries = [
            "What is universal healthcare?",
            "Explain the history of education in Kenya",
            "Tell me about the budget process",
            "How does the healthcare system work?",
            "What are the counties in Kenya?"
        ]
        
        for query in exploratory_queries:
            result = classify_query(query)
            assert result == "exploratory", f"Query '{query}' should be exploratory, got {result}"


class TestLLMService:
    """Test LLM service functionality"""
    
    def test_llm_service_exists(self):
        """Test LLM service is initialized"""
        from app.services.llm_service import llm_service
        assert llm_service is not None
        assert llm_service.model == "llama-3.3-70b-versatile"
    
    def test_system_prompts_exist(self):
        """Test system prompts are defined"""
        from app.services.llm_service import SYSTEM_PROMPT, DECISION_REPORT_SYSTEM_PROMPT
        assert len(SYSTEM_PROMPT) > 100
        assert len(DECISION_REPORT_SYSTEM_PROMPT) > 100
        assert "decision" in DECISION_REPORT_SYSTEM_PROMPT.lower()
        assert "markdown" in SYSTEM_PROMPT.lower()
    
    def test_create_prompt_method(self):
        """Test prompt creation method"""
        from app.services.llm_service import llm_service
        
        prompt = llm_service.create_prompt(
            question="Test question?",
            context_chunks=[{"filename": "test.pdf", "text": "Test content"}],
            news_context=[{"title": "Test news"}]
        )
        
        assert "Test question?" in prompt
        assert "test.pdf" in prompt or "Test content" in prompt


class TestChatService:
    """Test chat service orchestration"""
    
    def test_chat_service_exists(self):
        """Test chat service is initialized"""
        from app.services.chat_service import chat_service
        assert chat_service is not None
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        from app.services.chat_service import chat_service
        
        keywords = chat_service._extract_keywords("What is the impact of healthcare policy?")
        assert len(keywords) > 0
        assert 'kenya' in [k.lower() for k in keywords]  # Always includes Kenya
    
    def test_stream_message_structure(self):
        """Test that stream_message yields proper structure"""
        from app.services.chat_service import chat_service
        
        # Test the generator structure (without actually calling LLM)
        stream = chat_service.stream_message("test question", include_news=False, include_sentiment=False)
        
        # Should yield at least classification and context
        results = list(stream)[:2]  # Get first 2 items
        
        assert len(results) >= 1
        assert 'type' in results[0]
        assert 'data' in results[0]


class TestAPIEndpoints:
    """Test API endpoint availability (without actually calling them)"""
    
    def test_chat_endpoints_exist(self):
        """Test chat API endpoints are defined"""
        from app.api.chat import router
        
        routes = [route.path for route in router.routes]
        assert '/stream' in routes
        assert '/generate-report' in routes
    
    def test_main_app_routes(self):
        """Test main app has all required routes"""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        assert '/api/chat/stream' in routes
        assert '/api/chat/generate-report' in routes
        assert '/health' in routes


class TestConfigAndSettings:
    """Test configuration"""
    
    def test_config_import(self):
        """Test config imports correctly"""
        from app.config import settings
        assert settings is not None
    
    def test_required_env_vars(self):
        """Test that critical environment variables are accessible"""
        from app.config import settings
        
        # These should be defined (may be None if not set, but should be accessible)
        assert hasattr(settings, 'GROQ_API_KEY')
        assert hasattr(settings, 'QDRANT_URL')


class TestDataModels:
    """Test Pydantic models"""
    
    def test_chat_request_model(self):
        """Test ChatRequest model"""
        from app.api.chat import ChatRequest
        
        request = ChatRequest(message="test", include_news=True, include_sentiment=True)
        assert request.message == "test"
        assert request.include_news == True
    
    def test_report_request_model(self):
        """Test ReportRequest model"""
        from app.api.chat import ReportRequest
        
        request = ReportRequest(question="test question")
        assert request.question == "test question"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
