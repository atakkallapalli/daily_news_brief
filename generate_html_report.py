
#!/usr/bin/env python3
"""
Generate a static HTML report from the collected news data
"""

import json
from datetime import datetime
import re

def clean_description(desc):
    """Clean HTML tags and entities from description"""
    if not desc:
        return ""
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', desc)
    # Replace HTML entities
    clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return clean[:200] + "..." if len(clean) > 200 else clean

def generate_html_report():
    """Generate HTML report from JSON data"""
    
    # Load data
    with open('/workspace/articles_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Format date
    collection_date = datetime.fromisoformat(data['collection_date'])
    formatted_date = collection_date.strftime('%B %d, %Y at %I:%M %p UTC')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Economic & Financial News Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 15px;
            font-weight: 300;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .topic-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            overflow: hidden;
        }}
        
        .topic-header {{
            background: #34495e;
            color: white;
            padding: 25px;
            font-size: 1.4em;
            font-weight: 600;
        }}
        
        .topic-content {{
            padding: 30px;
        }}
        
        .article {{
            border-bottom: 2px solid #ecf0f1;
            padding: 25px 0;
            transition: all 0.3s ease;
        }}
        
        .article:last-child {{
            border-bottom: none;
        }}
        
        .article:hover {{
            background-color: #f8f9fa;
            padding-left: 10px;
        }}
        
        .article-title {{
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .article-title a {{
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .article-title a:hover {{
            color: #3498db;
        }}
        
        .article-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}
        
        .article-source {{
            background: #e8f4fd;
            color: #2980b9;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .article-date {{
            color: #7f8c8d;
            font-style: italic;
        }}
        
        .article-summary {{
            color: #555;
            line-height: 1.6;
            font-size: 1em;
        }}
        
        .more-articles {{
            text-align: center;
            margin-top: 25px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            color: #7f8c8d;
            font-style: italic;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: #34495e;
            color: white;
            border-radius: 12px;
        }}
        
        .sources-list {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        .sources-list h3 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .sources-list ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .sources-list li {{
            background: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            color: #34495e;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2.2em;
            }}
            
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .article-meta {{
                flex-direction: column;
                gap: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Economic & Financial News Report</h1>
            <p>Comprehensive Analysis of Market Trends and Economic Indicators</p>
            <p><strong>Collection Period:</strong> Past 7 Days | <strong>Generated:</strong> {formatted_date}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{data['total_articles']}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(data['topics'])}</div>
                <div class="stat-label">Topic Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(data['sources_covered'])}</div>
                <div class="stat-label">News Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">7</div>
                <div class="stat-label">Days Coverage</div>
            </div>
        </div>
        
        <div class="sources-list">
            <h3>Sources Covered:</h3>
            <ul>
"""
    
    for source in data['sources_covered']:
        html_content += f"                <li>{source}</li>\n"
    
    html_content += """            </ul>
        </div>
        
"""
    
    # Add topic sections
    for topic, articles in data['topics'].items():
        html_content += f"""        <div class="topic-section">
            <div class="topic-header">
                {topic} ({len(articles)} articles)
            </div>
            <div class="topic-content">
"""
        
        # Show first 5 articles
        for article in articles[:5]:
            clean_desc = clean_description(article.get('description', ''))
            html_content += f"""                <div class="article">
                    <div class="article-title">
                        <a href="{article['url']}" target="_blank">{article['title']}</a>
                    </div>
                    <div class="article-meta">
                        <span class="article-source">{article['source']}</span>
                        <span class="article-date">{article.get('published', 'Date not available')}</span>
                    </div>
"""
            if clean_desc:
                html_content += f"""                    <div class="article-summary">
                        {clean_desc}
                    </div>
"""
            html_content += "                </div>\n"
        
        # Show count of remaining articles
        if len(articles) > 5:
            html_content += f"""                <div class="more-articles">
                    ... and {len(articles) - 5} more articles in this category
                </div>
"""
        
        html_content += """            </div>
        </div>
        
"""
    
    html_content += f"""        <div class="footer">
            <h3>Report Summary</h3>
            <p>This report aggregates economic and financial news from major sources including Bloomberg, Reuters, Fox News, NBC, AP News, WSJ, and LinkedIn over the past week.</p>
            <p>The analysis covers key economic indicators: unemployment trends, inflation data, market risk assessments, and banking sector developments.</p>
            <p><strong>Data Collection Method:</strong> Automated aggregation from publicly available RSS feeds and Google News</p>
            <p><strong>Generated on:</strong> {formatted_date}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save the HTML file
    with open('/workspace/economic_news_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML report generated successfully: economic_news_report.html")

if __name__ == "__main__":
    generate_html_report()

