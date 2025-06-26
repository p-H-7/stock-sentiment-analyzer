from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.database import Base, StockInfo

# Create all tables
def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")

# Initialize with some popular stocks
def init_popular_stocks():
    db = SessionLocal()
    
    popular_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services"},
    ]
    
    for stock_data in popular_stocks:
        # Check if stock already exists
        existing = db.query(StockInfo).filter(StockInfo.symbol == stock_data["symbol"]).first()
        if not existing:
            stock = StockInfo(**stock_data)
            db.add(stock)
    
    db.commit()
    db.close()
    print("✓ Popular stocks initialized!")

def init_database():
    """Initialize the entire database"""
    create_tables()
    init_popular_stocks()

if __name__ == "__main__":
    init_database()