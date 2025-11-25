




#!/usr/bin/env python3
"""
Convert LiteLLM Digest to HTML
"""

import re
from datetime import datetime

def convert_litellm_digest_to_html():
    # Read the markdown file
    with open('robust_litellm_digest_2025-11-25_01-12.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # HTML template with modern LiteLLM styling
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Financial & Economic News Digest - LiteLLM Analysis</title>
    <style>
        body { 
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1100px; 
            margin: 0 auto; 
            padding: 25px; 
            line-height: 1.7;
            color: #1a202c;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 45px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #4c51bf, #667eea); 
            color: white; 
            padding: 40px; 
            border-radius: 12px; 
            text-align: center; 
            margin-bottom: 40px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .section { 
            margin: 35px 0; 
            padding: 30px; 
            border-radius: 10px;
            border-left: 6px solid #4c51bf;
            background: #f8fafc;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .executive-summary { border-left-color: #e53e3e; background: #fed7d7; }
        .fed-policy { border-left-color: #38a169; background: #c6f6d5; }
        .economic { border-left-color: #805ad5; background: #e9d8fd; }
        .banking { border-left-color: #d69e2e; background: #faf089; }
        .technology { border-left-color: #dd6b20; background: #fbd38d; }
        .global { border-left-color: #0987a0; background: #bee3f8; }
        .implications { 
            background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
            border: none;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        }
        
        h1 { margin: 0; font-size: 2.3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        h2 { 
            color: #2d3748; 
            border-bottom: 4px solid #4c51bf; 
            padding-bottom: 15px; 
            margin-top: 0;
            font-size: 1.6em;
        }
        h3 { color: #4a5568; font-size: 1.3em; margin-bottom: 18px; }
        
        .meta { 
            color: #718096; 
            font-size: 0.95em; 
            margin: 12px 0;
            font-style: italic;
        }
        
        .generation-method {
            background: #edf2f7;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #4299e1;
            font-weight: 500;
        }
        
        .article-entry {
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
        }
        
        .article-title {
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 12px;
            font-size: 1.1em;
        }
        
        .article-source {
            color: #718096;
            font-style: italic;
            font-size: 0.9em;
        }
        
        .bullet-point {
            margin: 15px 0;
            padding: 18px 25px;
            background: white;
            border-radius: 8px;
            border-left: 5px solid #4c51bf;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        
        .implication-item {
            margin: 18px 0;
            padding: 18px;
            background: #f7fafc;
            border-left: 6px solid #319795;
            border-radius: 8px;
        }
        
        .implication-category {
            font-weight: bold;
            color: #2d3748;
            font-size: 1.1em;
        }
        
        a { color: #4c51bf; text-decoration: none; }
        a:hover { text-decoration: underline; color: #553c9a; }
        
        .footer {
            margin-top: 45px;
            padding: 30px;
            background: #edf2f7;
            border-radius: 12px;
            text-align: center;
            color: #4a5568;
            font-size: 0.95em;
            border-left: 6px solid #a0aec0;
        }
        
        .litellm-badge {
            display: inline-block;
            background: #4c51bf;
            color: white;
            padding: 8px 18px;
            border-radius: 25px;
            font-size: 0.85em;
            margin: 0 10px;
        }
        
        .analysis-stats {
            display: flex;
            justify-content: space-around;
            margin: 25px 0;
            flex-wrap: wrap;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            margin: 5px;
            min-width: 120px;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: white;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: rgba(255,255,255,0.9);
        }
    </style>
</head>
<body>
    <div class="container">
"""
    
    # Parse and convert the markdown content
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            # Main title
            html += f'<div class="header"><h1>{line[2:]} <span class="litellm-badge">LiteLLM Analysis</span></h1>'
        elif line.startswith('**Date:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Generated:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Articles Analyzed:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Generation Method:**'):
            method_text = line[21:]  # Remove "**Generation Method:** "
            html += f'<div class="generation-method"><strong>Generation Method:</strong> {method_text}</div>'
            # Add analysis stats
            html += '''<div class="analysis-stats">
                <div class="stat-item">
                    <div class="stat-number">28</div>
                    <div class="stat-label">Articles</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Sections</div>
                </div>
            </div></div>'''
        elif line.startswith('---') and len(line) == 3:
            continue  # Skip separators
        elif line.startswith('## Executive Summary'):
            html += '<div class="section executive-summary"><h2>Executive Summary</h2>'
            current_section = 'executive'
        elif line.startswith('## Federal Reserve'):
            html += '</div><div class="section fed-policy"><h2>Federal Reserve & Monetary Policy</h2>'
            current_section = 'fed'
        elif line.startswith('## Economic Indicators'):
            html += '</div><div class="section economic"><h2>Economic Indicators & Market Conditions</h2>'
            current_section = 'economic'
        elif line.startswith('## Banking'):
            html += '</div><div class="section banking"><h2>Banking & Financial Services</h2>'
            current_section = 'banking'
        elif line.startswith('## Technology'):
            html += '</div><div class="section technology"><h2>Technology & Innovation in Finance</h2>'
            current_section = 'technology'
        elif line.startswith('## Global'):
            html += '</div><div class="section global"><h2>Global Economic Developments</h2>'
            current_section = 'global'
        elif line.startswith('## Key Implications'):
            html += '</div><div class="implications"><h2>Key Implications</h2>'
            current_section = 'implications'
        elif line.startswith('**') and line.endswith('**)') and current_section in ['fed', 'economic']:
            # Article titles
            # Extract title and source
            title_match = re.match(r'\*\*(.+?)\*\* \(\*(.+?)\*\)', line)
            if title_match:
                title = title_match.group(1)
                source = title_match.group(2)
                html += f'<div class="article-entry"><div class="article-title">{title}</div><div class="article-source">Source: {source}</div></div>'
        elif line.startswith('• **') and current_section == 'implications':
            # Implications bullets
            clean_line = line[2:]  # Remove "• "
            # Extract category and description
            if ':**' in clean_line:
                parts = clean_line.split(':**', 1)
                category = parts[0].replace('**', '')
                description = parts[1].strip() if len(parts) > 1 else ''
                html += f'<div class="implication-item"><span class="implication-category">{category}:</span> {description}</div>'
            else:
                html += f'<div class="implication-item">{clean_line}</div>'
        elif line.startswith('• **'):
            # Article bullets with links
            clean_line = line[2:]  # Remove "• "
            # Convert markdown links to HTML
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', clean_line)
            clean_line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', clean_line)
            html += f'<div class="bullet-point">{clean_line}</div>'
        elif line.startswith('• '):
            # Regular bullets
            clean_line = line[2:]  # Remove "• "
            html += f'<div class="bullet-point">{clean_line}</div>'
        elif line and not line.startswith('*Generated using') and current_section:
            # Regular content
            if line:
                html += f'<p>{line}</p>'
        elif line.startswith('*Generated using'):
            # Footer
            html += f'</div><div class="footer">{line}<br>'
        elif line.startswith('*28 articles') or line.startswith('*{total_articles}'):
            html += f'{line.replace("{total_articles}", "28")}<br>'
        elif line.startswith('*Analysis includes'):
            html += f'{line}</div>'
    
    # Close any remaining sections
    if current_section and current_section != 'implications':
        html += '</div>'
    
    html += """
    </div>
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"litellm_digest_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

if __name__ == "__main__":
    convert_litellm_digest_to_html()





