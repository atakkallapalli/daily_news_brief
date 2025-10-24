#!/usr/bin/env python3
"""
Economic News Dashboard
Creates a web interface to display the curated economic news
"""

from flask import Flask, render_template_string, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Economic & Financial News Dashboard</title>
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
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .topics {
            display: grid;
            gap: 30px;
        }
        
        .topic-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .topic-header {
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
        }
        
        .topic-content {
            padding: 20px;
        }
        
        .article {
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }
        
        .article:last-child {
            border-bottom: none;
        }
        
        .article-title {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .article-title a {
            color: #333;
            text-decoration: none;
        }
        
        .article-title a:hover {
            color: #667eea;
        }
        
        .article-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .article-source {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        .article-date {
            color: #888;
        }
        
        .article-summary {
            color: #555;
            line-height: 1.5;
        }
        
        .load-more {
            text-align: center;
            margin-top: 20px;
        }
        
        .load-more button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }
        
        .load-more button:hover {
            background: #5a6fd8;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Economic & Financial News Dashboard</h1>
            <p>Curated news from Bloomberg, Reuters, Fox News, NBC, AP, WSJ, and LinkedIn</p>
            <p><strong>Collection Date:</strong> {{ collection_date }}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_articles }}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ topic_count }}</div>
                <div class="stat-label">Topic Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ source_count }}</div>
                <div class="stat-label">News Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">7</div>
                <div class="stat-label">Days Coverage</div>
            </div>
        </div>
        
        <div class="topics">
            {% for topic, articles in topics.items() %}
            <div class="topic-section">
                <div class="topic-header">
                    {{ topic }} ({{ articles|length }} articles)
                </div>
                <div class="topic-content">
                    {% for article in articles[:5] %}
                    <div class="article">
                        <div class="article-title">
                            <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
                        </div>
                        <div class="article-meta">
                            <span class="article-source">{{ article.source }}</span>
                            <span class="article-date">{{ article.published }}</span>
                        </div>
                        {% if article.description %}
                        <div class="article-summary">
                            {{ article.description|striptags|truncate(200) }}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                    
                    {% if articles|length > 5 %}
                    <div class="load-more">
                        <p><em>... and {{ articles|length - 5 }} more articles in this category</em></p>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Data collected from publicly available sources including Google News RSS feeds and major news outlets.</p>
            <p>This dashboard provides a curated view of recent economic and financial news for analysis and review.</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard route"""
    try:
        # Load the articles data
        with open('/workspace/articles_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format the collection date
        collection_date = datetime.fromisoformat(data['collection_date'].replace('Z', '+00:00'))
        formatted_date = collection_date.strftime('%B %d, %Y at %I:%M %p UTC')
        
        return render_template_string(
            DASHBOARD_TEMPLATE,
            collection_date=formatted_date,
            total_articles=data['total_articles'],
            topic_count=len(data['topics']),
            source_count=len(data['sources_covered']),
            topics=data['topics']
        )
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/api/data')
def api_data():
    """API endpoint to get raw data"""
    try:
        with open('/workspace/articles_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary')
def api_summary():
    """API endpoint to get summary statistics"""
    try:
        with open('/workspace/articles_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = {
            'total_articles': data['total_articles'],
            'topics': {topic: len(articles) for topic, articles in data['topics'].items()},
            'sources': data['sources_covered'],
            'collection_date': data['collection_date']
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=51487, debug=True)
