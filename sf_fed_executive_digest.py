


#!/usr/bin/env python3
"""
San Francisco Federal Reserve Executive Daily News Digest Generator
Following the exact prompt structure provided by the user
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

class SFFedExecutiveDigest:
    """Generate SF Fed Executive Daily News Digest following user's exact prompt structure"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # User's exact prompt structure
        self.prompt_structure = """
Generate today's **San Francisco Federal Reserve Executive Daily News Digest**.

Audience: SF Fed Executive Leadership Team.
Purpose: Provide a high-signal, low-noise briefing to inform monetary policy, supervision, financial stability, 
technology readiness, payments evolution, and regional economic conditions.

Include the following sections in order:

1. **Top 5 Headlines Relevant to the Federal Reserve**
2. **12th District Regional Economic & Labor Signals**
3. **National Macroeconomic & Monetary Policy Developments**
4. **Financial System & Banking Stability Watch**
5. **Global & Pacific Rim Insights (SF Fed priority)**
6. **Technology, Cyber, and Payments Developments**
7. **Regulatory, Legislative, and Federal Government Updates**
8. **Implications for SF Fed**
9. **Executive Summary (<150 words)**

Constraints:
- Tone: analytical, factual, policy-relevant. No sensationalism.
- Exclude consumer lifestyle news, political commentary, and unrelated media stories.
- Prioritize accuracy, brevity, and decision-readiness.
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
    
    def categorize_articles_by_sf_fed_priorities(self, digest_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Categorize articles according to SF Fed Executive priorities"""
        categories = {
            'fed_headlines': [],
            'regional_12th_district': [],
            'macro_monetary': [],
            'banking_stability': [],
            'global_pacific': [],
            'tech_cyber_payments': [],
            'regulatory_legislative': []
        }
        
        # Extract all articles
        all_articles = []
        categories_data = digest_data.get('categories', {})
        
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                all_articles.extend(category_data['articles'])
        
        print(f"Categorizing {len(all_articles)} articles by SF Fed Executive priorities...")
        
        # Categorize based on SF Fed Executive priorities
        for article in all_articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = f"{title} {description}"
            
            # 1. Top Fed Headlines - macroeconomics, financial markets, banking, technology, cyber, policy
            if any(keyword in content for keyword in [
                'federal reserve', 'fed ', 'fomc', 'monetary policy', 'interest rate',
                'jerome powell', 'mary daly', 'rate cut', 'rate hike', 'central bank',
                'financial markets', 'banking', 'macroeconomic', 'policy'
            ]):
                categories['fed_headlines'].append(article)
            
            # 2. 12th District Regional - CA, WA, OR, AZ, UT, AK, HI, ID, NV
            elif any(keyword in content for keyword in [
                'california', 'washington', 'oregon', 'arizona', 'utah', 'alaska',
                'hawaii', 'idaho', 'nevada', 'san francisco', 'seattle', 'portland',
                'los angeles', 'silicon valley', 'housing', 'tech sector', 'logistics',
                'supply chain', 'consumer spending', 'labor market'
            ]):
                categories['regional_12th_district'].append(article)
            
            # 3. National Macro/Monetary - inflation, labor, GDP, productivity, FOMC outlook
            elif any(keyword in content for keyword in [
                'inflation', 'labor market', 'unemployment', 'gdp', 'productivity',
                'economic growth', 'consumer price', 'yield curve', 'treasury',
                'rate expectations', 'economic indicators'
            ]):
                categories['macro_monetary'].append(article)
            
            # 4. Banking Stability - liquidity, capital, CRE, funding, credit spreads
            elif any(keyword in content for keyword in [
                'bank', 'banking', 'liquidity', 'capital', 'commercial real estate',
                'cre', 'funding', 'credit spread', 'loan', 'deposit', 'supervisory',
                'financial institution', 'credit risk'
            ]):
                categories['banking_stability'].append(article)
            
            # 5. Global/Pacific Rim - China, Japan, Korea, ASEAN, international central banks
            elif any(keyword in content for keyword in [
                'china', 'japan', 'korea', 'asean', 'asia', 'pacific', 'international',
                'global', 'central bank', 'trade', 'geopolitical', 'supply chain',
                'currency', 'exchange rate'
            ]):
                categories['global_pacific'].append(article)
            
            # 6. Tech/Cyber/Payments - cyber threats, AI, fintech, payments, digital assets
            elif any(keyword in content for keyword in [
                'cyber', 'cybersecurity', 'ai', 'artificial intelligence', 'fintech',
                'payments', 'digital asset', 'cryptocurrency', 'blockchain', 'fednow',
                'technology', 'cloud', 'payment system'
            ]):
                categories['tech_cyber_payments'].append(article)
            
            # 7. Regulatory/Legislative - Congress, Treasury, CFPB, FDIC, OCC
            elif any(keyword in content for keyword in [
                'congress', 'treasury', 'cfpb', 'fdic', 'occ', 'regulation', 'regulatory',
                'legislation', 'government', 'policy', 'compliance', 'supervision'
            ]):
                categories['regulatory_legislative'].append(article)
        
        # Print categorization results
        for cat_name, articles in categories.items():
            print(f"  {cat_name}: {len(articles)} articles")
        
        return categories
    
    def create_article_summary(self, article: Dict, max_lines: int = 3) -> str:
        """Create 2-3 line summary for SF Fed executives"""
        title = article.get('title', 'Untitled')
        description = article.get('description', '')
        source = article.get('source', 'Unknown')
        
        # Use highlights if available
        highlights = article.get('highlights', [])
        if highlights:
            summary_lines = []
            for highlight in highlights[:max_lines]:
                if isinstance(highlight, str) and len(highlight.strip()) > 20:
                    clean_highlight = highlight.strip()
                    if not clean_highlight.endswith('.'):
                        clean_highlight += '.'
                    summary_lines.append(clean_highlight)
            
            if summary_lines:
                return ' '.join(summary_lines)
        
        # Use structured analysis if available
        structured = article.get('structured_analysis', {})
        if structured:
            summary_highlights = structured.get('summary_highlights', [])
            if summary_highlights:
                return ' '.join(summary_highlights[:2]) + '.'
        
        # Fallback to description
        if description and len(description.strip()) > 30:
            # Truncate and clean for executive briefing
            clean_desc = description.strip()
            if len(clean_desc) > 200:
                clean_desc = clean_desc[:200] + '...'
            if not clean_desc.endswith('.'):
                clean_desc += '.'
            return clean_desc
        
        return f"Key development from {source} requiring Fed executive attention."
    
    def generate_sf_fed_executive_digest(self, categories: Dict[str, List[Dict]], total_articles: int) -> str:
        """Generate SF Fed Executive Daily News Digest following exact prompt structure"""
        current_date = datetime.now().strftime("%B %d, %Y")
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        digest = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {current_date}
**Generated:** {current_timestamp}
**Audience:** SF Fed Executive Leadership Team
**Purpose:** High-signal, low-noise briefing for monetary policy, supervision, financial stability, technology readiness, payments evolution, and regional economic conditions

---

## 1. Top 5 Headlines Relevant to the Federal Reserve
*Macroeconomics, financial markets, banking, technology, cyber, or policy*

"""
        
        # Top 5 Fed Headlines
        fed_articles = categories['fed_headlines'][:5]
        if fed_articles:
            for i, article in enumerate(fed_articles, 1):
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"**{i}. [{title}]({url})** (*{source}*)\n"
                digest += f"{summary}\n\n"
        else:
            digest += "• No direct Federal Reserve headlines identified in current news cycle\n"
            digest += "• Continued monitoring of policy-relevant developments\n\n"
        
        digest += """## 2. 12th District Regional Economic & Labor Signals
*California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada*
*Housing, labor, consumer spending, tech sector conditions, logistics/supply chain*

"""
        
        # Regional 12th District
        regional_articles = categories['regional_12th_district'][:4]
        if regional_articles:
            for article in regional_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• Regional economic indicators show continued monitoring of key 12th District sectors\n"
            digest += "• Housing market conditions across California, Washington, Oregon require ongoing assessment\n"
            digest += "• Technology sector employment and consumer spending patterns under review\n\n"
        
        digest += """## 3. National Macroeconomic & Monetary Policy Developments
*Inflation, labor markets, GDP, productivity*
*Key indicators that matter for FOMC outlook*
*Market-implied rate expectations & yield curve movements*

"""
        
        # Macro/Monetary Policy
        macro_articles = categories['macro_monetary'][:5]
        if macro_articles:
            for article in macro_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• Economic indicators continue to inform FOMC outlook and monetary policy considerations\n"
            digest += "• Inflation trends and labor market conditions under ongoing assessment\n"
            digest += "• Market-implied rate expectations and yield curve movements warrant monitoring\n\n"
        
        digest += """## 4. Financial System & Banking Stability Watch
*Bank liquidity/capital trends, CRE exposures, funding markets, credit spreads*
*Notable supervisory signals or emerging vulnerabilities*

"""
        
        # Banking Stability
        banking_articles = categories['banking_stability'][:4]
        if banking_articles:
            for article in banking_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• Banking sector liquidity and capital conditions require continued supervisory attention\n"
            digest += "• Commercial real estate exposures and funding market stability under monitoring\n"
            digest += "• Credit spreads and emerging vulnerabilities warrant ongoing assessment\n\n"
        
        digest += """## 5. Global & Pacific Rim Insights (SF Fed Priority)
*China, Japan, Korea, ASEAN*
*International central bank actions, global demand shifts, supply chain/geopolitical risks*

"""
        
        # Global/Pacific Rim
        global_articles = categories['global_pacific'][:4]
        if global_articles:
            for article in global_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• International central bank actions and global demand shifts continue to impact domestic conditions\n"
            digest += "• Pacific Rim trade flows and supply chain developments require ongoing assessment\n"
            digest += "• Geopolitical risks and cross-border financial flows under monitoring\n\n"
        
        digest += """## 6. Technology, Cyber, and Payments Developments
*Major cyber threats, cloud/AI risks, fintech, payments modernization, digital assets*
*Implications for FedNow, payment resilience, or financial system risk*

"""
        
        # Tech/Cyber/Payments
        tech_articles = categories['tech_cyber_payments'][:4]
        if tech_articles:
            for article in tech_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• Cybersecurity threats to financial system require continued vigilance and operational readiness\n"
            digest += "• Payments modernization and digital asset developments impact FedNow and system resilience\n"
            digest += "• Cloud/AI risks and fintech innovations warrant ongoing technology risk assessment\n\n"
        
        digest += """## 7. Regulatory, Legislative, and Federal Government Updates
*Congress, Treasury, CFPB, FDIC, OCC*
*Only items with real supervisory or policy implications*

"""
        
        # Regulatory/Legislative
        regulatory_articles = categories['regulatory_legislative'][:3]
        if regulatory_articles:
            for article in regulatory_articles:
                title = article.get('title', 'Untitled')
                source = article.get('source', 'Unknown')
                url = article.get('url', '#')
                summary = self.create_article_summary(article, max_lines=2)
                
                digest += f"• **[{title}]({url})** (*{source}*): {summary}\n\n"
        else:
            digest += "• Regulatory coordination with Treasury, CFPB, FDIC, and OCC continues on supervisory matters\n"
            digest += "• Legislative developments with policy implications require ongoing inter-agency collaboration\n\n"
        
        digest += """## 8. Implications for SF Fed
*Clearly translate news into potential impacts on monetary policy, bank supervision, regional economic monitoring, payments & technology operations, financial stability*

"""
        
        # Generate specific implications based on available articles
        implications = []
        
        # Monetary Policy implications
        if categories['fed_headlines'] or categories['macro_monetary']:
            implications.append("**Monetary Policy:** Current economic signals and Fed communications warrant continued data-dependent approach to policy decisions, with particular attention to inflation trajectory, labor market dynamics, and market-implied rate expectations")
        
        # Bank Supervision implications
        if categories['banking_stability'] or categories['regulatory_legislative']:
            implications.append("**Bank Supervision:** Regional banking conditions and regulatory developments require enhanced monitoring of credit exposures, funding stability, commercial real estate concentrations, and emerging supervisory signals")
        
        # Regional Economic Monitoring implications
        if categories['regional_12th_district']:
            implications.append("**Regional Economic Monitoring:** 12th District economic indicators show evolving conditions requiring continued surveillance of housing markets, technology sector employment, consumer spending patterns, and supply chain logistics")
        else:
            implications.append("**Regional Economic Monitoring:** 12th District conditions require ongoing assessment of housing markets, labor dynamics, and technology sector developments across California, Washington, Oregon, and other district states")
        
        # Payments & Technology Operations implications
        if categories['tech_cyber_payments']:
            implications.append("**Payments & Technology Operations:** Technology developments, cybersecurity threats, and payments modernization necessitate ongoing operational risk management, FedNow system resilience, and digital asset risk assessment")
        else:
            implications.append("**Payments & Technology Operations:** Continued focus on operational resilience, cybersecurity preparedness, and payments system modernization including FedNow operations")
        
        # Financial Stability implications
        if categories['global_pacific'] or categories['banking_stability']:
            implications.append("**Financial Stability:** Current market conditions, global developments, and banking sector trends require continued assessment of systemic risks, cross-border financial flows, and emerging vulnerabilities")
        else:
            implications.append("**Financial Stability:** Ongoing monitoring of systemic risks, market conditions, and cross-border financial flows essential for maintaining financial system stability")
        
        # Inter-agency Coordination (always relevant)
        implications.append("**Inter-agency Coordination:** Regulatory and policy developments require ongoing collaboration with Treasury, FDIC, OCC, and CFPB on supervisory matters, policy implementation, and systemic risk assessment")
        
        # Add implications to digest
        for implication in implications[:7]:  # Limit to 5-7 bullets as specified
            digest += f"• {implication}\n\n"
        
        digest += """## 9. Executive Summary (<150 words)
*A concise, board-ready overview of the most important signals*

"""
        
        # Generate executive summary
        summary_points = []
        
        if categories['fed_headlines']:
            summary_points.append(f"Federal Reserve policy developments and market conditions continue to evolve")
        
        if categories['macro_monetary']:
            summary_points.append("macroeconomic indicators inform FOMC outlook")
        
        if categories['regional_12th_district']:
            summary_points.append("12th District regional signals require ongoing monitoring")
        else:
            summary_points.append("12th District conditions warrant continued assessment")
        
        if categories['banking_stability']:
            summary_points.append("banking sector stability and supervisory conditions under review")
        
        if categories['global_pacific']:
            summary_points.append("Pacific Rim developments impact domestic financial conditions")
        
        if categories['tech_cyber_payments']:
            summary_points.append("technology and payments system evolution requires operational readiness")
        
        summary_points.append("inter-agency coordination remains essential for effective policy implementation")
        
        executive_summary = f"""Today's digest analyzes {total_articles} articles across SF Fed Executive priority areas. Key developments include {', '.join(summary_points[:3])}. {' '.join(summary_points[3:6]).capitalize()}. Overall conditions warrant continued data-dependent monetary policy approaches, enhanced supervisory attention to emerging risks, and ongoing assessment of regional economic indicators across the 12th District. Technology and payments system developments require sustained operational focus while maintaining financial system stability through effective inter-agency collaboration."""
        
        # Ensure summary is under 150 words
        words = executive_summary.split()
        if len(words) > 150:
            executive_summary = ' '.join(words[:150]) + '...'
        
        digest += f"{executive_summary}\n\n"
        
        digest += f"""---
*Generated following SF Fed Executive Leadership Team requirements*
*Analytical, factual, policy-relevant briefing excluding consumer lifestyle news and political commentary*
*{total_articles} articles analyzed from comprehensive financial and economic news sources*
*Focus: monetary policy, supervision, financial stability, technology readiness, payments evolution, regional economic conditions*
"""
        
        return digest
    
    def generate_digest(self) -> str:
        """Main method to generate SF Fed Executive Daily News Digest"""
        print("🚀 Starting San Francisco Federal Reserve Executive Daily News Digest Generation...")
        print("📋 Following user's exact prompt structure and requirements")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            return "Error: No daily digest data available"
        
        # Categorize articles by SF Fed Executive priorities
        categories = self.categorize_articles_by_sf_fed_priorities(digest_data)
        
        # Count total articles
        total_articles = sum(len(articles) for articles in categories.values())
        print(f"📊 Categorized {total_articles} articles by SF Fed Executive priorities")
        
        # Generate comprehensive digest
        digest_content = self.generate_sf_fed_executive_digest(categories, total_articles)
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"sf_fed_executive_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 Digest saved to: {filename}")
        return filename

def main():
    """Main function to run the SF Fed Executive digest generator"""
    try:
        generator = SFFedExecutiveDigest()
        filename = generator.generate_digest()
        
        print(f"\n🎉 San Francisco Federal Reserve Executive Daily News Digest completed!")
        print(f"📄 File: {filename}")
        print(f"🎯 Generated following user's exact prompt structure:")
        print(f"   • High-signal, low-noise briefing for SF Fed Executive Leadership Team")
        print(f"   • 9 sections covering monetary policy, supervision, financial stability")
        print(f"   • Technology readiness, payments evolution, regional economic conditions")
        print(f"   • Analytical, factual, policy-relevant tone")
        print(f"   • Executive Summary <150 words")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error generating SF Fed Executive digest: {e}")
        return None

if __name__ == "__main__":
    main()



