#!/usr/bin/env python3
"""
Test script for LiteLLM integration with Claude Sonnet 4
"""

import os
import json
from litellm_client import LiteLLMClient

def test_litellm_integration():
    """Test LiteLLM integration with Claude Sonnet 4"""
    
    print("Testing LiteLLM Integration with Claude Sonnet 4")
    print("=" * 50)
    
    # Test with LiteLLM provider
    try:
        # Initialize LLM client with config file
        llm = LiteLLMClient("llm_config_example.json")
        
        print(f"✅ LLM Client initialized")
        print(f"✅ Model: {llm.model}")
        print(f"✅ Max Tokens: {llm.max_tokens}")
        print(f"✅ Temperature: {llm.temperature}")
        
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
        print(json.dumps(analysis, indent=2))
        
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
        print("1. Valid llm_config_example.json file")
        print("2. API key in config or environment variable")
        print("3. LiteLLM package installed")
        return False

def test_fallback_behavior():
    """Test fallback behavior when LiteLLM is not available"""
    
    print("\n" + "=" * 50)
    print("Testing Fallback Behavior")
    print("=" * 50)
    
    try:
        # Test with missing config file
        llm = LiteLLMClient("nonexistent_config.json")
        print(f"✅ Fallback initialization successful")
        
        test_article = {
            'title': 'Economic Test Article',
            'description': 'This is a test article for fallback behavior testing.',
        }
        
        print("✅ Config fallback behavior working")
        
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
    print(f"Config Fallback: {'✅ PASS' if fallback_success else '❌ FAIL'}")
    
    if litellm_success:
        print("\n🎉 LiteLLM integration is ready!")
    else:
        print("\n⚠️  Check llm_config_example.json and API keys.")
