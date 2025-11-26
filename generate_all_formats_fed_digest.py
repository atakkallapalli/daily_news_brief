#!/usr/bin/env python3
"""
Generate Federal Reserve Executive Daily News Digest in All Formats
Uses LLM settings from config and generates Markdown, HTML, and JSON outputs
"""

import json
import os
from datetime import datetime
from pathlib import Path
from litellm_fed_executive_digest import LiteLLMFedExecutiveDigest, LiteLLMConfig

def load_llm_config():
    """Load LLM configuration from config file"""
    try:
        config_path = Path("/workspace/daily_news_brief/llm_config_example.json")
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        llm_settings = config_data.get('llm_settings', {})
        
        # Create LiteLLM config from settings
        litellm_config = LiteLLMConfig(
            api_base=llm_settings.get('provider', 'http://35.175.151.231:8250'),
            api_key=llm_settings.get('api_key', 'sk-12345'),
            model=llm_settings.get('models', {}).get('litellm', 'litellm_proxy/ClaudeSonnet4'),
            max_tokens=llm_settings.get('max_tokens', 2000),
            temperature=llm_settings.get('temperature', 0.3)
        )
        
        return litellm_config, llm_settings
        
    except Exception as e:
        print(f"Error loading config: {e}")
        return LiteLLMConfig(), {}

def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown content to HTML"""
    html_content = markdown_content
    
    # Convert markdown headers
    html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
    html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n', 1)
    html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n', 1)
    
    # Convert bold text
    import re
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Convert bullet points
    lines = html_content.split('\n')
    in_list = False
    processed_lines = []
    
    for line in lines:
        if line.strip().startswith('• '):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)
    
    if in_list:
        processed_lines.append('</ul>')
    
    html_content = '\n'.join(processed_lines)
    
    # Convert links
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
    
    # Add basic HTML structure
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federal Reserve Executive Daily News Digest</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; }}
        .article {{ margin-bottom: 30px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .author {{ font-style: italic; color: #7f8c8d; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; font-size: 0.9em; color: #7f8c8d; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    return html_template

def create_json_format(markdown_content: str, articles_data: list) -> dict:
    """Create JSON format from markdown content and articles data"""
    current_date = datetime.now()
    
    json_data = {
        "digest_info": {
            "title": "Federal Reserve Executive Daily News Digest",
            "date": current_date.strftime("%Y-%m-%d"),
            "generated_at": current_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "format_version": "2.0",
            "total_articles": len(articles_data),
            "digest_type": "fed_executive_enhanced"
        },
        "articles": [],
        "metadata": {
            "llm_generated": True,
            "enhanced_format": True,
            "bullet_points_per_article": "4-5",
            "includes_author_attribution": True,
            "includes_content_insights": True
        }
    }
    
    # Extract articles from markdown (simplified parsing)
    lines = markdown_content.split('\n')
    current_article = None
    
    for i, line in enumerate(lines):
        if line.startswith('**') and line.endswith('**') and len(line) > 10:
            # New article title
            if current_article:
                json_data["articles"].append(current_article)
            
            title = line.strip('*')
            current_article = {
                "title": title,
                "author": "",
                "summary_bullets": [],
                "source_url": "",
                "fed_relevance": "high"
            }
        elif line.startswith('Author: ') and current_article:
            current_article["author"] = line.replace('Author: ', '').strip()
        elif line.startswith('• ') and current_article:
            bullet = line.replace('• ', '').strip()
            current_article["summary_bullets"].append(bullet)
        elif line.startswith('Read more: ') and current_article:
            # Extract URL from markdown link
            import re
            url_match = re.search(r'\(([^)]+)\)', line)
            if url_match:
                current_article["source_url"] = url_match.group(1)
    
    # Add the last article
    if current_article:
        json_data["articles"].append(current_article)
    
    return json_data

def main():
    """Generate Fed executive digest in all formats"""
    print("🚀 Generating Federal Reserve Executive Digest in All Formats...")
    print("📋 Using LLM settings from config file")
    
    # Load configuration
    litellm_config, llm_settings = load_llm_config()
    print(f"🔧 Using LLM provider: {litellm_config.api_base}")
    print(f"🤖 Using model: {litellm_config.model}")
    
    # Generate the digest
    generator = LiteLLMFedExecutiveDigest(litellm_config)
    
    try:
        # Generate markdown content
        print("\n📝 Generating Markdown format...")
        markdown_filename = generator.generate_digest()
        
        if not markdown_filename:
            print("❌ Failed to generate digest")
            return
        
        # Read the generated markdown content
        with open(markdown_filename, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ Markdown generated: {markdown_filename}")
        
        # Generate HTML format
        print("🌐 Converting to HTML format...")
        html_content = markdown_to_html(markdown_content)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        html_filename = f"fed_executive_digest_all_formats_{timestamp}.html"
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML generated: {html_filename}")
        
        # Generate JSON format
        print("📊 Creating JSON format...")
        
        # Load articles data for JSON
        digest_data = generator.load_latest_daily_digest()
        selected_articles = generator.select_fed_relevant_articles(digest_data)
        
        json_data = create_json_format(markdown_content, selected_articles)
        
        json_filename = f"fed_executive_digest_all_formats_{timestamp}.json"
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON generated: {json_filename}")
        
        # Summary
        print(f"\n🎉 All formats generated successfully!")
        print(f"📄 Markdown: {markdown_filename}")
        print(f"🌐 HTML: {html_filename}")
        print(f"📊 JSON: {json_filename}")
        print(f"\n📈 Features included:")
        print(f"   • 4-5 bullet points per article")
        print(f"   • Enhanced author attribution")
        print(f"   • Content insights and analysis")
        print(f"   • Clean HTML formatting")
        print(f"   • Federal Reserve executive focus")
        
        return {
            "markdown": markdown_filename,
            "html": html_filename,
            "json": json_filename
        }
        
    except Exception as e:
        print(f"❌ Error generating digest: {e}")
        return None

if __name__ == "__main__":
    main()
