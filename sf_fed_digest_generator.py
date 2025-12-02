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
        
        # Ensure articles have detailed analysis
        if hasattr(self.aggregator, 'llm_service') and self.aggregator.llm_service:
            print("Enhancing articles with LLM analysis...")
            for topic_articles in summary.get('topics', {}).values():
                for article in topic_articles:
                    if not article.get('structured_analysis') and not article.get('highlights'):
                        try:
                            content = article.get('description', '') or article.get('content', '')
                            if content:
                                # Generate structured analysis
                                analysis = self.aggregator.llm_service.generate_structured_analysis(article)
                                if analysis:
                                    article['structured_analysis'] = analysis
                        except Exception as e:
                            print(f"Failed to analyze article {article.get('title', 'Unknown')}: {e}")
                            continue
        
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
        """Format individual article for digest with 4 bullet points"""
        title = article['title']
        source = article.get('source', 'Unknown')
        
        # Use structured analysis if available for detailed bullets
        if article.get('structured_analysis'):
            analysis = article['structured_analysis']
            highlights = analysis.get('summary_highlights', [])
            if len(highlights) >= 4:
                bullets = '\n'.join([f"  • {bullet}" for bullet in highlights[:4]])
                return f"**{title}**\n{bullets}\n*Source: {source}*"
        
        # Use highlights if available
        if article.get('highlights') and len(article['highlights']) >= 4:
            bullets = '\n'.join([f"  • {highlight}" for highlight in article['highlights'][:4]])
            return f"**{title}**\n{bullets}\n*Source: {source}*"
        
        # Generate 4 bullets using LLM if available
        if hasattr(self.aggregator, 'llm_service') and self.aggregator.llm_service:
            try:
                content = article.get('description', '') or article.get('content', '')
                if content:
                    insights = self.aggregator.llm_service.extract_key_insights(content)
                    if insights and len(insights) >= 4:
                        bullets = '\n'.join([f"  • {insight}" for insight in insights[:4]])
                        return f"**{title}**\n{bullets}\n*Source: {source}*"
            except Exception as e:
                print(f"LLM analysis failed for {title}: {e}")
        
        # Fallback to single description
        summary = article.get('description', '')[:150] + "..."
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
    
    def generate_digest_data(self, target_date: datetime = None) -> dict:
        """Generate structured SF Fed digest data"""
        if target_date is None:
            target_date = datetime.now()
        
        print("Generating SF Fed Executive Daily News Digest data...")
        
        # Collect articles
        summary = self.collect_sf_fed_articles(target_date)
        
        if not summary.get('topics'):
            return {
                "date": target_date.strftime("%Y-%m-%d"),
                "generated_at": datetime.now().isoformat(),
                "total_articles": 0,
                "executive_summary": "No relevant articles found for today's digest.",
                "categories": {},
                "sources_covered": []
            }
        
        # Extract all articles from topics
        all_articles = []
        for topic_articles in summary['topics'].values():
            all_articles.extend(topic_articles)
        
        # Categorize for SF Fed structure
        categories = self.categorize_for_sf_fed(all_articles)
        
        # Generate structured data
        digest_data = {
            "date": target_date.strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(all_articles),
            "executive_summary": self.generate_executive_summary(categories),
            "categories": {
                "top_headlines": {
                    "display_name": "Top 5 Headlines Relevant to the Federal Reserve",
                    "articles": categories['top_headlines'][:5] if categories['top_headlines'] else (categories['national_macro'] + categories['financial_banking'])[:5]
                },
                "district_regional": {
                    "display_name": "12th District Regional Economic & Labor Signals",
                    "articles": categories['district_regional'][:5]
                },
                "national_macro": {
                    "display_name": "National Macroeconomic & Monetary Policy Developments",
                    "articles": categories['national_macro'][:5]
                },
                "financial_banking": {
                    "display_name": "Financial System & Banking Stability Watch",
                    "articles": categories['financial_banking'][:5]
                },
                "global_pacific": {
                    "display_name": "Global & Pacific Rim Insights (SF Fed Priority)",
                    "articles": categories['global_pacific'][:5]
                },
                "technology_cyber": {
                    "display_name": "Technology, Cyber, and Payments Developments",
                    "articles": categories['technology_cyber'][:5]
                },
                "regulatory_legislative": {
                    "display_name": "Regulatory, Legislative, and Federal Government Updates",
                    "articles": categories['regulatory_legislative'][:5]
                }
            },
            "sf_fed_implications": self.generate_sf_fed_implications(categories),
            "sources_covered": summary.get('sources_covered', [])
        }
        
        return digest_data
    
    def format_digest_markdown(self, digest_data: dict) -> str:
        """Format digest data as markdown"""
        digest_date = datetime.strptime(digest_data['date'], "%Y-%m-%d").strftime("%B %d, %Y")
        
        digest = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date**: {digest_date}
**Prepared for**: SF Fed Executive Leadership Team

---

"""
        
        # Add categories
        for category_key, category_data in digest_data['categories'].items():
            if not category_data['articles']:
                continue
                
            digest += f"## {category_data['display_name']}\n\n"
            
            if category_key == 'top_headlines':
                for i, article in enumerate(category_data['articles'], 1):
                    digest += f"{i}. {self.format_article_summary(article)}\n\n"
            else:
                for article in category_data['articles']:
                    digest += f"• {self.format_article_summary(article)}\n\n"
            
            if not category_data['articles'] and category_key in ['district_regional', 'global_pacific', 'technology_cyber', 'financial_banking']:
                digest += f"*No significant {category_data['display_name'].lower()} identified in today's coverage.*\n\n"
            
            digest += "---\n\n"
        
        # SF Fed implications
        digest += "## Implications for SF Fed\n\n"
        for implication in digest_data.get('sf_fed_implications', []):
            digest += f"• {implication}\n\n"
        
        digest += "---\n\n"
        
        # Executive summary
        digest += digest_data.get('executive_summary', '')
        
        digest += f"""

---

*Digest prepared from {digest_data['total_articles']} articles across {len(digest_data['sources_covered'])} sources*
*Sources: {', '.join(digest_data['sources_covered'][:5])}{'...' if len(digest_data['sources_covered']) > 5 else ''}*
"""
        
        return digest
    
    def generate_digest(self, target_date: datetime = None) -> str:
        """Generate complete SF Fed Executive Daily News Digest (legacy method)"""
        digest_data = self.generate_digest_data(target_date)
        return self.format_digest_markdown(digest_data)

    
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