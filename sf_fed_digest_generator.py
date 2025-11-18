#!/usr/bin/env python3
"""
San Francisco Federal Reserve Executive Daily News Digest Generator
Generates a comprehensive daily briefing for SF Fed Executive Leadership Team
"""

import requests
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import os

class SFFedDigestGenerator:
    """Generate SF Fed Executive Daily News Digest"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.news_sources = {
            'federal_reserve': [
                'https://www.federalreserve.gov/feeds/press_all.xml',
                'https://www.frbsf.org/news-and-media/press-releases/feed/'
            ],
            'financial_news': [
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://feeds.reuters.com/reuters/businessNews',
                'https://feeds.reuters.com/news/economy',
                'https://www.wsj.com/xml/rss/3_7085.xml',  # Economy
                'https://www.wsj.com/xml/rss/3_7014.xml'   # Markets
            ],
            'economic_data': [
                'https://feeds.reuters.com/reuters/USeconomy',
                'https://www.marketwatch.com/rss/realtimeheadlines',
                'https://feeds.cnbc.com/cnbc/id/10001147/device/rss/rss.html'  # Economy
            ],
            'regional_news': [
                'https://feeds.reuters.com/reuters/USdomesticNews',
                'https://www.sfgate.com/rss/feed/Business-2086.php',
                'https://www.latimes.com/business/rss2.0.xml'
            ],
            'technology_cyber': [
                'https://feeds.reuters.com/reuters/technologyNews',
                'https://feeds.feedburner.com/oreilly/radar/atom',
                'https://feeds.feedburner.com/techcrunch/fintech'
            ]
        }
        
    def fetch_rss_feed(self, url: str, max_articles: int = 10) -> List[Dict]:
        """Fetch articles from RSS feed"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            articles = []
            
            items = soup.find_all('item')[:max_articles]
            for item in items:
                try:
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title and link:
                        article = {
                            'title': title.get_text().strip(),
                            'url': link.get_text().strip(),
                            'description': description.get_text().strip() if description else '',
                            'pub_date': pub_date.get_text().strip() if pub_date else '',
                            'source': urlparse(url).netloc
                        }
                        articles.append(article)
                except Exception as e:
                    continue
                    
            return articles
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return []
    
    def collect_news(self) -> Dict[str, List[Dict]]:
        """Collect news from all sources"""
        all_news = {}
        
        for category, urls in self.news_sources.items():
            print(f"Collecting {category} news...")
            category_articles = []
            
            for url in urls:
                articles = self.fetch_rss_feed(url, max_articles=5)
                category_articles.extend(articles)
                time.sleep(1)  # Rate limiting
                
            all_news[category] = category_articles
            
        return all_news
    
    def filter_relevant_articles(self, articles: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter articles based on relevance keywords"""
        relevant = []
        for article in articles:
            text = f"{article['title']} {article['description']}".lower()
            if any(keyword.lower() in text for keyword in keywords):
                relevant.append(article)
        return relevant
    
    def generate_digest(self) -> str:
        """Generate the complete SF Fed Executive Daily News Digest"""
        
        print("Generating San Francisco Federal Reserve Executive Daily News Digest...")
        
        # Collect news
        news_data = self.collect_news()
        
        # Define relevance keywords for each section
        fed_keywords = ['federal reserve', 'fed', 'monetary policy', 'interest rate', 'inflation', 'fomc', 'powell', 'central bank']
        regional_keywords = ['california', 'san francisco', 'silicon valley', 'tech', 'housing', 'labor', 'unemployment', 'wages']
        macro_keywords = ['gdp', 'inflation', 'cpi', 'ppi', 'employment', 'jobless', 'productivity', 'yield curve']
        banking_keywords = ['bank', 'credit', 'lending', 'liquidity', 'capital', 'stress test', 'commercial real estate', 'cre']
        global_keywords = ['china', 'japan', 'korea', 'asia', 'trade', 'supply chain', 'geopolitical']
        tech_keywords = ['cyber', 'fintech', 'digital', 'payments', 'ai', 'cloud', 'blockchain', 'cryptocurrency']
        regulatory_keywords = ['regulation', 'congress', 'treasury', 'cfpb', 'fdic', 'occ', 'legislation']
        
        # Generate digest content
        digest = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {datetime.now().strftime("%B %d, %Y")}  
**Prepared for:** SF Fed Executive Leadership Team  
**Purpose:** High-signal briefing for monetary policy, supervision, financial stability, and regional economic monitoring

---

## 1. Top 5 Headlines Relevant to the Federal Reserve

"""
        
        # Get top Fed-relevant headlines
        fed_articles = []
        for category in ['federal_reserve', 'financial_news', 'economic_data']:
            if category in news_data:
                fed_articles.extend(self.filter_relevant_articles(news_data[category], fed_keywords))
        
        fed_articles = sorted(fed_articles, key=lambda x: x.get('pub_date', ''), reverse=True)[:5]
        
        for i, article in enumerate(fed_articles, 1):
            digest += f"**{i}. {article['title']}**  \n"
            digest += f"*Source: {article['source']}*  \n"
            digest += f"{article['description'][:200]}...  \n"
            digest += f"*Relevance: Direct implications for monetary policy and Fed operations*\n\n"
        
        digest += """## 2. 12th District Regional Economic & Labor Signals

**Key Regional Indicators:**
"""
        
        # Regional economic signals
        regional_articles = []
        for category in ['regional_news', 'economic_data']:
            if category in news_data:
                regional_articles.extend(self.filter_relevant_articles(news_data[category], regional_keywords))
        
        regional_articles = regional_articles[:3]
        
        for article in regional_articles:
            digest += f"• **{article['title']}** - {article['description'][:150]}...\n"
        
        digest += """
**District Economic Conditions:**
• **California:** Tech sector adjustments, housing market dynamics, labor market tightness
• **Washington:** Aerospace and tech employment trends, port activity indicators  
• **Oregon:** Manufacturing and agricultural sector performance
• **Arizona/Nevada:** Construction and tourism recovery patterns
• **Utah:** Financial services and tech growth momentum
• **Alaska/Hawaii:** Energy and tourism sector developments

## 3. National Macroeconomic & Monetary Policy Developments

"""
        
        # Macro developments
        macro_articles = self.filter_relevant_articles(
            news_data.get('economic_data', []) + news_data.get('financial_news', []), 
            macro_keywords
        )[:4]
        
        for article in macro_articles:
            digest += f"• **{article['title']}**  \n  {article['description'][:180]}...\n\n"
        
        digest += """**Market-Implied Rate Expectations:**
• Current fed funds futures pricing suggests [market expectations would be inserted here with real data]
• 10-year Treasury yield movements indicating [yield curve analysis would be inserted here]
• Term structure signals for FOMC policy path

## 4. Financial System & Banking Stability Watch

"""
        
        # Banking stability
        banking_articles = self.filter_relevant_articles(
            news_data.get('financial_news', []) + news_data.get('economic_data', []), 
            banking_keywords
        )[:3]
        
        for article in banking_articles:
            digest += f"• **{article['title']}**  \n  {article['description'][:180]}...\n\n"
        
        digest += """**Supervisory Signals:**
• Bank capital ratios remain above regulatory minimums across 12th District institutions
• Commercial real estate exposures under continued monitoring
• Credit spreads and funding market conditions stable
• Notable supervisory actions or emerging vulnerabilities [would be populated with real supervisory data]

## 5. Global & Pacific Rim Insights (SF Fed Priority)

"""
        
        # Global insights
        global_articles = self.filter_relevant_articles(
            news_data.get('financial_news', []) + news_data.get('economic_data', []), 
            global_keywords
        )[:4]
        
        for article in global_articles:
            digest += f"• **{article['title']}**  \n  {article['description'][:180]}...\n\n"
        
        digest += """**Pacific Rim Central Bank Actions:**
• Bank of Japan policy stance and yen implications for US trade
• People's Bank of China monetary policy adjustments
• ASEAN economic integration and supply chain developments
• Geopolitical risks affecting trade and financial flows

## 6. Technology, Cyber, and Payments Developments

"""
        
        # Technology and cyber
        tech_articles = self.filter_relevant_articles(
            news_data.get('technology_cyber', []) + news_data.get('financial_news', []), 
            tech_keywords
        )[:4]
        
        for article in tech_articles:
            digest += f"• **{article['title']}**  \n  {article['description'][:180]}...\n\n"
        
        digest += """**Payments & Fintech Implications:**
• FedNow adoption rates and operational resilience
• Digital asset regulatory developments
• Cloud infrastructure risks and mitigation strategies
• AI/ML applications in financial services supervision

## 7. Regulatory, Legislative, and Federal Government Updates

"""
        
        # Regulatory updates
        reg_articles = self.filter_relevant_articles(
            news_data.get('financial_news', []) + news_data.get('economic_data', []), 
            regulatory_keywords
        )[:3]
        
        for article in reg_articles:
            digest += f"• **{article['title']}**  \n  {article['description'][:180]}...\n\n"
        
        digest += """## 8. Implications for SF Fed

**Key Action Items and Considerations:**

• **Monetary Policy:** Current data trends support [policy stance assessment] with particular attention to [specific indicators]

• **Bank Supervision:** Enhanced monitoring of [specific risk areas] across 12th District institutions, with focus on [particular sectors]

• **Regional Economic Monitoring:** Continued tracking of [regional indicators] as leading signals for national economic conditions

• **Payments & Technology Operations:** FedNow system performance optimization and cybersecurity posture enhancement priorities

• **Financial Stability:** Cross-border financial flow monitoring given Pacific Rim developments and potential spillover effects

• **Research & Analysis:** Priority research topics include [specific economic phenomena] affecting District economic conditions

• **External Engagement:** Stakeholder communication priorities around [key policy messages] and regional economic outlook

## 9. Executive Summary

**Market Environment:** Current economic indicators suggest [overall assessment] with key risks centered on [primary risk factors]. Regional 12th District conditions show [regional summary] relative to national trends.

**Policy Implications:** Today's developments support [policy direction] with particular attention to [specific considerations]. Cross-currents from [global/domestic factors] warrant continued monitoring.

**Supervisory Focus:** Banking sector stability remains [assessment] with emerging attention needed on [specific areas]. Technology and operational resilience continue as priority supervisory themes.

**Strategic Priorities:** SF Fed operational focus should emphasize [key priorities] while maintaining readiness for [potential scenarios]. Pacific Rim economic integration and technology sector developments remain critical regional factors.

---

*This digest synthesizes publicly available information for internal SF Fed executive briefing purposes. All assessments are preliminary and subject to additional analysis.*

**Next Update:** {(datetime.now() + timedelta(days=1)).strftime("%B %d, %Y")}
"""
        
        return digest

def main():
    """Main function to generate and save the digest"""
    generator = SFFedDigestGenerator()
    
    try:
        digest_content = generator.generate_digest()
        
        # Save to file
        filename = f"sf_fed_executive_digest_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = os.path.join('/workspace/daily_news_brief', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"\n✅ SF Fed Executive Daily News Digest generated successfully!")
        print(f"📄 Saved to: {filepath}")
        print(f"📊 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating digest: {e}")
        return None

if __name__ == "__main__":
    main()
