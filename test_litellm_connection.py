#!/usr/bin/env python3
"""
Test LiteLLM connection to custom endpoint
"""

import json
import requests
from litellm_client import LiteLLMClient

def test_endpoint_connectivity():
    """Test basic connectivity to the LiteLLM endpoint"""
    
    # Load config
    try:
        with open("llm_config_example.json", 'r') as f:
            config = json.load(f)
        
        provider_url = config.get('llm_settings', {}).get('provider', '')
        api_key = config.get('llm_settings', {}).get('api_key', '')
        
        print(f"Testing endpoint: {provider_url}")
        print(f"API Key: {api_key[:10]}..." if api_key else "No API key")
        
        # Test basic HTTP connectivity
        print("\n1. Testing HTTP connectivity...")
        try:
            response = requests.get(provider_url, timeout=10)
            print(f"[OK] HTTP Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] HTTP Error: {e}")
            return False
        
        # Test LiteLLM client
        print("\n2. Testing LiteLLM client...")
        try:
            client = LiteLLMClient("llm_config_example.json")
            print(f"[OK] Client initialized with model: {client.model}")
            
            # Test simple completion
            print("\n3. Testing completion...")
            test_text = "The Federal Reserve announced interest rate changes."
            summary = client.generate_summary(test_text, max_length=50)
            print(f"[OK] Summary generated: {summary[:100]}...")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] LiteLLM Error: {e}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Config Error: {e}")
        return False

def test_news_aggregator_integration():
    """Test news_aggregator.py integration with LiteLLM"""
    
    print("\n" + "="*50)
    print("Testing news_aggregator.py integration")
    print("="*50)
    
    try:
        from news_aggregator import LLMService
        
        # Test with config-based initialization
        llm = LLMService(provider="litellm")
        
        if llm.available:
            print(f"[OK] LLMService initialized with provider: {llm.provider}")
            
            test_article = {
                'title': 'Fed Raises Interest Rates',
                'description': 'The Federal Reserve raised rates by 0.25% today.'
            }
            
            # Test summary generation
            summary = llm.generate_summary(test_article['description'])
            print(f"[OK] Summary: {summary}")
            
            # Test sentiment analysis
            sentiment = llm.analyze_sentiment(test_article['description'])
            print(f"[OK] Sentiment: {sentiment}")
            
            return True
        else:
            print("[ERROR] LLMService not available")
            return False
            
    except Exception as e:
        print(f"[ERROR] Integration Error: {e}")
        return False

if __name__ == "__main__":
    print("LiteLLM Connection Troubleshooting")
    print("="*60)
    
    # Test endpoint connectivity
    endpoint_ok = test_endpoint_connectivity()
    
    # Test news aggregator integration
    integration_ok = test_news_aggregator_integration()
    
    print("\n" + "="*60)
    print("TROUBLESHOOTING RESULTS:")
    print(f"Endpoint Connectivity: {'[PASS]' if endpoint_ok else '[FAIL]'}")
    print(f"News Aggregator Integration: {'[PASS]' if integration_ok else '[FAIL]'}")
    
    if not endpoint_ok:
        print("\nTROUBLESHOOTING STEPS:")
        print("1. Check if endpoint http://44.201.244.45:8250/ is accessible")
        print("2. Verify API key is correct")
        print("3. Check firewall/network restrictions")
        print("4. Test with curl: curl -X GET http://44.201.244.45:8250/")
    
    if not integration_ok:
        print("\nINTEGRATION ISSUES:")
        print("1. Update news_aggregator.py to use config file")
        print("2. Check LiteLLM package version")
        print("3. Verify model name in config")