



#!/usr/bin/env python3
"""
Convert SF Fed Executive Digest to HTML
"""

import re
from datetime import datetime

def convert_sf_fed_digest_to_html():
    # Read the markdown file
    with open('sf_fed_executive_digest_2025-11-25_01-05.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # HTML template with professional SF Fed styling
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>San Francisco Federal Reserve Executive Daily News Digest</title>
    <style>
        body { 
            font-family: 'Georgia', 'Times New Roman', serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6;
            color: #1a202c;
            background: #f8fafc;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #1a365d, #2c5282); 
            color: white; 
            padding: 35px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 35px; 
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        .section { 
            margin: 30px 0; 
            padding: 25px; 
            border-radius: 8px;
            border-left: 5px solid #2c5282;
            background: #f7fafc;
        }
        .fed-headlines { border-left-color: #c53030; background: #fed7d7; }
        .regional { border-left-color: #38a169; background: #c6f6d5; }
        .macro { border-left-color: #805ad5; background: #e9d8fd; }
        .banking { border-left-color: #d69e2e; background: #faf089; }
        .global { border-left-color: #0987a0; background: #bee3f8; }
        .tech { border-left-color: #dd6b20; background: #fbd38d; }
        .regulatory { border-left-color: #553c9a; background: #ddd6fe; }
        .implications { border-left-color: #319795; background: #b2f5ea; }
        .executive-summary { 
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border: none;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        h1 { margin: 0; font-size: 2.2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        h2 { 
            color: #2d3748; 
            border-bottom: 3px solid #2c5282; 
            padding-bottom: 12px; 
            margin-top: 0;
            font-size: 1.5em;
        }
        h3 { color: #4a5568; font-size: 1.2em; margin-bottom: 15px; }
        
        .meta { 
            color: #718096; 
            font-size: 0.95em; 
            margin: 10px 0;
            font-style: italic;
        }
        
        .purpose {
            background: #edf2f7;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #4299e1;
            font-style: italic;
        }
        
        .article-entry {
            margin: 20px 0;
            padding: 18px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        
        .article-title {
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .article-source {
            color: #718096;
            font-style: italic;
            font-size: 0.9em;
        }
        
        .bullet-point {
            margin: 12px 0;
            padding: 15px 20px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #2c5282;
        }
        
        .implications-list {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .implication-item {
            margin: 15px 0;
            padding: 15px;
            background: #f7fafc;
            border-left: 5px solid #319795;
            border-radius: 6px;
        }
        
        .implication-category {
            font-weight: bold;
            color: #2d3748;
            font-size: 1.05em;
        }
        
        a { color: #2c5282; text-decoration: none; }
        a:hover { text-decoration: underline; color: #1a365d; }
        
        .footer {
            margin-top: 40px;
            padding: 25px;
            background: #edf2f7;
            border-radius: 10px;
            text-align: center;
            color: #4a5568;
            font-size: 0.9em;
            border-left: 5px solid #a0aec0;
        }
        
        .sf-fed-badge {
            display: inline-block;
            background: #2c5282;
            color: white;
            padding: 6px 15px;
            border-radius: 25px;
            font-size: 0.85em;
            margin: 0 8px;
        }
        
        .category-indicator {
            font-style: italic;
            color: #718096;
            font-size: 0.95em;
            margin-bottom: 18px;
            padding: 10px;
            background: #f1f5f9;
            border-radius: 5px;
        }
        
        .headline-number {
            background: #2c5282;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9em;
            margin-right: 10px;
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
            html += f'<div class="header"><h1>{line[2:]} <span class="sf-fed-badge">Executive Leadership</span></h1>'
        elif line.startswith('**Date:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Generated:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Audience:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Purpose:**'):
            purpose_text = line[12:]  # Remove "**Purpose:** "
            html += f'<div class="purpose"><strong>Purpose:</strong> {purpose_text}</div></div>'
        elif line.startswith('---') and len(line) == 3:
            continue  # Skip separators
        elif line.startswith('## 1. Top 5 Headlines'):
            html += '<div class="section fed-headlines"><h2>1. Top 5 Headlines Relevant to the Federal Reserve</h2>'
            current_section = 'fed_headlines'
        elif line.startswith('## 2. 12th District'):
            html += '</div><div class="section regional"><h2>2. 12th District Regional Economic & Labor Signals</h2>'
            current_section = 'regional'
        elif line.startswith('## 3. National Macro'):
            html += '</div><div class="section macro"><h2>3. National Macroeconomic & Monetary Policy Developments</h2>'
            current_section = 'macro'
        elif line.startswith('## 4. Financial System'):
            html += '</div><div class="section banking"><h2>4. Financial System & Banking Stability Watch</h2>'
            current_section = 'banking'
        elif line.startswith('## 5. Global'):
            html += '</div><div class="section global"><h2>5. Global & Pacific Rim Insights (SF Fed Priority)</h2>'
            current_section = 'global'
        elif line.startswith('## 6. Technology'):
            html += '</div><div class="section tech"><h2>6. Technology, Cyber, and Payments Developments</h2>'
            current_section = 'tech'
        elif line.startswith('## 7. Regulatory'):
            html += '</div><div class="section regulatory"><h2>7. Regulatory, Legislative, and Federal Government Updates</h2>'
            current_section = 'regulatory'
        elif line.startswith('## 8. Implications'):
            html += '</div><div class="section implications"><h2>8. Implications for SF Fed</h2><div class="implications-list">'
            current_section = 'implications'
        elif line.startswith('## 9. Executive Summary'):
            html += '</div></div><div class="executive-summary"><h2>9. Executive Summary (&lt;150 words)</h2>'
            current_section = 'summary'
        elif line.startswith('*') and line.endswith('*') and current_section in ['fed_headlines', 'regional', 'macro', 'banking', 'global', 'tech', 'regulatory', 'implications', 'summary']:
            # Category descriptions and summary descriptions
            html += f'<div class="category-indicator">{line}</div>'
        elif line.startswith('**') and '. [' in line and current_section == 'fed_headlines':
            # Fed headlines with numbers
            # Extract number and format
            number_match = re.match(r'\*\*(\d+)\. (.+?)\*\*', line)
            if number_match:
                number = number_match.group(1)
                rest = number_match.group(2)
                # Convert markdown links to HTML
                rest = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', rest)
                rest = re.sub(r'\*(.+?)\*', r'<em>\1</em>', rest)
                html += f'<div class="article-entry"><div class="article-title"><span class="headline-number">{number}</span>{rest}</div>'
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
            clean_line = re.sub(r'\*\*\[(.+?)\]\((.+?)\)\*\*', r'<strong><a href="\2" target="_blank">\1</a></strong>', clean_line)
            clean_line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', clean_line)
            html += f'<div class="bullet-point">{clean_line}</div>'
        elif line.startswith('• '):
            # Regular bullets
            clean_line = line[2:]  # Remove "• "
            html += f'<div class="bullet-point">{clean_line}</div>'
        elif line and not line.startswith('*Generated following') and current_section == 'summary':
            # Executive summary content
            html += f'<p>{line}</p>'
        elif line.startswith('*Generated following'):
            # Footer
            html += f'</div><div class="footer">{line}<br>'
        elif line.startswith('*Analytical'):
            html += f'{line}<br>'
        elif line.startswith('*18 articles'):
            html += f'{line}<br>'
        elif line.startswith('*Focus:'):
            html += f'{line}</div>'
        elif line and current_section == 'fed_headlines' and not line.startswith('**'):
            # Article summary lines for headlines
            # Clean up any HTML artifacts
            clean_line = re.sub(r'<a href="[^"]*"[^>]*>', '', line)
            clean_line = re.sub(r'</a>', '', clean_line)
            clean_line = clean_line.replace('&nbsp;', ' ')
            if clean_line.strip() and len(clean_line.strip()) > 10:
                html += f'<div style="margin: 10px 0; color: #4a5568; font-size: 0.95em;">{clean_line}</div></div>'
    
    # Close any remaining sections
    if current_section and current_section != 'summary':
        html += '</div>'
    
    html += """
    </div>
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"sf_fed_executive_digest_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

if __name__ == "__main__":
    convert_sf_fed_digest_to_html()




