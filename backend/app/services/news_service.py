import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
        
        if not self.api_key:
            print("Warning: No NEWS_API_KEY found. Please set it in .env file")
    
    def get_stock_news(self, symbol: str, days_back: int = 7) -> Dict:
        """Fetch news articles for a specific stock symbol"""
        if not self.api_key:
            return {"articles": []}
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Search queries for better results
        queries = [
            f'"{symbol}" stock',
            f'"{symbol}" earnings',
            f'"{symbol}" company'
        ]
        
        all_articles = []
        
        for query in queries:
            params = {
                'q': query,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'language': 'en',
                'apiKey': self.api_key,
                'pageSize': 20  # Limit per query
            }
            
            try:
                response = requests.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get('articles'):
                    all_articles.extend(data['articles'])
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching news for query '{query}': {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return {"articles": unique_articles[:50]}  # Limit total results
    
    def get_trending_news(self, category: str = "business") -> Dict:
        """Get trending business/financial news"""
        if not self.api_key:
            return {"articles": []}
            
        params = {
            'category': category,
            'country': 'us',
            'apiKey': self.api_key,
            'pageSize': 20
        }
        
        try:
            response = requests.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending news: {e}")
            return {"articles": []}

# Test function
if __name__ == "__main__":
    news_service = NewsService()
    
    # Test with a popular stock
    print("Testing news service...")
    news_data = news_service.get_stock_news("AAPL", days_back=3)
    print(f"Found {len(news_data.get('articles', []))} articles for AAPL")
    
    if news_data.get('articles'):
        print(f"Sample article: {news_data['articles'][0]['title']}")