#!/usr/bin/env python3
"""
Generate HTML version of SF Fed Executive Daily News Digest
"""

import markdown
import os
from datetime import datetime

def convert_md_to_html(md_file_path, output_path):
    """Convert markdown digest to HTML with professional styling"""
    
    # Read the markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'toc'])
    
    # Add professional CSS styling
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .content {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            margin: 0;
            font-size: 2.2em;
            font-weight: 300;
        }}
        
        h2 {{
            color: #1e3a8a;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
            margin-top: 40px;
            font-size: 1.4em;
        }}
        
        h3 {{
            color: #374151;
            margin-top: 25px;
        }}
        
        .meta-info {{
            background: #e5e7eb;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 0.95em;
        }}
        
        .headline {{
            background: #f3f4f6;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        
        .headline strong {{
            color: #1e3a8a;
            display: block;
            margin-bottom: 5px;
        }}
        
        .source {{
            font-style: italic;
            color: #6b7280;
            font-size: 0.9em;
        }}
        
        .relevance {{
            font-style: italic;
            color: #059669;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        ul {{
            padding-left: 20px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        .executive-summary {{
            background: #fef3c7;
            border: 2px solid #f59e0b;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .implications {{
            background: #ecfdf5;
            border-left: 4px solid #10b981;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: #f3f4f6;
            border-radius: 5px;
            font-size: 0.9em;
            color: #6b7280;
        }}
        
        @media print {{
            body {{ background: white; }}
            .header {{ background: #1e3a8a !important; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>San Francisco Federal Reserve</h1>
        <h2 style="margin: 10px 0; border: none; color: #e5e7eb;">Executive Daily News Digest</h2>
        <div style="font-size: 1.1em; margin-top: 15px;">
            {datetime.now().strftime('%B %d, %Y')}
        </div>
    </div>
    
    <div class="content">
        {html_content}
    </div>
    
    <div class="footer">
        <p><strong>Federal Reserve Bank of San Francisco</strong><br>
        101 Market Street, San Francisco, CA 94105<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ HTML digest generated: {output_path}")

if __name__ == "__main__":
    # Install markdown if not available
    try:
        import markdown
    except ImportError:
        os.system("pip install markdown")
        import markdown
    
    md_file = "/workspace/daily_news_brief/sf_fed_executive_digest_20251118_comprehensive.md"
    html_file = "/workspace/daily_news_brief/sf_fed_executive_digest_20251118_comprehensive.html"
    
    convert_md_to_html(md_file, html_file)
