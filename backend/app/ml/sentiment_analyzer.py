from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import logging
from typing import Dict, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, model_type: str = "finbert"):
        """
        Initialize sentiment analyzer
        
        Args:
            model_type: "finbert", "vader", or "textblob"
        """
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.classifier = None
        
        try:
            if model_type == "finbert":
                self._load_finbert()
            elif model_type == "vader":
                self.analyzer = SentimentIntensityAnalyzer()
            elif model_type == "textblob":
                # TextBlob doesn't need initialization
                pass
            else:
                raise ValueError(f"Unknown model type: {model_type}")
                
            logger.info(f"✅ Sentiment analyzer loaded: {model_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load {model_type}, falling back to VADER: {e}")
            self.model_type = "vader"
            self.analyzer = SentimentIntensityAnalyzer()
    
    def _load_finbert(self):
        """Load FinBERT model for financial sentiment analysis"""
        model_name = "ProsusAI/finbert"
        
        logger.info("Loading FinBERT model (this may take a moment)...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Create pipeline
        self.classifier = pipeline(
            "sentiment-analysis",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            return_all_scores=True
        )
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Returns:
            Dict with 'score' (-1 to 1) and 'label' (positive/negative/neutral)
        """
        if not text or not text.strip():
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}
        
        # Preprocess text
        clean_text = self.preprocess_text(text)
        
        try:
            if self.model_type == "finbert":
                return self._analyze_with_finbert(clean_text)
            elif self.model_type == "vader":
                return self._analyze_with_vader(clean_text)
            elif self.model_type == "textblob":
                return self._analyze_with_textblob(clean_text)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            # Fallback to neutral
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove extra whitespace and special characters
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        text = ' '.join(text.split())
        
        # Truncate for model limits (FinBERT has 512 token limit)
        return text[:2000]  # Conservative limit
    
    def _analyze_with_finbert(self, text: str) -> Dict[str, float]:
        """Analyze with FinBERT model"""
        results = self.classifier(text)[0]  # Get all scores
        
        # FinBERT returns: positive, negative, neutral
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for result in results:
            label = result['label'].lower()
            score = result['score']
            
            if label == 'positive':
                positive_score = score
            elif label == 'negative':
                negative_score = score
            elif label == 'neutral':
                neutral_score = score
        
        # Convert to -1 to 1 scale
        if positive_score > negative_score and positive_score > neutral_score:
            sentiment_score = positive_score
            sentiment_label = "positive"
            confidence = positive_score
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment_score = -negative_score
            sentiment_label = "negative"
            confidence = negative_score
        else:
            sentiment_score = 0.0
            sentiment_label = "neutral"
            confidence = neutral_score
        
        return {
            "score": round(sentiment_score, 3),
            "label": sentiment_label,
            "confidence": round(confidence, 3)
        }
    
    def _analyze_with_vader(self, text: str) -> Dict[str, float]:
        """Analyze with VADER"""
        scores = self.analyzer.polarity_scores(text)
        compound_score = scores['compound']
        
        # Determine label
        if compound_score >= 0.05:
            label = "positive"
        elif compound_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "score": round(compound_score, 3),
            "label": label,
            "confidence": round(abs(compound_score), 3)
        }
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, float]:
        """Analyze with TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        # Determine label
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        return {
            "score": round(polarity, 3),
            "label": label,
            "confidence": round(abs(polarity), 3)
        }

# Test function
if __name__ == "__main__":
    # Test all models
    test_texts = [
        "Apple stock surges on strong quarterly earnings and positive outlook for growth",
        "Tesla faces major challenges with declining sales and regulatory hurdles",
        "Microsoft releases quarterly financial report with mixed results",
        "Amazon reports record profits and expansion plans"
    ]
    
    for model_type in ["vader", "textblob", "finbert"]:
        print(f"\n=== Testing {model_type.upper()} ===")
        try:
            analyzer = SentimentAnalyzer(model_type=model_type)
            
            for text in test_texts:
                result = analyzer.analyze_text(text)
                print(f"Text: {text[:50]}...")
                print(f"Score: {result['score']}, Label: {result['label']}, Confidence: {result['confidence']}")
                print()
                
        except Exception as e:
            print(f"Failed to test {model_type}: {e}")