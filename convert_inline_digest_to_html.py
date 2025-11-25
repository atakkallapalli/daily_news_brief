

#!/usr/bin/env python3
"""
Convert Inline Prompt Digest to HTML
"""

import re
from datetime import datetime

def convert_inline_digest_to_html():
    # Read the markdown file
    with open('inline_prompt_digest_2025-11-25_00-50.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # HTML template with enhanced styling
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest - Inline Prompt Analysis</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1100px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 30px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 30px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .section { 
            margin: 25px 0; 
            padding: 20px; 
            border-radius: 8px;
            border-left: 4px solid #667eea;
            background: #f8fafc;
        }
        .fed-headlines { border-left-color: #e53e3e; background: #fed7d7; }
        .regional { border-left-color: #38a169; background: #c6f6d5; }
        .macro { border-left-color: #805ad5; background: #e9d8fd; }
        .banking { border-left-color: #dd6b20; background: #fbd38d; }
        .global { border-left-color: #0987a0; background: #bee3f8; }
        .tech { border-left-color: #d69e2e; background: #faf089; }
        .regulatory { border-left-color: #553c9a; background: #ddd6fe; }
        .implications { border-left-color: #319795; background: #b2f5ea; }
        .executive-summary { 
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border: none;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        h1 { margin: 0; font-size: 2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        h2 { 
            color: #2d3748; 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 10px; 
            margin-top: 0;
            font-size: 1.4em;
        }
        h3 { color: #4a5568; font-size: 1.2em; margin-bottom: 15px; }
        
        .meta { 
            color: #718096; 
            font-size: 0.95em; 
            margin: 8px 0;
            font-style: italic;
        }
        
        .article-entry {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .article-title {
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 8px;
        }
        
        .article-source {
            color: #718096;
            font-style: italic;
            font-size: 0.9em;
        }
        
        .bullet-point {
            margin: 8px 0;
            padding: 10px 15px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }
        
        .implications-list {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .implication-item {
            margin: 12px 0;
            padding: 12px;
            background: #f7fafc;
            border-left: 4px solid #319795;
            border-radius: 4px;
        }
        
        .implication-category {
            font-weight: bold;
            color: #2d3748;
        }
        
        a { color: #667eea; text-decoration: none; }
        a:hover { text-decoration: underline; color: #553c9a; }
        
        .footer {
            margin-top: 30px;
            padding: 20px;
            background: #edf2f7;
            border-radius: 8px;
            text-align: center;
            color: #4a5568;
            font-size: 0.9em;
            border-left: 4px solid #a0aec0;
        }
        
        .stats-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin: 0 5px;
        }
        
        .category-indicator {
            font-style: italic;
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 15px;
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
            html += f'<div class="header"><h1>{line[2:]}</h1>'
        elif line.startswith('**Date:**'):
            html += f'<div class="meta">{line} <span class="stats-badge">Inline Prompt Analysis</span></div>'
        elif line.startswith('**Generated:**'):
            html += f'<div class="meta">{line}</div>'
        elif line.startswith('**Total Articles:**'):
            html += f'<div class="meta">{line}</div></div>'
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
        elif line.startswith('### '):
            # Article headlines
            title = line[4:]  # Remove "### "
            html += f'<div class="article-entry"><h3>{title}</h3>'
        elif line.startswith('*') and line.endswith('*') and current_section in ['regional', 'macro', 'banking', 'global', 'tech', 'regulatory']:
            # Category descriptions
            html += f'<div class="category-indicator">{line}</div>'
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
        elif line.startswith('  - '):
            # Sub-bullets (article details)
            clean_line = line[4:]  # Remove "  - "
            # Clean up any HTML artifacts
            clean_line = re.sub(r'<a href="[^"]*"[^>]*>', '', clean_line)
            clean_line = re.sub(r'</a>', '', clean_line)
            clean_line = clean_line.replace('&nbsp;', ' ')
            if clean_line.strip():
                html += f'<div style="margin-left: 20px; color: #718096; font-size: 0.9em;">{clean_line}</div>'
        elif line and not line.startswith('*Generated using') and current_section == 'summary':
            # Executive summary content
            html += f'<p>{line}</p>'
        elif line.startswith('*Generated using'):
            # Footer
            html += f'</div><div class="footer">{line}<br>'
        elif line.startswith('*Source articles'):
            html += f'{line}</div>'
    
    # Close any remaining sections
    if current_section and current_section != 'summary':
        html += '</div>'
    
    html += """
    </div>
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"inline_prompt_digest_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

if __name__ == "__main__":
    convert_inline_digest_to_html()


