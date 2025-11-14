#!/usr/bin/env python3
"""
Economic News Dashboard
Creates a web interface to display the curated economic news
"""

from flask import Flask, render_template_string, jsonify, request
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
    <title>Daily News AIssistant (DNA)</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            background: #667eea;
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
            border-bottom: 2px solid #667eea;
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
            background-color: #667eea;
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
            background: #667eea;
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
            <h1>Daily News AIssistant (DNA)</h1>
            <p>Curated news from Bloomberg, Reuters, Fox News, NBC, AP, WSJ, and LinkedIn</p>
            <p><strong>Collection Date:</strong> {{ collection_date }}</p>
            <div class="header-buttons">
                <button class="refresh-btn" onclick="refreshNews()" id="refreshBtn">🔄 Refresh News</button>
            </div>
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
                    <span>{{ topic }} ({{ articles|length }} articles)</span>
                    <button class="topic-export-btn" onclick="exportTopicToPDF('{{ topic }}', '{{ loop.index0 }}')">📄 Export PDF</button>
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
                        {% if article.get('summary_highlights') %}
                        <div class="article-highlights">
                            <strong>Key Points:</strong>
                            <button class="edit-btn" onclick="toggleEdit('{{ loop.index0 }}')">✏️ Edit</button>
                            <ul id="highlights-{{ loop.index0 }}" class="editable-highlights">
                                {% for highlight in article.summary_highlights[:4] %}
                                <li contenteditable="false" class="highlight-item">{{ highlight }}</li>
                                {% endfor %}
                            </ul>
                            <div class="edit-controls" id="controls-{{ loop.index0 }}" style="display: none;">
                                <button class="save-btn" onclick="saveHighlights('{{ loop.index0 }}')">💾 Save</button>
                                <button class="cancel-btn" onclick="cancelEdit('{{ loop.index0 }}')">❌ Cancel</button>
                            </div>
                        </div>
                        {% elif article.description %}
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
    
    <!-- Keywords Editor Panel -->
    <div class="keywords-panel" id="keywordsPanel">
        <div class="keywords-header" onclick="toggleKeywordsPanel()">
            <span>Application Settings</span>
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
                    <input type="text" class="add-keyword" id="newKeyword" placeholder="Add new keyword..." onkeypress="handleKeywordInput(event)">
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
                saveKeywords(); // Auto-save after adding
            }
        }
        
        function removeKeyword(index) {
            currentKeywords.splice(index, 1);
            loadKeywords();
        }
        
        let currentSources = [];
        
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
            fetch('/api/keywords', {
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
                'unemployment', 'inflation', 'market risk', 'banking',
                'federal reserve', 'interest rates', 'economic outlook',
                'GDP', 'recession', 'monetary policy', 'fiscal policy',
                'fed', 'jerome powell', 'fomc', 'federal open market committee',
                'fed chair', 'fed governor', 'fed official', 'fed policy',
                'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
            ];
            loadKeywords();
        }
        
        let originalHighlights = {};
        
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
        
        let globalArticleIndex = 0;
        
        function saveHighlights(articleId) {
            const highlights = document.getElementById(`highlights-${articleId}`);
            const controls = document.getElementById(`controls-${articleId}`);
            const items = highlights.querySelectorAll('.highlight-item');
            
            // Collect edited content
            const editedHighlights = Array.from(items).map(item => item.textContent);
            
            // Save to server
            fetch('/api/save-highlights', {
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
            const elementsToHide = ['.stats', '.keywords-panel', '.header-buttons'];
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
            headerTitle.textContent = `Economic News: ${topicName}`;
            
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
        
        function refreshNews() {
            const btn = document.getElementById('refreshBtn');
            btn.disabled = true;
            btn.innerHTML = '⏳ Scanning...';
            
            fetch('/api/refresh-news', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('News refresh completed! Reloading page...');
                    window.location.reload();
                } else {
                    alert('Error refreshing news: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error refreshing news: ' + error);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = '🔄 Refresh News';
            });
        }
        
        // Load keywords on page load
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/api/keywords')
            .then(response => response.json())
            .then(data => {
                currentKeywords = data.keywords || [
                    'unemployment', 'inflation', 'market risk', 'banking',
                    'federal reserve', 'interest rates', 'economic outlook',
                    'GDP', 'recession', 'monetary policy', 'fiscal policy',
                    'fed', 'jerome powell', 'fomc', 'federal open market committee',
                    'fed chair', 'fed governor', 'fed official', 'fed policy',
                    'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
                ];
                loadKeywords();
            })
            .catch(error => {
                console.error('Error loading keywords:', error);
                currentKeywords = [
                    'unemployment', 'inflation', 'market risk', 'banking',
                    'federal reserve', 'interest rates', 'economic outlook',
                    'GDP', 'recession', 'monetary policy', 'fiscal policy',
                    'fed', 'jerome powell', 'fomc', 'federal open market committee',
                    'fed chair', 'fed governor', 'fed official', 'fed policy',
                    'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
                ];
                loadKeywords();
            });
        });
    </script>
</body>
</html>
"""

def clean_highlight(highlight):
    """Remove sub-header prefixes from highlights"""
    prefixes = [
        'Economic news:', 'Market development:', 'Federal Reserve development:', 
        'Inflation update:', 'Employment market news:', 'Context:', 
        'Key statement:', 'Economic data:', 'Source:', 'Fed Chair Jerome Powell statement:',
        'Federal Reserve interest rate policy:'
    ]
    
    cleaned = highlight
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    
    return cleaned

@app.route('/')
def dashboard():
    """Main dashboard route"""
    try:
        # Load the articles data
        with open('articles_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean highlights in all articles
        for topic_name, articles in data.get('topics', {}).items():
            for article in articles:
                if 'summary_highlights' in article:
                    article['summary_highlights'] = [clean_highlight(h) for h in article['summary_highlights']]
                if 'highlights' in article:
                    article['highlights'] = [clean_highlight(h) for h in article['highlights']]
        
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
        with open('articles_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary')
def api_summary():
    """API endpoint to get summary statistics"""
    try:
        with open('articles_data.json', 'r', encoding='utf-8') as f:
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

@app.route('/api/keywords', methods=['GET', 'POST'])
def api_keywords():
    """API endpoint to get and update keywords"""
    keywords_file = 'keywords.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return jsonify(data)
            else:
                # Return default keywords
                default_keywords = [
                    'unemployment', 'inflation', 'market risk', 'banking',
                    'federal reserve', 'interest rates', 'economic outlook',
                    'GDP', 'recession', 'monetary policy', 'fiscal policy',
                    'fed', 'jerome powell', 'fomc', 'federal open market committee',
                    'fed chair', 'fed governor', 'fed official', 'fed policy',
                    'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
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
            
            return jsonify({'success': True, 'message': 'Keywords saved successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sources', methods=['GET', 'POST'])
def api_sources():
    """API endpoint to get and update news sources"""
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

@app.route('/api/save-highlights', methods=['POST'])
def api_save_highlights():
    """API endpoint to save edited highlights"""
    try:
        data = request.get_json()
        article_id = data.get('articleId')
        highlights = data.get('highlights', [])
        
        # Load current articles data
        with open('articles_data.json', 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        # Find and update the article
        # Parse article_id (now just a simple index)
        article_idx = int(article_id)
        
        # Flatten all articles to find by index
        all_articles = []
        topic_article_map = []
        
        for topic_name, topic_articles in articles_data['topics'].items():
            for i, article in enumerate(topic_articles):
                all_articles.append(article)
                topic_article_map.append((topic_name, i))
        
        if article_idx < len(all_articles):
            topic_name, topic_article_idx = topic_article_map[article_idx]
            articles_data['topics'][topic_name][topic_article_idx]['summary_highlights'] = highlights
            
            # Save updated data
            with open('articles_data.json', 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, indent=2, default=str)
            
            return jsonify({'success': True, 'message': 'Highlights saved successfully'})
        
        return jsonify({'success': False, 'error': 'Article not found'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-news', methods=['POST'])
def api_refresh_news():
    """API endpoint to trigger news aggregation"""
    try:
        import subprocess
        import sys
        
        # Run the news aggregator script
        result = subprocess.run([sys.executable, 'news_aggregator.py'], 
                              capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'News refresh completed successfully'})
        else:
            return jsonify({'success': False, 'error': f'News aggregator failed: {result.stderr}'})
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'News aggregation timed out (15 minutes)'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
