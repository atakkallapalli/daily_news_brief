

#!/usr/bin/env python3
"""
LiteLLM Federal Reserve Executive Daily News Digest Generator
Uses the specific inline prompt format provided by the user
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import litellm
from dataclasses import dataclass

# User-provided inline prompt for Federal Reserve Executive Daily News Digest
USER_INLINE_PROMPT = """
System Prompt: Daily News Digest for Federal Reserve Executives

Objective: Generate a daily news digest summarizing key financial, economic, and policy-related articles that are relevant to Federal Reserve executives. The digest should include the article title, a concise summary in 4-5 bullet points with relevant quotes, the author's name, and a clickable link to the full article. Ensure there are no duplicates in the digest.

Format:

**Article Title**

Author: [Author Name]

Summary:

• Bullet point 1 with key information and relevant quote if available
• Bullet point 2 highlighting economic implications or policy impact
• Bullet point 3 with market reactions or data points mentioned
• Bullet point 4 covering Federal Reserve relevance or monetary policy connections
• Bullet point 5 with forward-looking implications or expert analysis (if applicable)

Read more: [Article Title](URL)

Requirements:

• Provide no more than 5-7 articles per digest.
• Each summary must contain 4-5 substantive bullet points, not generic statements.
• Include direct quotes from articles when available and relevant.
• Ensure that all articles are up-to-date and cover relevant topics such as economic trends, Federal Reserve policy, financial markets, and global economic issues.
• Avoid repetition of articles across multiple digests.
• Summarize the main points of each article in a neutral and clear manner with specific details.
• Include hyperlinks to the original sources for further reading.
• Summaries should be concise, informative, and targeted toward a high-level audience.
• Focus on actionable insights and policy implications for Fed executives.

Please analyze the provided news articles and create a digest following this exact format.
"""

@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM service"""
    api_base: str = "http://13.221.86.203:8250"
    api_key: str = "sk-12345"
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.1

class LiteLLMFedExecutiveDigest:
    """Generate Federal Reserve Executive digest using LiteLLM with user's inline prompt"""
    
    def __init__(self, config: Optional[LiteLLMConfig] = None):
        self.config = config or LiteLLMConfig()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Alternative LiteLLM configurations to try
        self.litellm_configs = [
            {
                "api_base": "http://13.221.86.203:8250",
                "api_key": "sk-12345",
                "model": "gpt-4o-mini"
            },
            {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv('OPENAI_API_KEY', 'sk-test')
            },
            {
                "model": "claude-3-haiku-20240307",
                "api_key": os.getenv('ANTHROPIC_API_KEY', 'sk-test')
            }
        ]
        
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
    
    def select_fed_relevant_articles(self, digest_data: Dict[str, Any]) -> List[Dict]:
        """Select the most Fed-relevant articles for the digest"""
        all_articles = []
        categories_data = digest_data.get('categories', {})
        
        # Extract all articles
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                all_articles.extend(category_data['articles'])
        
        print(f"Selecting Fed-relevant articles from {len(all_articles)} total articles...")
        
        # Score articles based on Fed relevance
        scored_articles = []
        
        for article in all_articles:
            score = 0
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # High priority Fed keywords
            high_priority = [
                'federal reserve', 'fed ', 'fomc', 'monetary policy', 'interest rate',
                'jerome powell', 'mary daly', 'rate cut', 'rate hike', 'central bank',
                'inflation', 'unemployment', 'economic policy'
            ]
            
            # Medium priority economic keywords
            medium_priority = [
                'economy', 'economic', 'gdp', 'labor market', 'employment',
                'banking', 'financial markets', 'treasury', 'yield curve',
                'credit', 'liquidity', 'financial stability'
            ]
            
            # Low priority but relevant
            low_priority = [
                'market', 'investment', 'trade', 'global economy',
                'regulation', 'policy', 'government'
            ]
            
            # Calculate relevance score
            for keyword in high_priority:
                if keyword in content:
                    score += 10
            
            for keyword in medium_priority:
                if keyword in content:
                    score += 5
            
            for keyword in low_priority:
                if keyword in content:
                    score += 2
            
            # Bonus for quality sources
            source = article.get('source', '').lower()
            quality_sources = [
                'wall street journal', 'financial times', 'reuters', 'bloomberg',
                'federal reserve', 'wsj', 'ft', 'cnbc', 'marketwatch', 'economist'
            ]
            
            for quality_source in quality_sources:
                if quality_source in source:
                    score += 3
                    break
            
            if score > 0:  # Only include articles with some relevance
                scored_articles.append((score, article))
        
        # Sort by score and select top 5-7 articles
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        selected_articles = [article for score, article in scored_articles[:7]]
        
        print(f"Selected {len(selected_articles)} articles for Fed executive digest")
        return selected_articles
    
    def prepare_articles_for_llm(self, articles: List[Dict]) -> str:
        """Prepare articles data for LLM analysis with enhanced content extraction"""
        articles_text = "NEWS ARTICLES TO ANALYZE:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            description = article.get('description', '')
            source = article.get('source', 'Unknown')
            url = article.get('url', '')
            author = self.extract_author_from_article(article)
            
            articles_text += f"ARTICLE {i}:\n"
            articles_text += f"Title: {title}\n"
            articles_text += f"Source: {source}\n"
            articles_text += f"Author: {author}\n"
            articles_text += f"URL: {url}\n"
            articles_text += f"Description: {description}\n"
            
            # Add content if available
            content = article.get('content', '')
            if content and len(content) > 100:
                # Truncate content to manageable size for LLM
                content_preview = content[:800] + "..." if len(content) > 800 else content
                articles_text += f"Content Preview: {content_preview}\n"
            
            # Add highlights if available
            highlights = article.get('highlights', [])
            if highlights:
                articles_text += f"Key Points: {'; '.join(highlights[:5])}\n"
            
            # Add structured analysis if available
            structured = article.get('structured_analysis', {})
            if structured:
                summary_highlights = structured.get('summary_highlights', [])
                if summary_highlights:
                    articles_text += f"Analysis: {'; '.join(summary_highlights[:3])}\n"
                
                key_quotes = structured.get('key_quotes', [])
                if key_quotes:
                    articles_text += f"Key Quotes: {'; '.join(key_quotes[:2])}\n"
                
                fed_relevance = structured.get('fed_relevance_score', 0)
                if fed_relevance > 0:
                    articles_text += f"Fed Relevance Score: {fed_relevance}/10\n"
            
            # Add publication date if available
            pub_date = article.get('published_date', '') or article.get('pubDate', '')
            if pub_date:
                articles_text += f"Published: {pub_date}\n"
            
            articles_text += "\n---\n\n"
        
        return articles_text
    
    def extract_author_from_article(self, article: Dict) -> str:
        """Extract or infer author information with enhanced mapping"""
        # Check if author is already available and not generic
        author = article.get('author', '')
        if author and author not in ['Unknown', 'Staff Writer', '']:
            return author
        
        # Try to extract from source
        source = article.get('source', '')
        url = article.get('url', '')
        
        # Enhanced domain mapping for better author attribution
        if url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                
                domain_mapping = {
                    'wsj.com': 'Wall Street Journal',
                    'www.wsj.com': 'Wall Street Journal',
                    'ft.com': 'Financial Times',
                    'www.ft.com': 'Financial Times',
                    'reuters.com': 'Reuters',
                    'www.reuters.com': 'Reuters',
                    'bloomberg.com': 'Bloomberg',
                    'www.bloomberg.com': 'Bloomberg',
                    'cnbc.com': 'CNBC',
                    'www.cnbc.com': 'CNBC',
                    'marketwatch.com': 'MarketWatch',
                    'www.marketwatch.com': 'MarketWatch',
                    'federalreserve.gov': 'Federal Reserve',
                    'www.federalreserve.gov': 'Federal Reserve',
                    'nytimes.com': 'The New York Times',
                    'www.nytimes.com': 'The New York Times',
                    'washingtonpost.com': 'The Washington Post',
                    'www.washingtonpost.com': 'The Washington Post',
                    'economist.com': 'The Economist',
                    'www.economist.com': 'The Economist',
                    'foxbusiness.com': 'Fox Business',
                    'www.foxbusiness.com': 'Fox Business',
                    'usatoday.com': 'USA Today',
                    'www.usatoday.com': 'USA Today',
                    'tradingview.com': 'TradingView',
                    'www.tradingview.com': 'TradingView',
                    'kitco.com': 'Kitco News',
                    'www.kitco.com': 'Kitco News'
                }
                
                for domain_key, publication in domain_mapping.items():
                    if domain_key in domain:
                        return f"Editorial Team, {publication}"
                        
            except Exception:
                pass
        
        # If source is available and not Google News, use it
        if source and source not in ['Google News', 'Unknown', '']:
            # Clean up source name
            clean_source = source.replace(' - ', ' ').replace('  ', ' ').strip()
            return f"Editorial Team, {clean_source}"
        
        # Last resort
        return "Editorial Team"
    
    def try_litellm_generation(self, prompt: str) -> Optional[str]:
        """Try multiple LiteLLM configurations"""
        for i, config in enumerate(self.litellm_configs):
            try:
                print(f"Trying LiteLLM configuration {i+1}: {config.get('model', 'unknown model')}")
                
                # Configure LiteLLM
                if "api_base" in config:
                    litellm.api_base = config["api_base"]
                if "api_key" in config:
                    litellm.api_key = config["api_key"]
                
                # Make API call with shorter timeout
                response = litellm.completion(
                    model=config["model"],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert financial analyst creating daily news digests for Federal Reserve executives. Follow the provided format exactly."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2500,
                    temperature=0.1,
                    timeout=10
                )
                
                content = response.choices[0].message.content
                print(f"✅ Successfully generated digest with {config.get('model', 'LiteLLM')}")
                return content
                
            except Exception as e:
                print(f"❌ Configuration {i+1} failed: {e}")
                continue
        
        return None
    
    def generate_fallback_digest(self, articles: List[Dict]) -> str:
        """Generate digest using rule-based approach when LLM fails"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        digest = f"""# Daily News Digest for Federal Reserve Executives
**Date:** {current_date}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

---

"""
        
        for i, article in enumerate(articles[:6], 1):  # Limit to 6 articles
            title = article.get('title', 'Untitled Article')
            author = self.extract_author_from_article(article)
            url = article.get('url', '#')
            description = article.get('description', '')
            source = article.get('source', 'Unknown')
            
            # Extract key information for better bullet points
            import re
            import html
            if description:
                clean_description = re.sub(r'<[^>]+>', '', description)
                clean_description = html.unescape(clean_description)
                clean_description = re.sub(r'&\w+;', ' ', clean_description)  # Remove remaining HTML entities
                clean_description = re.sub(r'\s+', ' ', clean_description).strip()  # Clean up whitespace
            else:
                clean_description = ''
            content_preview = clean_description[:150] + '...' if len(clean_description) > 150 else clean_description
            
            # Create more specific bullet points based on content
            bullet_points = []
            
            # First bullet: Main content
            if content_preview:
                bullet_points.append(f"Article reports: {content_preview}")
            else:
                bullet_points.append("Key developments in economic and financial markets are under analysis")
            
            # Second bullet: Fed policy implications
            fed_keywords = ['fed', 'federal reserve', 'monetary policy', 'interest rate', 'inflation']
            if any(keyword in title.lower() or keyword in clean_description.lower() for keyword in fed_keywords):
                bullet_points.append("Federal Reserve policy implications and monetary decisions are central to this development")
            else:
                bullet_points.append("Economic developments may influence Federal Reserve policy considerations")
            
            # Third bullet: Market impact
            market_keywords = ['market', 'economic', 'financial', 'banking', 'investment']
            if any(keyword in title.lower() or keyword in clean_description.lower() for keyword in market_keywords):
                bullet_points.append("Financial markets and economic indicators show measurable impacts from these developments")
            else:
                bullet_points.append("Market participants and analysts are monitoring developments for potential policy responses")
            
            # Fourth bullet: Analysis
            bullet_points.append("Economic indicators and data points mentioned may influence future Fed decision-making processes")
            
            # Fifth bullet: Forward-looking
            bullet_points.append("Financial markets and banking sector impacts warrant continued executive attention and policy evaluation")
            
            digest += f"""**{title}**

Author: {author}

Summary:

• {bullet_points[0]}
• {bullet_points[1]}
• {bullet_points[2]}
• {bullet_points[3]}
• {bullet_points[4]}

Read more: [{title}]({url})

---

"""
        
        digest += f"""
*This digest was generated using enhanced fallback analysis due to LiteLLM service unavailability.*
*{len(articles)} articles analyzed for Federal Reserve executive relevance covering economic trends, monetary policy, financial markets, and global economic issues.*
*Format updated to include 4-5 bullet points per article with enhanced author attribution and source links.*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate the complete digest"""
        print("🚀 Starting LiteLLM Federal Reserve Executive Digest Generation...")
        print("📋 Using user-provided inline prompt format")
        
        # Load latest daily digest data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Select Fed-relevant articles
        selected_articles = self.select_fed_relevant_articles(digest_data)
        if not selected_articles:
            return "Error: No Fed-relevant articles found"
        
        # Prepare articles for LLM analysis
        articles_text = self.prepare_articles_for_llm(selected_articles)
        
        # Create full prompt with user's inline prompt
        full_prompt = f"""{USER_INLINE_PROMPT}

{articles_text}

Please create a Federal Reserve Executive Daily News Digest following the exact format specified above. Select the 5-7 most relevant articles and format them according to the requirements."""
        
        print(f"📊 Prepared {len(selected_articles)} articles for LiteLLM analysis")
        print(f"📝 Prompt length: {len(full_prompt)} characters")
        
        # Try LiteLLM generation
        print("🤖 Attempting LiteLLM generation with user's inline prompt...")
        llm_result = self.try_litellm_generation(full_prompt)
        
        if llm_result:
            digest_content = llm_result
            print("✅ Successfully generated digest with LiteLLM")
        else:
            print("⚠️  LiteLLM failed, using fallback generation...")
            digest_content = self.generate_fallback_digest(selected_articles)
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"litellm_fed_executive_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        return filename

def main():
    """Main function to run the LiteLLM Fed executive digest generator"""
    try:
        generator = LiteLLMFedExecutiveDigest()
        filename = generator.generate_digest()
        
        print(f"\n🎉 LiteLLM Federal Reserve Executive Digest completed!")
        print(f"📄 File: {filename}")
        print(f"🎯 Generated using user-provided inline prompt format")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating LiteLLM Fed executive digest: {e}")
        return None

if __name__ == "__main__":
    main()


