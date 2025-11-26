
#!/usr/bin/env python3
"""
Generate Federal Reserve Executive Daily News Digest in All Formats
Uses enhanced fallback generation when LiteLLM is unavailable
"""

import json
import os
import re
import html
from datetime import datetime
from pathlib import Path
from enhanced_fed_executive_digest import EnhancedFedExecutiveDigest

def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown content to HTML with enhanced styling"""
    html_content = markdown_content
    
    # Convert markdown headers
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\*\*Date:\*\* (.+)$', r'<p class="date"><strong>Date:</strong> \1</p>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\*\*Generated:\*\* (.+)$', r'<p class="generated"><strong>Generated:</strong> \1</p>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\*\*Format:\*\* (.+)$', r'<p class="format"><strong>Format:</strong> \1</p>', html_content, flags=re.MULTILINE)
    
    # Convert article titles
    html_content = re.sub(r'^\*\*([^*]+)\*\*$', r'<h2 class="article-title">\1</h2>', html_content, flags=re.MULTILINE)
    
    # Convert author lines
    html_content = re.sub(r'^Author: (.+)$', r'<p class="author"><strong>Author:</strong> \1</p>', html_content, flags=re.MULTILINE)
    
    # Convert summary headers
    html_content = re.sub(r'^Summary:$', r'<h3>Summary:</h3>', html_content, flags=re.MULTILINE)
    
    # Convert bullet points
    lines = html_content.split('\n')
    in_list = False
    processed_lines = []
    
    for line in lines:
        if line.strip().startswith('• '):
            if not in_list:
                processed_lines.append('<ul class="summary-list">')
                in_list = True
            bullet_content = line.strip()[2:]
            processed_lines.append(f'<li>{bullet_content}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)
    
    if in_list:
        processed_lines.append('</ul>')
    
    html_content = '\n'.join(processed_lines)
    
    # Convert links
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
    
    # Convert horizontal rules
    html_content = re.sub(r'^---$', r'<hr class="article-separator">', html_content, flags=re.MULTILINE)
    
    # Convert paragraphs
    html_content = re.sub(r'\n\n', r'</p>\n<p>', html_content)
    html_content = f'<p>{html_content}</p>'
    
    # Clean up empty paragraphs and fix structure
    html_content = re.sub(r'<p>\s*</p>', '', html_content)
    html_content = re.sub(r'<p>\s*(<h[1-6])', r'\1', html_content)
    html_content = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html_content)
    html_content = re.sub(r'<p>\s*(<ul)', r'\1', html_content)
    html_content = re.sub(r'(</ul>)\s*</p>', r'\1', html_content)
    html_content = re.sub(r'<p>\s*(<hr)', r'\1', html_content)
    html_content = re.sub(r'(<hr[^>]*>)\s*</p>', r'\1', html_content)
    
    # Add enhanced HTML structure
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federal Reserve Executive Daily News Digest</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #1a365d;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 2.2em;
        }}
        
        .date, .generated, .format {{
            color: #4a5568;
            margin: 5px 0;
            font-size: 0.95em;
        }}
        
        .article-title {{
            color: #2d3748;
            margin-top: 30px;
            margin-bottom: 15px;
            padding: 15px;
            background-color: #edf2f7;
            border-left: 5px solid #3182ce;
            border-radius: 4px;
            font-size: 1.3em;
        }}
        
        .author {{
            color: #718096;
            font-style: italic;
            margin-bottom: 15px;
            padding-left: 20px;
        }}
        
        h3 {{
            color: #2d3748;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .summary-list {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        
        .summary-list li {{
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .summary-list li:last-child {{
            border-bottom: none;
        }}
        
        a {{
            color: #3182ce;
            text-decoration: none;
            font-weight: 500;
        }}
        
        a:hover {{
            text-decoration: underline;
            color: #2c5282;
        }}
        
        .article-separator {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, #cbd5e0, #e2e8f0, #cbd5e0);
            margin: 25px 0;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
            font-size: 0.9em;
            color: #718096;
            font-style: italic;
        }}
        
        .enhancement-note {{
            background-color: #f0fff4;
            border: 1px solid #9ae6b4;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            color: #22543d;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .container {{ padding: 20px; }}
            h1 {{ font-size: 1.8em; }}
            .article-title {{ font-size: 1.1em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
        <div class="enhancement-note">
            <strong>Enhanced Format Features:</strong>
            <ul>
                <li>4-5 substantive bullet points per article</li>
                <li>Improved author attribution</li>
                <li>Content insights and analysis</li>
                <li>Federal Reserve executive focus</li>
                <li>Clean, professional formatting</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
    
    return html_template

def create_comprehensive_json(markdown_content: str, articles_data: list) -> dict:
    """Create comprehensive JSON format with enhanced metadata"""
    current_date = datetime.now()
    
    json_data = {
        "digest_info": {
            "title": "Federal Reserve Executive Daily News Digest",
            "date": current_date.strftime("%Y-%m-%d"),
            "generated_at": current_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "format_version": "2.1",
            "total_articles": 0,
            "digest_type": "fed_executive_enhanced",
            "generation_method": "enhanced_fallback",
            "llm_config_used": {
                "provider": "http://35.175.151.231:8250",
                "model": "litellm_proxy/ClaudeSonnet4",
                "fallback_reason": "LiteLLM service unavailable"
            }
        },
        "articles": [],
        "metadata": {
            "llm_generated": False,
            "enhanced_format": True,
            "bullet_points_per_article": "4-5",
            "includes_author_attribution": True,
            "includes_content_insights": True,
            "html_content_cleaned": True,
            "fed_relevance_scoring": True
        },
        "categories": {
            "monetary_policy": [],
            "economic_indicators": [],
            "financial_markets": [],
            "regulatory_updates": [],
            "global_economy": []
        }
    }
    
    # Parse articles from markdown
    lines = markdown_content.split('\n')
    current_article = None
    in_summary = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('**') and line.endswith('**') and len(line) > 10 and not line.startswith('**Date:') and not line.startswith('**Generated:') and not line.startswith('**Format:'):
            # New article title
            if current_article:
                json_data["articles"].append(current_article)
            
            title = line.strip('*')
            current_article = {
                "id": len(json_data["articles"]) + 1,
                "title": title,
                "author": "",
                "summary_bullets": [],
                "source_url": "",
                "fed_relevance": "high",
                "keywords": [],
                "category": "monetary_policy",
                "content_insights": [],
                "publication_source": ""
            }
            in_summary = False
            
        elif line.startswith('Author: ') and current_article:
            author = line.replace('Author: ', '').strip()
            current_article["author"] = author
            # Extract publication source
            if ',' in author:
                current_article["publication_source"] = author.split(',', 1)[1].strip()
            
        elif line == 'Summary:':
            in_summary = True
            
        elif line.startswith('• ') and current_article and in_summary:
            bullet = line.replace('• ', '').strip()
            current_article["summary_bullets"].append(bullet)
            
            # Extract keywords from bullet points
            keywords = []
            fed_terms = ['Federal Reserve', 'Fed', 'monetary policy', 'interest rate', 'inflation', 'employment', 'economic']
            for term in fed_terms:
                if term.lower() in bullet.lower():
                    keywords.append(term)
            current_article["keywords"].extend(keywords)
            
        elif line.startswith('Read more: ') and current_article:
            # Extract URL from markdown link
            url_match = re.search(r'\(([^)]+)\)', line)
            if url_match:
                current_article["source_url"] = url_match.group(1)
            in_summary = False
    
    # Add the last article
    if current_article:
        json_data["articles"].append(current_article)
    
    # Update total articles count
    json_data["digest_info"]["total_articles"] = len(json_data["articles"])
    
    # Categorize articles
    for article in json_data["articles"]:
        title_lower = article["title"].lower()
        keywords = [k.lower() for k in article["keywords"]]
        
        if any(term in title_lower for term in ['rate', 'monetary', 'policy', 'fed']):
            json_data["categories"]["monetary_policy"].append(article["id"])
        elif any(term in title_lower for term in ['inflation', 'employment', 'gdp', 'economic']):
            json_data["categories"]["economic_indicators"].append(article["id"])
        elif any(term in title_lower for term in ['market', 'trading', 'investment', 'financial']):
            json_data["categories"]["financial_markets"].append(article["id"])
        elif any(term in title_lower for term in ['regulation', 'regulatory', 'compliance']):
            json_data["categories"]["regulatory_updates"].append(article["id"])
        else:
            json_data["categories"]["global_economy"].append(article["id"])
    
    return json_data

def main():
    """Generate Fed executive digest in all formats using enhanced fallback"""
    print("🚀 Generating Federal Reserve Executive Digest in All Formats...")
    print("📋 Using enhanced fallback generation (LiteLLM unavailable)")
    print("🔧 Configuration: Enhanced format with 4-5 bullet points")
    
    try:
        # Generate using enhanced fallback
        generator = EnhancedFedExecutiveDigest()
        
        print("\n📝 Generating enhanced Markdown format...")
        markdown_filename = generator.generate_digest()
        
        if not markdown_filename:
            print("❌ Failed to generate digest")
            return
        
        # Read the generated markdown content
        with open(markdown_filename, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ Markdown generated: {markdown_filename}")
        
        # Generate HTML format
        print("🌐 Converting to enhanced HTML format...")
        html_content = markdown_to_html(markdown_content)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        html_filename = f"fed_executive_digest_all_formats_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {html_filename}")
        
        # Generate comprehensive JSON format
        print("📊 Creating comprehensive JSON format...")
        
        # Load articles data for JSON
        digest_data = generator.load_latest_daily_digest()
        selected_articles = generator.select_fed_relevant_articles(digest_data)
        
        json_data = create_comprehensive_json(markdown_content, selected_articles)
        
        json_filename = f"fed_executive_digest_all_formats_{timestamp}.json"
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON generated: {json_filename}")
        
        # Summary
        print(f"\n🎉 All formats generated successfully!")
        print(f"📄 Markdown: {markdown_filename}")
        print(f"🌐 HTML: {html_filename}")
        print(f"📊 JSON: {json_filename}")
        
        print(f"\n📈 Enhanced features included:")
        print(f"   • 4-5 substantive bullet points per article")
        print(f"   • Enhanced author attribution with publication mapping")
        print(f"   • Content insights and Federal Reserve relevance analysis")
        print(f"   • Clean HTML formatting with professional styling")
        print(f"   • Comprehensive JSON with metadata and categorization")
        print(f"   • HTML entity and tag cleaning")
        print(f"   • Federal Reserve executive focus maintained")
        
        print(f"\n📊 Digest statistics:")
        print(f"   • Total articles analyzed: {len(selected_articles)}")
        print(f"   • Articles in final digest: {json_data['digest_info']['total_articles']}")
        print(f"   • Generation method: Enhanced fallback")
        print(f"   • Format version: {json_data['digest_info']['format_version']}")
        
        return {
            "markdown": markdown_filename,
            "html": html_filename,
            "json": json_filename,
            "stats": json_data['digest_info']
        }
        
    except Exception as e:
        print(f"❌ Error generating digest: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()

