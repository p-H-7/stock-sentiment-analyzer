from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.core.database import get_db
from app.models.database import NewsArticle
from app.services.sentiment_service import SentimentService
from app.services.database_service import DatabaseService
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel

router = APIRouter()

# Response models
class SentimentResponse(BaseModel):
    symbol: str
    avg_sentiment: float
    total_articles: int
    daily_trends: List[Dict]
    sentiment_distribution: Dict[str, int]

class TrendingStock(BaseModel):
    symbol: str
    article_count: int
    avg_sentiment: float
    sentiment_label: str

class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: datetime
    sentiment_score: float
    sentiment_label: str
    source: str

@router.get("/stock/{symbol}", response_model=SentimentResponse)
def get_stock_sentiment(
    symbol: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for a specific stock symbol"""
    
    # Get sentiment data using database service
    db_service = DatabaseService()
    sentiment_data = db_service.get_stock_sentiment_data(symbol, days)
    
    if not sentiment_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No sentiment data found for symbol {symbol} in the last {days} days"
        )
    
    # Get sentiment distribution
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    distribution = db.query(
        NewsArticle.sentiment_label,
        func.count(NewsArticle.id).label('count')
    ).filter(
        and_(
            NewsArticle.symbol == symbol.upper(),
            NewsArticle.published_at >= start_date,
            NewsArticle.sentiment_score.isnot(None)
        )
    ).group_by(NewsArticle.sentiment_label).all()
    
    sentiment_distribution = {item.sentiment_label or 'neutral': item.count for item in distribution}
    
    return SentimentResponse(
        symbol=sentiment_data["symbol"],
        avg_sentiment=sentiment_data["avg_sentiment"],
        total_articles=sentiment_data["total_articles"],
        daily_trends=sentiment_data["daily_trends"],
        sentiment_distribution=sentiment_distribution
    )

@router.get("/trending", response_model=List[TrendingStock])
def get_trending_stocks(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of stocks to return"),
    db: Session = Depends(get_db)
):
    """Get stocks with most sentiment activity in recent hours"""
    
    db_service = DatabaseService()
    trending_data = db_service.get_trending_stocks(hours)
    
    # Convert to response model and add sentiment labels
    trending_stocks = []
    for stock in trending_data[:limit]:
        sentiment_score = stock["avg_sentiment"]
        if sentiment_score > 0.1:
            label = "positive"
        elif sentiment_score < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        trending_stocks.append(TrendingStock(
            symbol=stock["symbol"],
            article_count=stock["article_count"],
            avg_sentiment=stock["avg_sentiment"],
            sentiment_label=label
        ))
    
    return trending_stocks

@router.get("/stock/{symbol}/articles", response_model=List[ArticleResponse])
def get_stock_articles(
    symbol: str,
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    sentiment_filter: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    db: Session = Depends(get_db)
):
    """Get recent articles for a stock with sentiment scores"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(NewsArticle).filter(
        and_(
            NewsArticle.symbol == symbol.upper(),
            NewsArticle.published_at >= start_date,
            NewsArticle.sentiment_score.isnot(None)
        )
    )
    
    # Apply sentiment filter if provided
    if sentiment_filter:
        query = query.filter(NewsArticle.sentiment_label == sentiment_filter)
    
    articles = query.order_by(desc(NewsArticle.published_at)).limit(limit).all()
    
    if not articles:
        raise HTTPException(
            status_code=404,
            detail=f"No articles found for {symbol}"
        )
    
    return [
        ArticleResponse(
            id=article.id,
            title=article.title,
            url=article.url,
            published_at=article.published_at,
            sentiment_score=article.sentiment_score,
            sentiment_label=article.sentiment_label or 'neutral',
            source=article.source or 'Unknown'
        )
        for article in articles
    ]

@router.post("/analyze")
def analyze_text_sentiment(text: str):
    """Analyze sentiment of custom text"""
    
    if not text or len(text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Text must be at least 3 characters long")
    
    sentiment_service = SentimentService()
    result = sentiment_service.analyze_single_text(text)
    
    return {
        "text": text[:100] + "..." if len(text) > 100 else text,
        "sentiment_score": result["score"],
        "sentiment_label": result["label"],
        "confidence": result["confidence"]
    }

@router.get("/summary")
def get_sentiment_summary(db: Session = Depends(get_db)):
    """Get overall sentiment summary across all stocks"""
    
    # Get summary stats
    total_articles = db.query(func.count(NewsArticle.id)).filter(
        NewsArticle.sentiment_score.isnot(None)
    ).scalar()
    
    avg_sentiment = db.query(func.avg(NewsArticle.sentiment_score)).filter(
        NewsArticle.sentiment_score.isnot(None)
    ).scalar()
    
    # Get sentiment distribution
    distribution = db.query(
        NewsArticle.sentiment_label,
        func.count(NewsArticle.id).label('count')
    ).filter(
        NewsArticle.sentiment_score.isnot(None)
    ).group_by(NewsArticle.sentiment_label).all()
    
    sentiment_dist = {item.sentiment_label or 'neutral': item.count for item in distribution}
    
    # Get unique symbols count
    unique_symbols = db.query(func.count(func.distinct(NewsArticle.symbol))).filter(
        NewsArticle.sentiment_score.isnot(None)
    ).scalar()
    
    return {
        "total_articles_analyzed": total_articles or 0,
        "average_sentiment": round(avg_sentiment or 0, 3),
        "sentiment_distribution": sentiment_dist,
        "stocks_tracked": unique_symbols or 0,
        "last_updated": datetime.now().isoformat()
    }