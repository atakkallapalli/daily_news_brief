#!/usr/bin/env python3
"""
News Aggregator for Economic and Financial News
Fetches articles from major news sources about unemployment, inflation, market risk, and banking
"""

import requests
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any
import os

class NewsAggregator:
    def __init__(self):
        self.keywords = ['unemployment', 'inflation', 'market risk', 'banking', 'federal reserve', 'interest rates', 'economic outlook']
        self.sources = {
            'Bloomberg': 'https://www.bloomberg.com',
            'Reuters': 'https://www.reuters.com',
            'Fox News': 'https://www.foxnews.com',
            'NBC': 'https://www.nbcnews.com',
            'AP News': 'https://apnews.com',
            'WSJ': 'https://www.wsj.com',
            'LinkedIn': 'https://www.linkedin.com'
        }
        self.articles = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
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
    
    def fetch_public_rss_feeds(self) -> List[Dict]:
        """Fetch from publicly available RSS feeds"""
        rss_feeds = {
            'Reuters Business': 'https://www.reuters.com/business/finance/rss',
            'AP Business': 'https://feeds.apnews.com/rss/apf-business',
            'NBC Business': 'https://feeds.nbcnews.com/nbcnews/public/business',
        }
        
        articles = []
        for source_name, feed_url in rss_feeds.items():
            try:
                response = self.session.get(feed_url, timeout=10)
                if response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(response.content)
                        for item in root.findall('.//item')[:5]:  # Limit articles per feed
                            title = item.find('title')
                            link = item.find('link')
                            pub_date = item.find('pubDate')
                            description = item.find('description')
                            
                            if title is not None and link is not None:
                                title_text = title.text.lower()
                                desc_text = (description.text or '').lower()
                                
                                # Check if article is relevant to our keywords
                                if any(keyword in title_text or keyword in desc_text for keyword in self.keywords):
                                    articles.append({
                                        'title': title.text,
                                        'url': link.text,
                                        'published': pub_date.text if pub_date is not None else '',
                                        'description': description.text if description is not None else '',
                                        'source': source_name,
                                        'keyword': 'RSS Feed'
                                    })
                    except ET.ParseError:
                        print(f"Error parsing RSS feed: {source_name}")
                        
            except Exception as e:
                print(f"Error fetching RSS feed {source_name}: {e}")
                
        return articles
    
    def collect_articles(self) -> List[Dict]:
        """Collect articles from all sources"""
        print("Collecting articles from various sources...")
        
        # Search Google News for each keyword
        for keyword in self.keywords:
            print(f"Searching for: {keyword}")
            articles = self.search_google_news(keyword)
            self.articles.extend(articles)
            time.sleep(1)  # Be respectful with requests
        
        # Fetch from RSS feeds
        print("Fetching from RSS feeds...")
        rss_articles = self.fetch_public_rss_feeds()
        self.articles.extend(rss_articles)
        
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
        """Generate a formatted report"""
        report = []
        report.append("# Economic and Financial News Summary")
        report.append(f"**Collection Date:** {summary['collection_date']}")
        report.append(f"**Total Articles:** {summary['total_articles']}")
        report.append(f"**Sources:** {', '.join(summary['sources_covered'])}")
        report.append("\n---\n")
        
        for topic, articles in summary['topics'].items():
            report.append(f"## {topic} ({len(articles)} articles)")
            report.append("")
            
            for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles per topic
                report.append(f"### {i}. {article['title']}")
                report.append(f"**Source:** {article['source']}")
                report.append(f"**Published:** {article.get('published', 'N/A')}")
                report.append(f"**URL:** {article['url']}")
                if article.get('description'):
                    # Clean up description
                    desc = re.sub(r'<[^>]+>', '', article['description'])[:200]
                    report.append(f"**Summary:** {desc}...")
                report.append("")
            
            if len(articles) > 5:
                report.append(f"*... and {len(articles) - 5} more articles in this category*")
            report.append("")
        
        return "\n".join(report)

def main():
    aggregator = NewsAggregator()
    
    print("Starting news collection...")
    articles = aggregator.collect_articles()
    
    if not articles:
        print("No articles were collected. This might be due to rate limiting or access restrictions.")
        return
    
    print("Generating summary...")
    summary = aggregator.summarize_articles()
    
    print("Creating report...")
    report = aggregator.generate_report(summary)
    
    # Save report to file
    with open('/workspace/economic_news_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save raw data as JSON
    with open('/workspace/articles_data.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("Report saved to economic_news_report.md")
    print("Raw data saved to articles_data.json")
    
    return report

if __name__ == "__main__":
    main()
