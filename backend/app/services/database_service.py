from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.models.database import NewsArticle, StockPrice, StockInfo, SentimentSummary
from app.core.database import SessionLocal
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DatabaseService:
    def __init__(self):
        pass
    
    def store_news_articles(self, symbol: str, articles_data: Dict) -> int:
        """Store news articles in database, return count of new articles"""
        db = SessionLocal()
        new_articles_count = 0
        
        try:
            for article in articles_data.get('articles', []):
                # Check if article already exists (by URL)
                existing = db.query(NewsArticle).filter(
                    NewsArticle.url == article['url']
                ).first()
                
                if not existing:
                    # Parse published date
                    published_at = None
                    if article.get('publishedAt'):
                        try:
                            published_at = datetime.fromisoformat(
                                article['publishedAt'].replace('Z', '+00:00')
                            )
                        except:
                            published_at = datetime.now()
                    
                    new_article = NewsArticle(
                        symbol=symbol.upper(),
                        title=article.get('title', '')[:500],  # Truncate if too long
                        content=article.get('description') or article.get('content', ''),
                        url=article['url'],
                        published_at=published_at,
                        source=article.get('source', {}).get('name', ''),
                        author=article.get('author', '')
                    )
                    db.add(new_article)
                    new_articles_count += 1
            
            db.commit()
            print(f"✓ Stored {new_articles_count} new articles for {symbol}")
            return new_articles_count
            
        except Exception as e:
            db.rollback()
            print(f"Error storing articles for {symbol}: {e}")
            return 0
        finally:
            db.close()
    
    def get_unanalyzed_articles(self, limit: int = 100) -> List[NewsArticle]:
        """Get articles that don't have sentiment scores yet"""
        db = SessionLocal()
        try:
            articles = db.query(NewsArticle).filter(
                NewsArticle.sentiment_score.is_(None)
            ).limit(limit).all()
            return articles
        finally:
            db.close()
    
    def update_article_sentiment(self, article_id: int, sentiment_score: float, sentiment_label: str):
        """Update sentiment score for an article"""
        db = SessionLocal()
        try:
            article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if article:
                article.sentiment_score = sentiment_score
                article.sentiment_label = sentiment_label
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error updating sentiment for article {article_id}: {e}")
        finally:
            db.close()
    
    def get_stock_sentiment_data(self, symbol: str, days: int = 7) -> Dict:
        """Get aggregated sentiment data for a stock"""
        db = SessionLocal()
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get all articles with sentiment scores
            articles = db.query(NewsArticle).filter(
                and_(
                    NewsArticle.symbol == symbol.upper(),
                    NewsArticle.published_at >= start_date,
                    NewsArticle.sentiment_score.isnot(None)
                )
            ).all()
            
            if not articles:
                return None
            
            # Calculate overall sentiment
            sentiment_scores = [article.sentiment_score for article in articles]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            # Get daily breakdown
            daily_sentiment = db.query(
                func.date(NewsArticle.published_at).label('date'),
                func.avg(NewsArticle.sentiment_score).label('avg_sentiment'),
                func.count(NewsArticle.id).label('article_count')
            ).filter(
                and_(
                    NewsArticle.symbol == symbol.upper(),
                    NewsArticle.published_at >= start_date,
                    NewsArticle.sentiment_score.isnot(None)
                )
            ).group_by(func.date(NewsArticle.published_at)).order_by('date').all()
            
            return {
                "symbol": symbol.upper(),
                "avg_sentiment": round(avg_sentiment, 3),
                "total_articles": len(articles),
                "daily_trends": [
                    {
                        "date": str(day.date),
                        "sentiment": round(day.avg_sentiment, 3),
                        "article_count": day.article_count
                    }
                    for day in daily_sentiment
                ]
            }
            
        finally:
            db.close()
    
    def get_trending_stocks(self, hours: int = 24) -> List[Dict]:
        """Get stocks with most sentiment activity in recent hours"""
        db = SessionLocal()
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            trending = db.query(
                NewsArticle.symbol,
                func.count(NewsArticle.id).label('article_count'),
                func.avg(NewsArticle.sentiment_score).label('avg_sentiment')
            ).filter(
                and_(
                    NewsArticle.published_at >= cutoff_time,
                    NewsArticle.sentiment_score.isnot(None)
                )
            ).group_by(NewsArticle.symbol).order_by(
                desc('article_count')
            ).limit(10).all()
            
            return [
                {
                    "symbol": stock.symbol,
                    "article_count": stock.article_count,
                    "avg_sentiment": round(stock.avg_sentiment, 3) if stock.avg_sentiment else 0
                }
                for stock in trending
            ]
            
        finally:
            db.close()

# Test function
if __name__ == "__main__":
    db_service = DatabaseService()
    print("Database service ready!")