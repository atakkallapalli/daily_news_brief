#!/usr/bin/env python3
"""
Test script for LLM integration in the news aggregator
Demonstrates enhanced analysis capabilities
"""

import os
import sys
from news_aggregator import NewsAggregator, LLMService

def test_llm_service():
    """Test LLM service functionality"""
    print("🧪 Testing LLM Service Integration")
    print("=" * 50)
    
    # Initialize LLM service
    llm = LLMService(provider="auto")
    
    # Test article content
    test_article = {
        'title': 'Federal Reserve Raises Interest Rates by 0.25%',
        'description': 'The Federal Reserve announced a quarter-point increase in interest rates to combat inflation, marking the third rate hike this year.',
        'url': 'https://example.com/fed-rates',
        'published': '2024-11-08'
    }
    
    test_content = """
    The Federal Reserve announced Wednesday that it is raising its benchmark interest rate by 0.25 percentage points, 
    bringing the federal funds rate to 5.5%. Fed Chair Jerome Powell said in a statement that "the committee remains 
    committed to bringing inflation back to our 2% objective." The decision was unanimous among voting members. 
    Powell noted that while inflation has shown signs of cooling, "we still have more work to do." 
    The rate increase affects borrowing costs for consumers and businesses across the economy.
    """
    
    print("📰 Test Article:")
    print(f"Title: {test_article['title']}")
    print(f"Description: {test_article['description']}")
    print()
    
    # Test summarization
    print("🤖 LLM-Generated Summary:")
    summary = llm.generate_summary(test_content, max_length=100)
    print(f"Summary: {summary}")
    print()
    
    # Test key insights extraction
    print("🔍 Key Insights:")
    insights = llm.extract_key_insights(test_content)
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")
    print()
    
    # Test sentiment analysis
    print("📊 Sentiment Analysis:")
    sentiment = llm.analyze_sentiment(test_content)
    print(f"Sentiment: {sentiment.get('sentiment', 'N/A')}")
    print(f"Economic Tone: {sentiment.get('economic_tone', 'N/A')}")
    print(f"Confidence: {sentiment.get('confidence', 0):.2f}")
    if 'reasoning' in sentiment:
        print(f"Reasoning: {sentiment['reasoning']}")
    print()

def test_news_aggregator_llm():
    """Test news aggregator with LLM integration"""
    print("🗞️  Testing News Aggregator with LLM")
    print("=" * 50)
    
    # Initialize aggregator with LLM
    aggregator = NewsAggregator(llm_provider="auto")
    
    # Test article
    test_article = {
        'title': 'Unemployment Rate Drops to 3.7% as Job Market Shows Resilience',
        'description': 'The latest jobs report shows unemployment falling to 3.7%, with 250,000 new jobs added last month.',
        'url': 'https://example.com/jobs-report',
        'published': '2024-11-08'
    }
    
    print("📈 Testing Enhanced Article Processing:")
    print(f"Original Title: {test_article['title']}")
    print()
    
    # Test LLM-enhanced highlights
    print("✨ LLM-Enhanced Highlights:")
    highlights = aggregator.generate_highlights(test_article)
    for i, highlight in enumerate(highlights, 1):
        print(f"{i}. {highlight}")
    print()
    
    # Test LLM summary generation
    print("📝 LLM-Generated TL;DR:")
    summary = aggregator.generate_llm_summary(test_article)
    print(f"TL;DR: {summary}")
    print()
    
    # Test full article enhancement
    print("🚀 Full Article Enhancement:")
    enhanced = aggregator.enhance_article_with_llm(test_article)
    
    if enhanced.get('llm_enhanced'):
        print("✅ Article successfully enhanced with LLM")
        if 'sentiment_analysis' in enhanced:
            sentiment = enhanced['sentiment_analysis']
            print(f"📊 Sentiment: {sentiment.get('sentiment', 'N/A')} ({sentiment.get('confidence', 0):.2f})")
        
        if 'key_insights' in enhanced:
            print("🔍 Key Insights:")
            for insight in enhanced['key_insights'][:3]:
                print(f"  • {insight}")
    else:
        print("⚠️  LLM enhancement not available, using fallback methods")
    print()

def main():
    """Main test function"""
    print("🤖 LLM Integration Test Suite")
    print("=" * 60)
    print()
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print("🔑 API Key Status:")
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print()
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Testing will use rule-based fallbacks.")
        print("💡 To test LLM features, set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
        print()
    
    try:
        # Test LLM service
        test_llm_service()
        
        # Test news aggregator integration
        test_news_aggregator_llm()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
