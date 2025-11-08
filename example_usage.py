#!/usr/bin/env python3
"""
Example usage of the Enhanced News Aggregator
Demonstrates how to add new sources and use the flexible configuration
"""

from news_aggregator import NewsAggregator, NewsSource

def example_add_custom_sources():
    """Example: Adding custom news sources"""
    
    # Initialize the aggregator
    aggregator = NewsAggregator()
    
    # Add a new free RSS source
    custom_free_source = NewsSource(
        name="TechCrunch Finance",
        url="https://techcrunch.com/category/fintech/feed/",
        source_type="free_rss",
        category="free",
        max_articles=8,
        rate_limit=1.5,
        active=True
    )
    aggregator.add_free_source(custom_free_source)
    
    # Add a new subscription source (inactive by default)
    custom_subscription_source = NewsSource(
        name="Alpha Vantage News",
        url="https://www.alphavantage.co/query",
        source_type="api",
        category="subscription",
        api_key="YOUR_API_KEY_HERE",  # Replace with actual API key
        headers={"User-Agent": "NewsAggregator/1.0"},
        max_articles=15,
        rate_limit=2.0,
        active=False  # Set to True when you have a valid API key
    )
    aggregator.add_subscription_source(custom_subscription_source)
    
    # List all sources
    print("=== Current Sources Configuration ===")
    aggregator.list_sources()
    
    # Save the configuration for future use
    aggregator.save_sources_config("my_custom_config.json")
    
    return aggregator

def example_run_with_highlights():
    """Example: Run news collection with highlights"""
    
    # Load aggregator with custom config
    aggregator = NewsAggregator(config_file="news_sources_config.json")
    
    print("Starting news collection with highlights...")
    
    # Collect articles
    articles = aggregator.collect_articles()
    
    if articles:
        print(f"\n✅ Successfully collected {len(articles)} articles")
        
        # Show sample article with highlights
        sample_article = articles[0]
        print(f"\n📰 Sample Article: {sample_article['title']}")
        print(f"🏢 Source: {sample_article['source']} ({sample_article.get('source_category', 'unknown')})")
        
        if sample_article.get('highlights'):
            print("🔍 Key Highlights:")
            for highlight in sample_article['highlights']:
                print(f"   • {highlight}")
        
        # Generate and save report
        summary = aggregator.summarize_articles()
        report = aggregator.generate_report(summary)
        
        with open('example_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n📄 Report saved to example_report.md")
    else:
        print("❌ No articles collected")

def example_source_management():
    """Example: Managing sources dynamically"""
    
    aggregator = NewsAggregator()
    
    print("=== Source Management Example ===")
    
    # List current sources
    aggregator.list_sources()
    
    # Deactivate a source
    print("\n🔄 Deactivating 'BBC Business'...")
    aggregator.deactivate_source("BBC Business")
    
    # Activate a subscription source (if you have credentials)
    print("\n🔄 Attempting to activate 'Yahoo Finance'...")
    aggregator.activate_source("Yahoo Finance")
    
    # Show updated status
    print("\n=== Updated Sources ===")
    aggregator.list_sources()

if __name__ == "__main__":
    print("🚀 Enhanced News Aggregator Examples")
    print("=" * 50)
    
    # Example 1: Add custom sources
    print("\n1️⃣ Adding Custom Sources")
    example_add_custom_sources()
    
    # Example 2: Source management
    print("\n2️⃣ Source Management")
    example_source_management()
    
    # Example 3: Run with highlights
    print("\n3️⃣ Running Collection with Highlights")
    example_run_with_highlights()
    
    print("\n✨ Examples completed!")
