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
from bs4 import BeautifulSoup
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
            'GDP', 'recession', 'monetary policy', 'fiscal policy',
            'fed', 'jerome powell', 'fomc', 'federal open market committee',
            'fed chair', 'fed governor', 'fed official', 'fed policy',
            'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
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
            ),
            NewsSource(
                name='Federal Reserve News',
                url='https://www.federalreserve.gov/feeds/press_all.xml',
                source_type='free_rss',
                category='free',
                max_articles=20
            ),
            NewsSource(
                name='Fed Economic Data (FRED)',
                url='https://fred.stlouisfed.org/releases/rss',
                source_type='free_rss',
                category='free',
                max_articles=15
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
    
    def fetch_article_content(self, url: str) -> str:
        """Fetch full article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Try common article content selectors
                content_selectors = [
                    'article', '.article-content', '.story-body', '.entry-content',
                    '.post-content', '.content', '.article-body', 'main'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Get text and clean it
                        text = content_elem.get_text(separator=' ', strip=True)
                        # Limit to first 2000 characters to avoid too much content
                        return text[:2000] if len(text) > 2000 else text
                
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                    return text[:2000] if len(text) > 2000 else text
                    
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
        
        return ""

    def extract_quotes(self, text: str) -> List[str]:
        """Extract quotes from article text"""
        quotes = []
        
        # Find text in quotes
        import re
        quote_patterns = [
            r'"([^"]{20,200})"',  # Double quotes
            r"'([^']{20,200})'",  # Single quotes
            r'"([^"]{20,200})"',  # Curly quotes
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches[:3])  # Limit to 3 quotes per pattern
        
        return quotes[:5]  # Return max 5 quotes

    def generate_highlights(self, article: Dict[str, Any]) -> List[str]:
        """Generate 4-5 content-based highlights with quotes from the article"""
        highlights = []
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        
        # Fetch full article content
        full_content = self.fetch_article_content(url)
        
        # Combine all available text
        all_text = f"{title} {description} {full_content}"
        
        # Extract quotes from the content
        quotes = self.extract_quotes(all_text)
        
        # Generate content-based highlights
        sentences = all_text.split('.')
        key_sentences = []
        
        # Look for key economic indicators and statements
        economic_keywords = [
            'federal reserve', 'fed', 'inflation', 'unemployment', 'interest rate',
            'monetary policy', 'economic growth', 'gdp', 'market', 'banking'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 150:  # Good length for highlights
                if any(keyword in sentence.lower() for keyword in economic_keywords):
                    key_sentences.append(sentence)
        
        # Create highlights from key sentences and quotes
        highlight_count = 0
        
        # Add quotes as highlights (prioritize these)
        for quote in quotes[:2]:  # Max 2 quotes
            if highlight_count < 5:
                highlights.append(f'💬 "{quote}"')
                highlight_count += 1
        
        # Add key sentences as highlights
        for sentence in key_sentences[:3]:  # Max 3 key sentences
            if highlight_count < 5:
                # Clean up the sentence
                clean_sentence = sentence.replace('\n', ' ').replace('\r', ' ')
                clean_sentence = ' '.join(clean_sentence.split())  # Remove extra whitespace
                if len(clean_sentence) > 20:
                    highlights.append(f'📊 {clean_sentence}')
                    highlight_count += 1
        
        # If we don't have enough highlights, add generic ones based on content analysis
        if highlight_count < 4:
            content_lower = all_text.lower()
            
            if 'federal reserve' in content_lower or 'fed' in content_lower:
                highlights.append("🏛️ Federal Reserve policy developments discussed")
                highlight_count += 1
            
            if highlight_count < 4 and ('inflation' in content_lower or 'price' in content_lower):
                highlights.append("💰 Inflation and pricing trends analyzed")
                highlight_count += 1
            
            if highlight_count < 4 and ('employment' in content_lower or 'job' in content_lower):
                highlights.append("💼 Employment market conditions reported")
                highlight_count += 1
            
            if highlight_count < 4 and ('market' in content_lower or 'economic' in content_lower):
                highlights.append("📈 Economic and market developments covered")
                highlight_count += 1
        
        # Remove duplicates while preserving order
        highlights = list(dict.fromkeys(highlights))
        
        # Ensure we have exactly 4-5 highlights
        if len(highlights) < 4:
            # Add more generic highlights if needed
            generic_highlights = [
                "📊 Economic indicators and market analysis",
                "🏛️ Policy implications and regulatory updates", 
                "🌍 Global economic impact assessment",
                "🔮 Economic outlook and forecasts"
            ]
            
            for generic in generic_highlights:
                if len(highlights) < 4 and generic not in highlights:
                    highlights.append(generic)
        
        # Limit to maximum 5 highlights
        return highlights[:5]
        
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
    
    def is_article_recent(self, article: Dict, target_date: datetime = None) -> bool:
        """Check if article was published on target date or day before"""
        if target_date is None:
            target_date = datetime.now()
        
        # Define the date range (target date and day before)
        day_before = target_date - timedelta(days=1)
        
        published_str = article.get('published', '')
        if not published_str:
            # If no publish date, assume it's recent
            return True
        
        try:
            # Try to parse various date formats
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',  # RFC 2822 format
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822 with timezone
                '%Y-%m-%dT%H:%M:%S%z',       # ISO format
                '%Y-%m-%d %H:%M:%S',         # Simple format
                '%Y-%m-%d',                  # Date only
                '%d %b %Y',                  # Day Month Year
                '%b %d, %Y',                 # Month Day, Year
            ]
            
            article_date = None
            for fmt in date_formats:
                try:
                    article_date = datetime.strptime(published_str.strip(), fmt)
                    break
                except ValueError:
                    continue
            
            if article_date is None:
                # Try parsing partial dates (like "Thu, 06 No" from RSS feeds)
                import re
                date_match = re.search(r'(\w{3}),?\s*(\d{1,2})\s*(\w{2,3})', published_str)
                if date_match:
                    day_name, day_num, month_abbr = date_match.groups()
                    # Assume current year and try to match with target date range
                    current_year = target_date.year
                    
                    # Map month abbreviations
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
                        'ja': 1, 'fe': 2, 'mr': 3, 'ap': 4, 'my': 5, 'jn': 6,
                        'jl': 7, 'au': 8, 'se': 9, 'oc': 10, 'no': 11, 'de': 12
                    }
                    
                    month_num = month_map.get(month_abbr.lower()[:2])
                    if month_num:
                        try:
                            article_date = datetime(current_year, month_num, int(day_num))
                        except ValueError:
                            pass
            
            if article_date:
                # Remove timezone info for comparison
                if article_date.tzinfo:
                    article_date = article_date.replace(tzinfo=None)
                
                # Check if article date is within our range (target date or day before)
                target_date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_before_only = day_before.replace(hour=0, minute=0, second=0, microsecond=0)
                article_date_only = article_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                return day_before_only <= article_date_only <= target_date_only
            
        except Exception as e:
            print(f"Error parsing date '{published_str}': {e}")
        
        # If we can't parse the date, assume it's recent
        return True

    def collect_articles(self, target_date: datetime = None) -> List[Dict]:
        """Collect articles from all sources, filtered by date"""
        if target_date is None:
            target_date = datetime.now()
            
        print("Collecting articles from various sources...")
        
        # Fetch from all configured sources
        source_articles = self.fetch_all_sources()
        
        # Filter articles by date before adding to collection
        recent_source_articles = []
        for article in source_articles:
            if self.is_article_recent(article, target_date):
                recent_source_articles.append(article)
        
        print(f"Filtered {len(source_articles)} source articles to {len(recent_source_articles)} recent articles")
        self.articles.extend(recent_source_articles)
        
        # Search Google News for each keyword (as backup/additional source)
        print("Searching Google News for additional coverage...")
        # Prioritize Fed-related searches
        priority_keywords = [
            'unemployment', 'inflation', 'market risk', 
            'federal reserve', 'jerome powell', 'fed policy'
        ]
        for keyword in priority_keywords:
            print(f"Searching for: {keyword}")
            articles = self.search_google_news(keyword, days_back=2)  # Search last 2 days
            
            # Filter Google News articles by date
            recent_google_articles = []
            for article in articles:
                if self.is_article_recent(article, target_date):
                    article['highlights'] = self.generate_highlights(article)
                    article['source_category'] = 'free'
                    recent_google_articles.append(article)
            
            self.articles.extend(recent_google_articles)
            time.sleep(1)  # Be respectful with requests
        
        # Remove duplicates based on title similarity
        self.articles = self.remove_duplicates(self.articles)
        
        print(f"Collected {len(self.articles)} unique recent articles")
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
            content = f"{title_lower} {desc_lower}"
            
            # Fed-related keywords for comprehensive detection
            fed_keywords = [
                'federal reserve', 'fed', 'fomc', 'jerome powell', 'fed chair', 
                'fed governor', 'fed official', 'fed policy', 'fed meeting', 
                'fed minutes', 'fed speech', 'fed testimony', 'federal open market committee',
                'monetary policy', 'interest rate', 'rate cut', 'rate hike', 'rate decision',
                'powell says', 'fed says', 'central bank', 'fed fund', 'fed rate'
            ]
            
            # Categorize articles with Fed priority
            if any(keyword in content for keyword in fed_keywords):
                topic = 'Federal Reserve & Monetary Policy'
            elif any(word in content for word in ['unemployment', 'job', 'employment', 'jobless', 'labor']):
                topic = 'Unemployment & Employment'
            elif any(word in content for word in ['inflation', 'price', 'cpi', 'deflation', 'pce']):
                topic = 'Inflation'
            elif any(word in content for word in ['market risk', 'volatility', 'risk', 'market crash', 'correction']):
                topic = 'Market Risk'
            elif any(word in content for word in ['banking', 'bank', 'financial institution', 'credit']):
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
