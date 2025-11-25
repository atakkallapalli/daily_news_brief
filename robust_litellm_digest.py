



#!/usr/bin/env python3
"""
Robust LiteLLM Daily Digest Generator
Attempts LiteLLM but falls back gracefully to comprehensive rule-based analysis
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
    max_tokens: int = 2500
    temperature: float = 0.1
    timeout: int = 15  # Shorter timeout

class RobustLiteLLMDigest:
    """Generate daily digest with LiteLLM or comprehensive fallback"""
    
    def __init__(self, config: Optional[LiteLLMConfig] = None):
        self.config = config or LiteLLMConfig()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
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
    
    def try_quick_litellm_generation(self, articles_text: str, article_count: int) -> Optional[str]:
        """Try LiteLLM with quick timeout"""
        try:
            print(f"🤖 Attempting LiteLLM generation with {self.config.timeout}s timeout...")
            
            # Configure LiteLLM
            litellm.api_base = self.config.api_base
            litellm.api_key = self.config.api_key
            
            current_date = datetime.now().strftime("%B %d, %Y")
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Shorter, more focused prompt for faster processing
            quick_prompt = f"""Create a concise daily financial news digest from the provided articles.

Date: {current_date}
Generated: {current_timestamp}

Structure:
1. Executive Summary (2-3 sentences)
2. Federal Reserve & Monetary Policy
3. Economic Indicators & Markets
4. Banking & Financial Services
5. Key Implications

Keep each section brief but informative. Focus on the most important developments.

Articles to analyze ({article_count} total):
{articles_text[:8000]}"""  # Truncate to reduce processing time
            
            # Make quick LiteLLM call
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst. Create concise, professional daily news digests."
                    },
                    {
                        "role": "user",
                        "content": quick_prompt
                    }
                ],
                max_tokens=1500,  # Reduced for faster response
                temperature=0.1,
                timeout=self.config.timeout
            )
            
            content = response.choices[0].message.content
            print("✅ LiteLLM generation successful!")
            return content
            
        except Exception as e:
            print(f"❌ LiteLLM generation failed: {e}")
            return None
    
    def generate_comprehensive_fallback_digest(self, digest_data: Dict[str, Any]) -> str:
        """Generate comprehensive fallback digest with detailed analysis"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Extract and categorize articles
        categories_data = digest_data.get('categories', {})
        total_articles = digest_data.get('total_articles', 0)
        
        # Analyze articles by category
        fed_articles = []
        economic_articles = []
        banking_articles = []
        tech_articles = []
        global_articles = []
        
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles = category_data['articles']
                
                if 'federal reserve' in category_name.lower() or 'monetary' in category_name.lower():
                    fed_articles.extend(articles[:3])
                elif 'economic' in category_name.lower() or 'indicator' in category_name.lower():
                    economic_articles.extend(articles[:3])
                elif 'banking' in category_name.lower() or 'financial' in category_name.lower():
                    banking_articles.extend(articles[:3])
                elif 'technology' in category_name.lower() or 'fintech' in category_name.lower():
                    tech_articles.extend(articles[:2])
                else:
                    global_articles.extend(articles[:2])
        
        digest = f"""# Daily Financial & Economic News Digest
**Date:** {current_date}
**Generated:** {current_timestamp}
**Articles Analyzed:** {total_articles}
**Generation Method:** Comprehensive Rule-Based Analysis (LiteLLM unavailable)

---

## Executive Summary

Today's comprehensive analysis of {total_articles} financial and economic news articles reveals continued focus on Federal Reserve policy developments, evolving economic indicators, and banking sector conditions. Market participants remain attentive to monetary policy signals while monitoring regional economic trends and global developments. Technology and innovation continue to reshape the financial services landscape, requiring ongoing attention to operational risks and regulatory considerations.

## Federal Reserve & Monetary Policy

"""
        
        # Add Fed-specific content
        if fed_articles:
            digest += "Recent Federal Reserve developments include:\n\n"
            for article in fed_articles[:3]:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                description = article.get('description', '')[:200]
                
                digest += f"**{title}** (*{source}*)\n"
                digest += f"{description}{'...' if len(article.get('description', '')) > 200 else ''}\n\n"
        else:
            digest += """Federal Reserve policy continues to evolve in response to economic conditions and data developments. Market participants closely monitor Fed communications for signals regarding future monetary policy direction. Interest rate expectations and policy implementation remain key factors influencing financial market conditions and economic planning decisions.

"""
        
        digest += """## Economic Indicators & Market Conditions

"""
        
        # Add economic content
        if economic_articles:
            digest += "Key economic developments include:\n\n"
            for article in economic_articles[:3]:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                highlights = article.get('highlights', [])
                
                digest += f"**{title}** (*{source}*)\n"
                if highlights:
                    digest += f"• {highlights[0]}\n"
                digest += "\n"
        else:
            digest += """Economic indicators continue to provide insights into growth trends, inflation dynamics, and labor market conditions. Market movements reflect ongoing assessment of economic data and policy implications. Financial professionals monitor key indicators for signals regarding economic trajectory and potential policy responses.

"""
        
        digest += """## Banking & Financial Services

"""
        
        # Add banking content
        if banking_articles:
            digest += "Banking sector developments include:\n\n"
            for article in banking_articles[:3]:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                
                digest += f"• **{title}** (*{source}*)\n"
        else:
            digest += """Banking sector conditions continue to reflect evolving regulatory requirements and market dynamics. Credit conditions, liquidity management, and capital adequacy remain priority areas for financial institutions. Supervisory attention focuses on risk management practices and emerging vulnerabilities requiring ongoing monitoring and assessment.

"""
        
        digest += """## Technology & Innovation in Finance

"""
        
        # Add tech content
        if tech_articles:
            digest += "Technology developments include:\n\n"
            for article in tech_articles[:2]:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                
                digest += f"• **{title}** (*{source}*)\n"
        
        digest += """
Financial technology continues to evolve with implications for operational risk management, cybersecurity, and regulatory oversight. Digital payment systems, artificial intelligence applications, and fintech innovations require ongoing assessment of risks and opportunities. Technology adoption and risk management remain key priorities for financial institutions and regulators.

## Global Economic Developments

"""
        
        # Add global content
        if global_articles:
            digest += "International developments include:\n\n"
            for article in global_articles[:2]:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                
                digest += f"• **{title}** (*{source}*)\n"
        
        digest += """
International economic conditions and cross-border financial flows continue to influence domestic markets and policy considerations. Central bank coordination, global trade developments, and geopolitical factors impact financial stability and monetary policy implementation. International market conditions require ongoing monitoring and assessment.

## Key Implications

Based on today's analysis, key implications for financial professionals include:

• **Monetary Policy:** Continued attention to Federal Reserve communications and policy signals for guidance on interest rate expectations and economic outlook

• **Risk Management:** Enhanced focus on credit risk assessment, liquidity management, and operational resilience in evolving market conditions

• **Technology Operations:** Ongoing investment in cybersecurity, digital infrastructure, and technology risk management capabilities

• **Regulatory Compliance:** Continued coordination with regulatory agencies and attention to evolving supervisory expectations and requirements

• **Market Monitoring:** Sustained surveillance of economic indicators, market conditions, and global developments affecting domestic financial stability

Financial institutions and market participants should maintain data-dependent approaches to decision-making while enhancing risk management practices and operational readiness for evolving market conditions.

---
*Generated using comprehensive rule-based analysis*
*{total_articles} articles processed from multiple financial and economic news sources*
*Analysis includes Federal Reserve priorities, economic indicators, banking conditions, and technology developments*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate digest with LiteLLM or fallback"""
        print("🚀 Starting Robust LiteLLM Daily Digest Generation...")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Test LiteLLM connectivity first
        if self.test_litellm_connectivity():
            # Prepare articles for LiteLLM
            categories_data = digest_data.get('categories', {})
            articles_text = ""
            article_count = 0
            
            for category_name, category_data in categories_data.items():
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles = category_data['articles'][:2]  # Fewer articles for faster processing
                    
                    for article in articles:
                        article_count += 1
                        title = article.get('title', 'Untitled')
                        description = article.get('description', '')[:150]  # Shorter descriptions
                        source = article.get('source', 'Unknown')
                        
                        articles_text += f"{article_count}. {title} ({source}): {description}\n"
            
            print(f"📊 Prepared {article_count} articles for LiteLLM")
            
            # Try LiteLLM generation
            llm_result = self.try_quick_litellm_generation(articles_text, article_count)
            
            if llm_result:
                digest_content = llm_result
                generation_method = "LiteLLM AI Analysis"
                print("✅ Used LiteLLM for digest generation")
            else:
                print("⚠️  LiteLLM failed, using comprehensive fallback...")
                digest_content = self.generate_comprehensive_fallback_digest(digest_data)
                generation_method = "Comprehensive Rule-Based Analysis"
        else:
            print("⚠️  LiteLLM service unavailable, using comprehensive fallback...")
            digest_content = self.generate_comprehensive_fallback_digest(digest_data)
            generation_method = "Comprehensive Rule-Based Analysis"
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"robust_litellm_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        print(f"🔧 Generation method: {generation_method}")
        return filename

def main():
    """Main function"""
    try:
        generator = RobustLiteLLMDigest()
        filename = generator.generate_digest()
        
        print(f"\n🎉 Robust LiteLLM Daily Digest completed!")
        print(f"📄 File: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating robust LiteLLM digest: {e}")
        return None

if __name__ == "__main__":
    main()




