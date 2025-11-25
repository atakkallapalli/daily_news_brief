
#!/usr/bin/env python3
"""
Enhanced Daily News Summary Generator
Generates bullet-point summaries with source links, authors, and quotes
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup

class EnhancedDailySummaryGenerator:
    """Generate enhanced daily news summary with bullet points, links, authors, and quotes"""
    
    def __init__(self, prompt_file: str = "/workspace/prompt.txt"):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.prompt_file = prompt_file
        self.load_prompt_template()
        
        # Load latest daily digest data
        self.daily_digest_data = self.load_latest_daily_digest()
        
    def load_prompt_template(self):
        """Load the prompt template from file"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            self.prompt_template = ""
    
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            # Find the latest digest JSON file
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
    
    def extract_article_content(self, url: str) -> Dict[str, str]:
        """Extract additional content from article URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract author
                author = self.extract_author(soup)
                
                # Try to extract quotes
                quotes = self.extract_quotes(soup)
                
                return {
                    'author': author,
                    'quotes': quotes
                }
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
        
        return {'author': 'Unknown', 'quotes': []}
    
    def extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author from article HTML"""
        # Common author selectors
        author_selectors = [
            '[rel="author"]',
            '.author',
            '.byline',
            '.writer',
            '[class*="author"]',
            '[class*="byline"]',
            'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        return element.get('content', '').strip()
                    else:
                        text = element.get_text().strip()
                        # Clean up common prefixes
                        text = re.sub(r'^(By|Author:|Written by)\s*', '', text, flags=re.IGNORECASE)
                        if text and len(text) < 100:  # Reasonable author name length
                            return text
            except:
                continue
        
        return 'Unknown'
    
    def extract_quotes(self, soup: BeautifulSoup) -> List[str]:
        """Extract quotes from article HTML"""
        quotes = []
        
        # Look for blockquotes
        blockquotes = soup.find_all('blockquote')
        for quote in blockquotes:
            text = quote.get_text().strip()
            if text and len(text) > 20 and len(text) < 500:  # Reasonable quote length
                quotes.append(f'"{text}"')
        
        # Look for quoted text in paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text()
            # Find quoted text
            quote_matches = re.findall(r'"([^"]{20,300})"', text)
            for match in quote_matches:
                if match not in [q.strip('"') for q in quotes]:
                    quotes.append(f'"{match}"')
        
        return quotes[:3]  # Return top 3 quotes
    
    def categorize_articles_by_sf_fed_priorities(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles according to SF Fed priorities from prompt"""
        categories = {
            'fed_headlines': [],
            'regional_economic': [],
            'macroeconomic_monetary': [],
            'banking_stability': [],
            'global_pacific_rim': [],
            'technology_cyber': [],
            'regulatory_legislative': []
        }
        
        # Enhanced keywords based on the prompt
        fed_keywords = ['federal reserve', 'fed', 'fomc', 'monetary policy', 'interest rate', 'inflation', 'jerome powell', 'rate cut', 'rate hike']
        regional_keywords = ['california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada', 'housing', 'tech sector', 'silicon valley', '12th district']
        macro_keywords = ['inflation', 'gdp', 'unemployment', 'labor market', 'productivity', 'yield curve', 'treasury', 'economy', 'economic growth']
        banking_keywords = ['bank', 'banking', 'credit', 'liquidity', 'capital', 'lending', 'financial stability', 'cre', 'commercial real estate']
        global_keywords = ['china', 'japan', 'korea', 'asia', 'pacific', 'international', 'global', 'trade', 'asean']
        tech_keywords = ['technology', 'cyber', 'fintech', 'digital', 'ai', 'artificial intelligence', 'payments', 'blockchain', 'fednow']
        regulatory_keywords = ['regulation', 'regulatory', 'congress', 'treasury', 'cfpb', 'fdic', 'occ', 'legislation', 'policy']
        
        for article in articles:
            title_lower = article.get('title', '').lower()
            description_lower = article.get('description', '').lower()
            content = f"{title_lower} {description_lower}"
            
            # Check each category (articles can be in multiple categories)
            if any(keyword in content for keyword in fed_keywords):
                categories['fed_headlines'].append(article)
            if any(keyword in content for keyword in regional_keywords):
                categories['regional_economic'].append(article)
            if any(keyword in content for keyword in macro_keywords):
                categories['macroeconomic_monetary'].append(article)
            if any(keyword in content for keyword in banking_keywords):
                categories['banking_stability'].append(article)
            if any(keyword in content for keyword in global_keywords):
                categories['global_pacific_rim'].append(article)
            if any(keyword in content for keyword in tech_keywords):
                categories['technology_cyber'].append(article)
            if any(keyword in content for keyword in regulatory_keywords):
                categories['regulatory_legislative'].append(article)
        
        return categories
    
    def enhance_article_with_details(self, article: Dict) -> Dict:
        """Enhance article with author and quotes"""
        enhanced_article = article.copy()
        
        # Try to extract additional details from URL
        url = article.get('url', '')
        if url and not url.startswith('https://news.google.com'):
            # Only try to extract from direct URLs, not Google News redirects
            details = self.extract_article_content(url)
            enhanced_article.update(details)
        else:
            enhanced_article['author'] = 'Unknown'
            enhanced_article['quotes'] = []
        
        return enhanced_article
    
    def generate_bullet_point_summary(self) -> str:
        """Generate bullet point summary following the SF Fed prompt structure"""
        if not self.daily_digest_data:
            return "Error: No daily digest data available"
        
        # Extract articles from daily digest
        articles = []
        categories_data = self.daily_digest_data.get('categories', {})
        
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles.extend(category_data['articles'])
        
        print(f"Processing {len(articles)} articles...")
        
        # Categorize articles according to SF Fed priorities
        categorized_articles = self.categorize_articles_by_sf_fed_priorities(articles)
        
        # Generate the summary
        content = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Total Articles Analyzed:** {len(articles)}

---

## 1. Top 5 Headlines Relevant to the Federal Reserve

"""
        
        # Top Fed Headlines
        fed_articles = categorized_articles['fed_headlines'][:5]
        for i, article in enumerate(fed_articles, 1):
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_article_bullet(i, enhanced_article)
        
        if not fed_articles:
            content += "• No Federal Reserve specific headlines identified in current news cycle.\n\n"
        
        content += """## 2. 12th District Regional Economic & Labor Signals
*California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada*

"""
        
        # Regional Economic Signals
        regional_articles = categorized_articles['regional_economic'][:5]
        for article in regional_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_regional_bullet(enhanced_article)
        
        if not regional_articles:
            content += "• No specific 12th District regional signals identified in current news cycle.\n\n"
        
        content += """## 3. National Macroeconomic & Monetary Policy Developments
*Inflation, labor markets, GDP, productivity, FOMC outlook*

"""
        
        # Macroeconomic Developments
        macro_articles = categorized_articles['macroeconomic_monetary'][:6]
        for article in macro_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_macro_bullet(enhanced_article)
        
        content += """## 4. Financial System & Banking Stability Watch
*Bank liquidity/capital, CRE exposures, funding markets, credit spreads*

"""
        
        # Banking Stability
        banking_articles = categorized_articles['banking_stability'][:4]
        for article in banking_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_banking_bullet(enhanced_article)
        
        if not banking_articles:
            content += "• No significant banking stability developments identified.\n\n"
        
        content += """## 5. Global & Pacific Rim Insights (SF Fed Priority)
*China, Japan, Korea, ASEAN, international central bank actions*

"""
        
        # Global Insights
        global_articles = categorized_articles['global_pacific_rim'][:4]
        for article in global_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_global_bullet(enhanced_article)
        
        if not global_articles:
            content += "• No significant global or Pacific Rim developments identified.\n\n"
        
        content += """## 6. Technology, Cyber, and Payments Developments
*Cyber threats, AI risks, fintech, FedNow, digital assets*

"""
        
        # Technology Developments
        tech_articles = categorized_articles['technology_cyber'][:4]
        for article in tech_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_tech_bullet(enhanced_article)
        
        if not tech_articles:
            content += "• No significant technology or cyber developments identified.\n\n"
        
        content += """## 7. Regulatory, Legislative, and Federal Government Updates
*Congress, Treasury, CFPB, FDIC, OCC*

"""
        
        # Regulatory Updates
        regulatory_articles = categorized_articles['regulatory_legislative'][:4]
        for article in regulatory_articles:
            enhanced_article = self.enhance_article_with_details(article)
            content += self.format_regulatory_bullet(enhanced_article)
        
        if not regulatory_articles:
            content += "• No significant regulatory or legislative developments identified.\n\n"
        
        # Generate implications and summary
        content += self.generate_implications_section(categorized_articles)
        content += self.generate_executive_summary_section(categorized_articles, len(articles))
        
        return content
    
    def format_article_bullet(self, number: int, article: Dict) -> str:
        """Format article as bullet point with full details"""
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown')
        author = article.get('author', 'Unknown')
        description = article.get('description', '')
        quotes = article.get('quotes', [])
        
        content = f"**{number}. [{title}]({url})**\n"
        content += f"   - **Source:** {source}\n"
        if author != 'Unknown':
            content += f"   - **Author:** {author}\n"
        
        # Add description/summary (2-3 lines)
        if description:
            summary = description[:200] + "..." if len(description) > 200 else description
            content += f"   - **Summary:** {summary}\n"
        
        # Add quotes if available
        if quotes:
            content += f"   - **Key Quote:** {quotes[0]}\n"
        
        content += f"   - **Relevance:** Direct implications for monetary policy and Fed operations\n\n"
        
        return content
    
    def format_regional_bullet(self, article: Dict) -> str:
        """Format regional economic article"""
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown')
        highlights = article.get('highlights', [])
        
        content = f"• **[{title}]({url})** ({source})\n"
        if highlights:
            highlight = highlights[0] if isinstance(highlights, list) else str(highlights)
            content += f"  - {highlight}\n"
        content += "\n"
        
        return content
    
    def format_macro_bullet(self, article: Dict) -> str:
        """Format macroeconomic article"""
        title = article.get('title', 'No title')
        url = article.get('url', '#')
        source = article.get('source', 'Unknown')
        highlights = article.get('highlights', [])
        
        content = f"• **[{title}]({url})** ({source})\n"
        if highlights:
            for highlight in highlights[:2]:  # Show top 2 highlights
                if isinstance(highlight, str):
                    content += f"  - {highlight}\n"
        content += "\n"
        
        return content
    
    def format_banking_bullet(self, article: Dict) -> str:
        """Format banking stability article"""
        return self.format_macro_bullet(article)  # Same format
    
    def format_global_bullet(self, article: Dict) -> str:
        """Format global insights article"""
        return self.format_macro_bullet(article)  # Same format
    
    def format_tech_bullet(self, article: Dict) -> str:
        """Format technology article"""
        return self.format_macro_bullet(article)  # Same format
    
    def format_regulatory_bullet(self, article: Dict) -> str:
        """Format regulatory article"""
        return self.format_macro_bullet(article)  # Same format
    
    def generate_implications_section(self, categorized_articles: Dict[str, List[Dict]]) -> str:
        """Generate implications for SF Fed section"""
        content = """## 8. Implications for SF Fed

"""
        
        implications = []
        
        if categorized_articles['fed_headlines'] or categorized_articles['macroeconomic_monetary']:
            implications.append("**Monetary Policy:** Current economic signals warrant continued assessment of inflation trajectory and labor market dynamics for future FOMC policy decisions.")
        
        if categorized_articles['banking_stability']:
            implications.append("**Bank Supervision:** Regional banking conditions require enhanced monitoring, particularly commercial real estate exposures and funding market conditions.")
        
        if categorized_articles['regional_economic']:
            implications.append("**Regional Economic Monitoring:** 12th District economic indicators show evolving conditions requiring continued surveillance of key sectors.")
        
        if categorized_articles['technology_cyber']:
            implications.append("**Payments & Technology Operations:** Technology developments and cyber risks necessitate ongoing system resilience and operational risk management.")
        
        implications.append("**Financial Stability:** Current market and economic conditions require continued assessment of systemic risks and emerging vulnerabilities.")
        
        if categorized_articles['global_pacific_rim']:
            implications.append("**International Coordination:** Global economic developments may impact regional trade flows and financial market conditions.")
        
        for implication in implications:
            content += f"• {implication}\n\n"
        
        return content
    
    def generate_executive_summary_section(self, categorized_articles: Dict[str, List[Dict]], total_articles: int) -> str:
        """Generate executive summary section"""
        content = """## 9. Executive Summary (<150 words)

"""
        
        # Count articles by category
        category_counts = {k: len(v) for k, v in categorized_articles.items() if v}
        
        summary = f"Today's digest analyzes {total_articles} articles across Federal Reserve priority areas. "
        
        if category_counts:
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            category_names = {
                'fed_headlines': 'Federal Reserve developments',
                'macroeconomic_monetary': 'macroeconomic indicators',
                'regional_economic': '12th District conditions',
                'technology_cyber': 'technology risks',
                'banking_stability': 'banking stability',
                'global_pacific_rim': 'global developments',
                'regulatory_legislative': 'regulatory updates'
            }
            
            focus_areas = [category_names.get(cat, cat) for cat, _ in top_categories]
            summary += f"Primary focus areas include {', '.join(focus_areas)}. "
        
        summary += "Key themes indicate continued need for monetary policy vigilance, enhanced supervisory attention to emerging risks, and operational readiness for evolving financial system conditions. "
        summary += "Regional economic monitoring and technology risk management remain critical priorities."
        
        content += summary + "\n\n"
        
        return content
    
    def save_summary(self, content: str) -> str:
        """Save the summary to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"enhanced_daily_summary_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename

def main():
    """Main function to generate enhanced daily summary"""
    generator = EnhancedDailySummaryGenerator()
    
    print("Generating enhanced daily news summary with bullet points...")
    summary_content = generator.generate_bullet_point_summary()
    
    filename = generator.save_summary(summary_content)
    print(f"Enhanced summary saved to: {filename}")
    
    return filename

if __name__ == "__main__":
    main()

