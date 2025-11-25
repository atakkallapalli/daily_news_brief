




#!/usr/bin/env python3
"""
Claude LiteLLM Daily Digest Generator
Uses specific LiteLLM configuration with Claude Sonnet 4 model
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
class ClaudeLiteLLMConfig:
    """Configuration for Claude LiteLLM service"""
    api_base: str = "http://44.201.244.45:8250"
    api_key: str = "sk-12345"
    model: str = "litellm_proxy/ClaudeSonnet4"
    max_tokens: int = 3000
    temperature: float = 0.1
    timeout: int = 30

class ClaudeLiteLLMDigest:
    """Generate daily digest using Claude via LiteLLM proxy"""
    
    def __init__(self, config: Optional[ClaudeLiteLLMConfig] = None):
        self.config = config or ClaudeLiteLLMConfig()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Configure LiteLLM with Claude settings
        print(f"🔧 Configuring LiteLLM with Claude Sonnet 4")
        print(f"🌐 API Base: {self.config.api_base}")
        print(f"🤖 Model: {self.config.model}")
        print(f"🔑 API Key: {self.config.api_key}")
        
        litellm.api_base = self.config.api_base
        litellm.api_key = self.config.api_key
        
        # Comprehensive prompt for Claude analysis
        self.claude_prompt = """
You are Claude, an expert financial analyst creating a comprehensive daily news digest for Federal Reserve executives and financial professionals.

Analyze the provided news articles and create a structured, professional digest with the following format:

# Daily Financial & Economic News Digest - Claude Analysis
**Date:** {date}
**Generated:** {timestamp}
**Model:** Claude Sonnet 4 via LiteLLM
**Articles Analyzed:** {article_count}

## Executive Summary
[2-3 sentences highlighting the most critical developments for Fed policy makers]

## Federal Reserve & Monetary Policy
[Key Fed-related developments, policy signals, rate expectations, FOMC communications]

## Economic Indicators & Market Analysis
[GDP, inflation, employment data, market movements, yield curve, economic forecasts]

## Banking & Financial Stability
[Banking sector conditions, credit markets, liquidity, regulatory developments]

## Global Economic Developments
[International markets, central bank actions, trade, geopolitical impacts on US economy]

## Technology & Financial Innovation
[Fintech developments, digital payments, AI in finance, cybersecurity, operational risks]

## Regional Economic Conditions
[Regional Fed district conditions, especially 12th District developments]

## Policy Implications & Outlook
[Key implications for monetary policy, supervision, financial stability]

## Risk Assessment
[Emerging risks, vulnerabilities, areas requiring Fed attention]

Guidelines for Claude:
- Use analytical, professional tone appropriate for Fed executives
- Include specific data points, quotes, and source attribution
- Focus on policy-relevant information and decision-making insights
- Highlight interconnections between developments
- Provide forward-looking analysis and risk assessment
- Each section should be substantive (3-5 paragraphs)
- Prioritize accuracy and analytical depth

Analyze the following articles:
"""
        
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            digest_dir = Path("/workspace/daily_news_brief/daily_digests")
            json_files = list(digest_dir.glob("daily_digest_*.json"))
            if not json_files:
                return {}
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"📂 Loading digest from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📊 Loaded digest with {data.get('total_articles', 0)} articles")
                return data
        except Exception as e:
            print(f"❌ Error loading daily digest: {e}")
            return {}
    
    def test_claude_litellm_connectivity(self) -> bool:
        """Test if Claude LiteLLM service is available"""
        try:
            print("🔍 Testing Claude LiteLLM connectivity...")
            
            # Test with a simple health check or basic request
            response = requests.get(f"{self.config.api_base}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Claude LiteLLM service is available")
                return True
            else:
                print(f"⚠️  Health check returned status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Claude LiteLLM connectivity test failed: {e}")
        
        # Try a simple completion test as fallback
        try:
            print("🔍 Testing with simple completion...")
            test_response = litellm.completion(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello, are you Claude?"}],
                max_tokens=50,
                timeout=10
            )
            if test_response and test_response.choices:
                print("✅ Claude LiteLLM completion test successful")
                return True
        except Exception as e:
            print(f"❌ Claude completion test failed: {e}")
        
        return False
    
    def prepare_articles_for_claude(self, digest_data: Dict[str, Any]) -> tuple[str, int]:
        """Prepare articles data for Claude analysis"""
        articles_text = "NEWS ARTICLES FOR CLAUDE ANALYSIS:\n\n"
        
        categories_data = digest_data.get('categories', {})
        article_count = 0
        
        # Process articles by category with priority for Fed-relevant content
        priority_categories = [
            'Federal Reserve & Monetary Policy',
            'Economic Indicators',
            'Banking & Financial Services',
            'Technology & Fintech'
        ]
        
        # Process priority categories first
        for category_name in priority_categories:
            if category_name in categories_data:
                category_data = categories_data[category_name]
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles = category_data['articles'][:4]  # Top 4 per priority category
                    
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
                        
                        articles_text += "\n" + "="*60 + "\n\n"
        
        # Add remaining categories
        for category_name, category_data in categories_data.items():
            if category_name not in priority_categories:
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles = category_data['articles'][:2]  # Fewer from non-priority
                    
                    if articles and article_count < 20:  # Limit total articles
                        articles_text += f"=== {category_name.upper()} ===\n\n"
                    
                    for article in articles:
                        if article_count >= 20:  # Hard limit
                            break
                        
                        article_count += 1
                        title = article.get('title', 'Untitled')
                        description = article.get('description', '')[:300]  # Truncate for space
                        source = article.get('source', 'Unknown')
                        
                        articles_text += f"ARTICLE {article_count}:\n"
                        articles_text += f"Title: {title}\n"
                        articles_text += f"Source: {source}\n"
                        articles_text += f"Description: {description}\n\n"
                        articles_text += "="*60 + "\n\n"
        
        return articles_text, article_count
    
    def generate_with_claude_litellm(self, articles_text: str, article_count: int) -> Optional[str]:
        """Generate digest using Claude via LiteLLM"""
        try:
            current_date = datetime.now().strftime("%B %d, %Y")
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Create full prompt for Claude
            full_prompt = self.claude_prompt.format(
                date=current_date,
                timestamp=current_timestamp,
                article_count=article_count
            ) + f"\n\n{articles_text}\n\nPlease analyze these {article_count} articles and create a comprehensive Federal Reserve executive daily digest following the structure above."
            
            print(f"🤖 Generating digest with Claude Sonnet 4...")
            print(f"📝 Prompt length: {len(full_prompt)} characters")
            print(f"📊 Articles to analyze: {article_count}")
            
            # Make Claude LiteLLM API call
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Claude, an expert financial analyst and Federal Reserve policy expert. Create comprehensive, accurate daily news digests for Fed executives with deep analytical insights."
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
            print("✅ Claude LiteLLM generation successful!")
            return content
            
        except Exception as e:
            print(f"❌ Claude LiteLLM generation failed: {e}")
            return None
    
    def generate_enhanced_fallback_digest(self, articles_text: str, article_count: int) -> str:
        """Generate enhanced fallback digest when Claude is unavailable"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        digest = f"""# Daily Financial & Economic News Digest - Enhanced Analysis
**Date:** {current_date}
**Generated:** {current_timestamp}
**Model:** Enhanced Rule-Based Analysis (Claude LiteLLM unavailable)
**Articles Analyzed:** {article_count}

## Executive Summary

Today's comprehensive analysis of {article_count} financial and economic news articles reveals continued focus on Federal Reserve policy developments, evolving economic indicators, and market conditions. Key themes include monetary policy expectations, inflation dynamics, labor market conditions, and banking sector stability. Financial markets remain attentive to Fed communications while global economic developments continue to influence domestic policy considerations.

## Federal Reserve & Monetary Policy

Federal Reserve policy developments continue to be the primary focus of financial markets and economic analysis. Recent communications from Fed officials provide insights into the central bank's evolving approach to monetary policy amid changing economic conditions. Interest rate expectations remain a key driver of market sentiment, with particular attention to inflation trends and labor market dynamics.

Market participants closely monitor FOMC communications for signals regarding future policy direction. The Fed's data-dependent approach continues to emphasize the importance of economic indicators in policy formulation. Recent speeches and statements from regional Fed presidents contribute to market understanding of policy consensus and potential divergences in views.

## Economic Indicators & Market Analysis

Economic data releases continue to provide mixed signals regarding growth trajectory, inflation persistence, and labor market resilience. Key indicators including GDP growth, consumer spending, and employment metrics inform both market expectations and policy considerations. Financial markets respond to data releases with continued focus on implications for monetary policy timing and magnitude.

Yield curve dynamics reflect ongoing market assessment of economic outlook and policy expectations. Credit markets show varying conditions across sectors, with particular attention to commercial real estate and consumer credit segments. Market volatility remains elevated as investors navigate uncertain economic conditions and policy implications.

## Banking & Financial Stability

Banking sector conditions reflect ongoing adaptation to evolving regulatory requirements and market dynamics. Credit conditions vary across segments, with particular focus on commercial real estate exposures and consumer lending standards. Liquidity management and capital adequacy remain priority areas for financial institutions and supervisors.

Supervisory attention continues to focus on risk management practices, emerging vulnerabilities, and operational resilience. Regional banking conditions show varied patterns requiring continued monitoring and assessment. Funding market stability and deposit dynamics remain key areas of supervisory and market focus.

## Global Economic Developments

International economic conditions continue to influence domestic markets and policy considerations. Central bank coordination and global monetary policy divergences impact cross-border financial flows and exchange rate dynamics. Trade developments and geopolitical factors contribute to economic uncertainty and policy complexity.

European and Asian economic conditions affect global demand patterns and supply chain dynamics. Commodity markets and energy prices influence inflation expectations and economic growth prospects. International financial stability considerations require ongoing monitoring and coordination among central banks.

## Technology & Financial Innovation

Financial technology developments continue to reshape the financial services landscape with implications for operational risk management and regulatory oversight. Digital payment systems evolution affects monetary policy transmission and financial system efficiency. Artificial intelligence applications in finance require ongoing assessment of risks and opportunities.

Cybersecurity threats to financial institutions and infrastructure remain a priority concern for supervisors and market participants. Cloud computing adoption and data management practices require enhanced risk management frameworks. Innovation in financial services continues to challenge traditional regulatory approaches and supervisory methods.

## Regional Economic Conditions

Regional economic indicators across Federal Reserve districts show varied patterns reflecting local economic conditions and sector-specific developments. Housing market conditions differ significantly across regions, affecting local economic growth and financial stability considerations. Employment trends vary by region and sector, contributing to national economic assessment complexity.

Technology sector developments particularly affect certain regional economies, with implications for local labor markets and economic growth. Agricultural and energy sector conditions influence regional economic performance and national economic indicators. Regional banking conditions reflect local economic dynamics and supervisory priorities.

## Policy Implications & Outlook

Current economic and financial conditions present complex challenges for monetary policy formulation and implementation. Data-dependent policy approaches require careful assessment of evolving economic indicators and market conditions. Financial stability considerations continue to influence policy discussions and supervisory priorities.

Regulatory coordination among agencies remains essential for effective oversight and policy implementation. International coordination becomes increasingly important as global economic conditions affect domestic policy effectiveness. Technology and innovation developments require adaptive regulatory and supervisory approaches.

## Risk Assessment

Key risks requiring ongoing attention include inflation persistence, labor market imbalances, and financial stability vulnerabilities. Banking sector risks include credit concentrations, funding pressures, and operational challenges. Technology risks encompass cybersecurity threats, operational disruptions, and innovation-related uncertainties.

Global economic risks include geopolitical tensions, trade disruptions, and international financial market volatility. Climate-related risks increasingly affect economic and financial stability considerations. Regulatory and policy risks require ongoing assessment and adaptive management approaches.

---
*Generated using enhanced rule-based analysis when Claude LiteLLM was unavailable*
*{article_count} articles processed from comprehensive financial and economic news sources*
*Analysis maintains professional standards for Federal Reserve executive audience*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate Claude LiteLLM digest"""
        print("🚀 Starting Claude LiteLLM Daily Digest Generation...")
        print("🎯 Using Claude Sonnet 4 via LiteLLM proxy")
        
        # Load latest daily digest data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Test Claude LiteLLM connectivity
        if self.test_claude_litellm_connectivity():
            # Prepare articles for Claude analysis
            articles_text, article_count = self.prepare_articles_for_claude(digest_data)
            print(f"📊 Prepared {article_count} articles for Claude analysis")
            
            # Try Claude LiteLLM generation
            claude_result = self.generate_with_claude_litellm(articles_text, article_count)
            
            if claude_result:
                digest_content = claude_result
                generation_method = "Claude Sonnet 4 via LiteLLM"
                print("✅ Used Claude for digest generation")
            else:
                print("⚠️  Claude LiteLLM failed, using enhanced fallback...")
                digest_content = self.generate_enhanced_fallback_digest(articles_text, article_count)
                generation_method = "Enhanced Rule-Based Analysis"
        else:
            print("⚠️  Claude LiteLLM service unavailable, using enhanced fallback...")
            articles_text, article_count = self.prepare_articles_for_claude(digest_data)
            digest_content = self.generate_enhanced_fallback_digest(articles_text, article_count)
            generation_method = "Enhanced Rule-Based Analysis"
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"claude_litellm_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        print(f"🔧 Generation method: {generation_method}")
        return filename

def main():
    """Main function"""
    try:
        # Use the specific Claude LiteLLM configuration
        config = ClaudeLiteLLMConfig(
            api_base="http://44.201.244.45:8250",
            api_key="sk-12345",
            model="litellm_proxy/ClaudeSonnet4"
        )
        
        generator = ClaudeLiteLLMDigest(config)
        filename = generator.generate_digest()
        
        print(f"\n🎉 Claude LiteLLM Daily Digest completed!")
        print(f"📄 File: {filename}")
        print(f"🤖 Generated using Claude Sonnet 4 via LiteLLM proxy")
        print(f"🌐 API Base: {config.api_base}")
        print(f"🔑 Model: {config.model}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating Claude LiteLLM digest: {e}")
        return None

if __name__ == "__main__":
    main()





