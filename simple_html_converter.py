
#!/usr/bin/env python3
"""
Simple HTML converter for enhanced summary
"""

import re
from datetime import datetime

def create_html_version():
    # Read the markdown file
    with open('enhanced_daily_summary_2025-11-25_00-29.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple HTML template
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest - Enhanced Summary</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        .header { background: #1e3a8a; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
        .section { margin: 20px 0; padding: 15px; background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 5px; }
        h1 { margin: 0; color: white; }
        h2 { color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }
        .article { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border: 1px solid #e5e7eb; }
        a { color: #2563eb; text-decoration: none; }
        a:hover { text-decoration: underline; }
        strong { color: #1f2937; }
        em { color: #6b7280; }
        .meta { color: #6b7280; font-size: 0.9em; }
    </style>
</head>
<body>
"""
    
    # Convert markdown to basic HTML
    lines = content.split('\n')
    in_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            html += '<br>\n'
            continue
            
        # Headers
        if line.startswith('# '):
            html += f'<div class="header"><h1>{line[2:]}</h1></div>\n'
        elif line.startswith('## '):
            if in_section:
                html += '</div>\n'
            html += f'<div class="section"><h2>{line[3:]}</h2>\n'
            in_section = True
        elif line.startswith('**Date:**') or line.startswith('**Generated:**') or line.startswith('**Total Articles:**'):
            html += f'<p class="meta">{line}</p>\n'
        elif line.startswith('*') and not line.startswith('**'):
            html += f'<p class="meta">{line}</p>\n'
        elif line.startswith('**') and line.endswith('**'):
            # Article headlines
            clean_line = line[2:-2]  # Remove ** from both ends
            # Convert markdown links to HTML
            clean_line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', clean_line)
            html += f'<div class="article"><strong>{clean_line}</strong>\n'
        elif line.startswith('   - **'):
            # Article details
            clean_line = line[5:]  # Remove leading spaces and dash
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', clean_line)
            clean_line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', clean_line)
            html += f'<div class="meta">{clean_line}</div>\n'
        elif line.startswith('• **'):
            # Bullet points with links
            clean_line = line[2:]  # Remove bullet
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', clean_line)
            clean_line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', clean_line)
            html += f'<div class="article">• {clean_line}</div>\n'
        elif line.startswith('  - '):
            # Sub-bullets
            clean_line = line[4:]  # Remove leading spaces and dash
            html += f'<div class="meta">  - {clean_line}</div>\n'
        elif line.startswith('• '):
            # Regular bullets
            clean_line = line[2:]  # Remove bullet
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', clean_line)
            html += f'<p>• {clean_line}</p>\n'
        else:
            # Regular paragraphs
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            clean_line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', clean_line)
            html += f'<p>{clean_line}</p>\n'
    
    if in_section:
        html += '</div>\n'
    
    html += """
</body>
</html>"""
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"enhanced_daily_summary_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

if __name__ == "__main__":
    create_html_version()

