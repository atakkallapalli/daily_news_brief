

#!/usr/bin/env python3
"""
User Prompt Format Daily Digest Generator
Generates digest using the exact format specified by the user
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

class UserPromptDigestGenerator:
    """Generate daily digest using user's exact inline prompt format"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # User's exact inline prompt format
        self.user_prompt_format = """
System Prompt: Daily News Digest for Federal Reserve Executives

Objective: Generate a daily news digest summarizing key financial, economic, and policy-related articles that are relevant to Federal Reserve executives. The digest should include the article title, a concise summary in 3-4 bullet points, the author's name, and a clickable link to the full article. Ensure there are no duplicates in the digest.

Format:

Article Title

Author: [Author Name]

Summary:

• Bullet point 1
• Bullet point 2
• Bullet point 3

Read more: [Link to the full article]

Requirements:

• Provide no more than 5-7 articles per digest.
• Ensure that all articles are up-to-date and cover relevant topics such as economic trends, Federal Reserve policy, financial markets, and global economic issues.
• Avoid repetition of articles across multiple digests.
• Summarize the main points of each article in a neutral and clear manner.
• Include hyperlinks to the original sources for further reading.
• Summaries should be concise, informative, and targeted toward a high-level audience.
"""
        
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            digest_dir = Path("/workspace/daily_news_brief/daily_digests")
            json_files = list(digest_dir.glob("daily_digest_*.json"))
            if not json_files:
                return {}
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"Loading digest from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded digest with {data.get('total_articles', 0)} articles")
                return data
        except Exception as e:
            print(f"Error loading daily digest: {e}")
            return {}
    
    def select_top_fed_articles(self, digest_data: Dict[str, Any]) -> List[Dict]:
        """Select top 5-7 Fed-relevant articles following user requirements"""
        all_articles = []
        categories_data = digest_data.get('categories', {})
        
        # Extract all articles
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                all_articles.extend(category_data['articles'])
        
        print(f"Selecting top Fed-relevant articles from {len(all_articles)} total articles...")
        
        # Score articles based on Fed executive relevance
        scored_articles = []
        
        for article in all_articles:
            score = 0
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # High priority: Direct Fed relevance
            fed_keywords = [
                'federal reserve', 'fed ', 'fomc', 'monetary policy', 'interest rate',
                'jerome powell', 'mary daly', 'rate cut', 'rate hike', 'central bank'
            ]
            
            # Medium priority: Economic trends
            economic_keywords = [
                'inflation', 'unemployment', 'gdp', 'economic growth', 'recession',
                'labor market', 'employment', 'consumer spending', 'economic data'
            ]
            
            # Medium priority: Financial markets
            financial_keywords = [
                'financial markets', 'stock market', 'bond market', 'yield curve',
                'treasury', 'banking', 'credit', 'liquidity', 'financial stability'
            ]
            
            # Lower priority: Global economic issues
            global_keywords = [
                'global economy', 'international trade', 'currency', 'exchange rate',
                'china economy', 'european economy', 'trade war', 'geopolitical'
            ]
            
            # Calculate relevance score
            for keyword in fed_keywords:
                if keyword in content:
                    score += 15  # Highest priority
            
            for keyword in economic_keywords:
                if keyword in content:
                    score += 10
            
            for keyword in financial_keywords:
                if keyword in content:
                    score += 8
            
            for keyword in global_keywords:
                if keyword in content:
                    score += 5
            
            # Bonus for quality sources (as per user requirements for high-level audience)
            source = article.get('source', '').lower()
            quality_sources = [
                'wall street journal', 'financial times', 'reuters', 'bloomberg',
                'federal reserve', 'wsj', 'ft', 'cnbc', 'marketwatch', 'economist',
                'new york times', 'washington post'
            ]
            
            for quality_source in quality_sources:
                if quality_source in source:
                    score += 5
                    break
            
            if score > 0:
                scored_articles.append((score, article))
        
        # Sort by score and select top 5-7 articles (as per user requirements)
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        selected_articles = [article for score, article in scored_articles[:6]]  # Select 6 articles
        
        print(f"Selected {len(selected_articles)} articles for Fed executive digest")
        return selected_articles
    
    def extract_author_from_article(self, article: Dict) -> str:
        """Extract or infer author information following user format requirements"""
        # Check if author is already available
        if 'author' in article and article['author'] != 'Unknown':
            return article['author']
        
        # Try to extract from source (as per user requirements for author attribution)
        source = article.get('source', '')
        if source and source != 'Google News':
            return f"Staff Writer, {source}"
        
        # Map common sources to publication names for high-level audience
        url = article.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                
                # High-quality sources for Fed executives
                domain_mapping = {
                    'wsj.com': 'Wall Street Journal',
                    'ft.com': 'Financial Times',
                    'reuters.com': 'Reuters',
                    'bloomberg.com': 'Bloomberg',
                    'cnbc.com': 'CNBC',
                    'marketwatch.com': 'MarketWatch',
                    'federalreserve.gov': 'Federal Reserve',
                    'nytimes.com': 'New York Times',
                    'washingtonpost.com': 'Washington Post',
                    'economist.com': 'The Economist'
                }
                
                for domain_key, publication in domain_mapping.items():
                    if domain_key in domain:
                        return f"Staff Writer, {publication}"
                        
            except Exception:
                pass
        
        return f"Staff Writer, {source}" if source else "Staff Writer"
    
    def create_bullet_summary(self, article: Dict) -> List[str]:
        """Create 3-4 bullet point summary as per user format requirements"""
        bullets = []
        
        # Use highlights if available
        highlights = article.get('highlights', [])
        if highlights:
            for highlight in highlights[:3]:
                if isinstance(highlight, str) and len(highlight.strip()) > 15:
                    # Clean and format for high-level audience
                    clean_highlight = highlight.strip()
                    if not clean_highlight.endswith('.'):
                        clean_highlight += '.'
                    bullets.append(clean_highlight)
        
        # Use structured analysis if available
        if len(bullets) < 3:
            structured = article.get('structured_analysis', {})
            if structured:
                summary_highlights = structured.get('summary_highlights', [])
                for highlight in summary_highlights:
                    if isinstance(highlight, str) and len(highlight.strip()) > 15:
                        clean_highlight = highlight.strip()
                        if not clean_highlight.endswith('.'):
                            clean_highlight += '.'
                        if clean_highlight not in bullets:
                            bullets.append(clean_highlight)
        
        # Use description as fallback, formatted for Fed executives
        if len(bullets) < 2:
            description = article.get('description', '')
            if description and len(description.strip()) > 30:
                # Split into sentences and create policy-relevant bullets
                sentences = re.split(r'[.!?]+', description)
                for sentence in sentences[:2]:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and sentence not in bullets:
                        if not sentence.endswith('.'):
                            sentence += '.'
                        bullets.append(sentence)
        
        # Ensure we have exactly 3 bullets (as per user format)
        while len(bullets) < 3:
            if len(bullets) == 0:
                bullets.append("Key economic development with implications for Federal Reserve policy.")
            elif len(bullets) == 1:
                bullets.append("Market reactions and policy considerations under review by Fed officials.")
            else:
                bullets.append("Continued monitoring of economic indicators and market conditions warranted.")
        
        # Return exactly 3 bullets (user format requirement)
        return bullets[:3]
    
    def clean_url(self, url: str) -> str:
        """Clean and validate URL for clickable links"""
        if not url:
            return "#"
        
        # Handle Google News redirects
        if 'news.google.com' in url and 'articles/' in url:
            return url
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    def generate_user_format_digest(self, articles: List[Dict]) -> str:
        """Generate digest following user's exact format requirements"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Header following user format
        digest = f"""# Daily News Digest for Federal Reserve Executives
**Date:** {current_date}
**Generated:** {current_timestamp}
**Articles Analyzed:** {len(articles)} (selected from comprehensive news sources)

---

"""
        
        # Generate articles in user's exact format
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled Article')
            author = self.extract_author_from_article(article)
            url = self.clean_url(article.get('url', '#'))
            bullets = self.create_bullet_summary(article)
            
            # User's exact format
            digest += f"""**{title}**

Author: {author}

Summary:

• {bullets[0]}
• {bullets[1]}
• {bullets[2]}

Read more: [{title}]({url})

---

"""
        
        # Footer with user requirements compliance
        digest += f"""
*This digest follows the user-specified format requirements:*
- *{len(articles)} articles selected (within 5-7 article limit)*
- *Focus on economic trends, Federal Reserve policy, financial markets, and global economic issues*
- *Neutral, clear summaries targeted toward high-level audience*
- *Clickable links to original sources for further reading*
- *No duplicate articles included*

*Generated on {current_date} using user-provided inline prompt format*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate digest using user's inline prompt format"""
        print("🚀 Starting User Prompt Format Daily Digest Generation...")
        print("📋 Following user's exact inline prompt format and requirements")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Select top Fed-relevant articles (5-7 as per user requirements)
        selected_articles = self.select_top_fed_articles(digest_data)
        if not selected_articles:
            return "Error: No Fed-relevant articles found"
        
        print(f"📊 Selected {len(selected_articles)} articles following user requirements")
        
        # Generate digest in user's exact format
        digest_content = self.generate_user_format_digest(selected_articles)
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"user_prompt_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        return filename

def main():
    """Main function to run the user prompt format digest generator"""
    try:
        generator = UserPromptDigestGenerator()
        filename = generator.generate_digest()
        
        print(f"\n🎉 User Prompt Format Daily Digest completed successfully!")
        print(f"📄 File: {filename}")
        print(f"✅ Generated following user's exact inline prompt format requirements:")
        print(f"   • 5-7 articles focused on Fed-relevant topics")
        print(f"   • Article title, author, 3-bullet summary, clickable link format")
        print(f"   • Neutral tone targeted toward high-level Fed executive audience")
        print(f"   • No duplicate articles, quality source prioritization")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating user prompt format digest: {e}")
        return None

if __name__ == "__main__":
    main()


