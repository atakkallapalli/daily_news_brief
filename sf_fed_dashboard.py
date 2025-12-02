#!/usr/bin/env python3
"""
SF Fed Executive Daily News Dashboard
Creates a web interface to display the SF Fed executive digest with same features as main dashboard
"""

from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime
import os

app = Flask(__name__)

# HTML template for the SF Fed dashboard (same styling as main dashboard)
SF_FED_DASHBOARD_TEMPLATE = """
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
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            margin-left: 420px;
            transition: margin-left 0.3s ease;
        }
        
        .container.panel-minimized {
            margin-left: 80px;
        }
        
        .header {
            background: linear-gradient(135deg, #1f4e79 0%, #2c5f8a 100%);
            color: white;
            padding: 30px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .header-buttons {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .refresh-btn {
            background: #e9ecef;
            color: #495057;
            border: 1px solid #ced4da;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            transition: background 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .refresh-btn:hover {
            background: #dee2e6;
        }
        
        .refresh-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .edit-btn {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .edit-btn:hover {
            background: #138496;
        }
        
        .save-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
            margin-right: 5px;
        }
        
        .cancel-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .highlight-item[contenteditable="true"] {
            background: #fff3cd;
            border: 1px dashed #ffc107;
            padding: 4px;
            margin: 2px 0;
            border-radius: 3px;
        }
        
        .edit-controls {
            margin-top: 8px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .executive-summary {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            border-left: 5px solid #1f4e79;
        }
        
        .executive-summary h2 {
            color: #1f4e79;
            margin-bottom: 15px;
            font-size: 1.5em;
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
            color: #1f4e79;
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
            background: #1f4e79;
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }
        
        .topic-header:hover {
            background: #1a4269;
        }
        
        .collapse-icon {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }
        
        .topic-section.collapsed .collapse-icon {
            transform: rotate(-90deg);
        }
        
        .topic-export-btn {
            background: #e9ecef;
            color: #495057;
            border: 1px solid #ced4da;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.65em;
            transition: background 0.3s ease;
        }
        
        .topic-export-btn:hover {
            background: #dee2e6;
        }
        
        .topic-content {
            padding: 20px;
            transition: max-height 0.3s ease, opacity 0.3s ease;
            overflow: hidden;
        }
        
        .topic-section.collapsed .topic-content {
            max-height: 0;
            padding: 0 20px;
            opacity: 0;
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
            color: #1f4e79;
        }
        
        .article-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .article-author {
            color: #495057;
            font-style: italic;
            margin-top: 5px;
            font-size: 0.85em;
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
        
        .article-highlights {
            color: #555;
            line-height: 1.5;
        }
        
        .article-highlights ul {
            margin: 8px 0;
            padding-left: 20px;
            width: 100%;
            box-sizing: border-box;
        }
        
        .article-highlights li {
            margin: 4px 0;
            color: #444;
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: normal;
            line-height: 1.4;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        .keywords-panel {
            position: fixed;
            left: 20px;
            top: 20px;
            bottom: 20px;
            width: 400px;
            background: white;
            border-radius: 10px;
            box-shadow: 2px 0 12px rgba(0,0,0,0.15);
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .keywords-panel.minimized {
            width: 60px;
            transform: translateX(-20px);
        }
        
        .keywords-header {
            background: #1f4e79;
            color: white;
            padding: 15px;
            border-radius: 0 10px 0 0;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            writing-mode: horizontal-tb;
        }
        
        .keywords-panel.minimized .keywords-header {
            writing-mode: vertical-rl;
            text-orientation: mixed;
            padding: 10px 5px;
            border-radius: 0 10px 10px 0;
        }
        
        .keywords-panel.minimized .keywords-header span:first-child {
            font-size: 0.8em;
        }
        
        .keywords-content {
            padding: 0;
            height: calc(100% - 60px);
            overflow-y: auto;
        }
        
        .tab-buttons {
            display: flex;
            background: #f5f5f5;
        }
        
        .tab-button {
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .tab-button.active {
            background: white;
            border-bottom: 2px solid #1f4e79;
        }
        
        .tab-content {
            padding: 15px;
        }
        
        .tab-pane {
            display: none;
        }
        
        .tab-pane.active {
            display: block;
        }
        
        .keyword-tag {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 4px;
            font-size: 0.8em;
            position: relative;
        }
        
        .keyword-tag .remove-btn {
            margin-left: 5px;
            color: #d32f2f;
            cursor: pointer;
            font-weight: bold;
        }
        
        .toggle-switch {
            position: relative;
            width: 40px;
            height: 20px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 20px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 2px;
            bottom: 2px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background-color: #1f4e79;
        }
        
        input:checked + .slider:before {
            transform: translateX(20px);
        }
        
        .source-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .source-info {
            flex: 1;
        }
        
        .source-name {
            font-size: 0.9em;
            font-weight: bold;
            color: #333;
        }
        
        .source-type {
            font-size: 0.7em;
            color: #666;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            margin-top: 2px;
            display: inline-block;
        }
        
        .source-controls {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .remove-source {
            color: #d32f2f;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .add-source {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 10px;
        }
        
        .source-form {
            display: grid;
            gap: 5px;
            margin-top: 10px;
        }
        
        .source-form input, .source-form select {
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .add-keyword {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 10px;
        }
        
        .btn-group {
            margin-top: 10px;
            display: flex;
            gap: 5px;
        }
        
        .btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .btn-primary {
            background: #1f4e79;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .toggle-icon {
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }
        
        .keywords-panel.minimized .toggle-icon {
            transform: rotate(180deg);
        }
        
        .keywords-panel.minimized .keywords-content {
            display: none;
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
            
            .keywords-panel {
                width: 320px;
            }
            
            .keywords-panel.minimized {
                transform: translateX(-280px);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ SF Fed Executive Daily News Digest</h1>
            <p>Prepared for SF Fed Executive Leadership Team</p>
            <p><strong>Collection Date:</strong> {{ collection_date }}</p>
            <div class="header-buttons">
                <button class="refresh-btn" onclick="refreshNews()" id="refreshBtn">🔄 Refresh Digest</button>
            </div>
        </div>
        
        <div class="executive-summary">
            <h2>📊 Executive Summary</h2>
            <p>{{ executive_summary }}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_articles }}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ category_count }}</div>
                <div class="stat-label">Priority Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ source_count }}</div>
                <div class="stat-label">News Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">7</div>
                <div class="stat-label">SF Fed Implications</div>
            </div>
        </div>
        
        <div class="topics">
            {% for category_key, category_data in categories.items() %}
            {% if category_data.articles %}
            <div class="topic-section collapsed" id="topic-{{ loop.index0 }}">
                <div class="topic-header" onclick="toggleTopic('{{ loop.index0 }}')">
                    <span>{{ category_data.display_name }} ({{ category_data.articles|length }} articles)</span>
                    <div>
                        <button class="topic-export-btn" onclick="event.stopPropagation(); exportTopicToPDF('{{ category_data.display_name }}', '{{ loop.index0 }}')" >📄 Export PDF</button>
                        <span class="collapse-icon">▼</span>
                    </div>
                </div>
                <div class="topic-content">
                    {% for article in category_data.articles[:5] %}
                    <div class="article">
                        <div class="article-title">
                            <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
                        </div>
                        <div class="article-meta">
                            <span class="article-source">{{ article.source }}</span>
                            <span class="article-date">{{ article.published }}</span>
                        </div>
                        {% if article.get('author') %}
                        <div class="article-author">By {{ article.author }}</div>
                        {% endif %}
                        {% if article.get('highlights') %}
                        <div class="article-highlights">
                            <strong>Key Points:</strong>
                            <button class="edit-btn" onclick="toggleEdit('{{ loop.index0 }}-{{ loop.index }}')" >✏️ Edit</button>
                            <ul id="highlights-{{ loop.index0 }}-{{ loop.index }}" class="editable-highlights">
                                {% for highlight in article.highlights[:4] %}
                                <li contenteditable="false" class="highlight-item">{{ highlight }}</li>
                                {% endfor %}
                            </ul>
                            <div class="edit-controls" id="controls-{{ loop.index0 }}-{{ loop.index }}" style="display: none;">
                                <button class="save-btn" onclick="saveHighlights('{{ loop.index0 }}-{{ loop.index }}')">💾 Save</button>
                                <button class="cancel-btn" onclick="cancelEdit('{{ loop.index0 }}-{{ loop.index }}')">❌ Cancel</button>
                            </div>
                        </div>
                        {% elif article.description %}
                        <div class="article-summary">
                            {{ article.description|striptags|truncate(200) }}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                    
                    {% if category_data.articles|length > 5 %}
                    <div class="load-more">
                        <p><em>... and {{ category_data.articles|length - 5 }} more articles in this category</em></p>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>SF Fed Executive Digest prepared from publicly available sources with Fed-specific analysis.</p>
            <p>This dashboard provides curated economic and financial news relevant to SF Fed priorities.</p>
        </div>
    </div>
    
    <!-- Keywords Editor Panel -->
    <div class="keywords-panel" id="keywordsPanel">
        <div class="keywords-header" onclick="toggleKeywordsPanel()">
            <span>SF Fed Settings</span>
            <span class="toggle-icon">◀</span>
        </div>
        <div class="keywords-content" id="keywordsContent">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="switchTab('keywords')"><strong>Keywords</strong></button>
                <button class="tab-button" onclick="switchTab('sources')"><strong>Sources</strong></button>
            </div>
            
            <div class="tab-content">
                <div id="keywords-tab" class="tab-pane active">
                    <div id="keywordsList" style="height: calc(100% - 100px); overflow-y: auto; margin-bottom: 10px;">
                        <!-- Keywords will be loaded here -->
                    </div>
                    <input type="text" class="add-keyword" id="newKeyword" placeholder="Add SF Fed keyword..." onkeypress="handleKeywordInput(event)">
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="addKeyword()">Add</button>
                        <button class="btn btn-secondary" onclick="resetKeywords()">Reset</button>
                    </div>
                </div>
                
                <div id="sources-tab" class="tab-pane">
                    <div id="sourcesList" style="height: calc(100% - 140px); overflow-y: auto; margin-bottom: 10px;">
                        <!-- Sources will be loaded here -->
                    </div>
                    <div class="source-form">
                        <input type="text" id="newSourceName" placeholder="Source name...">
                        <input type="url" id="newSourceUrl" placeholder="RSS URL...">
                        <select id="newSourceType">
                            <option value="free_rss">Free RSS</option>
                            <option value="subscription_rss">Subscription RSS</option>
                        </select>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="addSource()">Add Source</button>
                        <button class="btn btn-secondary" onclick="saveSources()">Save</button>
                        <button class="btn btn-secondary" onclick="resetSources()">Reset</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentKeywords = [];
        let currentSources = [];
        let originalHighlights = {};
        
        function toggleKeywordsPanel() {
            const panel = document.getElementById('keywordsPanel');
            const container = document.querySelector('.container');
            panel.classList.toggle('minimized');
            container.classList.toggle('panel-minimized');
        }
        
        function loadKeywords() {
            const keywordsList = document.getElementById('keywordsList');
            keywordsList.innerHTML = '';
            
            currentKeywords.forEach((keyword, index) => {
                const tag = document.createElement('span');
                tag.className = 'keyword-tag';
                tag.innerHTML = `${keyword} <span class="remove-btn" onclick="removeKeyword(${index})">×</span>`;
                keywordsList.appendChild(tag);
            });
        }
        
        function addKeyword() {
            const input = document.getElementById('newKeyword');
            const keyword = input.value.trim().toLowerCase();
            
            if (keyword && !currentKeywords.includes(keyword)) {
                currentKeywords.push(keyword);
                input.value = '';
                loadKeywords();
                saveKeywords();
            }
        }
        
        function removeKeyword(index) {
            currentKeywords.splice(index, 1);
            loadKeywords();
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            
            if (tabName === 'sources') {
                loadSources();
            }
        }
        
        function loadSources() {
            fetch('/api/sources')
            .then(response => response.json())
            .then(data => {
                currentSources = data.sources || [];
                displaySources();
            })
            .catch(error => {
                console.error('Error loading sources:', error);
            });
        }
        
        function displaySources() {
            const sourcesList = document.getElementById('sourcesList');
            sourcesList.innerHTML = '';
            
            currentSources.forEach((source, index) => {
                const item = document.createElement('div');
                item.className = 'source-item';
                item.innerHTML = `
                    <div class="source-info">
                        <div class="source-name">${source.name}</div>
                        <div class="source-type">${source.source_type} - ${source.category}</div>
                    </div>
                    <div class="source-controls">
                        <label class="toggle-switch">
                            <input type="checkbox" ${source.active ? 'checked' : ''} onchange="toggleSource(${index})">
                            <span class="slider"></span>
                        </label>
                        <span class="remove-source" onclick="removeSource(${index})">×</span>
                    </div>
                `;
                sourcesList.appendChild(item);
            });
        }
        
        function toggleSource(index) {
            currentSources[index].active = !currentSources[index].active;
        }
        
        function saveSources() {
            fetch('/api/sources', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sources: currentSources })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Sources saved successfully!');
                } else {
                    alert('Error saving sources: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error saving sources: ' + error);
            });
        }
        
        function resetSources() {
            loadSources();
        }
        
        function addSource() {
            const name = document.getElementById('newSourceName').value.trim();
            const url = document.getElementById('newSourceUrl').value.trim();
            const type = document.getElementById('newSourceType').value;
            
            if (name && url) {
                const newSource = {
                    name: name,
                    url: url,
                    source_type: type,
                    category: type === 'free_rss' ? 'free' : 'subscription',
                    active: true
                };
                
                currentSources.push(newSource);
                displaySources();
                
                // Clear form
                document.getElementById('newSourceName').value = '';
                document.getElementById('newSourceUrl').value = '';
                document.getElementById('newSourceType').value = 'free_rss';
            }
        }
        
        function removeSource(index) {
            currentSources.splice(index, 1);
            displaySources();
        }
        
        function handleKeywordInput(event) {
            if (event.key === 'Enter') {
                addKeyword();
            }
        }
        
        function saveKeywords() {
            fetch('/api/sf-fed-keywords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ keywords: currentKeywords })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('Error saving keywords: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error saving keywords: ' + error);
            });
        }
        
        function resetKeywords() {
            currentKeywords = [
                'federal reserve', 'fed', 'fomc', 'jerome powell', 'monetary policy', 'interest rates',
                'fed chair', 'fed governor', 'fed official', 'fed policy', 'fed meeting', 'fed minutes',
                'california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada',
                'san francisco fed', '12th district', 'west coast', 'pacific', 'silicon valley',
                'inflation', 'unemployment', 'gdp', 'productivity', 'labor market', 'employment',
                'housing market', 'consumer spending', 'supply chain', 'logistics',
                'banking', 'financial stability', 'credit', 'liquidity', 'capital', 'stress test',
                'commercial real estate', 'cre', 'funding markets', 'credit spreads',
                'fintech', 'digital payments', 'fednow', 'cbdc', 'cryptocurrency', 'blockchain',
                'cyber security', 'cloud computing', 'artificial intelligence', 'ai risk',
                'china', 'japan', 'korea', 'asean', 'trade war', 'tariffs', 'supply chain',
                'geopolitical', 'international trade', 'central bank',
                'cfpb', 'fdic', 'occ', 'treasury', 'congress', 'regulation', 'supervision'
            ];
            loadKeywords();
        }
        
        function toggleEdit(articleId) {
            const highlights = document.getElementById(`highlights-${articleId}`);
            const controls = document.getElementById(`controls-${articleId}`);
            const items = highlights.querySelectorAll('.highlight-item');
            
            // Store original content
            originalHighlights[articleId] = Array.from(items).map(item => item.textContent);
            
            // Enable editing
            items.forEach(item => {
                item.contentEditable = 'true';
            });
            
            controls.style.display = 'block';
        }
        
        function saveHighlights(articleId) {
            const highlights = document.getElementById(`highlights-${articleId}`);
            const controls = document.getElementById(`controls-${articleId}`);
            const items = highlights.querySelectorAll('.highlight-item');
            
            // Collect edited content
            const editedHighlights = Array.from(items).map(item => item.textContent);
            
            // Save to server
            fetch('/api/save-sf-fed-highlights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    articleId: articleId,
                    highlights: editedHighlights
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Disable editing
                    items.forEach(item => {
                        item.contentEditable = 'false';
                    });
                    controls.style.display = 'none';
                    alert('Highlights saved successfully!');
                } else {
                    alert('Error saving highlights: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error saving highlights: ' + error);
            });
        }
        
        function cancelEdit(articleId) {
            const highlights = document.getElementById(`highlights-${articleId}`);
            const controls = document.getElementById(`controls-${articleId}`);
            const items = highlights.querySelectorAll('.highlight-item');
            
            // Restore original content
            if (originalHighlights[articleId]) {
                items.forEach((item, index) => {
                    item.textContent = originalHighlights[articleId][index];
                    item.contentEditable = 'false';
                });
            }
            
            controls.style.display = 'none';
        }
        
        function exportTopicToPDF(topicName, topicIndex) {
            // Hide all other topics
            const allTopics = document.querySelectorAll('.topic-section');
            const targetTopic = allTopics[topicIndex];
            
            // Store original display states
            const originalStates = [];
            allTopics.forEach((topic, index) => {
                originalStates[index] = topic.style.display;
                if (index != topicIndex) {
                    topic.style.display = 'none';
                }
            });
            
            // Hide other elements
            const elementsToHide = ['.stats', '.keywords-panel', '.header-buttons', '.executive-summary'];
            const hiddenElements = [];
            elementsToHide.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    hiddenElements.push({element: el, display: el.style.display});
                    el.style.display = 'none';
                });
            });
            
            // Update header title
            const headerTitle = document.querySelector('.header h1');
            const originalTitle = headerTitle.textContent;
            headerTitle.textContent = `SF Fed: ${topicName}`;
            
            // Print
            window.print();
            
            // Restore everything
            setTimeout(() => {
                allTopics.forEach((topic, index) => {
                    topic.style.display = originalStates[index];
                });
                
                hiddenElements.forEach(item => {
                    item.element.style.display = item.display;
                });
                
                headerTitle.textContent = originalTitle;
            }, 100);
        }
        
        function toggleTopic(topicIndex) {
            const topicSection = document.getElementById(`topic-${topicIndex}`);
            topicSection.classList.toggle('collapsed');
        }
        
        function refreshNews() {
            const btn = document.getElementById('refreshBtn');
            btn.disabled = true;
            btn.innerHTML = '⏳ Generating...';
            
            fetch('/api/refresh-sf-fed-digest', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('SF Fed digest refresh completed! Reloading page...');
                    window.location.reload();
                } else {
                    alert('Error refreshing digest: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error refreshing digest: ' + error);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '🔄 Refresh Digest';
            });
        }
        
        // Load keywords on page load
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/api/sf-fed-keywords')
            .then(response => response.json())
            .then(data => {
                currentKeywords = data.keywords || [
                    'federal reserve', 'fed', 'fomc', 'jerome powell', 'monetary policy', 'interest rates',
                    'fed chair', 'fed governor', 'fed official', 'fed policy', 'fed meeting', 'fed minutes',
                    'california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada',
                    'san francisco fed', '12th district', 'west coast', 'pacific', 'silicon valley',
                    'inflation', 'unemployment', 'gdp', 'productivity', 'labor market', 'employment',
                    'housing market', 'consumer spending', 'supply chain', 'logistics',
                    'banking', 'financial stability', 'credit', 'liquidity', 'capital', 'stress test',
                    'commercial real estate', 'cre', 'funding markets', 'credit spreads',
                    'fintech', 'digital payments', 'fednow', 'cbdc', 'cryptocurrency', 'blockchain',
                    'cyber security', 'cloud computing', 'artificial intelligence', 'ai risk',
                    'china', 'japan', 'korea', 'asean', 'trade war', 'tariffs', 'supply chain',
                    'geopolitical', 'international trade', 'central bank',
                    'cfpb', 'fdic', 'occ', 'treasury', 'congress', 'regulation', 'supervision'
                ];
                loadKeywords();
            })
            .catch(error => {
                console.error('Error loading keywords:', error);
                resetKeywords();
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def sf_fed_dashboard():
    """SF Fed dashboard route"""
    try:
        # Load the SF Fed digest JSON data
        with open('daily_digests/latest_sf_fed_digest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Format the collection date
        collection_date = datetime.fromisoformat(data['date']).strftime('%B %d, %Y')
        
        # Count categories with articles
        category_count = sum(1 for cat_data in data['categories'].values() if cat_data['articles'])
        
        return render_template_string(
            SF_FED_DASHBOARD_TEMPLATE,
            collection_date=collection_date,
            total_articles=data['total_articles'],
            category_count=category_count,
            source_count=len(data['sources_covered']),
            executive_summary=data['executive_summary'],
            categories=data['categories']
        )
    except Exception as e:
        return f"Error loading SF Fed dashboard: {str(e)}", 500

@app.route('/api/data')
def api_data():
    """API endpoint to get raw SF Fed data"""
    try:
        with open('daily_digests/latest_sf_fed_digest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary')
def api_summary():
    """API endpoint to get SF Fed summary statistics"""
    try:
        with open('daily_digests/latest_sf_fed_digest.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = {
            'total_articles': data['total_articles'],
            'categories': {cat_key: len(cat_data['articles']) for cat_key, cat_data in data['categories'].items()},
            'sources': data['sources_covered'],
            'collection_date': data['date']
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sf-fed-keywords', methods=['GET', 'POST'])
def api_sf_fed_keywords():
    """API endpoint to get and update SF Fed keywords"""
    keywords_file = 'sf_fed_keywords.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify(data)
            else:
                # Return default SF Fed keywords
                default_keywords = [
                    'federal reserve', 'fed', 'fomc', 'jerome powell', 'monetary policy', 'interest rates',
                    'fed chair', 'fed governor', 'fed official', 'fed policy', 'fed meeting', 'fed minutes',
                    'california', 'washington', 'oregon', 'arizona', 'utah', 'alaska', 'hawaii', 'idaho', 'nevada',
                    'san francisco fed', '12th district', 'west coast', 'pacific', 'silicon valley',
                    'inflation', 'unemployment', 'gdp', 'productivity', 'labor market', 'employment',
                    'housing market', 'consumer spending', 'supply chain', 'logistics',
                    'banking', 'financial stability', 'credit', 'liquidity', 'capital', 'stress test',
                    'commercial real estate', 'cre', 'funding markets', 'credit spreads',
                    'fintech', 'digital payments', 'fednow', 'cbdc', 'cryptocurrency', 'blockchain',
                    'cyber security', 'cloud computing', 'artificial intelligence', 'ai risk',
                    'china', 'japan', 'korea', 'asean', 'trade war', 'tariffs', 'supply chain',
                    'geopolitical', 'international trade', 'central bank',
                    'cfpb', 'fdic', 'occ', 'treasury', 'congress', 'regulation', 'supervision'
                ]
                return jsonify({'keywords': default_keywords})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            keywords = data.get('keywords', [])
            
            # Save keywords to file
            with open(keywords_file, 'w', encoding='utf-8') as f:
                json.dump({'keywords': keywords}, f, indent=2)
            
            return jsonify({'success': True, 'message': 'SF Fed keywords saved successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sources', methods=['GET', 'POST'])
def api_sources():
    """API endpoint to get and update news sources (same as main dashboard)"""
    sources_file = 'sources.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(sources_file):
                with open(sources_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify(data)
            else:
                # Return default sources
                default_sources = [
                    {'name': 'Reuters Business', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'AP Business', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'NBC Business', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'BBC Business', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'CNN Business', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'MarketWatch', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'Federal Reserve News', 'source_type': 'free_rss', 'category': 'free', 'active': True},
                    {'name': 'Wall Street Journal', 'source_type': 'subscription_rss', 'category': 'subscription', 'active': False},
                    {'name': 'Financial Times', 'source_type': 'subscription_rss', 'category': 'subscription', 'active': False}
                ]
                return jsonify({'sources': default_sources})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            sources = data.get('sources', [])
            
            # Save sources to file
            with open(sources_file, 'w', encoding='utf-8') as f:
                json.dump({'sources': sources}, f, indent=2)
            
            return jsonify({'success': True, 'message': 'Sources saved successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-sf-fed-highlights', methods=['POST'])
def api_save_sf_fed_highlights():
    """API endpoint to save edited SF Fed highlights"""
    try:
        data = request.get_json()
        article_id = data.get('articleId')
        highlights = data.get('highlights', [])
        
        # Load current SF Fed digest data
        with open('daily_digests/latest_sf_fed_digest.json', 'r', encoding='utf-8') as f:
            digest_data = json.load(f)
        
        # Parse article_id (format: "categoryIndex-articleIndex")
        category_idx, article_idx = map(int, article_id.split('-'))
        
        # Get category keys in order
        category_keys = list(digest_data['categories'].keys())
        
        if category_idx < len(category_keys):
            category_key = category_keys[category_idx]
            category_articles = digest_data['categories'][category_key]['articles']
            
            if article_idx - 1 < len(category_articles):  # article_idx is 1-based in template
                category_articles[article_idx - 1]['highlights'] = highlights
                
                # Save updated data
                with open('daily_digests/latest_sf_fed_digest.json', 'w', encoding='utf-8') as f:
                    json.dump(digest_data, f, indent=2, default=str)
                
                return jsonify({'success': True, 'message': 'SF Fed highlights saved successfully'})
        
        return jsonify({'success': False, 'error': 'Article not found'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-sf-fed-digest', methods=['POST'])
def api_refresh_sf_fed_digest():
    """API endpoint to trigger SF Fed digest generation"""
    try:
        import subprocess
        import sys
        
        # Run the daily scheduler with SF Fed only flag
        result = subprocess.run([sys.executable, 'daily_scheduler.py', '--sf-fed-only'], 
                              capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'SF Fed digest refresh completed successfully'})
        else:
            return jsonify({'success': False, 'error': f'SF Fed digest generation failed: {result.stderr}'})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'SF Fed digest generation timed out (15 minutes)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)