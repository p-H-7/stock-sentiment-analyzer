from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import StockInfo
from app.services.stock_service import StockService
from app.services.news_service import NewsService
from app.services.database_service import DatabaseService
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter()

# Response models
class StockInfoResponse(BaseModel):
    symbol: str
    name: str
    current_price: float = None
    sector: str = None
    industry: str = None
    market_cap: float = None
    description: str = None

class StockPriceResponse(BaseModel):
    symbol: str
    current_price: float
    change: float = None
    change_percent: float = None

@router.get("/info/{symbol}", response_model=StockInfoResponse)
def get_stock_info(symbol: str):
    """Get comprehensive stock information"""
    
    stock_service = StockService()
    stock_info = stock_service.get_stock_info(symbol)
    
    if not stock_info:
        raise HTTPException(status_code=404, detail=f"Stock information not found for symbol {symbol}")
    
    return StockInfoResponse(**stock_info)

@router.get("/price/{symbol}", response_model=StockPriceResponse)
def get_stock_price(symbol: str):
    """Get current stock price and change"""
    
    stock_service = StockService()
    
    # Get current price
    current_price = stock_service.get_current_price(symbol)
    if current_price is None:
        raise HTTPException(status_code=404, detail=f"Price data not found for symbol {symbol}")
    
    # Get price change
    price_change = stock_service.get_price_change(symbol, days=1)
    
    return StockPriceResponse(
        symbol=symbol.upper(),
        current_price=current_price,
        change=price_change.get("change") if price_change else None,
        change_percent=price_change.get("change_percent") if price_change else None
    )

@router.get("/list", response_model=List[Dict])
def get_tracked_stocks(db: Session = Depends(get_db)):
    """Get list of all tracked stocks"""
    
    stocks = db.query(StockInfo).filter(StockInfo.is_active == True).all()
    
    return [
        {
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "industry": stock.industry
        }
        for stock in stocks
    ]

@router.post("/refresh/{symbol}")
def refresh_stock_news(symbol: str):
    """Manually refresh news for a specific stock"""
    
    try:
        # Fetch latest news
        news_service = NewsService()
        news_data = news_service.get_stock_news(symbol, days_back=3)
        
        # Store in database
        db_service = DatabaseService()
        new_articles = db_service.store_news_articles(symbol, news_data)
        
        return {
            "symbol": symbol.upper(),
            "new_articles_found": new_articles,
            "total_articles_fetched": len(news_data.get("articles", [])),
            "message": f"Successfully refreshed news for {symbol}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing news: {str(e)}")

@router.get("/validate/{symbol}")
def validate_stock_symbol(symbol: str):
    """Validate if a stock symbol exists"""
    
    stock_service = StockService()
    is_valid = stock_service.validate_symbol(symbol)
    
    return {
        "symbol": symbol.upper(),
        "is_valid": is_valid,
        "message": "Valid stock symbol" if is_valid else "Invalid stock symbol"
    }