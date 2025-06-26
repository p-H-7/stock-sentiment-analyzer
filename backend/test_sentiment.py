from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.services.sentiment_service import SentimentService

def test_sentiment_analysis():
    print("🧠 Testing Sentiment Analysis...")
    
    # Test texts with known sentiment
    test_cases = [
        {
            "text": "Apple stock surges 15% on record quarterly earnings and strong guidance",
            "expected": "positive"
        },
        {
            "text": "Tesla stock plummets as sales decline and CEO faces investigation",
            "expected": "negative"
        },
        {
            "text": "Microsoft releases quarterly report with standard financial metrics",
            "expected": "neutral"
        },
        {
            "text": "Amazon announces massive layoffs and store closures amid economic downturn",
            "expected": "negative"
        },
        {
            "text": "Google parent Alphabet beats expectations with strong cloud revenue growth",
            "expected": "positive"
        }
    ]
    
    # Test VADER (fastest)
    print("\n=== Testing VADER Sentiment Analysis ===")
    analyzer = SentimentAnalyzer(model_type="vader")
    
    for i, case in enumerate(test_cases, 1):
        result = analyzer.analyze_text(case["text"])
        print(f"{i}. Text: {case['text'][:60]}...")
        print(f"   Expected: {case['expected']}")
        print(f"   Got: {result['label']} (score: {result['score']}, confidence: {result['confidence']})")
        print(f"   {'✅ Correct' if result['label'] == case['expected'] else '❌ Incorrect'}")
        print()
    
    # Test sentiment service
    print("=== Testing Sentiment Service ===")
    sentiment_service = SentimentService(model_type="vader")
    
    sample_result = sentiment_service.analyze_single_text(test_cases[0]["text"])
    print(f"Service test: {sample_result}")
    
    print("✅ Sentiment analysis tests complete!")

if __name__ == "__main__":
    test_sentiment_analysis()