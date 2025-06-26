from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.models.database import NewsArticle
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class SentimentService:
    def __init__(self, model_type: str = "vader"):
        """
        Initialize sentiment service
        
        Args:
            model_type: "finbert", "vader", or "textblob"
        """
        self.analyzer = SentimentAnalyzer(model_type=model_type)
        logger.info(f"✅ Sentiment service initialized with {model_type}")
    
    def process_unanalyzed_articles(self, batch_size: int = 50):
        """Process articles that don't have sentiment scores yet"""
        db = SessionLocal()
        
        try:
            # Get unanalyzed articles
            articles = db.query(NewsArticle).filter(
                NewsArticle.sentiment_score.is_(None)
            ).limit(batch_size).all()
            
            if not articles:
                logger.info("No unanalyzed articles found")
                return 0
            
            logger.info(f"Processing {len(articles)} articles for sentiment analysis...")
            
            processed_count = 0
            for article in articles:
                try:
                    # Combine title and content for analysis
                    text = f"{article.title}"
                    if article.content:
                        text += f" {article.content}"
                    
                    # Analyze sentiment
                    result = self.analyzer.analyze_text(text)
                    
                    # Update article
                    article.sentiment_score = result['score']
                    article.sentiment_label = result['label']
                    
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        logger.info(f"Processed {processed_count}/{len(articles)} articles")
                    
                except Exception as e:
                    logger.error(f"Error processing article {article.id}: {e}")
                    continue
            
            # Commit all changes
            db.commit()
            logger.info(f"✅ Successfully processed {processed_count} articles")
            return processed_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in batch processing: {e}")
            return 0
        finally:
            db.close()
    
    def analyze_single_text(self, text: str):
        """Analyze sentiment of a single text"""
        return self.analyzer.analyze_text(text)

# Test function
if __name__ == "__main__":
    sentiment_service = SentimentService(model_type="vader")
    
    # Test single text analysis
    test_text = "Apple stock price soars after excellent quarterly earnings report"
    result = sentiment_service.analyze_single_text(test_text)
    print(f"Test result: {result}")
    
    # Process unanalyzed articles
    processed = sentiment_service.process_unanalyzed_articles(batch_size=10)
    print(f"Processed {processed} articles")