#!/usr/bin/env python3
"""
LiteLLM-Integrated Daily News Digest Generator
Uses LiteLLM for enhanced article analysis and summarization
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import litellm
from dataclasses import dataclass

# Inline prompt for Federal Reserve Executive Daily News Digest
INLINE_PROMPT = """
You are an expert financial analyst creating a daily news digest for Federal Reserve executives. 

Your task is to analyze the provided news articles and create a comprehensive digest following this exact structure:

# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {date}
**Generated:** {timestamp}
**Total Articles Analyzed:** {total_articles}

## 1. Top 5 Headlines Relevant to the Federal Reserve
- Select the 5 most important articles directly related to Fed policy, monetary policy, or central banking
- For each article, provide:
  - Title with source link
  - 2-3 sentence summary focusing on Fed implications
  - Relevance score (High/Medium/Low)

## 2. 12th District Regional Economic & Labor Signals
*California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada*
- Housing market trends
- Labor market conditions  
- Consumer spending patterns
- Technology sector developments
- Supply chain/logistics updates

## 3. National Macroeconomic & Monetary Policy Developments
*Inflation, labor markets, GDP, productivity, FOMC outlook*
- Key economic indicators
- Market-implied rate expectations
- Yield curve movements
- Policy-relevant economic data

## 4. Financial System & Banking Stability Watch
*Bank liquidity/capital, CRE exposures, funding markets, credit spreads*
- Banking sector health indicators
- Credit market conditions
- Regulatory developments
- Systemic risk signals

## 5. Global & Pacific Rim Insights (SF Fed Priority)
*China, Japan, Korea, ASEAN, international central bank actions*
- International monetary policy actions
- Global trade developments
- Geopolitical economic impacts
- Cross-border financial flows

## 6. Technology, Cyber, and Payments Developments
*Cyber threats, AI risks, fintech, FedNow, digital assets*
- Cybersecurity threats to financial system
- Fintech innovations and risks
- Digital currency developments
- Payment system evolution

## 7. Regulatory, Legislative, and Federal Government Updates
*Congress, Treasury, CFPB, FDIC, OCC*
- New regulations affecting banks
- Congressional financial legislation
- Inter-agency coordination matters
- Policy implementation updates

## 8. Implications for SF Fed
Provide 5-7 bullet points covering:
• Monetary policy considerations
• Bank supervision priorities  
• Regional economic monitoring needs
• Payments & technology operations
• Financial stability assessments

## 9. Executive Summary (<150 words)
A concise, board-ready overview highlighting the most critical developments and their implications for Fed operations.

Guidelines:
- Maintain analytical, factual tone
- Focus on policy-relevant information
- Exclude consumer lifestyle news and political commentary
- Prioritize accuracy and decision-readiness
- Include specific data points and quotes where relevant
"""

@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM service"""
    api_base: str = "http://13.221.86.203:8250"
    api_key: str = "sk-12345"
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.1

class LiteLLMDigestGenerator:
    """Generate daily digest using LiteLLM for enhanced analysis"""
    
    def __init__(self, config: Optional[LiteLLMConfig] = None):
        self.config = config or LiteLLMConfig()
        self.setup_litellm()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
    def setup_litellm(self):
        """Configure LiteLLM client"""
        try:
            # Configure LiteLLM
            litellm.api_base = self.config.api_base
            litellm.api_key = self.config.api_key
            
            # Test connection
            print(f"Configuring LiteLLM with base: {self.config.api_base}")
            print(f"Using model: {self.config.model}")
            
        except Exception as e:
            print(f"Error setting up LiteLLM: {e}")
            raise
    
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            digest_dir = Path("/workspace/daily_news_brief/daily_digests")
            json_files = list(digest_dir.glob("daily_digest_*.json"))
            if not json_files:
                print("No daily digest files found")
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
    
    def prepare_articles_for_analysis(self, digest_data: Dict[str, Any]) -> str:
        """Prepare articles data for LLM analysis"""
        articles_text = "NEWS ARTICLES FOR ANALYSIS:\n\n"
        
        # Extract articles from categories
        categories_data = digest_data.get('categories', {})
        article_count = 0
        
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles = category_data['articles']
                
                for article in articles[:5]:  # Limit articles per category
                    article_count += 1
                    title = article.get('title', 'Untitled')
                    description = article.get('description', '')
                    source = article.get('source', 'Unknown')
                    url = article.get('url', '')
                    
                    articles_text += f"ARTICLE {article_count}:\n"
                    articles_text += f"Title: {title}\n"
                    articles_text += f"Source: {source}\n"
                    articles_text += f"Description: {description}\n"
                    articles_text += f"URL: {url}\n"
                    
                    # Add highlights if available
                    highlights = article.get('highlights', [])
                    if highlights:
                        articles_text += f"Key Points: {'; '.join(highlights[:3])}\n"
                    
                    articles_text += "\n---\n\n"
        
        return articles_text, article_count
    
    def generate_digest_with_litellm(self, articles_text: str, article_count: int) -> str:
        """Generate digest using LiteLLM"""
        try:
            # Prepare the prompt with current data
            current_date = datetime.now().strftime("%B %d, %Y")
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            formatted_prompt = INLINE_PROMPT.format(
                date=current_date,
                timestamp=current_timestamp,
                total_articles=article_count
            )
            
            # Combine prompt with articles
            full_prompt = f"{formatted_prompt}\n\n{articles_text}\n\nPlease analyze these articles and create the Federal Reserve Executive Daily News Digest following the exact structure provided above."
            
            print("Generating digest with LiteLLM...")
            print(f"Prompt length: {len(full_prompt)} characters")
            
            # Make LiteLLM API call
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert financial analyst specializing in Federal Reserve policy and economic analysis. Create comprehensive, accurate, and policy-relevant news digests."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            # Extract the generated content
            digest_content = response.choices[0].message.content
            print("Successfully generated digest with LiteLLM")
            
            return digest_content
            
        except Exception as e:
            print(f"Error generating digest with LiteLLM: {e}")
            return self.generate_fallback_digest(articles_text, article_count)
    
    def generate_fallback_digest(self, articles_text: str, article_count: int) -> str:
        """Generate a basic digest if LiteLLM fails"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {current_date}
**Generated:** {current_timestamp}
**Total Articles Analyzed:** {article_count}

## Note
This digest was generated using fallback analysis due to LiteLLM service unavailability.

## Articles Summary
{article_count} articles were collected and analyzed from various financial and economic news sources.

## Key Themes
- Federal Reserve policy developments
- Economic indicators and trends
- Financial market conditions
- Regional economic signals

## Recommendation
Manual review of source articles recommended for detailed policy analysis.

---
*Generated by LiteLLM Daily Digest Generator (Fallback Mode)*
"""
    
    def save_digest(self, content: str) -> str:
        """Save the generated digest"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"litellm_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Digest saved to: {filename}")
        return filename
    
    def generate_digest(self) -> str:
        """Main method to generate the complete digest"""
        print("Starting LiteLLM-integrated daily digest generation...")
        
        # Load latest daily digest data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Prepare articles for analysis
        articles_text, article_count = self.prepare_articles_for_analysis(digest_data)
        print(f"Prepared {article_count} articles for LiteLLM analysis")
        
        # Generate digest using LiteLLM
        digest_content = self.generate_digest_with_litellm(articles_text, article_count)
        
        # Save the digest
        filename = self.save_digest(digest_content)
        
        return filename

def main():
    """Main function to run the LiteLLM digest generator"""
    try:
        # Initialize generator
        generator = LiteLLMDigestGenerator()
        
        # Generate digest
        filename = generator.generate_digest()
        
        print(f"\n✅ LiteLLM Daily Digest generated successfully!")
        print(f"📄 File: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating LiteLLM digest: {e}")
        return None

if __name__ == "__main__":
    main()
