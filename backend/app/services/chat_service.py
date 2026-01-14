"""
Chat Service
Orchestrates RAG, news, sentiment, and LLM for chat responses
"""
from typing import Dict, List, Iterator
from app.services.vector_service import vector_service
from app.services.llm_service import llm_service, SYSTEM_PROMPT
from app.services.news.gdelt_service import gdelt_service
from app.services.social_media.youtube_service import youtube_service
from app.services.social_media.sentiment_service import sentiment_service
from app.services.social_media.social_aggregator import social_aggregator
from app.utils.query_classifier import classify_query, get_query_confidence
import json


class ChatService:
    """Main chat orchestration service"""
    
    def __init__(self):
        pass
    
    def _extract_keywords(self, question: str) -> list:
        """Extract key topics from question for targeted search"""
        # Remove common words
        stopwords = {'what', 'is', 'the', 'a', 'an', 'on', 'in', 'of', 'for', 'to', 'about', 'how', 'why', 'when', 'where', 'which'}
        words = question.lower().split()
        keywords = [w.strip('?,!.') for w in words if w.lower() not in stopwords and len(w) > 3]
        
        # Always include "Kenya" to keep context
        if 'kenya' not in keywords:
            keywords.insert(0, 'kenya')
        
        return keywords[:5]  # Max 5 keywords
    
    def get_context(self, question: str) -> Dict:
        """
        Gather all relevant context for the question
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with document, news, and sentiment context
        """
        # Extract keywords for dynamic search
        keywords = self._extract_keywords(question)
        search_query = ' '.join(keywords)
        
        print(f"🔍 Search keywords: {keywords}")
        print(f"🔍 Dynamic query: {search_query}")
        
        context = {
            'document_chunks': [],
            'news': [],
            'sentiment': None,
            'youtube': []
        }
        
        # 1. Get relevant document chunks (RAG)
        try:
            if vector_service.client:
                chunks = vector_service.search_similar(question, limit=5)
                context['document_chunks'] = chunks
                print(f"📄 Found {len(chunks)} relevant document chunks")
        except Exception as e:
            print(f"❌ Error fetching document context: {e}")
        
        # 2. Get recent Kenya news with dynamic query
        try:
            articles = gdelt_service.fetch_kenya_news(
                lookback_days=7,
                max_results=10,
                keywords=keywords
            )
            context['news'] = articles
            print(f"📰 Fetched {len(articles)} Kenya news articles on topic")
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
        
        # 3. Get YouTube videos on the topic
        try:
            from app.services.social_media.youtube_service import youtube_service
            if youtube_service.youtube:
                videos = youtube_service.search_kenya_videos(
                    query=search_query,
                    max_results=5
                )
                context['youtube'] = videos
                print(f"📺 Found {len(videos)} YouTube videos on '{search_query}'")
        except Exception as e:
            print(f"❌ Error fetching YouTube: {e}")
        
        # 4. Get social sentiment on the topic
        try:
            sentiment = social_aggregator.fetch_kenya_social(
                keywords=keywords
            )
            context['sentiment'] = sentiment
            print(f"💬 Fetched sentiment: {len(sentiment.get('posts', []))} posts")
        except Exception as e:
            print(f"❌ Error fetching sentiment: {e}")
        
        print(f"✅ Context ready: {len(context['document_chunks'])} docs, {len(context['news'])} news, {len(context.get('youtube', []))} videos")
        return context

    
    def process_message(
        self,
        message: str,
        include_news: bool = True,
        include_sentiment: bool = True
    ) -> Dict:
        """
        Process user message and generate response
        
        Args:
            message: User's message/question
            include_news: Include news context
            include_sentiment: Include sentiment context
            
        Returns:
            Response with answer and sources
        """
        # Gather context
        context = self.get_context(message)
        
        # Build prompt
        prompt = llm_service.create_prompt(
            question=message,
            context_chunks=context['document_chunks'],
            news_context=context['news'] if include_news else None,
            youtube_context=context.get('youtube', []),
            sentiment_context=context['sentiment'] if include_sentiment else None
        )
        
        print(f"\n{'='*60}")
        print(f"🔍 PROMPT BEING SENT TO LLM:")
        print(f"{'='*60}")
        print(prompt[:1000])  # First 1000 chars
        print(f"{'='*60}\n")
        
        # Generate response
        answer = llm_service.generate_response(prompt)
        
        # Format citations
        citations = self._format_citations(context)
        
        return {
            'answer': answer,
            'citations': citations,
            'context_used': {
                'documents': len(context['document_chunks']),
                'news_articles': len(context['news']),
                'sentiment_included': include_sentiment
            }
        }
    
    def stream_message(
        self,
        message: str,
        include_news: bool = True,
        include_sentiment: bool = True
    ) -> Iterator[Dict]:
        """
        Stream chat response for real-time UI updates
        AUTO-DETECTS if query needs decision report or exploratory response
        
        Args:
            message: User's message
            include_news: Include news context
            include_sentiment: Include sentiment context
            
        Yields:
            Response chunks and metadata
        """
        # Auto-detect query type
        query_classification = get_query_confidence(message)
        query_type = query_classification['type']
        
        print(f"\n🔍 Query Classification: {query_type.upper()} (confidence: {query_classification['confidence']:.0%})")
        print(f"   Reasoning: {query_classification['reasoning']}")
        
        # Send classification info to frontend
        yield {
            'type': 'classification',
            'data': query_classification
        }
        
        # Gather context (send as first chunk)
        context = self.get_context(message)
        
        yield {
            'type': 'context',
            'data': {
                'documents': len(context['document_chunks']),
                'news': len(context['news']),
                'sentiment': 'included' if include_sentiment else 'excluded'
            }
        }
        
        # Route based on query type
        if query_type == 'decision' and query_classification['confidence'] >= 0.70:
            # Generate structured decision report
            print(f"📊 Generating DECISION REPORT (structured JSON)")
            
            try:
                report = llm_service.generate_decision_report(
                    question=message,
                    context_chunks=context['document_chunks'],
                    news_context=context['news'] if include_news else None,
                    sentiment_context=context['sentiment'] if include_sentiment else None
                )
                
                # Yield the full report as JSON
                yield {
                    'type': 'report',
                    'data': report
                }
                
            except Exception as e:
                print(f"❌ Error generating decision report: {e}")
                # Fallback to streaming markdown
                prompt = llm_service.create_prompt(
                    question=message,
                    context_chunks=context['document_chunks'],
                    news_context=context['news'] if include_news else None,
                    sentiment_context=context['sentiment'] if include_sentiment else None
                )
                
                for chunk in llm_service.stream_response(prompt):
                    yield {
                        'type': 'content',
                        'data': chunk
                    }
        else:
            # Stream exploratory markdown response
            print(f"📝 Generating EXPLORATORY RESPONSE (markdown streaming)")
            
            # Build prompt
            prompt = llm_service.create_prompt(
                question=message,
                context_chunks=context['document_chunks'],
                news_context=context['news'] if include_news else None,
                sentiment_context=context['sentiment'] if include_sentiment else None
            )
            
            # Stream response
            for chunk in llm_service.stream_response(prompt):
                yield {
                    'type': 'content',
                    'data': chunk
                }
        
        # Send citations at the end
        citations = self._format_citations(context)
        yield {
            'type': 'citations',
            'data': citations
        }
    
    def _format_citations(self, context: Dict) -> List[Dict]:
        """Format sources as citations"""
        citations = []
        
        # Document citations
        for chunk in context['document_chunks']:
            citations.append({
                'type': 'document',
                'title': chunk['filename'],
                'source': f"Document: {chunk['filename']}",
                'relevance': round(chunk['score'], 2),
                'text_preview': chunk['text'][:150] + '...'
            })
        
        # News citations
        for article in context['news'][:5]:
            citations.append({
                'type': 'news',
                'title': article.get('title', ''),
                'source': article.get('domain', 'Unknown'),
                'url': article.get('url', ''),
                'date': article.get('published_at', '')
            })
        
        return citations


    def generate_decision_report(
        self,
        question: str,
        include_news: bool = True,
        include_sentiment: bool = True
    ) -> Dict:
        """
        Generate structured decision report for government decision-makers
        
        Args:
            question: Policy question or decision to analyze
            include_news: Include news context
            include_sentiment: Include sentiment context
            
        Returns:
            Structured decision report with all sections
        """
        from datetime import datetime
        
        # Gather full context
        context = self.get_context(question)
        
        print(f"\n{'='*60}")
        print(f"📊 GENERATING DECISION REPORT")
        print(f"{'='*60}")
        print(f"Question: {question}")
        print(f"Context: {len(context['document_chunks'])} docs, {len(context['news'])} news, {len(context.get('youtube', []))} videos")
        print(f"{'='*60}\n")
        
        # Generate structured report
        report = llm_service.generate_decision_report(
            question=question,
            context_chunks=context['document_chunks'],
            news_context=context['news'] if include_news else None,
            youtube_context=context.get('youtube', []),
            sentiment_context=context['sentiment'] if include_sentiment else None
        )
        
        # Add metadata
        report['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'question': question,
            'sources_count': {
                'documents': len(context['document_chunks']),
                'news_articles': len(context['news']),
                'youtube_videos': len(context.get('youtube', [])),
                'social_posts': len(context.get('sentiment', {}).get('posts', []))
            },
            'context_included': {
                'news': include_news,
                'sentiment': include_sentiment
            }
        }
        
        # Add document sources to data_sources if not already there
        if 'data_sources' not in report:
            report['data_sources'] = []
        
        for chunk in context['document_chunks'][:5]:
            source_entry = f"Document: {chunk.get('filename', 'Unknown')} (relevance: {chunk.get('score', 0):.2f})"
            if source_entry not in report['data_sources']:
                report['data_sources'].append(source_entry)
        
        return report


# Singleton instance
chat_service = ChatService()
