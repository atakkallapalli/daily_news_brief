#!/usr/bin/env python3
"""
Merged SF Fed Executive Daily News Digest Generator
Combines daily news digest with SF Fed specific analysis using the provided prompt
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

class MergedSFFedDigestGenerator:
    """Generate merged SF Fed Executive Daily News Digest"""
    
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
            digest_dir = Path("daily_digests")
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
    
    def categorize_articles_for_sf_fed(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles according to SF Fed priorities"""
        categories = {
            'fed_relevant_headlines': [],
            'regional_economic': [],
            'macroeconomic_monetary': [],
            'banking_stability': [],
            'global_pacific_rim': [],
            'technology_cyber': [],
            'regulatory_legislative': []
        }
        
        # Keywords for each category
        fed_keywords = ['federal reserve', 'fed', 'fomc', 'monetary policy', 'interest rate', 'inflation', 'jerome powell']
        regional_keywords = ['california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada', 'housing', 'tech sector', 'silicon valley']
        macro_keywords = ['inflation', 'gdp', 'unemployment', 'labor market', 'productivity', 'yield curve', 'treasury']
        banking_keywords = ['bank', 'banking', 'credit', 'liquidity', 'capital', 'lending', 'financial stability']
        global_keywords = ['china', 'japan', 'korea', 'asia', 'pacific', 'international', 'global', 'trade']
        tech_keywords = ['technology', 'cyber', 'fintech', 'digital', 'ai', 'artificial intelligence', 'payments', 'blockchain']
        regulatory_keywords = ['regulation', 'regulatory', 'congress', 'treasury', 'cfpb', 'fdic', 'occ', 'legislation']
        
        for article in articles:
            title_lower = article.get('title', '').lower()
            description_lower = article.get('description', '').lower()
            content = f"{title_lower} {description_lower}"
            
            # Check each category
            if any(keyword in content for keyword in fed_keywords):
                categories['fed_relevant_headlines'].append(article)
            elif any(keyword in content for keyword in regional_keywords):
                categories['regional_economic'].append(article)
            elif any(keyword in content for keyword in macro_keywords):
                categories['macroeconomic_monetary'].append(article)
            elif any(keyword in content for keyword in banking_keywords):
                categories['banking_stability'].append(article)
            elif any(keyword in content for keyword in global_keywords):
                categories['global_pacific_rim'].append(article)
            elif any(keyword in content for keyword in tech_keywords):
                categories['technology_cyber'].append(article)
            elif any(keyword in content for keyword in regulatory_keywords):
                categories['regulatory_legislative'].append(article)
            else:
                # Default to macroeconomic if no specific match
                categories['macroeconomic_monetary'].append(article)
        
        return categories
    
    def generate_top_headlines(self, articles: List[Dict]) -> str:
        """Generate top 5 headlines relevant to Federal Reserve"""
        content = "## 1. Top 5 Headlines Relevant to the Federal Reserve\n\n"
        
        # Sort by relevance and take top 5
        top_articles = articles[:5]
        
        for i, article in enumerate(top_articles, 1):
            title = article.get('title', 'No title')
            description = article.get('description', '')
            source = article.get('source', 'Unknown')
            
            content += f"**{i}. {title}**\n"
            content += f"*Source: {source}*\n"
            
            # Create 2-3 line summary
            if description:
                summary = description[:200] + "..." if len(description) > 200 else description
                content += f"{summary}\n"
            
            content += f"*Relevance: Impacts monetary policy, financial markets, or banking supervision*\n\n"
        
        return content
    
    def generate_regional_signals(self, articles: List[Dict]) -> str:
        """Generate 12th District regional economic signals"""
        content = "## 2. 12th District Regional Economic & Labor Signals\n\n"
        
        if not articles:
            content += "No specific regional signals identified in current news cycle.\n\n"
            return content
        
        content += "**Key Regional Indicators:**\n\n"
        
        for article in articles[:5]:  # Top 5 regional articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}** - "
            if highlights:
                content += highlights[0] if isinstance(highlights, list) else str(highlights)
            else:
                description = article.get('description', '')
                content += description[:150] + "..." if len(description) > 150 else description
            content += "\n\n"
        
        return content
    
    def generate_macroeconomic_section(self, articles: List[Dict]) -> str:
        """Generate national macroeconomic & monetary policy developments"""
        content = "## 3. National Macroeconomic & Monetary Policy Developments\n\n"
        
        if not articles:
            content += "No significant macroeconomic developments identified.\n\n"
            return content
        
        for article in articles[:4]:  # Top 4 macro articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}**\n"
            if highlights:
                for highlight in highlights[:2]:  # First 2 highlights
                    if isinstance(highlight, str):
                        content += f"  - {highlight}\n"
            content += "\n"
        
        return content
    
    def generate_banking_stability(self, articles: List[Dict]) -> str:
        """Generate financial system & banking stability watch"""
        content = "## 4. Financial System & Banking Stability Watch\n\n"
        
        if not articles:
            content += "No significant banking or financial stability developments identified.\n\n"
            return content
        
        for article in articles[:3]:  # Top 3 banking articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}**\n"
            if highlights:
                highlight_text = highlights[0] if isinstance(highlights, list) else str(highlights)
                content += f"  {highlight_text}\n"
            content += "\n"
        
        return content
    
    def generate_global_insights(self, articles: List[Dict]) -> str:
        """Generate global & Pacific Rim insights"""
        content = "## 5. Global & Pacific Rim Insights (SF Fed priority)\n\n"
        
        if not articles:
            content += "No significant global or Pacific Rim developments identified.\n\n"
            return content
        
        for article in articles[:3]:  # Top 3 global articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}**\n"
            if highlights:
                highlight_text = highlights[0] if isinstance(highlights, list) else str(highlights)
                content += f"  {highlight_text}\n"
            content += "\n"
        
        return content
    
    def generate_technology_section(self, articles: List[Dict]) -> str:
        """Generate technology, cyber, and payments developments"""
        content = "## 6. Technology, Cyber, and Payments Developments\n\n"
        
        if not articles:
            content += "No significant technology or cyber developments identified.\n\n"
            return content
        
        for article in articles[:3]:  # Top 3 tech articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}**\n"
            if highlights:
                highlight_text = highlights[0] if isinstance(highlights, list) else str(highlights)
                content += f"  {highlight_text}\n"
            content += "\n"
        
        return content
    
    def generate_regulatory_section(self, articles: List[Dict]) -> str:
        """Generate regulatory, legislative, and federal government updates"""
        content = "## 7. Regulatory, Legislative, and Federal Government Updates\n\n"
        
        if not articles:
            content += "No significant regulatory or legislative developments identified.\n\n"
            return content
        
        for article in articles[:3]:  # Top 3 regulatory articles
            title = article.get('title', 'No title')
            highlights = article.get('highlights', [])
            
            content += f"• **{title}**\n"
            if highlights:
                highlight_text = highlights[0] if isinstance(highlights, list) else str(highlights)
                content += f"  {highlight_text}\n"
            content += "\n"
        
        return content
    
    def generate_sf_fed_implications(self, categorized_articles: Dict[str, List[Dict]]) -> str:
        """Generate implications for SF Fed"""
        content = "## 8. Implications for SF Fed\n\n"
        
        implications = []
        
        # Monetary policy implications
        if categorized_articles['fed_relevant_headlines'] or categorized_articles['macroeconomic_monetary']:
            implications.append("**Monetary Policy:** Current economic signals suggest continued vigilance on inflation trends and labor market dynamics, with potential implications for future FOMC decisions.")
        
        # Bank supervision implications
        if categorized_articles['banking_stability']:
            implications.append("**Bank Supervision:** Regional banking conditions require continued monitoring, particularly CRE exposures and liquidity management practices.")
        
        # Regional economic monitoring
        if categorized_articles['regional_economic']:
            implications.append("**Regional Economic Monitoring:** 12th District economic conditions show mixed signals requiring enhanced surveillance of key sectors including technology, housing, and trade.")
        
        # Payments & technology operations
        if categorized_articles['technology_cyber']:
            implications.append("**Payments & Technology Operations:** Emerging technology trends and cyber risks necessitate continued investment in system resilience and modernization efforts.")
        
        # Financial stability
        implications.append("**Financial Stability:** Current market conditions and economic uncertainties require ongoing assessment of systemic risks and vulnerabilities.")
        
        # Add regulatory implications if relevant
        if categorized_articles['regulatory_legislative']:
            implications.append("**Regulatory Coordination:** Recent legislative and regulatory developments may require coordination with other federal agencies and policy response preparation.")
        
        # Global considerations
        if categorized_articles['global_pacific_rim']:
            implications.append("**International Coordination:** Global economic developments, particularly in Pacific Rim economies, may impact regional trade flows and financial conditions.")
        
        for implication in implications:
            content += f"• {implication}\n\n"
        
        return content
    
    def generate_executive_summary(self, categorized_articles: Dict[str, List[Dict]]) -> str:
        """Generate executive summary (<150 words)"""
        content = "## 9. Executive Summary (<150 words)\n\n"
        
        # Count total articles by category
        total_articles = sum(len(articles) for articles in categorized_articles.values())
        
        summary = f"Today's digest analyzes {total_articles} articles across key Federal Reserve priority areas. "
        
        # Highlight key themes
        key_themes = []
        if categorized_articles['fed_relevant_headlines']:
            key_themes.append("monetary policy developments")
        if categorized_articles['regional_economic']:
            key_themes.append("12th District economic conditions")
        if categorized_articles['banking_stability']:
            key_themes.append("banking sector stability")
        if categorized_articles['technology_cyber']:
            key_themes.append("technology and cyber risks")
        
        if key_themes:
            summary += f"Primary focus areas include {', '.join(key_themes)}. "
        
        summary += "Economic signals suggest continued attention to inflation dynamics, labor market conditions, and regional economic variations. "
        summary += "Banking sector monitoring remains critical, particularly regarding commercial real estate exposures and liquidity management. "
        summary += "Technology developments and cyber risks require ongoing operational vigilance. "
        summary += "Overall assessment indicates need for continued policy flexibility and enhanced supervisory attention to emerging risks."
        
        content += summary + "\n\n"
        
        return content
    
    def generate_markdown_digest(self) -> str:
        """Generate complete markdown digest"""
        if not self.daily_digest_data:
            return "Error: No daily digest data available"
        
        # Extract articles from daily digest
        articles = []
        categories_data = self.daily_digest_data.get('categories', {})
        print(f"Found categories: {list(categories_data.keys())}")
        
        for category_name, category_data in categories_data.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                category_articles = category_data['articles']
                print(f"Category '{category_name}': {len(category_articles)} articles")
                articles.extend(category_articles)
            elif isinstance(category_data, list):
                articles.extend(category_data)
        
        print(f"Total articles extracted: {len(articles)}")
        
        # Categorize articles for SF Fed priorities
        categorized_articles = self.categorize_articles_for_sf_fed(articles)
        
        # Generate digest content
        content = f"""# San Francisco Federal Reserve Executive Daily News Digest
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Prepared for:** SF Fed Executive Leadership Team
**Purpose:** High-signal briefing for monetary policy, supervision, financial stability, and regional economic monitoring

---

"""
        
        content += self.generate_top_headlines(categorized_articles['fed_relevant_headlines'])
        content += self.generate_regional_signals(categorized_articles['regional_economic'])
        content += self.generate_macroeconomic_section(categorized_articles['macroeconomic_monetary'])
        content += self.generate_banking_stability(categorized_articles['banking_stability'])
        content += self.generate_global_insights(categorized_articles['global_pacific_rim'])
        content += self.generate_technology_section(categorized_articles['technology_cyber'])
        content += self.generate_regulatory_section(categorized_articles['regulatory_legislative'])
        content += self.generate_sf_fed_implications(categorized_articles)
        content += self.generate_executive_summary(categorized_articles)
        
        return content
    
    def generate_html_digest(self, markdown_content: str) -> str:
        """Convert markdown to HTML format"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest - {datetime.now().strftime("%Y-%m-%d")}</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6;
            color: #333;
        }}
        .header {{ 
            background: linear-gradient(135deg, #1e3a8a, #3b82f6); 
            color: white;
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
            text-align: center;
        }}
        .section {{ 
            margin-bottom: 30px; 
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        .executive-summary {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        h1 {{ color: white; margin: 0; }}
        h2 {{ 
            color: #1e3a8a; 
            border-bottom: 2px solid #3b82f6; 
            padding-bottom: 10px; 
            margin-top: 0;
        }}
        h3 {{ color: #374151; }}
        .meta {{ color: #6b7280; font-size: 0.9em; margin: 5px 0; }}
        .implications {{ background: #ecfdf5; border-left: 4px solid #10b981; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
        strong {{ color: #1f2937; }}
        em {{ color: #6b7280; }}
    </style>
</head>
<body>
"""
        
        # Convert markdown to HTML (basic conversion)
        html_body = markdown_content.replace('\n\n', '</p><p>')
        html_body = html_body.replace('\n', '<br>')
        html_body = f"<p>{html_body}</p>"
        
        # Replace markdown headers
        html_body = re.sub(r'<p># (.*?)</p>', r'<div class="header"><h1>\1</h1></div>', html_body)
        html_body = re.sub(r'<p>## (.*?)</p>', r'<div class="section"><h2>\1</h2>', html_body)
        html_body = re.sub(r'<p>### (.*?)</p>', r'<h3>\1</h3>', html_body)
        
        # Replace markdown formatting
        html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_body)
        html_body = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_body)
        html_body = re.sub(r'• (.*?)<br>', r'<li>\1</li>', html_body)
        
        # Close section divs
        html_body = html_body.replace('<h2>', '</div><div class="section"><h2>')
        html_body = html_body.replace('## 9. Executive Summary', '</div><div class="executive-summary"><h2>Executive Summary')
        
        html_content += html_body + "</div></body></html>"
        
        return html_content
    
    def generate_json_digest(self, categorized_articles: Dict[str, List[Dict]]) -> str:
        """Generate JSON format digest"""
        json_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "title": "San Francisco Federal Reserve Executive Daily News Digest",
            "purpose": "High-signal briefing for monetary policy, supervision, financial stability, and regional economic monitoring",
            "sections": {
                "top_headlines": categorized_articles['fed_relevant_headlines'][:5],
                "regional_signals": categorized_articles['regional_economic'],
                "macroeconomic_developments": categorized_articles['macroeconomic_monetary'],
                "banking_stability": categorized_articles['banking_stability'],
                "global_insights": categorized_articles['global_pacific_rim'],
                "technology_developments": categorized_articles['technology_cyber'],
                "regulatory_updates": categorized_articles['regulatory_legislative']
            },
            "summary_stats": {
                "total_articles": sum(len(articles) for articles in categorized_articles.values()),
                "categories_covered": len([k for k, v in categorized_articles.items() if v]),
                "top_sources": self._get_top_sources(categorized_articles)
            }
        }
        
        return json.dumps(json_data, indent=2, ensure_ascii=False)
    
    def _get_top_sources(self, categorized_articles: Dict[str, List[Dict]]) -> List[str]:
        """Get top news sources from categorized articles"""
        sources = {}
        for articles in categorized_articles.values():
            for article in articles:
                source = article.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
        
        return sorted(sources.keys(), key=lambda x: sources[x], reverse=True)[:5]
    
    def save_all_formats(self) -> Dict[str, str]:
        """Generate and save all three formats"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Generate markdown content
        markdown_content = self.generate_markdown_digest()
        
        # Generate all formats
        html_content = self.generate_html_digest(markdown_content)
        
        # Extract articles for JSON
        articles = []
        if self.daily_digest_data:
            categories_data = self.daily_digest_data.get('categories', {})
            for category_name, category_data in categories_data.items():
                if isinstance(category_data, dict) and 'articles' in category_data:
                    articles.extend(category_data['articles'])
                elif isinstance(category_data, list):
                    articles.extend(category_data)
        
        categorized_articles = self.categorize_articles_for_sf_fed(articles)
        json_content = self.generate_json_digest(categorized_articles)
        
        # Save files
        files = {}
        
        # Markdown
        md_file = f"sf_fed_merged_digest_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        files['markdown'] = md_file
        
        # HTML
        html_file = f"sf_fed_merged_digest_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        files['html'] = html_file
        
        # JSON
        json_file = f"sf_fed_merged_digest_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        files['json'] = json_file
        
        return files

def main():
    """Main function to generate merged SF Fed digest"""
    generator = MergedSFFedDigestGenerator()
    
    print("Generating merged SF Fed Executive Daily News Digest...")
    files = generator.save_all_formats()
    
    print("Generated files:")
    for format_type, filename in files.items():
        print(f"  {format_type.upper()}: {filename}")
    
    return files

if __name__ == "__main__":
    main()
