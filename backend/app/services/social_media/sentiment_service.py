"""
Sentiment Analysis Service using TextBlob
Fast, lightweight sentiment analysis for social media
"""
from typing import Dict, List
from textblob import TextBlob


class SentimentAnalyzer:
    """Lightweight sentiment analysis using TextBlob"""
    
    def __init__(self):
        print("✅ Sentiment analyzer ready (TextBlob)")
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label and score
        """
        if not text or len(text.strip()) < 3:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 'low',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
        
        try:
            # Run TextBlob analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Map polarity to sentiment label
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence based on polarity strength and subjectivity
            abs_polarity = abs(polarity)
            if abs_polarity > 0.5:
                confidence = 'high'
            elif abs_polarity > 0.2:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'sentiment': sentiment,
                'score': round(abs_polarity, 3),
                'confidence': confidence,
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3)
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 'error',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
