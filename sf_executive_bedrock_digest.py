
#!/usr/bin/env python3
"""
San Francisco Executive News Summary Generator
Uses AWS Bedrock Claude Haiku 3 for LLM generation with enhanced fallback
"""

import json
import os
import re
import html
import boto3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

class SFExecutiveBedrockDigest:
    """Generate San Francisco Executive news summary using AWS Bedrock Claude Haiku 3"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.bedrock_client = None
        self.setup_bedrock_client()
        
    def setup_bedrock_client(self):
        """Set up AWS Bedrock client"""
        try:
            # Check for AWS credentials
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')  # Default to us-west-2 for SF
            
            if aws_access_key and aws_secret_key:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                print(f"✅ AWS Bedrock client initialized (region: {aws_region})")
            else:
                print("⚠️  AWS credentials not found - will use enhanced fallback")
                
        except Exception as e:
            print(f"❌ Error setting up Bedrock client: {e}")
            self.bedrock_client = None
    
    def generate_with_bedrock_claude(self, prompt: str) -> Optional[str]:
        """Generate content using AWS Bedrock Claude Haiku 3"""
        
        if not self.bedrock_client:
            print("❌ Bedrock client not available")
            return None
        
        try:
            print("🤖 Generating with AWS Bedrock Claude Haiku 3...")
            
            # Prepare the request for Claude Haiku 3
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            print("✅ Successfully generated with Bedrock Claude Haiku 3")
            return content
            
        except ClientError as e:
            print(f"❌ Bedrock API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Bedrock generation error: {e}")
            return None
    
    def load_latest_daily_digest(self) -> Dict[str, Any]:
        """Load the latest daily digest JSON data"""
        try:
            digest_dir = Path("daily_digests")
            if not digest_dir.exists():
                print("❌ Daily digests directory not found")
                return {}
            
            json_files = list(digest_dir.glob("daily_digest_*.json"))
            if not json_files:
                print("❌ No daily digest files found")
                return {}
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"Loading digest from: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"❌ Error loading digest: {e}")
            return {}
    
    def select_sf_relevant_articles(self, digest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select San Francisco and Bay Area relevant articles"""
        
        all_articles = []
        
        # Handle the specific structure: categories -> category_data -> articles
        categories = digest_data.get('categories', {})
        for category_name, category_data in categories.items():
            if isinstance(category_data, dict) and 'articles' in category_data:
                articles = category_data['articles']
                all_articles.extend(articles)
                print(f"Loaded {len(articles)} articles from {category_name}")
        
        print(f"Loaded {len(all_articles)} total articles from digest")
        
        # Filter for SF/Bay Area relevant articles
        sf_keywords = [
            'san francisco', 'sf', 'bay area', 'silicon valley', 'california',
            'tech', 'technology', 'startup', 'venture capital', 'vc',
            'apple', 'google', 'meta', 'facebook', 'twitter', 'x corp',
            'tesla', 'uber', 'lyft', 'airbnb', 'salesforce', 'oracle',
            'nvidia', 'intel', 'cisco', 'adobe', 'zoom', 'slack',
            'ai', 'artificial intelligence', 'machine learning', 'crypto',
            'blockchain', 'fintech', 'biotech', 'clean energy',
            'real estate', 'housing', 'employment', 'jobs', 'layoffs',
            'ipo', 'acquisition', 'merger', 'funding', 'investment',
            'regulation', 'policy', 'innovation', 'research'
        ]
        
        relevant_articles = []
        for article in all_articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            source = article.get('source', '').lower()
            
            # Check title, description, and source for SF-relevant keywords
            if (any(keyword in title or keyword in description or keyword in source 
                   for keyword in sf_keywords) or
                'california' in title or 'california' in description):
                relevant_articles.append(article)
                print(f"  ✓ Selected: {article.get('title', 'Untitled')[:60]}...")
        
        print(f"Selected {len(relevant_articles)} articles for SF executive digest")
        return relevant_articles[:12]  # Limit to top 12 for executive summary
    
    def clean_html_content(self, content: str) -> str:
        """Clean HTML tags and entities from content"""
        if not content:
            return "No description available"
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def extract_author_from_article(self, article: Dict[str, Any]) -> str:
        """Extract author with enhanced domain mapping for SF/tech publications"""
        
        # Try to get author from article data
        if 'author' in article and article['author']:
            return article['author']
        
        # Extract from URL domain with SF/tech focus
        url = article.get('url', '')
        source = article.get('source', '')
        
        domain_mapping = {
            'techcrunch.com': 'Editorial Team, TechCrunch',
            'venturebeat.com': 'Editorial Team, VentureBeat',
            'wired.com': 'Editorial Team, Wired',
            'theverge.com': 'Editorial Team, The Verge',
            'arstechnica.com': 'Editorial Team, Ars Technica',
            'engadget.com': 'Editorial Team, Engadget',
            'recode.net': 'Editorial Team, Recode',
            'sfgate.com': 'Editorial Team, SF Gate',
            'sfchronicle.com': 'Editorial Team, SF Chronicle',
            'mercurynews.com': 'Editorial Team, Mercury News',
            'siliconvalley.com': 'Editorial Team, Silicon Valley Business Journal',
            'bizjournals.com': 'Editorial Team, Business Journal',
            'reuters.com': 'Editorial Team, Reuters',
            'bloomberg.com': 'Editorial Team, Bloomberg',
            'wsj.com': 'Editorial Team, Wall Street Journal',
            'ft.com': 'Editorial Team, Financial Times',
            'cnbc.com': 'Editorial Team, CNBC',
            'cnn.com': 'Editorial Team, CNN Business',
            'yahoo.com': 'Editorial Team, Yahoo Finance'
        }
        
        for domain, author in domain_mapping.items():
            if domain in url:
                return author
        
        # Use source if available
        if source:
            return f"Editorial Team, {source}"
        
        return "Editorial Team"
    
    def generate_enhanced_sf_fallback(self, articles: List[Dict[str, Any]]) -> str:
        """Generate enhanced SF executive fallback digest"""
        
        print("🔄 Generating enhanced SF executive fallback digest...")
        
        digest_content = f"""# San Francisco Executive Daily News Summary
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Focus:** San Francisco Bay Area, Technology, Business & Innovation
**Format:** Executive summary with key insights and strategic implications

---

## Executive Summary

Today's digest covers {len(articles)} key developments affecting the San Francisco Bay Area business ecosystem, including technology sector updates, regulatory changes, market movements, and innovation trends relevant to executive decision-making.

---

## Key Articles

"""
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled Article')
            description = article.get('description', '')
            url = article.get('url', '#')
            source = article.get('source', 'Unknown Source')
            
            # Clean HTML content
            clean_description = self.clean_html_content(description)
            
            # Extract author
            author = self.extract_author_from_article(article)
            
            # Determine article category for better insights
            title_lower = title.lower()
            if any(term in title_lower for term in ['ai', 'artificial intelligence', 'machine learning']):
                category_insight = "AI/ML sector implications for competitive positioning and talent acquisition"
            elif any(term in title_lower for term in ['layoff', 'job', 'employment', 'hiring']):
                category_insight = "Workforce and talent market impacts on operational planning"
            elif any(term in title_lower for term in ['funding', 'investment', 'ipo', 'acquisition']):
                category_insight = "Capital markets and M&A activity affecting industry dynamics"
            elif any(term in title_lower for term in ['regulation', 'policy', 'government']):
                category_insight = "Regulatory environment changes requiring compliance and strategic adjustments"
            elif any(term in title_lower for term in ['real estate', 'housing', 'office']):
                category_insight = "Commercial real estate trends impacting facility and expansion decisions"
            else:
                category_insight = "Market developments with potential strategic and operational implications"
            
            digest_content += f"""### {i}. {title}

**Source:** {author}  
**Publication:** {source}

**Executive Summary:**
• **Key Development:** {clean_description[:200]}{'...' if len(clean_description) > 200 else ''}
• **Strategic Implication:** {category_insight}
• **Market Context:** Development reflects broader trends in Bay Area technology and business ecosystem
• **Executive Action:** Monitor for potential impacts on operations, partnerships, and strategic planning
• **Stakeholder Relevance:** Consider implications for investors, employees, customers, and regulatory compliance

**Read Full Article:** [{title}]({url})

---

"""
        
        # Add executive insights section
        digest_content += f"""## Strategic Insights & Recommendations

### Market Trends Identified:
• Technology sector continues evolution with AI/ML developments driving competitive dynamics
• Employment and talent market shifts requiring adaptive workforce strategies
• Regulatory environment changes necessitating proactive compliance planning
• Capital markets activity indicating investor sentiment and funding availability
• Real estate and infrastructure developments affecting operational costs and expansion plans

### Executive Action Items:
• **Short-term (1-30 days):** Review immediate impacts on current operations and partnerships
• **Medium-term (1-6 months):** Assess strategic positioning relative to identified market trends
• **Long-term (6+ months):** Incorporate insights into annual planning and strategic roadmap development

### Risk Factors to Monitor:
• Regulatory compliance requirements and potential policy changes
• Talent acquisition and retention challenges in competitive market
• Technology disruption and competitive positioning risks
• Economic indicators affecting customer demand and market conditions

---

**Digest Statistics:**
- Total articles analyzed: {len(articles)}
- Geographic focus: San Francisco Bay Area
- Sector emphasis: Technology, Business, Innovation
- Generation method: Enhanced executive analysis
- Next update: {datetime.now().strftime("%Y-%m-%d")} (daily)

*This digest is generated for executive decision-making and strategic planning purposes.*
"""
        
        return digest_content
    
    def create_sf_analysis_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for SF executive digest"""
        
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            description = self.clean_html_content(article.get('description', ''))
            url = article.get('url', '')
            source = article.get('source', 'Unknown')
            
            articles_text += f"""
Article {i}:
Title: {title}
Source: {source}
Description: {description}
URL: {url}
---
"""
        
        prompt = f"""Create a San Francisco Executive Daily News Summary with the following format:

# San Francisco Executive Daily News Summary
**Date:** {datetime.now().strftime("%B %d, %Y")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
**Focus:** San Francisco Bay Area, Technology, Business & Innovation
**Format:** Executive summary with key insights and strategic implications

## Executive Summary
[Provide a 2-3 sentence overview of the key themes and developments]

## Key Articles

For each article, use this format:

### [Number]. [Article Title]

**Source:** [Author/Publication]

**Executive Summary:**
• **Key Development:** [Main news/development from the article]
• **Strategic Implication:** [What this means for SF/Bay Area businesses and executives]
• **Market Context:** [How this fits into broader market trends]
• **Executive Action:** [Recommended actions or considerations for executives]
• **Stakeholder Relevance:** [Impact on investors, employees, customers, regulators]

**Read Full Article:** [[Article Title]]([URL])

---

## Strategic Insights & Recommendations
[Provide executive-level insights, trends, and action items based on the articles]

Articles to analyze:
{articles_text}

Focus on San Francisco Bay Area business implications, technology sector impacts, and executive decision-making insights. Emphasize strategic implications over basic news reporting.
"""
        
        return prompt
    
    def generate_digest(self) -> Optional[str]:
        """Generate the complete SF executive digest"""
        
        print("🚀 Starting San Francisco Executive Bedrock Digest Generation...")
        print("🌉 Focus: SF Bay Area Technology & Business News")
        
        # Load data
        digest_data = self.load_latest_daily_digest()
        if not digest_data:
            print("❌ No digest data available")
            return None
        
        # Select relevant articles
        selected_articles = self.select_sf_relevant_articles(digest_data)
        if not selected_articles:
            print("❌ No SF-relevant articles found")
            return None
        
        # Create prompt
        prompt = self.create_sf_analysis_prompt(selected_articles)
        
        # Try Bedrock Claude Haiku 3
        bedrock_result = self.generate_with_bedrock_claude(prompt)
        
        # Use fallback if Bedrock fails
        if bedrock_result:
            digest_content = bedrock_result
            generation_method = "AWS Bedrock Claude Haiku 3"
        else:
            print("🔄 Bedrock unavailable, using enhanced SF executive fallback...")
            digest_content = self.generate_enhanced_sf_fallback(selected_articles)
            generation_method = "Enhanced SF Executive Fallback"
        
        # Save digest
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"sf_executive_bedrock_digest_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest_content)
        
        print(f"💾 SF Executive digest saved to: {filename}")
        print(f"🤖 Generation method: {generation_method}")
        print(f"📈 Articles processed: {len(selected_articles)}")
        print(f"🌉 Geographic focus: San Francisco Bay Area")
        print(f"💼 Target audience: C-level executives and senior leadership")
        
        return filename

def main():
    """Main function to generate SF executive digest"""
    
    print("🌉 San Francisco Executive News Summary Generator")
    print("🤖 Using AWS Bedrock Claude Haiku 3")
    print("=" * 60)
    
    # Check AWS setup
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    
    if not aws_access_key or not aws_secret_key:
        print("⚠️  AWS credentials not found. Set the following environment variables:")
        print("   export AWS_ACCESS_KEY_ID='your-access-key'")
        print("   export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print("   export AWS_DEFAULT_REGION='us-west-2'  # Optional, defaults to us-west-2")
        print("   Will use enhanced SF executive fallback generation instead")
        print()
    
    # Generate digest
    generator = SFExecutiveBedrockDigest()
    result = generator.generate_digest()
    
    if result:
        print(f"\n✅ SF Executive digest generation completed!")
        print(f"📄 File: {result}")
        print(f"🎯 Optimized for: San Francisco Bay Area executives")
        print(f"📊 Content focus: Technology, business, innovation, strategic insights")
    else:
        print("❌ SF Executive digest generation failed")

if __name__ == "__main__":
    main()

