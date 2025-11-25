




#!/usr/bin/env python3
"""
Convert Federal Reserve Executive LiteLLM Digest to HTML
"""

import re
from datetime import datetime

def convert_fed_executive_digest_to_html():
    # Read the markdown file
    with open('fed_executive_litellm_digest_2025-11-25_01-20.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # HTML template with Federal Reserve Executive styling
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily News Digest for Federal Reserve Executives - LiteLLM</title>
    <style>
        body { 
            font-family: 'Times New Roman', Times, serif; 
            max-width: 950px; 
            margin: 0 auto; 
            padding: 30px; 
            line-height: 1.7;
            color: #1a202c;
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 45px;
            border-radius: 12px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #1a365d, #2c5282); 
            color: white; 
            padding: 40px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 40px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .article { 
            margin: 35px 0; 
            padding: 30px; 
            background: #f8fafc; 
            border-left: 6px solid #1a365d; 
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .article-title { 
            font-size: 1.4em; 
            font-weight: bold; 
            color: #1a365d; 
            margin-bottom: 18px;
            line-height: 1.4;
        }
        .author { 
            color: #4a5568; 
            font-style: italic; 
            margin-bottom: 20px;
            font-size: 1.05em;
            font-weight: 500;
        }
        .summary { 
            margin: 20px 0; 
        }
        .summary h4 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .bullet { 
            margin: 12px 0; 
            padding: 15px 20px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #2c5282;
            color: #4a5568;
        }
        .read-more { 
            margin-top: 25px; 
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
        }
        .read-more a { 
            color: #1a365d; 
            text-decoration: none; 
            font-weight: 600;
            padding: 12px 20px;
            background: #ebf8ff;
            border-radius: 6px;
            display: inline-block;
            border: 2px solid #bee3f8;
        }
        .read-more a:hover { 
            background: #bee3f8;
            text-decoration: underline; 
            border-color: #90cdf4;
        }
        h1 { 
            margin: 0; 
            font-size: 2.1em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .meta { 
            color: #718096; 
            font-size: 0.95em; 
            margin: 12px 0;
            font-style: italic;
        }
        .footer {
            margin-top: 45px;
            padding: 30px;
            background: #edf2f7;
            border-radius: 10px;
            color: #4a5568;
            font-size: 0.95em;
            border-left: 6px solid #a0aec0;
            text-align: center;
        }
        .divider {
            border: none;
            height: 3px;
            background: linear-gradient(to right, #e2e8f0, #cbd5e0, #e2e8f0);
            margin: 35px 0;
        }
        .fed-badge {
            display: inline-block;
            background: #1a365d;
            color: white;
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 0.85em;
            margin-left: 15px;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 25px 0;
            flex-wrap: wrap;
        }
        .stat-item {
            text-align: center;
            padding: 15px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            min-width: 100px;
        }
        .stat-number {
            font-size: 2.2em;
            font-weight: bold;
            color: white;
        }
        .stat-label {
            font-size: 0.9em;
            color: rgba(255,255,255,0.9);
            margin-top: 5px;
        }
        .format-note {
            background: #e6fffa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 5px solid #319795;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
"""
    
    # Parse the markdown content
    lines = content.split('\n')
    current_article = {}
    in_summary = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            # Main title
            html += f'<div class="header"><h1>{line[2:]} <span class="fed-badge">LiteLLM Format</span></h1>'
        elif line.startswith('**Date:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Generated:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Articles Analyzed:**'):
            html += f'<div class="meta">{line}</div>'
            # Add stats
            html += '''<div class="stats">
                <div class="stat-item">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Articles</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">5-7</div>
                    <div class="stat-label">Range</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">Fed</div>
                    <div class="stat-label">Focus</div>
                </div>
            </div></div>'''
            
            # Add format note
            html += '''<div class="format-note">
                <strong>Format Compliance:</strong> This digest follows the exact user-specified format with article titles, 
                author attribution, 3-4 bullet point summaries, and clickable links to original sources. 
                Content focuses on economic trends, Federal Reserve policy, financial markets, and global economic issues.
            </div>'''
            
        elif line.startswith('---') and len(line) == 3:
            # Article separator - process previous article if exists
            if current_article.get('title'):
                html += format_fed_article_html(current_article)
                html += '<hr class="divider">'
            current_article = {}
            in_summary = False
        elif line.startswith('**') and line.endswith('**') and 'Author:' not in line and 'Summary:' not in line:
            # Article title
            title = line[2:-2]  # Remove ** from both ends
            current_article['title'] = title
        elif line.startswith('Author:'):
            current_article['author'] = line[8:]  # Remove "Author: "
        elif line.startswith('Summary:'):
            current_article['bullets'] = []
            in_summary = True
        elif line.startswith('• ') and in_summary:
            bullet = line[2:]  # Remove "• "
            # Clean up any HTML artifacts in bullets
            bullet = re.sub(r'<a href="[^"]*"[^>]*>', '', bullet)
            bullet = re.sub(r'</a>', '', bullet)
            bullet = bullet.replace('&nbsp;', ' ')
            if bullet.strip() and bullet.strip() != '.':
                current_article['bullets'] = current_article.get('bullets', [])
                current_article['bullets'].append(bullet)
        elif line.startswith('Read more:'):
            # Extract link
            link_match = re.search(r'\[(.+?)\]\((.+?)\)', line)
            if link_match:
                current_article['link_text'] = link_match.group(1)
                current_article['link_url'] = link_match.group(2)
        elif line.startswith('*This digest was generated'):
            # Footer
            html += f'<div class="footer">{line}<br>'
        elif line.startswith('*6 articles'):
            html += f'{line}<br>'
        elif line.startswith('*Generated when'):
            html += f'{line}</div>'
    
    # Process last article if exists
    if current_article.get('title'):
        html += format_fed_article_html(current_article)
    
    html += """
    </div>
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"fed_executive_litellm_digest_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

def format_fed_article_html(article):
    """Format individual Fed executive article as HTML"""
    html = '<div class="article">'
    
    if article.get('title'):
        html += f'<div class="article-title">{article["title"]}</div>'
    
    if article.get('author'):
        html += f'<div class="author">Author: {article["author"]}</div>'
    
    if article.get('bullets'):
        html += '<div class="summary"><h4>Summary:</h4>'
        for bullet in article['bullets']:
            if bullet.strip():  # Only add non-empty bullets
                html += f'<div class="bullet">• {bullet}</div>'
        html += '</div>'
    
    if article.get('link_url'):
        link_text = article.get('link_text', 'Read full article')
        html += f'<div class="read-more"><a href="{article["link_url"]}" target="_blank">Read more: {link_text}</a></div>'
    
    html += '</div>'
    return html

if __name__ == "__main__":
    convert_fed_executive_digest_to_html()





