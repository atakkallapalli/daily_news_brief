#!/usr/bin/env python3
"""
SF Fed Executive Dashboard
Displays the San Francisco Federal Reserve Executive Daily News Digest
"""

from flask import Flask, render_template_string, jsonify
import os
import re
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# SF Fed Executive Dashboard Template
SF_FED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Fed Executive Daily News Digest</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            color: #1e3c72;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            color: #2a5298;
            margin-bottom: 15px;
        }
        
        .header .date {
            font-size: 1.1em;
            color: #666;
        }
        
        .fed-seal {
            width: 80px;
            height: 80px;
            background: #1e3c72;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 2em;
            font-weight: bold;
        }
        
        .digest-grid {
            display: grid;
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .section-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border-left: 5px solid #1e3c72;
        }
        
        .section-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3c72;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-icon {
            font-size: 1.2em;
        }
        
        .article-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 3px solid #2a5298;
        }
        
        .article-title {
            font-weight: 600;
            color: #1e3c72;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .article-content {
            color: #555;
            line-height: 1.5;
            margin-bottom: 8px;
        }
        
        .article-source {
            font-size: 0.9em;
            color: #888;
            font-style: italic;
        }
        
        .implications-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .implication-item {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1976d2;
        }
        
        .implication-title {
            font-weight: 600;
            color: #1976d2;
            margin-bottom: 8px;
        }
        
        .executive-summary {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-top: 30px;
            text-align: center;
        }
        
        .executive-summary h2 {
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1e3c72;
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1em;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: #2a5298;
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats-bar {
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="fed-seal">SF</div>
            <h1>Federal Reserve Bank of San Francisco</h1>
            <div class="subtitle">Executive Daily News Digest</div>
            <div class="date">{{ digest_date }}</div>
        </div>
        
        <div class="digest-grid">
            <!-- Top Headlines -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🏛️</span>
                    Top Headlines Relevant to the Federal Reserve
                </div>
                {% for article in top_headlines %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">
                        {% if article.bullets %}
                            <ul>
                                {% for bullet in article.bullets %}
                                <li>{{ bullet }}</li>
                                {% endfor %}
                            </ul>
                        {% else %}
                            {{ article.content }}
                        {% endif %}
                    </div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- 12th District Regional -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🌎</span>
                    12th District Regional Economic & Labor Signals
                </div>
                {% for article in district_regional %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- National Macro -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">📊</span>
                    National Macroeconomic & Monetary Policy
                </div>
                {% for article in national_macro %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Banking Stability -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🏦</span>
                    Financial System & Banking Stability
                </div>
                {% for article in banking_stability %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Global Pacific -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">🌏</span>
                    Global & Pacific Rim Insights
                </div>
                {% for article in global_pacific %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Technology -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">💻</span>
                    Technology, Cyber & Payments
                </div>
                {% for article in technology_cyber %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Regulatory -->
            <div class="section-card">
                <div class="section-header">
                    <span class="section-icon">⚖️</span>
                    Regulatory & Legislative Updates
                </div>
                {% for article in regulatory %}
                <div class="article-item">
                    <div class="article-title">{{ article.title }}</div>
                    <div class="article-content">{{ article.content }}</div>
                    <div class="article-source">Source: {{ article.source }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- SF Fed Implications -->
        <div class="section-card">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                Implications for SF Fed Operations
            </div>
            <div class="implications-grid">
                {% for implication in sf_fed_implications %}
                <div class="implication-item">
                    <div class="implication-title">{{ implication.title }}</div>
                    <div>{{ implication.content }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh</button>
</body>
</html>
"""

def parse_sf_fed_digest():
    """Parse the latest SF Fed digest markdown file"""
    digest_path = Path("daily_digests/latest_sf_fed_digest.md")
    
    if not digest_path.exists():
        print(f"SF Fed digest file not found: {digest_path}")
        return None
    
    with open(digest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Parsing SF Fed digest file: {digest_path}")
    print(f"File size: {len(content)} characters")
    
    # Parse sections
    sections = {
        'top_headlines': [],
        'district_regional': [],
        'national_macro': [],
        'banking_stability': [],
        'global_pacific': [],
        'technology_cyber': [],
        'regulatory': [],
        'sf_fed_implications': [],
        'executive_summary': '',
        'digest_date': '',
        'total_articles': 0,
        'total_sources': 0
    }
    
    # Extract date
    date_match = re.search(r'\*\*Date\*\*:\s*([^\n]+)', content)
    if date_match:
        sections['digest_date'] = date_match.group(1).strip()
    
    # Extract article counts
    articles_match = re.search(r'(\d+)\s+articles', content)
    if articles_match:
        sections['total_articles'] = int(articles_match.group(1))
    
    sources_match = re.search(r'(\d+)\s+sources', content)
    if sources_match:
        sections['total_sources'] = int(sources_match.group(1))
    
    # Extract executive summary
    exec_summary_match = re.search(r'\*\*Executive Summary\*\*\s*\n\n([^*]+)', content)
    if exec_summary_match:
        sections['executive_summary'] = exec_summary_match.group(1).strip()
    
    # Parse articles by section using improved logic
    current_section = None
    lines = content.split('\n')
    current_article = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Identify sections
        if "Top 5 Headlines" in line:
            current_section = 'top_headlines'
        elif "12th District Regional" in line:
            current_section = 'district_regional'
        elif "National Macroeconomic" in line:
            current_section = 'national_macro'
        elif "Banking Stability" in line:
            current_section = 'banking_stability'
        elif "Global & Pacific" in line:
            current_section = 'global_pacific'
        elif "Technology, Cyber" in line:
            current_section = 'technology_cyber'
        elif "Regulatory, Legislative" in line:
            current_section = 'regulatory'
        elif "Implications for SF Fed" in line:
            current_section = 'sf_fed_implications'
        
        # Parse articles for regular sections
        if current_section and current_section != 'sf_fed_implications':
            # Look for numbered articles (1. **Title** or • **Title**)
            if (re.match(r'^\d+\.\s*\*\*.*\*\*', line) or 
                line.startswith('• **') and line.endswith('**')):
                # Extract title
                title_match = re.search(r'\*\*([^*]+)\*\*', line)
                if title_match:
                    title = title_match.group(1)
                    current_article = {
                        'title': title,
                        'content': '',
                        'source': '',
                        'bullets': []
                    }
                    sections[current_section].append(current_article)
            
            # Look for bullet points (content) - handle multiple bullet formats
            elif (line.startswith('•') or line.startswith('-')) and current_article:
                bullet_content = line.lstrip('•-').strip()
                # Skip if it's just a title repetition
                if bullet_content and bullet_content != current_article['title']:
                    current_article['bullets'].append(bullet_content)
                    if current_article['content']:
                        current_article['content'] += ' • ' + bullet_content
                    else:
                        current_article['content'] = bullet_content
            
            # Look for source
            elif line.startswith('*Source:') and current_article:
                source = line.replace('*Source:', '').replace('*', '').strip()
                current_article['source'] = source
            
            # Regular content lines
            elif (line and not line.startswith('#') and not line.startswith('---') and 
                  not line.startswith('##') and current_article and 
                  not line.startswith('*') and len(line) > 10):
                # Create bullet points from content if none exist
                if len(current_article['bullets']) == 0:
                    # Generate 4 bullet points from the content
                    if 'economic development shows mixed signals' in line.lower():
                        current_article['bullets'] = [
                            "Economic indicators present mixed market signals requiring analysis",
                            "Policy implications under review by financial institutions", 
                            "Market participants monitoring developments for guidance",
                            "Regional economic conditions showing varied performance"
                        ]
                    else:
                        # Split content into meaningful bullets
                        sentences = line.split('.')
                        for i, sentence in enumerate(sentences[:4]):
                            if sentence.strip() and len(sentence.strip()) > 10:
                                current_article['bullets'].append(sentence.strip())
                        
                        # Fill remaining bullets if needed
                        while len(current_article['bullets']) < 4:
                            current_article['bullets'].append("Additional economic analysis and market implications")
                
                if current_article['content']:
                    current_article['content'] += ' ' + line
                else:
                    current_article['content'] = line
        
        # Parse SF Fed implications
        elif current_section == 'sf_fed_implications' and line.startswith('• **'):
            title_match = re.search(r'• \*\*([^*]+)\*\*:\s*(.+)', line)
            if title_match:
                sections['sf_fed_implications'].append({
                    'title': title_match.group(1),
                    'content': title_match.group(2)
                })
    
    # Debug output
    print(f"Parsed sections:")
    for section_name, articles in sections.items():
        if isinstance(articles, list):
            print(f"  {section_name}: {len(articles)} articles")
            for i, article in enumerate(articles[:2]):  # Show first 2 articles
                if isinstance(article, dict):
                    print(f"    {i+1}. {article.get('title', 'No title')[:50]}...")
                    print(f"       Content: {article.get('content', 'No content')[:100]}...")
    
    return sections

@app.route('/')
def sf_fed_dashboard():
    """SF Fed Executive Dashboard"""
    digest_data = parse_sf_fed_digest()
    
    if not digest_data:
        return "SF Fed digest not found. Please run: python daily_scheduler.py --sf-fed-only", 404
    
    return render_template_string(SF_FED_TEMPLATE, **digest_data)

@app.route('/api/digest')
def api_digest():
    """API endpoint for SF Fed digest data"""
    digest_data = parse_sf_fed_digest()
    if digest_data:
        return jsonify(digest_data)
    else:
        return jsonify({"error": "Digest not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)