#!/usr/bin/env python3
"""
San Francisco Federal Reserve Executive Daily News Digest Generator
Integrates with the existing daily_news_brief system to generate executive-level briefings
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from news_aggregator import NewsAggregator, LLMService
import re

class SFFedDigestGenerator:
    """Generate SF Fed Executive Daily News Digest using existing news aggregation system"""
    
    def __init__(self, llm_provider: str = "auto", llm_api_key: Optional[str] = None):
        # Initialize the existing news aggregator
        self.aggregator = NewsAggregator(llm_provider=llm_provider, llm_api_key=llm_api_key)
        
        # SF Fed specific keywords for enhanced filtering
        self.sf_fed_keywords = [
            # Federal Reserve & Monetary Policy
            'federal reserve', 'fed', 'fomc', 'jerome powell', 'monetary policy', 'interest rates',
            'fed chair', 'fed governor', 'fed official', 'fed policy', 'fed meeting', 'fed minutes',
            
            # 12th District Regional Focus
            'california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada',
            'san francisco fed', '12th district', 'west coast', 'pacific', 'silicon valley',
            
            # Economic Indicators
            'inflation', 'unemployment', 'gdp', 'productivity', 'labor market', 'employment',
            'housing market', 'consumer spending', 'supply chain', 'logistics',
            
            # Financial System & Banking
            'banking', 'financial stability', 'credit', 'liquidity', 'capital', 'stress test',
            'commercial real estate', 'cre', 'funding markets', 'credit spreads',
            
            # Technology & Payments
            'fintech', 'digital payments', 'fednow', 'cbdc', 'cryptocurrency', 'blockchain',
            'cyber security', 'cloud computing', 'artificial intelligence', 'ai risk',
            
            # Global & Pacific Rim
            'china', 'japan', 'korea', 'asean', 'trade war', 'tariffs', 'supply chain',
            'geopolitical', 'international trade', 'central bank',
            
            # Regulatory & Legislative
            'cfpb', 'fdic', 'occ', 'treasury', 'congress', 'regulation', 'supervision'
        ]
        
        # 12th District states for regional analysis
        self.district_states = [
            'california', 'washington', 'oregon', 'arizona', 'utah', 
            'alaska', 'hawaii', 'idaho', 'nevada'
        ]
        
    def collect_sf_fed_articles(self, target_date: datetime = None) -> Dict[str, Any]:
        """Collect articles relevant to SF Fed priorities"""
        if target_date is None:
            target_date = datetime.now()
            
        print("Collecting articles for SF Fed Executive Digest...")
        
        # Update aggregator keywords with SF Fed specific terms
        self.aggregator.keywords.extend(self.sf_fed_keywords)
        self.aggregator.keywords = list(set(self.aggregator.keywords))  # Remove duplicates
        
        # Collect articles using existing system
        articles = self.aggregator.collect_articles(target_date)
        
        # Generate summary with enhanced analysis
        summary = self.aggregator.summarize_articles()
        
        return summary
    
    def categorize_for_sf_fed(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles according to SF Fed digest structure"""
        categories = {
            'top_headlines': [],
            'district_regional': [],
            'national_macro': [],
            'financial_banking': [],
            'global_pacific': [],
            'technology_cyber': [],
            'regulatory_legislative': []
        }
        
        for article in articles:
            title_lower = article['title'].lower()
            desc_lower = (article.get('description', '') or '').lower()
            content = f"{title_lower} {desc_lower}"
            
            # Categorize based on SF Fed priorities
            if any(state in content for state in self.district_states):
                categories['district_regional'].append(article)
            elif any(term in content for term in ['china', 'japan', 'korea', 'asean', 'pacific', 'trade']):
                categories['global_pacific'].append(article)
            elif any(term in content for term in ['fintech', 'cyber', 'fednow', 'digital', 'ai', 'cloud']):
                categories['technology_cyber'].append(article)
            elif any(term in content for term in ['cfpb', 'fdic', 'occ', 'treasury', 'congress', 'regulation']):
                categories['regulatory_legislative'].append(article)
            elif any(term in content for term in ['banking', 'financial stability', 'credit', 'stress test']):
                categories['financial_banking'].append(article)
            elif any(term in content for term in ['inflation', 'unemployment', 'gdp', 'productivity', 'fomc']):
                categories['national_macro'].append(article)
            
            # Top headlines - high priority Fed-related content
            if any(term in content for term in ['fed', 'federal reserve', 'powell', 'monetary policy', 'interest rate']):
                categories['top_headlines'].append(article)
        
        return categories
    
    def generate_executive_summary(self, categories: Dict[str, List[Dict]]) -> str:
        """Generate executive summary section"""
        total_articles = sum(len(articles) for articles in categories.values())
        
        summary_points = []
        
        # Key themes
        if categories['top_headlines']:
            summary_points.append("Federal Reserve policy developments continue to drive market expectations")
        
        if categories['district_regional']:
            summary_points.append(f"12th District shows {len(categories['district_regional'])} regional economic signals")
        
        if categories['financial_banking']:
            summary_points.append("Banking sector stability indicators require continued monitoring")
        
        if categories['global_pacific']:
            summary_points.append("Pacific Rim developments present both opportunities and risks")
        
        if categories['technology_cyber']:
            summary_points.append("Technology and cyber developments impact payment system resilience")
        
        summary = f"""**Executive Summary**

Today's digest covers {total_articles} articles across key SF Fed priority areas. {' '.join(summary_points[:3])}. 

Key focus areas include monetary policy transmission, regional economic conditions in the 12th District, and emerging risks in financial technology and cyber security. Market participants continue to adjust expectations based on Fed communications and economic data releases."""
        
        return summary
    
    def format_article_summary(self, article: Dict) -> str:
        """Format individual article for digest"""
        title = article['title']
        source = article.get('source', 'Unknown')
        
        # Use structured analysis if available
        if article.get('structured_analysis'):
            analysis = article['structured_analysis']
            highlights = analysis.get('summary_highlights', [])
            if highlights:
                summary = highlights[0][:150] + "..." if len(highlights[0]) > 150 else highlights[0]
            else:
                summary = article.get('description', '')[:150] + "..."
        else:
            summary = article.get('description', '')[:150] + "..."
        
        # Clean HTML tags
        summary = re.sub(r'<[^>]+>', '', summary)
        
        return f"**{title}**\n{summary}\n*Source: {source}*"
    
    def generate_sf_fed_implications(self, categories: Dict[str, List[Dict]]) -> List[str]:
        """Generate SF Fed specific implications"""
        implications = []
        
        # Monetary Policy
        if categories['top_headlines'] or categories['national_macro']:
            implications.append("**Monetary Policy**: Recent developments may influence FOMC deliberations on rate path and balance sheet policy")
        
        # Bank Supervision
        if categories['financial_banking']:
            implications.append("**Bank Supervision**: Banking sector developments require enhanced supervisory attention, particularly for CRE exposures")
        
        # Regional Economic Monitoring
        if categories['district_regional']:
            implications.append("**Regional Economic Monitoring**: 12th District conditions show divergent trends requiring targeted analysis for Beige Book contributions")
        
        # Payments & Technology Operations
        if categories['technology_cyber']:
            implications.append("**Payments & Technology Operations**: Emerging fintech and cyber risks necessitate enhanced FedNow system monitoring and resilience planning")
        
        # Financial Stability
        if categories['global_pacific'] or categories['financial_banking']:
            implications.append("**Financial Stability**: Global interconnectedness and Pacific Rim developments present systemic risk considerations")
        
        # Additional implications based on content
        implications.append("**Research & Analysis**: Current developments provide input for SF Fed research on labor markets, housing, and technology sector dynamics")
        implications.append("**External Communications**: Market expectations and regional conditions inform public speaking opportunities and stakeholder engagement")
        
        return implications[:7]  # Limit to 5-7 bullets as requested
    
    def generate_digest(self, target_date: datetime = None) -> str:
        """Generate complete SF Fed Executive Daily News Digest"""
        if target_date is None:
            target_date = datetime.now()
        
        print("Generating SF Fed Executive Daily News Digest...")
        
        # Collect articles
        summary = self.collect_sf_fed_articles(target_date)
        
        if not summary.get('topics'):
            return "No relevant articles found for today's digest."
        
        # Extract all articles from topics
        all_articles = []
        for topic_articles in summary['topics'].values():
            all_articles.extend(topic_articles)
        
        # Categorize for SF Fed structure
        categories = self.categorize_for_sf_fed(all_articles)
        
        # Generate digest sections
        digest_date = target_date.strftime("%B %d, %Y")
        
        digest = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date**: {digest_date}
**Prepared for**: SF Fed Executive Leadership Team

---

## Top 5 Headlines Relevant to the Federal Reserve

"""
        
        # Top 5 headlines
        top_articles = categories['top_headlines'][:5]
        if not top_articles:
            # Fallback to most relevant articles
            top_articles = (categories['national_macro'] + categories['financial_banking'])[:5]
        
        for i, article in enumerate(top_articles, 1):
            digest += f"{i}. {self.format_article_summary(article)}\n\n"
        
        digest += """---

## 12th District Regional Economic & Labor Signals

"""
        
        # Regional articles
        regional_articles = categories['district_regional'][:5]
        if regional_articles:
            for article in regional_articles:
                digest += f"• {self.format_article_summary(article)}\n\n"
        else:
            digest += "*No specific 12th District developments identified in today's coverage.*\n\n"
        
        digest += """---

## National Macroeconomic & Monetary Policy Developments

"""
        
        # National macro articles
        macro_articles = categories['national_macro'][:5]
        for article in macro_articles:
            digest += f"• {self.format_article_summary(article)}\n\n"
        
        digest += """---

## Financial System & Banking Stability Watch

"""
        
        # Banking articles
        banking_articles = categories['financial_banking'][:5]
        if banking_articles:
            for article in banking_articles:
                digest += f"• {self.format_article_summary(article)}\n\n"
        else:
            digest += "*No significant banking sector developments identified.*\n\n"
        
        digest += """---

## Global & Pacific Rim Insights (SF Fed Priority)

"""
        
        # Global/Pacific articles
        global_articles = categories['global_pacific'][:5]
        if global_articles:
            for article in global_articles:
                digest += f"• {self.format_article_summary(article)}\n\n"
        else:
            digest += "*No major Pacific Rim developments in today's coverage.*\n\n"
        
        digest += """---

## Technology, Cyber, and Payments Developments

"""
        
        # Technology articles
        tech_articles = categories['technology_cyber'][:5]
        if tech_articles:
            for article in tech_articles:
                digest += f"• {self.format_article_summary(article)}\n\n"
        else:
            digest += "*No significant fintech or cyber developments identified.*\n\n"
        
        digest += """---

## Regulatory, Legislative, and Federal Government Updates

"""
        
        # Regulatory articles
        reg_articles = categories['regulatory_legislative'][:5]
        if reg_articles:
            for article in reg_articles:
                digest += f"• {self.format_article_summary(article)}\n\n"
        else:
            digest += "*No major regulatory developments in today's coverage.*\n\n"
        
        digest += """---

## Implications for SF Fed

"""
        
        # SF Fed implications
        implications = self.generate_sf_fed_implications(categories)
        for implication in implications:
            digest += f"• {implication}\n\n"
        
        digest += """---

"""
        
        # Executive summary
        digest += self.generate_executive_summary(categories)
        
        digest += f"""

---

*Digest prepared from {len(all_articles)} articles across {len(summary['sources_covered'])} sources*
*Sources: {', '.join(summary['sources_covered'][:5])}{'...' if len(summary['sources_covered']) > 5 else ''}*
"""
        
        return digest
    
    def save_digest(self, digest_content: str, target_date: datetime = None) -> str:
        """Save digest to file"""
        if target_date is None:
            target_date = datetime.now()
        
        # Create filename
        date_str = target_date.strftime("%Y-%m-%d")
        filename = f"sf_fed_executive_digest_{date_str}.md"
        
        # Ensure directory exists
        os.makedirs("daily_digests", exist_ok=True)
        filepath = os.path.join("daily_digests", filename)
        
        # Save digest
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        # Also save as latest
        latest_path = os.path.join("daily_digests", "latest_sf_fed_digest.md")
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        return filepath

def main():
    """Main function to generate SF Fed digest"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SF Fed Executive Daily News Digest Generator')
    parser.add_argument('--date', help='Target date (YYYY-MM-DD format)', default=None)
    parser.add_argument('--llm-provider', help='LLM provider (auto, openai, anthropic, litellm)', default='auto')
    parser.add_argument('--output', help='Output file path', default=None)
    
    args = parser.parse_args()
    
    # Parse target date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return
    
    # Initialize generator
    generator = SFFedDigestGenerator(llm_provider=args.llm_provider)
    
    # Generate digest
    digest_content = generator.generate_digest(target_date)
    
    # Save digest
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        print(f"SF Fed Executive Digest saved to: {args.output}")
    else:
        filepath = generator.save_digest(digest_content, target_date)
        print(f"SF Fed Executive Digest saved to: {filepath}")
    
    # Also print to console for immediate review
    print("\n" + "="*80)
    print("SF FED EXECUTIVE DAILY NEWS DIGEST")
    print("="*80)
    print(digest_content)

if __name__ == "__main__":
    main()