from app.services.news_service import NewsService
from app.services.database_service import DatabaseService

def test_database_integration():
    print("Testing database integration...")
    
    # Initialize services
    news_service = NewsService()
    db_service = DatabaseService()
    
    # Fetch some news
    print("1. Fetching news for AAPL...")
    news_data = news_service.get_stock_news("AAPL", days_back=2)
    print(f"   Found {len(news_data.get('articles', []))} articles")
    
    # Store in database
    print("2. Storing articles in database...")
    new_count = db_service.store_news_articles("AAPL", news_data)
    print(f"   Stored {new_count} new articles")
    
    # Check unanalyzed articles
    print("3. Checking unanalyzed articles...")
    unanalyzed = db_service.get_unanalyzed_articles(limit=5)
    print(f"   Found {len(unanalyzed)} unanalyzed articles")
    
    if unanalyzed:
        sample = unanalyzed[0]
        print(f"   Sample: {sample.title[:60]}...")
    
    print("✓ Database integration test complete!")

if __name__ == "__main__":
    test_database_integration()