#!/usr/bin/env python3
"""
Daily News Digest Scheduler
Automatically runs news aggregation at specified times and generates daily digests
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import json
from news_aggregator import NewsAggregator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_digest.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DailyDigestScheduler:
    def __init__(self, config_file: str = "scheduler_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize aggregator with LLM settings from config
        llm_config = self.config.get('llm_settings', {})
        self.aggregator = NewsAggregator(
            llm_provider=llm_config.get('provider', 'auto'),
            llm_api_key=llm_config.get('api_key')
        )
        
    def load_config(self) -> dict:
        """Load scheduler configuration"""
        default_config = {
            "schedule_times": ["07:00", "12:00", "18:00"],  # Morning, Noon, Evening
            "timezone": "UTC",
            "output_directory": "daily_digests",
            "archive_days": 30,  # Keep digests for 30 days
            "email_notifications": {
                "enabled": False,
                "recipients": [],
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": ""
            },
            "digest_settings": {
                "max_articles_per_category": 10,
                "include_highlights": True,
                "generate_summary": True,
                "format": "markdown"  # markdown, html, json
            },
            "llm_settings": {
                "provider": "auto",  # auto, openai, anthropic, local
                "api_key": None,  # Set via environment variable or here
                "enabled": True,
                "fallback_to_rule_based": True,
                "max_tokens": 200,
                "temperature": 0.3
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                logger.error(f"Error loading config: {e}. Using defaults.")
        else:
            # Create default config file
            self.save_config(default_config)
            
        return default_config
    
    def save_config(self, config: dict = None):
        """Save scheduler configuration"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def setup_output_directory(self):
        """Create output directory for daily digests"""
        output_dir = Path(self.config["output_directory"])
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    def generate_daily_digest(self, target_date: datetime = None):
        """Generate a daily news digest for the specified date"""
        try:
            if target_date is None:
                target_date = datetime.now()
                
            logger.info(f"Starting daily digest generation for {target_date.strftime('%Y-%m-%d')}...")
            
            # Setup output directory
            output_dir = self.setup_output_directory()
            
            # Generate timestamp for this digest
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Run news aggregation with date filtering
            self.aggregator.collect_articles(target_date)
            
            # Generate digest files
            digest_files = {}
            
            # Markdown digest
            if self.config["digest_settings"]["format"] in ["markdown", "all"]:
                md_file = output_dir / f"daily_digest_{timestamp}.md"
                self.generate_markdown_digest(md_file, date_str)
                digest_files["markdown"] = str(md_file)
            
            # HTML digest
            if self.config["digest_settings"]["format"] in ["html", "all"]:
                html_file = output_dir / f"daily_digest_{timestamp}.html"
                self.generate_html_digest(html_file, date_str)
                digest_files["html"] = str(html_file)
            
            # JSON digest
            if self.config["digest_settings"]["format"] in ["json", "all"]:
                json_file = output_dir / f"daily_digest_{timestamp}.json"
                self.generate_json_digest(json_file, date_str)
                digest_files["json"] = str(json_file)
            
            # Create latest symlinks
            self.create_latest_links(digest_files, output_dir)
            
            # Clean up old digests
            self.cleanup_old_digests(output_dir)
            
            # Send notifications if enabled
            if self.config["email_notifications"]["enabled"]:
                self.send_email_notification(digest_files, date_str)
            
            logger.info(f"Daily digest generated successfully: {digest_files}")
            return digest_files
            
        except Exception as e:
            logger.error(f"Error generating daily digest: {e}")
            raise
    
    def generate_markdown_digest(self, output_file: Path, date_str: str):
        """Generate markdown format digest"""
        summary = self.aggregator.summarize_articles()
        categorized_articles = summary.get('topics', {})
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Daily Economic News Digest\n")
            f.write(f"**Date:** {date_str}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"**Total Articles:** {len(self.aggregator.articles)}\n\n")
            
            # Executive Summary
            if self.config["digest_settings"]["generate_summary"]:
                f.write("## 📊 Executive Summary\n\n")
                summary_stats = self.generate_summary_stats(categorized_articles)
                for stat in summary_stats:
                    f.write(f"- {stat}\n")
                f.write("\n")
            
            # Categories
            for category, articles in categorized_articles.items():
                if not articles:
                    continue
                    
                max_articles = self.config["digest_settings"]["max_articles_per_category"]
                display_articles = articles[:max_articles]
                
                f.write(f"## {category} ({len(articles)} articles)\n\n")
                
                for i, article in enumerate(display_articles, 1):
                    # Custom format: headline, 1 sentence TL;DR, highlights in 4 bullet points, tags/annotations
                    f.write(f"### {i}. {article['title']}\n")
                    
                    # TL;DR - Extract first sentence or create concise summary
                    description = article.get('description', '')
                    if description:
                        # Get first sentence or first 100 chars as TL;DR
                        tldr = description.split('.')[0][:100] + "..." if len(description) > 100 else description.split('.')[0] + "."
                    else:
                        tldr = "Economic news update with market implications."
                    f.write(f"**TL;DR:** {tldr}\n")
                    
                    # 4 bullet point highlights
                    if self.config["digest_settings"]["include_highlights"] and article.get('highlights'):
                        f.write("**Key Highlights:**\n")
                        for highlight in article['highlights'][:4]:  # Ensure exactly 4
                            f.write(f"  • {highlight}\n")
                    
                    # Tags/Annotations
                    tags = []
                    # Add source tag
                    tags.append(f"Source: {article['source']}")
                    # Add category tag
                    if article.get('source_category'):
                        tags.append(f"Type: {article.get('source_category')}")
                    # Add date tag if available
                    if article.get('published'):
                        pub_date = article['published'][:10] if len(article['published']) > 10 else article['published']
                        tags.append(f"Date: {pub_date}")
                    # Add keyword tag if available
                    if article.get('keyword'):
                        tags.append(f"Keyword: {article['keyword']}")
                    
                    f.write(f"**Tags:** {' | '.join(tags)}\n")
                    f.write(f"**URL:** {article['url']}\n")
                    f.write("\n")
                
                if len(articles) > max_articles:
                    f.write(f"*... and {len(articles) - max_articles} more articles in this category*\n\n")
    
    def generate_html_digest(self, output_file: Path, date_str: str):
        """Generate HTML format digest"""
        summary = self.aggregator.summarize_articles()
        categorized_articles = summary.get('topics', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Economic News Digest - {date_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .category {{ margin-bottom: 40px; }}
        .article {{ border-left: 4px solid #007bff; padding-left: 15px; margin-bottom: 25px; }}
        .tldr {{ background: #e3f2fd; padding: 8px; border-radius: 4px; margin: 8px 0; font-style: italic; }}
        .highlights {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .highlight-item {{ margin: 5px 0; }}
        .tags {{ background: #fff3e0; padding: 8px; border-radius: 4px; margin: 8px 0; font-size: 0.9em; }}
        .meta {{ color: #666; font-size: 0.9em; }}
        .summary {{ margin-top: 10px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 5px; }}
        h3 {{ color: #333; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Daily Economic News Digest</h1>
        <p><strong>Date:</strong> {date_str}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p><strong>Total Articles:</strong> {len(self.aggregator.articles)}</p>
    </div>
"""
        
        # Executive Summary
        if self.config["digest_settings"]["generate_summary"]:
            html_content += "<h2>📊 Executive Summary</h2><ul>"
            summary_stats = self.generate_summary_stats(categorized_articles)
            for stat in summary_stats:
                html_content += f"<li>{stat}</li>"
            html_content += "</ul>"
        
        # Categories
        for category, articles in categorized_articles.items():
            if not articles:
                continue
                
            max_articles = self.config["digest_settings"]["max_articles_per_category"]
            display_articles = articles[:max_articles]
            
            html_content += f'<div class="category"><h2>{category} ({len(articles)} articles)</h2>'
            
            for i, article in enumerate(display_articles, 1):
                html_content += f'<div class="article">'
                html_content += f'<h3>{i}. <a href="{article["url"]}" target="_blank">{article["title"]}</a></h3>'
                
                # TL;DR
                description = article.get('description', '')
                if description:
                    tldr = description.split('.')[0][:100] + "..." if len(description) > 100 else description.split('.')[0] + "."
                else:
                    tldr = "Economic news update with market implications."
                html_content += f'<div class="tldr"><strong>TL;DR:</strong> {tldr}</div>'
                
                # 4 bullet point highlights
                if self.config["digest_settings"]["include_highlights"] and article.get('highlights'):
                    html_content += '<div class="highlights"><strong>Key Highlights:</strong>'
                    for highlight in article['highlights'][:4]:
                        html_content += f'<div class="highlight-item">• {highlight}</div>'
                    html_content += '</div>'
                
                # Tags/Annotations
                tags = []
                tags.append(f"Source: {article['source']}")
                if article.get('source_category'):
                    tags.append(f"Type: {article.get('source_category')}")
                if article.get('published'):
                    pub_date = article['published'][:10] if len(article['published']) > 10 else article['published']
                    tags.append(f"Date: {pub_date}")
                if article.get('keyword'):
                    tags.append(f"Keyword: {article['keyword']}")
                
                html_content += f'<div class="tags"><strong>Tags:</strong> {" | ".join(tags)}</div>'
                html_content += '</div>'
            
            if len(articles) > max_articles:
                html_content += f'<p><em>... and {len(articles) - max_articles} more articles in this category</em></p>'
            
            html_content += '</div>'
        
        html_content += """
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_json_digest(self, output_file: Path, date_str: str):
        """Generate JSON format digest"""
        summary = self.aggregator.summarize_articles()
        categorized_articles = summary.get('topics', {})
        
        digest_data = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(self.aggregator.articles),
            "categories": {}
        }
        
        for category, articles in categorized_articles.items():
            if not articles:
                continue
                
            max_articles = self.config["digest_settings"]["max_articles_per_category"]
            display_articles = articles[:max_articles]
            
            digest_data["categories"][category] = {
                "total_count": len(articles),
                "displayed_count": len(display_articles),
                "articles": display_articles
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)
    
    def generate_summary_stats(self, categorized_articles: dict) -> list:
        """Generate executive summary statistics"""
        stats = []
        
        # Category breakdown
        for category, articles in categorized_articles.items():
            if articles:
                stats.append(f"**{category}**: {len(articles)} articles")
        
        # Source breakdown
        sources = {}
        for article in self.aggregator.articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]
        stats.append(f"**Top Sources**: {', '.join([f'{s} ({c})' for s, c in top_sources])}")
        
        return stats
    
    def create_latest_links(self, digest_files: dict, output_dir: Path):
        """Create symlinks to latest digest files"""
        for format_type, file_path in digest_files.items():
            latest_link = output_dir / f"latest_digest.{format_type}"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            
            try:
                latest_link.symlink_to(Path(file_path).name)
            except OSError:
                # Fallback for systems that don't support symlinks
                import shutil
                shutil.copy2(file_path, latest_link)
    
    def cleanup_old_digests(self, output_dir: Path):
        """Remove digest files older than configured days"""
        cutoff_date = datetime.now() - timedelta(days=self.config["archive_days"])
        
        for file_path in output_dir.glob("daily_digest_*"):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                try:
                    file_path.unlink()
                    logger.info(f"Cleaned up old digest: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up {file_path}: {e}")
    
    def send_email_notification(self, digest_files: dict, date_str: str):
        """Send email notification with digest (placeholder)"""
        # This would require email configuration and SMTP setup
        logger.info(f"Email notification would be sent for digest {date_str}")
        # Implementation would go here for actual email sending
    
    def schedule_daily_runs(self):
        """Setup scheduled daily runs"""
        for time_str in self.config["schedule_times"]:
            schedule.every().day.at(time_str).do(self.generate_daily_digest)
            logger.info(f"Scheduled daily digest generation at {time_str}")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        logger.info("Starting daily digest scheduler...")
        self.schedule_daily_runs()
        
        logger.info(f"Scheduler running with times: {self.config['schedule_times']}")
        logger.info("Press Ctrl+C to stop the scheduler")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def run_once(self):
        """Run digest generation once (for testing)"""
        logger.info("Running one-time digest generation...")
        return self.generate_daily_digest()

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily News Digest Scheduler")
    parser.add_argument("--run-once", action="store_true", help="Run digest generation once")
    parser.add_argument("--schedule", action="store_true", help="Start continuous scheduler")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--times", nargs="+", help="Schedule times (HH:MM format)")
    
    args = parser.parse_args()
    
    # Initialize scheduler
    config_file = args.config or "scheduler_config.json"
    scheduler = DailyDigestScheduler(config_file)
    
    # Update schedule times if provided
    if args.times:
        scheduler.config["schedule_times"] = args.times
        scheduler.save_config()
    
    if args.run_once:
        digest_files = scheduler.run_once()
        print(f"Digest generated: {digest_files}")
    elif args.schedule:
        scheduler.run_scheduler()
    else:
        print("Use --run-once to generate a digest now, or --schedule to start continuous scheduling")
        print(f"Current schedule times: {scheduler.config['schedule_times']}")

if __name__ == "__main__":
    main()
