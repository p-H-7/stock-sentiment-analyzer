import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class StockService:
    def __init__(self):
        pass
    
    def get_stock_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Get historical stock data"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            return hist
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict:
        """Get comprehensive stock information"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'description': info.get('longBusinessSummary', '')[:500] + '...' if info.get('longBusinessSummary') else ''
            }
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return {}
    
    def get_price_change(self, symbol: str, days: int = 1) -> Optional[Dict]:
        """Get price change over specified days"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=f"{days + 5}d")  # Get extra days to ensure we have data
            
            if len(hist) < 2:
                return None
                
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-(days + 1)]
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            return {
                'current_price': current_price,
                'previous_price': previous_price,
                'change': change,
                'change_percent': change_percent
            }
        except Exception as e:
            print(f"Error calculating price change for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a stock symbol is valid"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            # Check if we got valid data
            return 'symbol' in info or 'shortName' in info
        except:
            return False

# Test function
if __name__ == "__main__":
    stock_service = StockService()
    
    # Test with a popular stock
    print("Testing stock service...")
    
    # Test current price
    price = stock_service.get_current_price("AAPL")
    print(f"AAPL current price: ${price}")
    
    # Test stock info
    info = stock_service.get_stock_info("AAPL")
    print(f"AAPL info: {info.get('name')} - {info.get('sector')}")
    
    # Test price change
    change = stock_service.get_price_change("AAPL", days=1)
    if change:
        print(f"AAPL 1-day change: {change['change_percent']:.2f}%")