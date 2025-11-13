#!/usr/bin/env python3
"""
Test script for LiteLLM integration with Claude Sonnet 4
"""

import os
from news_aggregator import LLMService

def test_litellm_integration():
    """Test LiteLLM integration with Claude Sonnet 4"""
    
    print("Testing LiteLLM Integration with Claude Sonnet 4")
    print("=" * 50)
    
    # Test with LiteLLM provider
    try:
        # Initialize LLM service with LiteLLM
        llm = LLMService(
            provider="litellm", 
            model="claude-3-5-sonnet-20241022",  # Updated Claude Sonnet model
            api_key=os.getenv('LITELLM_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        )
        
        print(f"✅ LLM Service initialized with provider: {llm.provider}")
        print(f"✅ Model: {llm.model}")
        
        # Test article for structured analysis
        test_article = {
            'title': 'Federal Reserve Raises Interest Rates by 0.25% Amid Inflation Concerns',
            'description': 'The Federal Reserve announced a quarter-point interest rate increase today, citing persistent inflation pressures. Fed Chair Jerome Powell stated that "we remain committed to bringing inflation back to our 2% target." The decision was unanimous among voting members. Markets reacted positively, with the S&P 500 gaining 1.2%. Economists predict this could be the final rate hike of the cycle if inflation continues to moderate.',
            'url': 'https://example.com/fed-rate-hike',
            'source': 'Financial News'
        }
        
        print("\n🔍 Testing Structured Analysis...")
        analysis = llm.generate_structured_analysis(test_article)
        
        print("\n📊 Structured Analysis Results:")
        print("-" * 30)
        
        if 'topic_headline' in analysis:
            print(f"Topic: {analysis['topic_headline']}")
        
        if 'summary_highlights' in analysis and analysis['summary_highlights']:
            print(f"\nSummary Highlights ({len(analysis['summary_highlights'])} points):")
            for i, highlight in enumerate(analysis['summary_highlights'], 1):
                print(f"  {i}. {highlight[:100]}...")
        
        if 'notable_quotes' in analysis and analysis['notable_quotes']:
            print(f"\nNotable Quotes ({len(analysis['notable_quotes'])}):")
            for quote in analysis['notable_quotes']:
                print(f"  • {quote}")
        
        if 'context_implications' in analysis:
            print(f"\nContext & Implications: {analysis['context_implications'][:150]}...")
        
        if 'market_sentiment' in analysis:
            sentiment = analysis['market_sentiment']
            print(f"\nMarket Sentiment: {sentiment}")
        
        print("\n✅ LiteLLM integration test completed successfully!")
        
        # Test summary generation
        print("\n🔍 Testing Summary Generation...")
        summary = llm.generate_summary(test_article['description'], max_length=100)
        print(f"Summary: {summary}")
        
        # Test sentiment analysis
        print("\n🔍 Testing Sentiment Analysis...")
        sentiment = llm.analyze_sentiment(test_article['description'])
        print(f"Sentiment Analysis: {sentiment}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LiteLLM integration: {e}")
        print("\nNote: This test requires:")
        print("1. LiteLLM proxy server running")
        print("2. LITELLM_API_KEY or ANTHROPIC_API_KEY environment variable")
        print("3. Proper model configuration")
        return False

def test_fallback_behavior():
    """Test fallback behavior when LiteLLM is not available"""
    
    print("\n" + "=" * 50)
    print("Testing Fallback Behavior")
    print("=" * 50)
    
    try:
        # Test auto-initialization (should fall back to available providers)
        llm = LLMService(provider="auto")
        print(f"✅ Auto-initialization successful with provider: {llm.provider}")
        
        test_article = {
            'title': 'Economic Test Article',
            'description': 'This is a test article for fallback behavior testing.',
        }
        
        # Test that methods work with fallback
        analysis = llm.generate_structured_analysis(test_article)
        print("✅ Structured analysis with fallback successful")
        
        summary = llm.generate_summary(test_article['description'])
        print("✅ Summary generation with fallback successful")
        
        sentiment = llm.analyze_sentiment(test_article['description'])
        print("✅ Sentiment analysis with fallback successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback behavior: {e}")
        return False

if __name__ == "__main__":
    print("LiteLLM Integration Test Suite")
    print("=" * 60)
    
    # Test LiteLLM integration
    litellm_success = test_litellm_integration()
    
    # Test fallback behavior
    fallback_success = test_fallback_behavior()
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"LiteLLM Integration: {'✅ PASS' if litellm_success else '❌ FAIL'}")
    print(f"Fallback Behavior: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if litellm_success and fallback_success:
        print("\n🎉 All tests passed! LiteLLM integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Check configuration and dependencies.")
