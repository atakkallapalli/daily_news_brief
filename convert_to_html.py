#!/usr/bin/env python3
"""
Convert markdown summary to HTML
"""

import re
from datetime import datetime

def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML with enhanced styling"""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest - Enhanced Summary</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6;
            color: #333;
            background-color: #f8fafc;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header { 
            background: linear-gradient(135deg, #1e3a8a, #3b82f6); 
            color: white;
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
            text-align: center;
        }
        .section { 
            margin-bottom: 30px; 
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        .fed-headlines {
            border-left: 4px solid #dc2626;
            background: #fef2f2;
        }
        .regional {
            border-left: 4px solid #059669;
            background: #ecfdf5;
        }
        .macro {
            border-left: 4px solid #7c3aed;
            background: #f3f4f6;
        }
        .banking {
            border-left: 4px solid #ea580c;
            background: #fff7ed;
        }
        .global {
            border-left: 4px solid #0891b2;
            background: #f0f9ff;
        }
        .tech {
            border-left: 4px solid #7c2d12;
            background: #fef3c7;
        }
        .regulatory {
            border-left: 4px solid #4338ca;
            background: #eef2ff;
        }
        .implications {
            background: #ecfdf5;
            border-left: 4px solid #10b981;
        }
        .executive-summary {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        h1 { 
            color: white; 
            margin: 0; 
            font-size: 2.2em;
        }
        h2 { 
            color: #1e3a8a; 
            border-bottom: 2px solid #3b82f6; 
            padding-bottom: 10px; 
            margin-top: 0;
            font-size: 1.4em;
        }
        h3 { 
            color: #374151; 
            font-size: 1.2em;
        }
        .meta { 
            color: #6b7280; 
            font-size: 0.9em; 
            margin: 5px 0; 
            font-style: italic;
        }
        .article-item {
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
        }
        .article-title {
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 8px;
        }
        .article-details {
            font-size: 0.9em;
            color: #6b7280;
            margin: 4px 0;
        }
        .article-summary {
            margin: 8px 0;
            color: #374151;
        }
        .article-quote {
            font-style: italic;
            color: #4b5563;
            border-left: 3px solid #d1d5db;
            padding-left: 12px;
            margin: 8px 0;
        }
        .relevance {
            font-size: 0.85em;
            color: #059669;
            font-weight: 500;
        }
        ul { 
            padding-left: 20px; 
        }
        li { 
            margin: 8px 0; 
        }
        strong { 
            color: #1f2937; 
        }
        em { 
            color: #6b7280; 
        }
        a {
            color: #2563eb;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .stats {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            text-align: center;
        }
        .bullet-point {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #3b82f6;
        }
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
    
    # Convert markdown to HTML
    html_content = markdown_content
    
    # Convert headers
    html_content = re.sub(r'^# (.+)$', r'<div class="header"><h1>\1</h1></div>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 1\. (.+)$', r'<div class="section fed-headlines"><h2>1. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 2\. (.+)$', r'</div><div class="section regional"><h2>2. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 3\. (.+)$', r'</div><div class="section macro"><h2>3. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 4\. (.+)$', r'</div><div class="section banking"><h2>4. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 5\. (.+)$', r'</div><div class="section global"><h2>5. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 6\. (.+)$', r'</div><div class="section tech"><h2>6. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 7\. (.+)$', r'</div><div class="section regulatory"><h2>7. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 8\. (.+)$', r'</div><div class="section implications"><h2>8. \1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## 9\. (.+)$', r'</div><div class="executive-summary"><h2>9. \1</h2>', html_content, flags=re.MULTILINE)
    
    # Convert bold and italic
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # Convert links
    html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
    
    # Convert bullet points
    html_content = re.sub(r'^• (.+)$', r'<div class="bullet-point">• \1</div>', html_content, flags=re.MULTILINE)
    
    # Convert line breaks
    html_content = html_content.replace('\n\n', '</p><p>')
    html_content = html_content.replace('\n', '<br>')
    html_content = f'<p>{html_content}</p>'
    
    # Clean up extra tags
    html_content = html_content.replace('<p></p>', '')
    html_content = html_content.replace('<p><br></p>', '')
    
    # Add closing div
    html_content += '</div>'
    
    return html_template.format(content=html_content)

def main():
    # Read the markdown file
    with open('enhanced_daily_summary_2025-11-25_00-29.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content)
    
    # Save HTML file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"enhanced_daily_summary_{timestamp}.html"
    
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML version saved to: {html_filename}")
    return html_filename

if __name__ == "__main__":
    main()
