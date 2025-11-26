#!/usr/bin/env python3
"""
Improved LiteLLM Federal Reserve Executive Digest
With enhanced error handling and multiple provider support
"""

import json
import os
import re
import html
import litellm
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class LLMConfig:
    """Enhanced LLM configuration with multiple providers"""
    primary_provider: str = "openai"
    primary_model: str = "gpt-3.5-turbo"
    primary_api_key: str = ""
    
    secondary_provider: str = "anthropic"
    secondary_model: str = "claude-3-haiku-20240307"
    secondary_api_key: str = ""
    
    max_tokens: int = 2000
    temperature: float = 0.3
    timeout: int = 15
    retry_attempts: int = 3
    fallback_enabled: bool = True

class ImprovedLiteLLMFedDigest:
    """Improved Federal Reserve Executive digest with robust error handling"""
    
    def __init__(self, config_path: str = "llm_config_working.json"):
        self.config = self.load_config(config_path)
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "llm_settings": {
                "fallback_to_rule_based": True,
                "max_tokens": 2000,
                "temperature": 0.3,
                "timeout": 15,
                "retry_attempts": 3
            }
        }
    
    def try_llm_providers(self, prompt: str) -> Optional[str]:
        """Try multiple LLM providers in order"""
        
        providers = [
            {
                "name": "OpenAI",
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv('OPENAI_API_KEY')
            },
            {
                "name": "Anthropic", 
                "model": "claude-3-haiku-20240307",
                "api_key": os.getenv('ANTHROPIC_API_KEY')
            }
        ]
        
        for provider in providers:
            if not provider['api_key']:
                print(f"⚠️  {provider['name']} API key not set")
                continue
                
            try:
                print(f"🤖 Trying {provider['name']} ({provider['model']})...")
                
                response = litellm.completion(
                    model=provider['model'],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert financial analyst creating daily news digests for Federal Reserve executives."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    api_key=provider['api_key'],
                    max_tokens=self.config.get('llm_settings', {}).get('max_tokens', 2000),
                    temperature=self.config.get('llm_settings', {}).get('temperature', 0.3),
                    timeout=self.config.get('llm_settings', {}).get('timeout', 15)
                )
                
                content = response.choices[0].message.content
                print(f"✅ Successfully generated digest with {provider['name']}")
                return content
                
            except Exception as e:
                print(f"❌ {provider['name']} failed: {str(e)[:100]}")
                continue
        
        return None
    
    def generate_enhanced_fallback(self, articles: List[Dict[str, Any]]) -> str:
        """Generate enhanced fallback digest when LLM providers fail"""
        
        print("🔄 Generating enhanced fallback digest...")
        
        digest_content = f"""# Daily News Digest for Federal Reserve Executives
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Format:** Enhanced fallback with 4-5 bullet points, author attribution, and content insights

---

"""
        
        for i, article in enumerate(articles[:8], 1):
            title = article.get('title', 'Untitled Article')
            description = article.get('description', '')
            url = article.get('url', '#')
            
            # Clean HTML content
            clean_description = self.clean_html_content(description)
            
            # Extract author
            author = self.extract_author_from_article(article)
            
            digest_content += f"""**{title}**

Author: {author}

Summary:

• Article reports: {clean_description[:150]}{'...' if len(clean_description) > 150 else ''}
• Federal Reserve policy implications and monetary decisions are central to this development
• Financial markets and economic indicators show measurable impacts from these developments
• Economic indicators and data points mentioned may influence future Fed decision-making processes
• Future policy decisions may need to account for evolving economic conditions and market responses

Read more: [{title}]({url})

---

"""
        
        return digest_content
    
    def clean_html_content(self, content: str) -> str:
        """Clean HTML tags and entities from content"""
        if not content:
            return "No description available"
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def extract_author_from_article(self, article: Dict[str, Any]) -> str:
        """Extract author with enhanced domain mapping"""
        
        # Try to get author from article data
        if 'author' in article and article['author']:
            return article['author']
        
        # Extract from URL domain
        url = article.get('url', '')
        domain_mapping = {
            'reuters.com': 'Editorial Team, Reuters',
            'bloomberg.com': 'Editorial Team, Bloomberg',
            'wsj.com': 'Editorial Team, Wall Street Journal',
            'ft.com': 'Editorial Team, Financial Times',
            'cnbc.com': 'Editorial Team, CNBC',
            'marketwatch.com': 'Editorial Team, MarketWatch',
            'yahoo.com': 'Editorial Team, Yahoo Finance',
            'cnn.com': 'Editorial Team, CNN Business',
            'foxbusiness.com': 'Editorial Team, Fox Business',
            'kitco.com': 'Editorial Team, Kitco News'
        }
        
        for domain, author in domain_mapping.items():
            if domain in url:
                return author
        
        return "Editorial Team"
    
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            digest_dir = Path("daily_digests")
            if not digest_dir.exists():
                print("❌ Daily digests directory not found")
                return {}
            
            json_files = list(digest_dir.glob("daily_digest_*.json"))
            if not json_files:
                print("❌ No daily digest files found")
                return {}
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"Loading digest from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error loading digest: {e}")
            return {}
    
    def select_fed_relevant_articles(self, digest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select Federal Reserve relevant articles"""
        
        all_articles = []
        
        # Handle the specific structure: categories -> category_data -> articles
        categories = digest_data.get('categories', {})
        for category_name, category_data in categories.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles = category_data['articles']
                all_articles.extend(articles)
                print(f"Loaded {len(articles)} articles from {category_name}")
        
        print(f"Loaded {len(all_articles)} total articles from digest")
        
        # Filter for Fed-relevant articles
        fed_keywords = [
            'federal reserve', 'fed', 'monetary policy', 'interest rate', 
            'inflation', 'employment', 'economic policy', 'central bank',
            'fomc', 'jerome powell', 'rate cut', 'rate hike', 'quantitative easing',
            'daly', 'gold', 'economist', 'economic', 'market', 'financial',
            'unemployment', 'jobs', 'labor', 'wage', 'gdp', 'recession'
        ]
        
        relevant_articles = []
        for article in all_articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            
            # Check title and description for Fed-relevant keywords
            if any(keyword in title or keyword in description for keyword in fed_keywords):
                relevant_articles.append(article)
                print(f"  ✓ Selected: {article.get('title', 'Untitled')[:60]}...")
        
        print(f"Selected {len(relevant_articles)} articles for Fed executive digest")
        return relevant_articles[:10]  # Limit to top 10
    
    def generate_digest(self) -> Optional[str]:
        """Generate the complete digest"""
        
        print("🚀 Starting Improved LiteLLM Federal Reserve Executive Digest Generation...")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            print("❌ No digest data available")
            return None
        
        # Select relevant articles
        selected_articles = self.select_fed_relevant_articles(digest_data)
        if not selected_articles:
            print("❌ No Fed-relevant articles found")
            return None
        
        # Create prompt
        prompt = self.create_analysis_prompt(selected_articles)
        
        # Try LLM providers
        llm_result = self.try_llm_providers(prompt)
        
        # Use fallback if LLM fails
        if llm_result:
            digest_content = llm_result
            generation_method = "LLM"
        else:
            print("🔄 All LLM providers failed, using enhanced fallback...")
            digest_content = self.generate_enhanced_fallback(selected_articles)
            generation_method = "Enhanced Fallback"
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"improved_fed_executive_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        print(f"📊 Generation method: {generation_method}")
        print(f"📈 Articles processed: {len(selected_articles)}")
        
        return filename
    
    def create_analysis_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for LLM"""
        
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            description = self.clean_html_content(article.get('description', ''))
            url = article.get('url', '')
            
            articles_text += f"""
Article {i}:
Title: {title}
Description: {description}
URL: {url}
---
"""
        
        prompt = f"""Create a Federal Reserve Executive Daily News Digest with the following format:

# Daily News Digest for Federal Reserve Executives
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Format:** Enhanced with 4-5 bullet points, author attribution, and content insights

For each article, use this exact format:

**[Article Title]**

Author: [Author Name or Editorial Team, Publication]

Summary:

• [First bullet point with key information from the article]
• [Second bullet point about Federal Reserve policy implications]
• [Third bullet point about market/economic impacts]
• [Fourth bullet point about economic indicators and Fed decision influence]
• [Fifth bullet point about future policy considerations]

Read more: [[Article Title]]([URL])

---

Articles to analyze:
{articles_text}

Please analyze these articles and create the digest following the exact format above.
"""
        
        return prompt

def main():
    """Main function to run the improved digest generation"""
    
    print("🔧 Setting up improved LiteLLM Fed Executive Digest...")
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        print("   Will use enhanced fallback generation instead")
    
    # Generate digest
    generator = ImprovedLiteLLMFedDigest()
    result = generator.generate_digest()
    
    if result:
        print(f"✅ Digest generation completed: {result}")
    else:
        print("❌ Digest generation failed")

if __name__ == "__main__":
    main()
