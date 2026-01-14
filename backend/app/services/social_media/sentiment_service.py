"""
Sentiment Analysis Service using TextBlob
Fast, lightweight sentiment analysis for social media
"""
from typing import Dict, List


class SentimentAnalyzer:
    """Lightweight sentiment analysis using TextBlob - lazy loaded"""
    
    def __init__(self):
        self._blob = None
    
    @property
    def TextBlob(self):
        if self._blob is None:
            from textblob import TextBlob
            self._blob = TextBlob
        return self._blob
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if not text or len(text.strip()) < 3:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 'low',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
        
        try:
            blob = self.TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
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
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 'error',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        return [self.analyze(text) for text in texts]


sentiment_analyzer = SentimentAnalyzer()
