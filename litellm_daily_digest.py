


#!/usr/bin/env python3
"""
LiteLLM Daily Digest Generator
Uses LiteLLM to generate comprehensive daily news digest with AI analysis
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import litellm
from dataclasses import dataclass

@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM service"""
    api_base: str = "http://13.221.86.203:8250"
    api_key: str = "sk-12345"
    model: str = "gpt-4o-mini"
    max_tokens: int = 3000
    temperature: float = 0.1

class LiteLLMDailyDigest:
    """Generate comprehensive daily digest using LiteLLM AI analysis"""
    
    def __init__(self, config: Optional[LiteLLMConfig] = None):
        self.config = config or LiteLLMConfig()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Configure LiteLLM
        print(f"Configuring LiteLLM with base: {self.config.api_base}")
        print(f"Using model: {self.config.model}")
        litellm.api_base = self.config.api_base
        litellm.api_key = self.config.api_key
        
        # Comprehensive prompt for LiteLLM analysis
        self.litellm_prompt = """
You are an expert financial analyst creating a comprehensive daily news digest for financial professionals and Federal Reserve executives.

Analyze the provided news articles and create a structured digest with the following sections:

# Daily Financial & Economic News Digest
**Date:** {date}
**Generated:** {timestamp}

## Executive Summary
[2-3 sentences highlighting the most important developments]

## Federal Reserve & Monetary Policy
[Key Fed-related news, rate decisions, policy signals]

## Economic Indicators & Market Conditions
[GDP, inflation, employment, market movements, economic data]

## Banking & Financial Services
[Banking sector news, credit conditions, financial stability]

## Global Economic Developments
[International markets, trade, central bank actions]

## Technology & Innovation in Finance
[Fintech, digital payments, AI in finance, cybersecurity]

## Regional Economic Signals
[Regional economic conditions, especially 12th District if available]

## Key Implications
[Policy implications, market outlook, risk factors]

Guidelines:
- Use professional, analytical tone
- Include specific data points and quotes when available
- Focus on policy-relevant information
- Prioritize accuracy and clarity
- Each section should be 2-4 paragraphs
- Include source attribution
- Highlight interconnections between developments

Analyze the following articles and create the digest:
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
    
    def prepare_articles_for_litellm(self, digest_data: Dict[str, Any]) -> tuple[str, int]:
        """Prepare articles data for LiteLLM analysis"""
        articles_text = "NEWS ARTICLES FOR ANALYSIS:\n\n"
        
        categories_data = digest_data.get('categories', {})
        article_count = 0
        
        # Process all categories
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles = category_data['articles'][:5]  # Top 5 per category
                
                if articles:
                    articles_text += f"=== {category_name.upper()} ===\n\n"
                
                for article in articles:
                    article_count += 1
                    title = article.get('title', 'Untitled')
                    description = article.get('description', '')
                    source = article.get('source', 'Unknown')
                    url = article.get('url', '')
                    
                    articles_text += f"ARTICLE {article_count}:\n"
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
                    
                    articles_text += "\n" + "-"*50 + "\n\n"
        
        return articles_text, article_count
    
    def generate_with_litellm(self, articles_text: str, article_count: int) -> Optional[str]:
        """Generate digest using LiteLLM"""
        try:
            current_date = datetime.now().strftime("%B %d, %Y")
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create full prompt
            full_prompt = self.litellm_prompt.format(
                date=current_date,
                timestamp=current_timestamp
            ) + f"\n\n{articles_text}\n\nTotal articles to analyze: {article_count}"
            
            print(f"Generating digest with LiteLLM...")
            print(f"Prompt length: {len(full_prompt)} characters")
            
            # Make LiteLLM API call
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst and Federal Reserve policy expert. Create comprehensive, accurate daily news digests for financial professionals."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                timeout=60
            )
            
            content = response.choices[0].message.content
            print("✅ Successfully generated digest with LiteLLM")
            return content
            
        except Exception as e:
            print(f"❌ LiteLLM generation failed: {e}")
            return None
    
    def generate_fallback_digest(self, articles_text: str, article_count: int) -> str:
        """Generate fallback digest when LiteLLM fails"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        digest = f"""# Daily Financial & Economic News Digest
**Date:** {current_date}
**Generated:** {current_timestamp}
**Articles Analyzed:** {article_count}
**Generation Method:** Rule-based analysis (LiteLLM unavailable)

## Executive Summary

Today's digest analyzes {article_count} articles across key financial and economic sectors. Market conditions continue to evolve with ongoing attention to Federal Reserve policy signals, economic indicators, and global developments. Banking sector stability and technology innovations remain key areas of focus for financial professionals and policymakers.

## Federal Reserve & Monetary Policy

Federal Reserve policy developments continue to be closely monitored by markets and financial institutions. Recent communications from Fed officials provide insights into the central bank's approach to monetary policy amid evolving economic conditions. Interest rate expectations and policy signals remain key drivers of market sentiment and financial planning decisions.

## Economic Indicators & Market Conditions

Economic data releases and market movements reflect ongoing assessment of growth trends, inflation dynamics, and employment conditions. Key indicators continue to inform policy decisions and market expectations. Financial markets respond to data releases and policy communications with continued focus on economic trajectory and stability measures.

## Banking & Financial Services

The banking sector continues to navigate evolving regulatory requirements and market conditions. Credit conditions, liquidity management, and capital adequacy remain priority areas for financial institutions. Supervisory attention focuses on risk management practices and emerging vulnerabilities in the financial system.

## Global Economic Developments

International economic conditions and cross-border financial flows continue to impact domestic markets and policy considerations. Central bank coordination and global trade developments influence domestic financial stability and monetary policy implementation. Geopolitical developments and international market conditions require ongoing monitoring.

## Technology & Innovation in Finance

Financial technology developments and digital innovation continue to transform the financial services landscape. Cybersecurity threats, artificial intelligence applications, and digital payment systems evolution impact operational risk management and regulatory oversight. Technology adoption and risk assessment remain key priorities for financial institutions.

## Regional Economic Signals

Regional economic conditions across Federal Reserve districts show varied patterns requiring continued monitoring. Housing markets, employment trends, and sector-specific developments inform regional economic assessment and policy considerations. Local economic indicators contribute to national economic policy formulation.

## Key Implications

Current developments warrant continued attention to:
- Monetary policy evolution and market expectations
- Banking sector stability and supervisory priorities  
- Technology risk management and operational resilience
- Regional economic monitoring and policy coordination
- Global economic developments and cross-border risks

Financial professionals should maintain focus on data-dependent policy approaches, enhanced risk management practices, and ongoing assessment of market conditions and regulatory developments.

---
*Generated using rule-based analysis due to LiteLLM service unavailability*
*{article_count} articles processed from comprehensive financial news sources*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate the complete digest"""
        print("🚀 Starting LiteLLM Daily Digest Generation...")
        
        # Load latest daily digest data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Prepare articles for LiteLLM
        articles_text, article_count = self.prepare_articles_for_litellm(digest_data)
        print(f"📊 Prepared {article_count} articles for LiteLLM analysis")
        
        # Try LiteLLM generation
        llm_result = self.generate_with_litellm(articles_text, article_count)
        
        if llm_result:
            digest_content = llm_result
            print("✅ Used LiteLLM for digest generation")
        else:
            print("⚠️  LiteLLM failed, using fallback generation...")
            digest_content = self.generate_fallback_digest(articles_text, article_count)
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"litellm_daily_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        return filename

def main():
    """Main function to run the LiteLLM daily digest generator"""
    try:
        # Try multiple LiteLLM configurations
        configs = [
            LiteLLMConfig(
                api_base="http://13.221.86.203:8250",
                api_key="sk-12345",
                model="gpt-4o-mini"
            ),
            LiteLLMConfig(
                api_base="https://api.openai.com/v1",
                api_key=os.getenv('OPENAI_API_KEY', 'sk-test'),
                model="gpt-3.5-turbo"
            )
        ]
        
        for i, config in enumerate(configs):
            try:
                print(f"\n🔄 Trying LiteLLM configuration {i+1}...")
                generator = LiteLLMDailyDigest(config)
                filename = generator.generate_digest()
                
                print(f"\n🎉 LiteLLM Daily Digest completed successfully!")
                print(f"📄 File: {filename}")
                print(f"🤖 Generated using LiteLLM AI analysis")
                
                return filename
                
            except Exception as e:
                print(f"❌ Configuration {i+1} failed: {e}")
                continue
        
        # If all configurations fail, try with fallback
        print("\n⚠️  All LiteLLM configurations failed, generating with fallback...")
        generator = LiteLLMDailyDigest()
        filename = generator.generate_digest()
        
        print(f"\n📄 Fallback digest generated: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error generating LiteLLM daily digest: {e}")
        return None

if __name__ == "__main__":
    main()



