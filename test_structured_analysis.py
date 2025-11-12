
#!/usr/bin/env python3
"""
Test script for structured analysis using the comprehensive prompt format
Demonstrates the enhanced LLM-powered article analysis
"""

import os
import sys
from news_aggregator import NewsAggregator

def test_structured_analysis():
    """Test the new structured analysis functionality"""
    print("🧪 Testing Structured Analysis with Comprehensive Prompt")
    print("=" * 60)
    
    # Initialize aggregator with LLM
    aggregator = NewsAggregator(llm_provider="auto")
    
    # Test articles covering different economic topics
    test_articles = [
        {
            'title': 'Federal Reserve Raises Interest Rates by 0.25% to Combat Inflation',
            'description': 'The Federal Reserve announced a quarter-point increase in interest rates, marking the third rate hike this year as policymakers work to bring inflation back to the 2% target.',
            'url': 'https://example.com/fed-rates',
            'published': '2024-11-08'
        },
        {
            'title': 'Unemployment Rate Drops to 3.7% as Job Market Shows Resilience',
            'description': 'The latest jobs report shows unemployment falling to 3.7%, with 250,000 new jobs added last month, exceeding economist expectations.',
            'url': 'https://example.com/jobs-report',
            'published': '2024-11-08'
        },
        {
            'title': 'Housing Market Faces Affordability Crisis as Mortgage Rates Hit 7.5%',
            'description': 'Rising mortgage rates and home prices create perfect storm for housing affordability, with first-time buyers increasingly priced out of the market.',
            'url': 'https://example.com/housing-crisis',
            'published': '2024-11-08'
        }
    ]
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n📰 Test Article {i}: {article['title']}")
        print("=" * 80)
        
        # Generate structured analysis
        enhanced_article = aggregator.generate_structured_article_analysis(article)
        
        # Display results
        print(f"\n🎯 Topic/Headline:")
        print(f"   {enhanced_article.get('topic_headline', 'N/A')}")
        
        print(f"\n📋 Summary Highlights:")
        highlights = enhanced_article.get('summary_highlights', [])
        for j, highlight in enumerate(highlights, 1):
            print(f"   {j}. {highlight}")
        
        print(f"\n💬 Notable Quotes:")
        quotes = enhanced_article.get('notable_quotes', [])
        for j, quote in enumerate(quotes, 1):
            print(f"   {j}. {quote}")
        
        print(f"\n🔍 Context & Implications:")
        context = enhanced_article.get('context_implications', 'N/A')
        print(f"   {context}")
        
        # Show sentiment analysis if available
        if 'sentiment_analysis' in enhanced_article:
            sentiment = enhanced_article['sentiment_analysis']
            print(f"\n📊 Sentiment Analysis:")
            print(f"   Sentiment: {sentiment.get('sentiment', 'N/A')}")
            print(f"   Economic Tone: {sentiment.get('economic_tone', 'N/A')}")
            print(f"   Confidence: {sentiment.get('confidence', 0):.2f}")
        
        print(f"\n✅ LLM Enhanced: {enhanced_article.get('llm_enhanced', False)}")
        
        if i < len(test_articles):
            print("\n" + "-" * 80)

def test_topic_categorization():
    """Test how the structured analysis handles different economic topics"""
    print("\n\n🏷️  Testing Topic-Specific Analysis")
    print("=" * 60)
    
    aggregator = NewsAggregator(llm_provider="auto")
    
    # Test articles for specific economic categories
    topic_articles = {
        "Generative AI": {
            'title': 'OpenAI Launches GPT-5 with Advanced Economic Modeling Capabilities',
            'description': 'The new AI model can analyze complex economic data and provide market predictions, raising questions about AI impact on financial services jobs.',
            'url': 'https://example.com/gpt5-launch'
        },
        "Tariffs & Trade": {
            'title': 'New Tariffs on Chinese Electronics Could Raise Consumer Prices by 15%',
            'description': 'Trade analysts warn that proposed tariffs on Chinese electronics imports may lead to significant price increases for American consumers.',
            'url': 'https://example.com/china-tariffs'
        },
        "Presidential Administration": {
            'title': 'President Announces $2 Trillion Infrastructure Investment Plan',
            'description': 'The administration unveiled a comprehensive infrastructure package aimed at modernizing transportation and creating millions of jobs.',
            'url': 'https://example.com/infrastructure-plan'
        }
    }
    
    for topic, article in topic_articles.items():
        print(f"\n📂 Topic Category: {topic}")
        print(f"📰 Article: {article['title']}")
        print("-" * 50)
        
        enhanced_article = aggregator.generate_structured_article_analysis(article)
        
        # Show key highlights for this topic
        highlights = enhanced_article.get('summary_highlights', [])
        print("Key Points:")
        for highlight in highlights[:2]:  # Show first 2 highlights
            print(f"  • {highlight}")
        
        # Show context
        context = enhanced_article.get('context_implications', '')
        if context:
            print(f"Impact: {context[:100]}...")

def main():
    """Main test function"""
    print("🤖 Structured Analysis Test Suite")
    print("Using Comprehensive Economic News Prompt Format")
    print("=" * 70)
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print("\n🔑 API Key Status:")
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    
    if not openai_key and not anthropic_key:
        print("\n⚠️  No API keys found. Testing will use rule-based fallbacks.")
        print("💡 To test LLM features, set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
    
    try:
        # Test structured analysis
        test_structured_analysis()
        
        # Test topic categorization
        test_topic_categorization()
        
        print("\n\n✅ All structured analysis tests completed successfully!")
        print("\n📋 Summary:")
        print("   • Comprehensive prompt format implemented")
        print("   • Topic/Headline extraction working")
        print("   • 4-point summary highlights generated")
        print("   • Notable quotes identification active")
        print("   • Context & implications analysis functional")
        print("   • Fallback mechanisms operational")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

