#!/usr/bin/env python3
"""
Enhanced News Aggregator for Economic and Financial News
Configurable news sources with free and subscription-based feeds
Includes article highlights and flexible source management
"""

import requests
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any, Optional
import os
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class NewsSource:
    """Configuration for a news source"""
    name: str
    url: str
    source_type: str  # 'free_rss', 'subscription_rss', 'api', 'web_scraping'
    category: str = 'general'  # 'free', 'subscription'
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: float = 1.0  # seconds between requests
    max_articles: int = 10
    active: bool = True

class NewsAggregator:
    def __init__(self, config_file: Optional[str] = None):
        self.keywords = [
            'unemployment', 'inflation', 'market risk', 'banking', 
            'federal reserve', 'interest rates', 'economic outlook',
            'GDP', 'recession', 'monetary policy', 'fiscal policy'
        ]
        
        # Initialize with default sources
        self.free_sources = self._get_default_free_sources()
        self.subscription_sources = self._get_default_subscription_sources()
        
        # Load custom configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_sources_config(config_file)
        
        self.articles = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _get_default_free_sources(self) -> List[NewsSource]:
        """Default free RSS feed sources"""
        return [
            NewsSource(
                name='Reuters Business',
                url='https://www.reuters.com/business/finance/rss',
                source_type='free_rss',
                category='free',
                max_articles=15
            ),
            NewsSource(
                name='AP Business',
                url='https://feeds.apnews.com/rss/apf-business',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='NBC Business',
                url='https://feeds.nbcnews.com/nbcnews/public/business',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='BBC Business',
                url='http://feeds.bbci.co.uk/news/business/rss.xml',
                source_type='free_rss',
                category='free',
                max_articles=12
            ),
            NewsSource(
                name='CNN Business',
                url='http://rss.cnn.com/rss/money_latest.rss',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='MarketWatch',
                url='https://feeds.marketwatch.com/marketwatch/topstories/',
                source_type='free_rss',
                category='free',
                max_articles=8
            )
        ]
    
    def _get_default_subscription_sources(self) -> List[NewsSource]:
        """Default subscription-based sources (require API keys or premium access)"""
        return [
            NewsSource(
                name='Wall Street Journal',
                url='https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
                source_type='subscription_rss',
                category='subscription',
                max_articles=15,
                active=False  # Requires subscription
            ),
            NewsSource(
                name='Financial Times',
                url='https://www.ft.com/rss/home/us',
                source_type='subscription_rss',
                category='subscription',
                max_articles=12,
                active=False  # Requires subscription
            ),
            NewsSource(
                name='Bloomberg Terminal',
                url='https://api.bloomberg.com/news',
                source_type='api',
                category='subscription',
                max_articles=20,
                active=False  # Requires Bloomberg Terminal access
            ),
            NewsSource(
                name='Yahoo Finance',
                url='https://feeds.finance.yahoo.com/rss/2.0/headline',
                source_type='free_rss',
                category='free',
                max_articles=10
            )
        ]
    
    def add_free_source(self, source: NewsSource) -> None:
        """Add a new free news source"""
        source.category = 'free'
        self.free_sources.append(source)
        print(f"Added free source: {source.name}")
    
    def add_subscription_source(self, source: NewsSource) -> None:
        """Add a new subscription-based news source"""
        source.category = 'subscription'
        self.subscription_sources.append(source)
        print(f"Added subscription source: {source.name}")
    
    def load_sources_config(self, config_file: str) -> None:
        """Load sources configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load free sources
            if 'free_sources' in config:
                for source_data in config['free_sources']:
                    source = NewsSource(**source_data)
                    self.free_sources.append(source)
            
            # Load subscription sources
            if 'subscription_sources' in config:
                for source_data in config['subscription_sources']:
                    source = NewsSource(**source_data)
                    self.subscription_sources.append(source)
                    
            print(f"Loaded configuration from {config_file}")
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
    
    def save_sources_config(self, config_file: str) -> None:
        """Save current sources configuration to JSON file"""
        config = {
            'free_sources': [source.__dict__ for source in self.free_sources],
            'subscription_sources': [source.__dict__ for source in self.subscription_sources]
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_file}")
    
    def generate_highlights(self, article: Dict[str, Any]) -> List[str]:
        """Generate 4-5 key highlights for an article based on title and description"""
        highlights = []
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"
        
        # Economic indicators highlights
        if any(word in content for word in ['unemployment', 'jobless', 'employment']):
            if 'increase' in content or 'rise' in content or 'up' in content:
                highlights.append("📈 Unemployment/employment metrics showing upward trend")
            elif 'decrease' in content or 'fall' in content or 'down' in content:
                highlights.append("📉 Employment situation showing improvement")
            else:
                highlights.append("💼 Employment market developments reported")
        
        if any(word in content for word in ['inflation', 'cpi', 'price']):
            if 'increase' in content or 'rise' in content or 'surge' in content:
                highlights.append("💰 Inflationary pressures intensifying")
            elif 'decrease' in content or 'fall' in content or 'decline' in content:
                highlights.append("💲 Price pressures showing signs of easing")
            else:
                highlights.append("📊 Inflation data and price trends updated")
        
        if any(word in content for word in ['federal reserve', 'fed', 'interest rate']):
            highlights.append("🏛️ Federal Reserve policy developments")
        
        if any(word in content for word in ['market', 'stock', 'trading', 'volatility']):
            highlights.append("📈 Market conditions and trading activity")
        
        if any(word in content for word in ['banking', 'bank', 'financial institution']):
            highlights.append("🏦 Banking sector and financial institution news")
        
        # Add generic highlights if we don't have enough specific ones
        while len(highlights) < 4:
            if 'economic' in content and "📊 Economic indicators and trends" not in highlights:
                highlights.append("📊 Economic indicators and trends")
            elif 'policy' in content and "🏛️ Policy implications and regulatory changes" not in highlights:
                highlights.append("🏛️ Policy implications and regulatory changes")
            elif 'global' in content or 'international' in content and "🌍 Global economic impact" not in highlights:
                highlights.append("🌍 Global economic impact")
            elif 'forecast' in content or 'outlook' in content and "🔮 Economic outlook and forecasts" not in highlights:
                highlights.append("🔮 Economic outlook and forecasts")
            else:
                highlights.append("📰 Economic and financial news update")
                break
        
        return highlights[:5]  # Limit to 5 highlights max
        
    def search_google_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Search Google News for articles with specific keywords"""
        articles = []
        try:
            # Use Google News RSS feed for public access
            base_url = "https://news.google.com/rss/search"
            params = {
                'q': query,
                'hl': 'en-US',
                'gl': 'US',
                'ceid': 'US:en'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                # Parse RSS feed (simplified)
                content = response.text
                # Extract article information from RSS
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(content)
                    for item in root.findall('.//item')[:10]:  # Limit to 10 articles per query
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            articles.append({
                                'title': title.text,
                                'url': link.text,
                                'published': pub_date.text if pub_date is not None else '',
                                'description': description.text if description is not None else '',
                                'source': 'Google News',
                                'keyword': query
                            })
                except ET.ParseError:
                    print(f"Error parsing RSS for query: {query}")
                    
        except Exception as e:
            print(f"Error searching Google News for '{query}': {e}")
            
        return articles
    
    def fetch_from_source(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from a single news source"""
        articles = []
        
        if not source.active:
            print(f"Skipping inactive source: {source.name}")
            return articles
            
        try:
            print(f"Fetching from {source.name} ({source.source_type})...")
            
            if source.source_type in ['free_rss', 'subscription_rss']:
                articles = self._fetch_rss_feed(source)
            elif source.source_type == 'api':
                articles = self._fetch_api_source(source)
            elif source.source_type == 'web_scraping':
                articles = self._fetch_web_scraping(source)
            
            # Add highlights to each article
            for article in articles:
                article['highlights'] = self.generate_highlights(article)
                article['source_category'] = source.category
            
            time.sleep(source.rate_limit)  # Respect rate limiting
            
        except Exception as e:
            print(f"Error fetching from {source.name}: {e}")
            
        return articles[:source.max_articles]
    
    def _fetch_rss_feed(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from RSS feed"""
        articles = []
        
        try:
            headers = source.headers.copy()
            if source.api_key:
                headers['Authorization'] = f"Bearer {source.api_key}"
                
            response = self.session.get(source.url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(response.content)
                    
                    for item in root.findall('.//item'):
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            title_text = title.text or ''
                            desc_text = (description.text or '') if description is not None else ''
                            
                            # Check if article is relevant to our keywords
                            content_lower = f"{title_text} {desc_text}".lower()
                            if any(keyword.lower() in content_lower for keyword in self.keywords):
                                articles.append({
                                    'title': title_text,
                                    'url': link.text,
                                    'published': pub_date.text if pub_date is not None else '',
                                    'description': desc_text,
                                    'source': source.name,
                                    'source_type': source.source_type,
                                    'keyword': 'RSS Feed'
                                })
                                
                except ET.ParseError as e:
                    print(f"Error parsing RSS feed from {source.name}: {e}")
            else:
                print(f"HTTP {response.status_code} error for {source.name}")
                
        except Exception as e:
            print(f"Error fetching RSS from {source.name}: {e}")
            
        return articles
    
    def _fetch_api_source(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from API-based source"""
        articles = []
        
        if not source.api_key:
            print(f"API key required for {source.name}")
            return articles
            
        try:
            headers = source.headers.copy()
            headers['Authorization'] = f"Bearer {source.api_key}"
            
            # This is a placeholder for API-specific implementations
            # Each API would need its own implementation
            print(f"API fetching not yet implemented for {source.name}")
            
        except Exception as e:
            print(f"Error fetching from API {source.name}: {e}")
            
        return articles
    
    def _fetch_web_scraping(self, source: NewsSource) -> List[Dict]:
        """Fetch articles via web scraping (placeholder)"""
        print(f"Web scraping not yet implemented for {source.name}")
        return []
    
    def fetch_all_sources(self) -> List[Dict]:
        """Fetch articles from all active sources"""
        all_articles = []
        
        # Fetch from free sources
        print("Fetching from free sources...")
        for source in self.free_sources:
            if source.active:
                articles = self.fetch_from_source(source)
                all_articles.extend(articles)
        
        # Fetch from subscription sources
        print("Fetching from subscription sources...")
        for source in self.subscription_sources:
            if source.active:
                articles = self.fetch_from_source(source)
                all_articles.extend(articles)
        
        return all_articles
    
    def collect_articles(self) -> List[Dict]:
        """Collect articles from all sources"""
        print("Collecting articles from various sources...")
        
        # Fetch from all configured sources
        source_articles = self.fetch_all_sources()
        self.articles.extend(source_articles)
        
        # Search Google News for each keyword (as backup/additional source)
        print("Searching Google News for additional coverage...")
        for keyword in self.keywords[:3]:  # Limit to avoid rate limiting
            print(f"Searching for: {keyword}")
            articles = self.search_google_news(keyword)
            # Add highlights to Google News articles
            for article in articles:
                article['highlights'] = self.generate_highlights(article)
                article['source_category'] = 'free'
            self.articles.extend(articles)
            time.sleep(1)  # Be respectful with requests
        
        # Remove duplicates based on title similarity
        self.articles = self.remove_duplicates(self.articles)
        
        print(f"Collected {len(self.articles)} unique articles")
        return self.articles
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = re.sub(r'[^\w\s]', '', article['title'].lower())[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
                
        return unique_articles
    
    def summarize_articles(self) -> Dict[str, Any]:
        """Create a summary of collected articles"""
        if not self.articles:
            return {"error": "No articles collected"}
        
        # Group articles by keyword/topic
        topics = {}
        for article in self.articles:
            title_lower = article['title'].lower()
            desc_lower = (article.get('description', '') or '').lower()
            
            # Categorize articles
            if any(word in title_lower or word in desc_lower for word in ['unemployment', 'job', 'employment']):
                topic = 'Unemployment & Employment'
            elif any(word in title_lower or word in desc_lower for word in ['inflation', 'price', 'cpi']):
                topic = 'Inflation'
            elif any(word in title_lower or word in desc_lower for word in ['market risk', 'volatility', 'risk']):
                topic = 'Market Risk'
            elif any(word in title_lower or word in desc_lower for word in ['banking', 'bank', 'financial']):
                topic = 'Banking & Finance'
            else:
                topic = 'General Economic News'
            
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(article)
        
        summary = {
            'collection_date': datetime.now().isoformat(),
            'total_articles': len(self.articles),
            'topics': topics,
            'sources_covered': list(set(article['source'] for article in self.articles))
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a formatted report with highlights"""
        report = []
        report.append("# Economic and Financial News Summary")
        report.append(f"**Collection Date:** {summary['collection_date']}")
        report.append(f"**Total Articles:** {summary['total_articles']}")
        report.append(f"**Sources:** {', '.join(summary['sources_covered'])}")
        
        # Add source breakdown
        free_sources = [s for s in summary['sources_covered'] if any(article.get('source_category') == 'free' for article in self.articles if article['source'] == s)]
        subscription_sources = [s for s in summary['sources_covered'] if any(article.get('source_category') == 'subscription' for article in self.articles if article['source'] == s)]
        
        if free_sources:
            report.append(f"**Free Sources:** {', '.join(free_sources)}")
        if subscription_sources:
            report.append(f"**Subscription Sources:** {', '.join(subscription_sources)}")
        
        report.append("\n---\n")
        
        for topic, articles in summary['topics'].items():
            report.append(f"## {topic} ({len(articles)} articles)")
            report.append("")
            
            for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles per topic
                report.append(f"### {i}. {article['title']}")
                report.append(f"**Source:** {article['source']} ({article.get('source_category', 'unknown')})")
                report.append(f"**Published:** {article.get('published', 'N/A')}")
                report.append(f"**URL:** {article['url']}")
                
                # Add highlights
                if article.get('highlights'):
                    report.append("**Key Highlights:**")
                    for highlight in article['highlights']:
                        report.append(f"  • {highlight}")
                
                if article.get('description'):
                    # Clean up description
                    desc = re.sub(r'<[^>]+>', '', article['description'])[:200]
                    report.append(f"**Summary:** {desc}...")
                report.append("")
            
            if len(articles) > 5:
                report.append(f"*... and {len(articles) - 5} more articles in this category*")
            report.append("")
        
        return "\n".join(report)

    def list_sources(self) -> None:
        """List all configured sources"""
        print("\n=== FREE SOURCES ===")
        for i, source in enumerate(self.free_sources, 1):
            status = "✅ Active" if source.active else "❌ Inactive"
            print(f"{i}. {source.name} ({source.source_type}) - {status}")
            print(f"   URL: {source.url}")
            print(f"   Max Articles: {source.max_articles}")
        
        print("\n=== SUBSCRIPTION SOURCES ===")
        for i, source in enumerate(self.subscription_sources, 1):
            status = "✅ Active" if source.active else "❌ Inactive"
            api_status = "🔑 API Key Set" if source.api_key else "🔓 No API Key"
            print(f"{i}. {source.name} ({source.source_type}) - {status} - {api_status}")
            print(f"   URL: {source.url}")
            print(f"   Max Articles: {source.max_articles}")
    
    def activate_source(self, source_name: str) -> bool:
        """Activate a source by name"""
        for source in self.free_sources + self.subscription_sources:
            if source.name.lower() == source_name.lower():
                source.active = True
                print(f"Activated source: {source.name}")
                return True
        print(f"Source not found: {source_name}")
        return False
    
    def deactivate_source(self, source_name: str) -> bool:
        """Deactivate a source by name"""
        for source in self.free_sources + self.subscription_sources:
            if source.name.lower() == source_name.lower():
                source.active = False
                print(f"Deactivated source: {source.name}")
                return True
        print(f"Source not found: {source_name}")
        return False

def main():
    """Main function with enhanced functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced News Aggregator')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--list-sources', action='store_true', help='List all sources')
    parser.add_argument('--activate', help='Activate a source by name')
    parser.add_argument('--deactivate', help='Deactivate a source by name')
    parser.add_argument('--save-config', help='Save current configuration to file')
    
    args = parser.parse_args()
    
    # Initialize aggregator
    aggregator = NewsAggregator(config_file=args.config)
    
    # Handle source management commands
    if args.list_sources:
        aggregator.list_sources()
        return
    
    if args.activate:
        aggregator.activate_source(args.activate)
        return
    
    if args.deactivate:
        aggregator.deactivate_source(args.deactivate)
        return
    
    if args.save_config:
        aggregator.save_sources_config(args.save_config)
        return
    
    # Run normal news collection
    print("Starting enhanced news collection...")
    print(f"Keywords: {', '.join(aggregator.keywords)}")
    
    articles = aggregator.collect_articles()
    
    if not articles:
        print("No articles were collected. This might be due to:")
        print("- Rate limiting or access restrictions")
        print("- Inactive sources (use --list-sources to check)")
        print("- Network connectivity issues")
        return
    
    print("Generating summary...")
    summary = aggregator.summarize_articles()
    
    print("Creating enhanced report...")
    report = aggregator.generate_report(summary)
    
    # Save report to file
    with open('economic_news_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save raw data as JSON
    with open('articles_data.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("✅ Report saved to economic_news_report.md")
    print("✅ Raw data saved to articles_data.json")
    print(f"📊 Collected {len(articles)} articles from {len(summary['sources_covered'])} sources")
    
    return report

def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "free_sources": [
            {
                "name": "Custom RSS Feed",
                "url": "https://example.com/rss",
                "source_type": "free_rss",
                "category": "free",
                "max_articles": 10,
                "active": False
            }
        ],
        "subscription_sources": [
            {
                "name": "Premium News API",
                "url": "https://api.example.com/news",
                "source_type": "api",
                "category": "subscription",
                "api_key": "your_api_key_here",
                "max_articles": 20,
                "active": False
            }
        ]
    }
    
    with open('news_sources_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration created: news_sources_config.json")

if __name__ == "__main__":
    main()
