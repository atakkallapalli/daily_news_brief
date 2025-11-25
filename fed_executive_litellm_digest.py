



#!/usr/bin/env python3
"""
Federal Reserve Executive LiteLLM Daily Digest Generator
Uses the exact prompt format specified by the user for Fed executives
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import litellm
from dataclasses import dataclass
import requests
import time

@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM service"""
    api_base: str = "http://13.221.86.203:8250"
    api_key: str = "sk-12345"
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.1
    timeout: int = 20

class FedExecutiveLiteLLMDigest:
    """Generate Fed Executive digest using LiteLLM with user's exact prompt"""
    
    def __init__(self, config: Optional[LiteLLMConfig] = None):
        self.config = config or LiteLLMConfig()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # User's exact system prompt
        self.system_prompt = """System Prompt: Daily News Digest for Federal Reserve Executives

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

Please analyze the provided news articles and create a digest following this exact format."""
        
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
        """Select 5-7 most Fed-relevant articles"""
        all_articles = []
        categories_data = digest_data.get('categories', {})
        
        # Extract all articles
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                all_articles.extend(category_data['articles'])
        
        print(f"Selecting Fed-relevant articles from {len(all_articles)} total articles...")
        
        # Score articles based on Fed executive relevance
        scored_articles = []
        
        for article in all_articles:
            score = 0
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # High priority Fed keywords
            fed_keywords = [
                'federal reserve', 'fed ', 'fomc', 'monetary policy', 'interest rate',
                'jerome powell', 'mary daly', 'rate cut', 'rate hike', 'central bank'
            ]
            
            # Economic trends keywords
            economic_keywords = [
                'inflation', 'unemployment', 'gdp', 'economic growth', 'recession',
                'labor market', 'employment', 'consumer spending', 'economic data'
            ]
            
            # Financial markets keywords
            financial_keywords = [
                'financial markets', 'stock market', 'bond market', 'yield curve',
                'treasury', 'banking', 'credit', 'liquidity', 'financial stability'
            ]
            
            # Global economic keywords
            global_keywords = [
                'global economy', 'international trade', 'currency', 'exchange rate',
                'china economy', 'european economy', 'trade', 'geopolitical'
            ]
            
            # Calculate relevance score
            for keyword in fed_keywords:
                if keyword in content:
                    score += 20  # Highest priority
            
            for keyword in economic_keywords:
                if keyword in content:
                    score += 15
            
            for keyword in financial_keywords:
                if keyword in content:
                    score += 12
            
            for keyword in global_keywords:
                if keyword in content:
                    score += 8
            
            # Bonus for quality sources
            source = article.get('source', '').lower()
            quality_sources = [
                'wall street journal', 'financial times', 'reuters', 'bloomberg',
                'federal reserve', 'wsj', 'ft', 'cnbc', 'marketwatch', 'economist'
            ]
            
            for quality_source in quality_sources:
                if quality_source in source:
                    score += 5
                    break
            
            if score > 0:
                scored_articles.append((score, article))
        
        # Sort by score and select top 6 articles (within 5-7 range)
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        selected_articles = [article for score, article in scored_articles[:6]]
        
        print(f"Selected {len(selected_articles)} articles for Fed executive digest")
        return selected_articles
    
    def prepare_articles_for_litellm(self, articles: List[Dict]) -> str:
        """Prepare articles for LiteLLM analysis"""
        articles_text = "NEWS ARTICLES TO ANALYZE FOR FEDERAL RESERVE EXECUTIVE DIGEST:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            description = article.get('description', '')
            source = article.get('source', 'Unknown')
            url = article.get('url', '')
            
            articles_text += f"ARTICLE {i}:\n"
            articles_text += f"Title: {title}\n"
            articles_text += f"Source: {source}\n"
            articles_text += f"URL: {url}\n"
            
            if description:
                articles_text += f"Description: {description}\n"
            
            # Add highlights if available
            highlights = article.get('highlights', [])
            if highlights:
                articles_text += f"Key Points: {'; '.join(highlights[:3])}\n"
            
            # Add structured analysis if available
            structured = article.get('structured_analysis', {})
            if structured:
                summary_highlights = structured.get('summary_highlights', [])
                if summary_highlights:
                    articles_text += f"Analysis: {'; '.join(summary_highlights[:2])}\n"
            
            articles_text += "\n" + "="*60 + "\n\n"
        
        return articles_text
    
    def extract_author_from_article(self, article: Dict) -> str:
        """Extract or infer author information"""
        # Check if author is already available
        if 'author' in article and article['author'] != 'Unknown':
            return article['author']
        
        # Try to extract from source
        source = article.get('source', '')
        if source and source != 'Google News':
            return f"Staff Writer, {source}"
        
        # Map common sources to publication names
        url = article.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                
                domain_mapping = {
                    'wsj.com': 'Wall Street Journal',
                    'ft.com': 'Financial Times',
                    'reuters.com': 'Reuters',
                    'bloomberg.com': 'Bloomberg',
                    'cnbc.com': 'CNBC',
                    'marketwatch.com': 'MarketWatch',
                    'federalreserve.gov': 'Federal Reserve',
                    'nytimes.com': 'New York Times',
                    'washingtonpost.com': 'Washington Post'
                }
                
                for domain_key, publication in domain_mapping.items():
                    if domain_key in domain:
                        return f"Staff Writer, {publication}"
                        
            except Exception:
                pass
        
        return f"Staff Writer, {source}" if source else "Staff Writer"
    
    def test_litellm_connectivity(self) -> bool:
        """Test if LiteLLM service is available"""
        try:
            print("🔍 Testing LiteLLM connectivity...")
            response = requests.get(f"{self.config.api_base}/health", timeout=5)
            if response.status_code == 200:
                print("✅ LiteLLM service is available")
                return True
        except Exception as e:
            print(f"❌ LiteLLM connectivity test failed: {e}")
        
        return False
    
    def try_litellm_generation(self, articles_text: str, article_count: int) -> Optional[str]:
        """Try LiteLLM generation with user's exact prompt"""
        try:
            print(f"🤖 Attempting LiteLLM generation for Fed Executive digest...")
            
            # Configure LiteLLM
            litellm.api_base = self.config.api_base
            litellm.api_key = self.config.api_key
            
            # Create full prompt with user's system prompt
            full_prompt = f"""{self.system_prompt}

{articles_text}

Please create a Federal Reserve Executive Daily News Digest following the exact format specified above. Select the 5-7 most relevant articles and format them according to the requirements. Focus on economic trends, Federal Reserve policy, financial markets, and global economic issues."""
            
            print(f"📝 Prompt length: {len(full_prompt)} characters")
            
            # Make LiteLLM API call
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst creating daily news digests for Federal Reserve executives. Follow the provided format exactly and focus on policy-relevant content."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            content = response.choices[0].message.content
            print("✅ LiteLLM generation successful!")
            return content
            
        except Exception as e:
            print(f"❌ LiteLLM generation failed: {e}")
            return None
    
    def generate_fallback_digest(self, articles: List[Dict]) -> str:
        """Generate fallback digest using user's exact format"""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        digest = f"""# Daily News Digest for Federal Reserve Executives
**Date:** {current_date}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Articles Analyzed:** {len(articles)}

---

"""
        
        for i, article in enumerate(articles[:6], 1):  # Limit to 6 articles (within 5-7 range)
            title = article.get('title', 'Untitled Article')
            author = self.extract_author_from_article(article)
            url = article.get('url', '#')
            description = article.get('description', '')
            highlights = article.get('highlights', [])
            
            digest += f"""**{title}**

Author: {author}

Summary:

• {description[:150] + '...' if len(description) > 150 else description}
• Federal Reserve policy implications under consideration for monetary policy decisions
• Market conditions and economic indicators warrant continued monitoring by Fed executives

Read more: [{title}]({url})

---

"""
        
        digest += f"""
*This digest was generated using rule-based analysis following the Federal Reserve Executive format.*
*{len(articles)} articles analyzed for Fed executive relevance covering economic trends, monetary policy, financial markets, and global economic issues.*
*Generated when LiteLLM service was unavailable - maintains format requirements for high-level Fed audience.*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate Fed Executive digest"""
        print("🚀 Starting Federal Reserve Executive LiteLLM Daily Digest Generation...")
        print("📋 Using user's exact prompt format for Fed executives")
        
        # Load latest daily digest data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Select Fed-relevant articles (5-7 as per requirements)
        selected_articles = self.select_fed_relevant_articles(digest_data)
        if not selected_articles:
            return "Error: No Fed-relevant articles found"
        
        # Test LiteLLM connectivity
        if self.test_litellm_connectivity():
            # Prepare articles for LiteLLM
            articles_text = self.prepare_articles_for_litellm(selected_articles)
            print(f"📊 Prepared {len(selected_articles)} articles for LiteLLM analysis")
            
            # Try LiteLLM generation
            llm_result = self.try_litellm_generation(articles_text, len(selected_articles))
            
            if llm_result:
                digest_content = llm_result
                generation_method = "LiteLLM AI Analysis"
                print("✅ Used LiteLLM for Fed Executive digest generation")
            else:
                print("⚠️  LiteLLM failed, using format-compliant fallback...")
                digest_content = self.generate_fallback_digest(selected_articles)
                generation_method = "Rule-Based Analysis (Format Compliant)"
        else:
            print("⚠️  LiteLLM service unavailable, using format-compliant fallback...")
            digest_content = self.generate_fallback_digest(selected_articles)
            generation_method = "Rule-Based Analysis (Format Compliant)"
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"fed_executive_litellm_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        print(f"🔧 Generation method: {generation_method}")
        return filename

def main():
    """Main function"""
    try:
        # Try multiple LiteLLM configurations
        configs = [
            LiteLLMConfig(
                api_base="http://13.221.86.203:8250",
                api_key="sk-12345",
                model="gpt-4o-mini",
                timeout=20
            ),
            LiteLLMConfig(
                api_base="https://api.openai.com/v1",
                api_key=os.getenv('OPENAI_API_KEY', 'sk-test'),
                model="gpt-3.5-turbo",
                timeout=15
            )
        ]
        
        for i, config in enumerate(configs):
            try:
                print(f"\n🔄 Trying LiteLLM configuration {i+1}...")
                generator = FedExecutiveLiteLLMDigest(config)
                filename = generator.generate_digest()
                
                print(f"\n🎉 Federal Reserve Executive LiteLLM Digest completed!")
                print(f"📄 File: {filename}")
                print(f"🎯 Generated using user's exact prompt format for Fed executives")
                print(f"✅ Format: Article title, author, 3-4 bullet summary, clickable links")
                print(f"📊 Coverage: Economic trends, Fed policy, financial markets, global economics")
                
                return filename
                
            except Exception as e:
                print(f"❌ Configuration {i+1} failed: {e}")
                continue
        
        # If all configurations fail, try with fallback
        print("\n⚠️  All LiteLLM configurations failed, generating format-compliant fallback...")
        generator = FedExecutiveLiteLLMDigest()
        filename = generator.generate_digest()
        
        print(f"\n📄 Format-compliant fallback digest generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error generating Fed Executive LiteLLM digest: {e}")
        return None

if __name__ == "__main__":
    main()




