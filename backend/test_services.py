# backend/test_services.py
from app.services.news_service import NewsService
from app.services.stock_service import StockService

def test_services():
    print("Testing Stock Service...")
    stock_service = StockService()
    
    # Test stock data
    price = stock_service.get_current_price("AAPL")
    print(f"✓ AAPL current price: ${price}")
    
    info = stock_service.get_stock_info("AAPL")
    print(f"✓ AAPL company: {info.get('name')}")
    
    print("\nTesting News Service...")
    news_service = NewsService()
    
    # Test news data
    news = news_service.get_stock_news("AAPL", days_back=2)
    print(f"✓ Found {len(news.get('articles', []))} news articles for AAPL")
    
    if news.get('articles'):
        sample_article = news['articles'][0]
        print(f"✓ Sample headline: {sample_article['title'][:80]}...")

if __name__ == "__main__":
    test_services()