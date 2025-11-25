
#!/usr/bin/env python3
"""
Enhanced LiteLLM Daily Digest Generator with Multiple Fallback Options
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import litellm
from dataclasses import dataclass

# Enhanced inline prompt for Federal Reserve Executive Daily News Digest
ENHANCED_INLINE_PROMPT = """
Create a comprehensive Federal Reserve Executive Daily News Digest from the provided articles.

STRUCTURE REQUIRED:

# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {date}
**Generated:** {timestamp}
**Total Articles Analyzed:** {total_articles}

## 1. Top 5 Headlines Relevant to the Federal Reserve
[Select most Fed-relevant articles with titles, sources, and 2-3 sentence summaries]

## 2. 12th District Regional Economic & Labor Signals
*California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada*
[Regional economic developments affecting SF Fed district]

## 3. National Macroeconomic & Monetary Policy Developments
*Inflation, labor markets, GDP, productivity, FOMC outlook*
[Key economic indicators and policy implications]

## 4. Financial System & Banking Stability Watch
*Bank liquidity/capital, CRE exposures, funding markets, credit spreads*
[Banking sector health and stability signals]

## 5. Global & Pacific Rim Insights (SF Fed Priority)
*China, Japan, Korea, ASEAN, international central bank actions*
[International developments affecting US monetary policy]

## 6. Technology, Cyber, and Payments Developments
*Cyber threats, AI risks, fintech, FedNow, digital assets*
[Technology risks and innovations in financial services]

## 7. Regulatory, Legislative, and Federal Government Updates
*Congress, Treasury, CFPB, FDIC, OCC*
[Policy and regulatory developments]

## 8. Implications for SF Fed
• [5-7 specific bullet points covering monetary policy, supervision, regional monitoring, payments, and financial stability]

## 9. Executive Summary (<150 words)
[Concise overview of key developments and implications]

GUIDELINES:
- Focus on policy-relevant information
- Include specific data points and quotes
- Maintain analytical, factual tone
- Prioritize Fed decision-making relevance
"""

class EnhancedLiteLLMDigest:
    """Enhanced LiteLLM digest generator with multiple fallback options"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.litellm_configs = [
            {
                "api_base": "http://13.221.86.203:8250",
                "api_key": "sk-12345",
                "model": "gpt-4o-mini"
            },
            {
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv('OPENAI_API_KEY', 'sk-test'),
                "model": "gpt-3.5-turbo"
            },
            {
                "model": "ollama/llama2",  # Local model fallback
                "api_base": "http://localhost:11434"
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
    
    def prepare_articles_summary(self, digest_data: Dict[str, Any]) -> tuple[str, int]:
        """Prepare a concise articles summary for LLM analysis"""
        articles_summary = "ARTICLES FOR ANALYSIS:\n\n"
        
        categories_data = digest_data.get('categories', {})
        article_count = 0
        
        # Prioritize Fed-relevant categories
        priority_categories = [
            'Federal Reserve & Monetary Policy',
            'Economic Indicators',
            'Banking & Financial Services',
            'Technology & Fintech'
        ]
        
        # Process priority categories first
        for priority_cat in priority_categories:
            if priority_cat in categories_data:
                category_data = categories_data[priority_cat]
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles = category_data['articles'][:3]  # Top 3 per priority category
                    
                    for article in articles:
                        article_count += 1
                        title = article.get('title', 'Untitled')
                        description = article.get('description', '')[:200]  # Truncate
                        source = article.get('source', 'Unknown')
                        
                        articles_summary += f"{article_count}. {title}\n"
                        articles_summary += f"   Source: {source}\n"
                        articles_summary += f"   Summary: {description}\n"
                        
                        # Add key highlights if available
                        highlights = article.get('highlights', [])
                        if highlights:
                            articles_summary += f"   Key Points: {highlights[0]}\n"
                        
                        articles_summary += "\n"
        
        # Add remaining articles from other categories
        for category_name, category_data in categories_data.items():
            if category_name not in priority_categories:
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles = category_data['articles'][:2]  # Fewer from non-priority
                    
                    for article in articles:
                        if article_count >= 15:  # Limit total articles
                            break
                        
                        article_count += 1
                        title = article.get('title', 'Untitled')
                        description = article.get('description', '')[:150]
                        source = article.get('source', 'Unknown')
                        
                        articles_summary += f"{article_count}. {title}\n"
                        articles_summary += f"   Source: {source}\n"
                        articles_summary += f"   Summary: {description}\n\n"
        
        return articles_summary, article_count
    
    def try_litellm_generation(self, prompt: str) -> Optional[str]:
        """Try multiple LiteLLM configurations"""
        for i, config in enumerate(self.litellm_configs):
            try:
                print(f"Trying LiteLLM configuration {i+1}...")
                
                # Configure LiteLLM
                if "api_base" in config:
                    litellm.api_base = config["api_base"]
                if "api_key" in config:
                    litellm.api_key = config["api_key"]
                
                # Make API call
                response = litellm.completion(
                    model=config["model"],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Federal Reserve analyst. Create comprehensive, accurate daily news digests for Fed executives."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2500,
                    temperature=0.1,
                    timeout=30
                )
                
                content = response.choices[0].message.content
                print(f"✅ Successfully generated digest with configuration {i+1}")
                return content
                
            except Exception as e:
                print(f"❌ Configuration {i+1} failed: {e}")
                continue
        
        return None
    
    def generate_rule_based_digest(self, articles_summary: str, article_count: int) -> str:
        """Generate a comprehensive rule-based digest when LLM fails"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Parse articles to extract key themes
        fed_articles = []
        economic_articles = []
        banking_articles = []
        tech_articles = []
        
        lines = articles_summary.split('\n')
        current_article = {}
        
        for line in lines:
            if line.strip() and line[0].isdigit():
                if current_article:
                    # Categorize previous article
                    title_lower = current_article.get('title', '').lower()
                    if any(word in title_lower for word in ['fed', 'federal reserve', 'monetary', 'rate']):
                        fed_articles.append(current_article)
                    elif any(word in title_lower for word in ['economy', 'inflation', 'jobs', 'gdp']):
                        economic_articles.append(current_article)
                    elif any(word in title_lower for word in ['bank', 'credit', 'financial']):
                        banking_articles.append(current_article)
                    elif any(word in title_lower for word in ['tech', 'ai', 'cyber', 'digital']):
                        tech_articles.append(current_article)
                
                # Start new article
                current_article = {'title': line.split('. ', 1)[1] if '. ' in line else line}
            elif line.strip().startswith('Source:'):
                current_article['source'] = line.replace('Source:', '').strip()
            elif line.strip().startswith('Summary:'):
                current_article['summary'] = line.replace('Summary:', '').strip()
        
        # Add last article
        if current_article:
            title_lower = current_article.get('title', '').lower()
            if any(word in title_lower for word in ['fed', 'federal reserve', 'monetary', 'rate']):
                fed_articles.append(current_article)
            elif any(word in title_lower for word in ['economy', 'inflation', 'jobs', 'gdp']):
                economic_articles.append(current_article)
        
        # Generate structured digest
        digest = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {current_date}
**Generated:** {current_timestamp}
**Total Articles Analyzed:** {article_count}

## 1. Top 5 Headlines Relevant to the Federal Reserve

"""
        
        # Add Fed-relevant articles
        for i, article in enumerate(fed_articles[:5], 1):
            digest += f"**{i}. {article.get('title', 'Untitled')}**\n"
            digest += f"*Source: {article.get('source', 'Unknown')}*\n"
            digest += f"• {article.get('summary', 'Federal Reserve policy development')}\n"
            digest += f"• Market implications and policy considerations under review\n"
            digest += f"• Continued monitoring of economic indicators warranted\n\n"
        
        digest += """## 2. 12th District Regional Economic & Labor Signals
*California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada*

"""
        
        # Add regional economic content
        for article in economic_articles[:3]:
            if any(state in article.get('title', '').lower() for state in ['california', 'washington', 'oregon']):
                digest += f"• **{article.get('title', 'Regional Development')}** - {article.get('summary', 'Regional economic indicator')}\n"
        
        if not any(state in str(economic_articles).lower() for state in ['california', 'washington', 'oregon']):
            digest += "• Regional economic indicators show continued monitoring of labor market conditions\n"
            digest += "• Housing market trends require ongoing assessment\n"
            digest += "• Technology sector developments impact regional employment\n"
        
        digest += """

## 3. National Macroeconomic & Monetary Policy Developments
*Inflation, labor markets, GDP, productivity, FOMC outlook*

"""
        
        # Add economic policy content
        for article in economic_articles[:4]:
            digest += f"• **{article.get('title', 'Economic Development')}** - {article.get('summary', 'Economic indicator update')}\n"
        
        digest += """

## 4. Financial System & Banking Stability Watch
*Bank liquidity/capital, CRE exposures, funding markets, credit spreads*

"""
        
        # Add banking content
        for article in banking_articles[:3]:
            digest += f"• **{article.get('title', 'Banking Development')}** - {article.get('summary', 'Banking sector update')}\n"
        
        if not banking_articles:
            digest += "• Banking sector conditions require continued supervisory attention\n"
            digest += "• Credit market stability remains a monitoring priority\n"
        
        digest += """

## 5. Global & Pacific Rim Insights (SF Fed Priority)
*China, Japan, Korea, ASEAN, international central bank actions*

• International monetary policy coordination continues
• Global trade developments impact domestic economic conditions
• Cross-border financial flows require ongoing assessment

## 6. Technology, Cyber, and Payments Developments
*Cyber threats, AI risks, fintech, FedNow, digital assets*

"""
        
        # Add tech content
        for article in tech_articles[:3]:
            digest += f"• **{article.get('title', 'Technology Development')}** - {article.get('summary', 'Technology sector update')}\n"
        
        if not tech_articles:
            digest += "• Cybersecurity threats to financial system require vigilance\n"
            digest += "• Digital payment innovations continue to evolve\n"
        
        digest += """

## 7. Regulatory, Legislative, and Federal Government Updates
*Congress, Treasury, CFPB, FDIC, OCC*

• Regulatory developments require ongoing coordination
• Legislative initiatives may impact monetary policy implementation
• Inter-agency collaboration remains essential

## 8. Implications for SF Fed

• **Monetary Policy:** Current economic signals warrant continued assessment of inflation trajectory and labor market dynamics
• **Bank Supervision:** Regional banking conditions require enhanced monitoring of credit exposures and funding stability
• **Regional Economic Monitoring:** 12th District indicators show evolving conditions requiring continued surveillance
• **Payments & Technology Operations:** Technology developments necessitate ongoing operational risk management
• **Financial Stability:** Market conditions require continued assessment of systemic risks and vulnerabilities

## 9. Executive Summary (<150 words)

Today's digest analyzes {article_count} articles across Federal Reserve priority areas. Key developments include monetary policy considerations, regional economic signals, and banking sector conditions. Federal Reserve policy remains focused on inflation management and labor market stability. Regional economic monitoring continues across the 12th District with attention to housing, employment, and technology sector developments. Banking supervision priorities include credit risk assessment and funding market stability. Technology and payments evolution requires ongoing operational readiness. Regulatory coordination with other agencies remains essential for effective policy implementation. Overall economic conditions warrant continued vigilance and data-dependent policy approaches.

---
*Generated by Enhanced LiteLLM Daily Digest Generator (Rule-Based Analysis)*
*{article_count} articles analyzed from multiple financial and economic news sources*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Generate the complete digest using LiteLLM or fallback"""
        print("🚀 Starting Enhanced LiteLLM Daily Digest Generation...")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Prepare articles
        articles_summary, article_count = self.prepare_articles_summary(digest_data)
        print(f"📊 Prepared {article_count} articles for analysis")
        
        # Create prompt
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        full_prompt = ENHANCED_INLINE_PROMPT.format(
            date=current_date,
            timestamp=current_timestamp,
            total_articles=article_count
        ) + f"\n\n{articles_summary}\n\nGenerate the Federal Reserve Executive Daily News Digest following the exact structure above."
        
        # Try LiteLLM generation
        print("🤖 Attempting LiteLLM generation...")
        llm_result = self.try_litellm_generation(full_prompt)
        
        if llm_result:
            digest_content = llm_result
            print("✅ Successfully generated digest with LiteLLM")
        else:
            print("⚠️  LiteLLM failed, using enhanced rule-based generation...")
            digest_content = self.generate_rule_based_digest(articles_summary, article_count)
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"enhanced_litellm_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        return filename

def main():
    """Main function"""
    try:
        generator = EnhancedLiteLLMDigest()
        filename = generator.generate_digest()
        
        print(f"\n🎉 Enhanced LiteLLM Daily Digest completed!")
        print(f"📄 File: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    main()

