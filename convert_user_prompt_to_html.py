


#!/usr/bin/env python3
"""
Convert User Prompt Digest to HTML
"""

import re
from datetime import datetime

def convert_user_prompt_digest_to_html():
    # Read the markdown file
    with open('user_prompt_digest_2025-11-25_00-54.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # HTML template with professional styling
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily News Digest for Federal Reserve Executives</title>
    <style>
        body { 
            font-family: 'Times New Roman', Times, serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 30px; 
            line-height: 1.7;
            color: #1a202c;
            background: #f7fafc;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #2d3748, #4a5568); 
            color: white; 
            padding: 30px; 
            border-radius: 8px; 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .article { 
            margin: 30px 0; 
            padding: 25px; 
            background: #f8fafc; 
            border-left: 5px solid #3182ce; 
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .article-title { 
            font-size: 1.3em; 
            font-weight: bold; 
            color: #2d3748; 
            margin-bottom: 15px;
            line-height: 1.4;
        }
        .author { 
            color: #4a5568; 
            font-style: italic; 
            margin-bottom: 15px;
            font-size: 0.95em;
        }
        .summary { 
            margin: 15px 0; 
        }
        .summary h4 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .bullet { 
            margin: 8px 0; 
            padding-left: 20px;
            color: #4a5568;
        }
        .read-more { 
            margin-top: 20px; 
            padding-top: 15px;
            border-top: 1px solid #e2e8f0;
        }
        .read-more a { 
            color: #3182ce; 
            text-decoration: none; 
            font-weight: 500;
            padding: 8px 16px;
            background: #ebf8ff;
            border-radius: 4px;
            display: inline-block;
        }
        .read-more a:hover { 
            background: #bee3f8;
            text-decoration: underline; 
        }
        h1 { 
            margin: 0; 
            font-size: 1.8em;
        }
        .meta { 
            color: #718096; 
            font-size: 0.9em; 
            margin: 10px 0;
        }
        .footer {
            margin-top: 40px;
            padding: 20px;
            background: #edf2f7;
            border-radius: 5px;
            color: #4a5568;
            font-size: 0.9em;
            border-left: 4px solid #a0aec0;
        }
        .divider {
            border: none;
            height: 2px;
            background: linear-gradient(to right, #e2e8f0, #cbd5e0, #e2e8f0);
            margin: 30px 0;
        }
        .format-badge {
            display: inline-block;
            background: #3182ce;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
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
            html += f'<div class="header"><h1>{line[2:]} <span class="format-badge">User Prompt Format</span></h1>'
        elif line.startswith('**Date:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Generated:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Articles Analyzed:**'):
            html += f'<div class="meta">{line}</div></div>'
        elif line.startswith('---') and len(line) == 3:
            # Article separator - process previous article if exists
            if current_article.get('title'):
                html += format_article_html(current_article)
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
        elif line.startswith('*This digest follows'):
            # Footer
            html += f'<div class="footer">{line}<br>'
        elif line.startswith('*Generated on'):
            html += f'{line}</div>'
        elif line.startswith('- *') and 'article' in line:
            # Footer bullet points
            clean_line = line[2:]  # Remove "- "
            html += f'{clean_line}<br>'
    
    # Process last article if exists
    if current_article.get('title'):
        html += format_article_html(current_article)
    
    html += """
    </div>
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"user_prompt_digest_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

def format_article_html(article):
    """Format individual article as HTML"""
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
    convert_user_prompt_digest_to_html()



