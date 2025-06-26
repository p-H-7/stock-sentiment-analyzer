from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sentiment, stocks

# Create FastAPI app
app = FastAPI(
    title="Stock Sentiment Analyzer API",
    description="Real-time sentiment analysis for stock market news",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])

@app.get("/")
def read_root():
    return {
        "message": "Stock Sentiment Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "sentiment": "/api/sentiment",
            "stocks": "/api/stocks",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}