#!/usr/bin/env python3
"""
Enhanced News Aggregator for Economic and Financial News
Configurable news sources with free and subscription-based feeds
Includes article highlights and flexible source management
Now with LLM-powered analysis and summarization
"""

import requests
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Any, Optional
import os
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# LLM Integration imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not available. Install with: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Anthropic not available. Install with: pip install anthropic")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available. Install with: pip install transformers torch")

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("LiteLLM not available. Install with: pip install litellm")

@dataclass
class NewsSource:
    """Configuration for a news source"""
    name: str
    url: str
    source_type: str  # 'free_rss', 'subscription_rss', 'api', 'web_scraping'
    category: str = 'general'  # 'free', 'subscription'
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: float = 1.0  # seconds between requests
    max_articles: int = 10
    active: bool = True

class LLMService:
    """Service for LLM-powered content analysis and generation"""
    
    def __init__(self, provider: str = "auto", api_key: Optional[str] = None, model: str = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY') or os.getenv('LITELLM_API_KEY')
        self.client = None
        self.local_model = None
        
        # Initialize based on available providers
        if provider == "auto":
            self._auto_initialize()
        elif provider == "openai" and OPENAI_AVAILABLE:
            self._init_openai()
        elif provider == "anthropic" and ANTHROPIC_AVAILABLE:
            self._init_anthropic()
        elif provider == "litellm" and LITELLM_AVAILABLE:
            self._init_litellm()
        elif provider == "local" and TRANSFORMERS_AVAILABLE:
            self._init_local()
        else:
            print(f"Provider {provider} not available or not installed")
    
    def _auto_initialize(self):
        """Automatically choose the best available LLM provider"""
        if LITELLM_AVAILABLE and (os.getenv('LITELLM_API_KEY') or self.api_key):
            self._init_litellm()
            self.provider = "litellm"
        elif OPENAI_AVAILABLE and (os.getenv('OPENAI_API_KEY') or self.api_key):
            self._init_openai()
            self.provider = "openai"
        elif ANTHROPIC_AVAILABLE and (os.getenv('ANTHROPIC_API_KEY') or self.api_key):
            self._init_anthropic()
            self.provider = "anthropic"
        elif TRANSFORMERS_AVAILABLE:
            self._init_local()
            self.provider = "local"
        else:
            print("No LLM providers available. Install openai, anthropic, litellm, or transformers")
    
    @property
    def available(self) -> bool:
        """Check if LLM service is available and properly initialized"""
        if self.provider == "openai":
            return self.client is not None and OPENAI_AVAILABLE
        elif self.provider == "anthropic":
            return self.client is not None and ANTHROPIC_AVAILABLE
        elif self.provider == "litellm":
            return self.client is not None and LITELLM_AVAILABLE
        elif self.provider == "local":
            return self.local_model is not None and TRANSFORMERS_AVAILABLE
        return False
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            openai.api_key = self.api_key or os.getenv('OPENAI_API_KEY')
            self.client = openai
            print("Initialized OpenAI LLM service")
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key or os.getenv('ANTHROPIC_API_KEY'))
            print("Initialized Anthropic LLM service")
        except Exception as e:
            print(f"Failed to initialize Anthropic: {e}")
    
    def _init_litellm(self):
        """Initialize LiteLLM client"""
        try:
            # Load config if available
            config = self._load_llm_config()
            llm_settings = config.get('llm_settings', {})
            
            # Configure LiteLLM proxy from config or fallback
            provider_url = llm_settings.get('provider', 'http://44.201.244.45:8250/')
            if provider_url.startswith('http'):
                litellm.api_base = provider_url
            
            litellm.api_key = llm_settings.get('api_key') or self.api_key or os.getenv('LITELLM_API_KEY') or "sk-12345"
            
            # Set model from config or default
            if not self.model:
                self.model = llm_settings.get('models', {}).get('litellm', 'claude-3-5-sonnet-20241022')
            
            # Test the connection
            litellm.set_verbose = False  # Reduce logging
            self.client = litellm
            print(f"Initialized LiteLLM service with endpoint: {provider_url}")
            print(f"Using model: {self.model}")
        except Exception as e:
            print(f"Failed to initialize LiteLLM: {e}")
    
    def _load_llm_config(self):
        """Load LLM configuration from file"""
        try:
            with open('llm_config_example.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _init_local(self):
        """Initialize local transformer model"""
        try:
            # Use a lightweight model for summarization
            self.local_model = pipeline("summarization", model="facebook/bart-large-cnn")
            print("Initialized local BART model for summarization")
        except Exception as e:
            print(f"Failed to initialize local model: {e}")
    
    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """Generate a concise summary of the text"""
        if not text or len(text.strip()) < 50:
            return text
        
        try:
            if self.provider == "openai" and self.client:
                return self._openai_summarize(text, max_length)
            elif self.provider == "anthropic" and self.client:
                return self._anthropic_summarize(text, max_length)
            elif self.provider == "litellm" and self.client:
                return self._litellm_summarize(text, max_length)
            elif self.provider == "local" and self.local_model:
                return self._local_summarize(text, max_length)
            else:
                # Fallback to simple truncation
                return text[:max_length] + "..." if len(text) > max_length else text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def _openai_summarize(self, text: str, max_length: int) -> str:
        """Summarize using OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial news analyst. Summarize the following article in one clear, concise sentence focusing on the key economic impact."},
                    {"role": "user", "content": f"Summarize this article: {text[:1500]}"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI summarization error: {e}")
            return text[:max_length] + "..."
    
    def _anthropic_summarize(self, text: str, max_length: int) -> str:
        """Summarize using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[
                    {"role": "user", "content": f"Summarize this economic news article in one clear sentence: {text[:1500]}"}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Anthropic summarization error: {e}")
            return text[:max_length] + "..."
    
    def _litellm_summarize(self, text: str, max_length: int) -> str:
        """Summarize using LiteLLM"""
        try:
            response = self.client.completion(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"Summarize this economic news article in one clear sentence: {text[:1500]}"}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LiteLLM summarization error: {e}")
            return text[:max_length] + "..."
    
    def _local_summarize(self, text: str, max_length: int) -> str:
        """Summarize using local BART model"""
        try:
            # BART works better with longer text, so ensure minimum length
            if len(text) < 100:
                return text
            
            summary = self.local_model(text[:1024], max_length=max_length//2, min_length=20, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Local summarization error: {e}")
            return text[:max_length] + "..."
    
    def extract_key_insights(self, text: str) -> List[str]:
        """Extract key insights and highlights from article text"""
        if not text or len(text.strip()) < 100:
            return []
        
        try:
            if self.provider == "openai" and self.client:
                return self._openai_insights(text)
            elif self.provider == "anthropic" and self.client:
                return self._anthropic_insights(text)
            elif self.provider == "litellm" and self.client:
                return self._litellm_insights(text)
            else:
                # Fallback to rule-based extraction
                return self._rule_based_insights(text)
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return self._rule_based_insights(text)
    
    def _openai_insights(self, text: str) -> List[str]:
        """Extract insights using OpenAI with structured prompt"""
        try:
            structured_prompt = """
You are a financial news analyst. For the given article, provide a structured analysis with:

Summary Highlights (4 Bullet Points):
- Concisely summarize key points focusing on main developments, key data, and notable changes
- Include important quotes from influential figures (government officials, CEOs, economists)
- Highlight potential economic or political implications
- Mention market reactions or predictions (stock market, interest rates, public sentiment)

Format each bullet point clearly and focus on actionable insights.
"""
            
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": structured_prompt},
                    {"role": "user", "content": f"Analyze this article: {text[:2000]}"}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            insights_text = response.choices[0].message.content.strip()
            # Split by bullet points or newlines
            insights = [insight.strip().lstrip('•-*').strip() for insight in insights_text.split('\n') if insight.strip()]
            return insights[:4]
        except Exception as e:
            print(f"OpenAI insights error: {e}")
            return []
    
    def _anthropic_insights(self, text: str) -> List[str]:
        """Extract insights using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": f"Extract 3-4 key economic insights from this article as bullet points: {text[:2000]}"}
                ]
            )
            
            insights_text = response.content[0].text.strip()
            insights = [insight.strip().lstrip('•-*').strip() for insight in insights_text.split('\n') if insight.strip()]
            return insights[:4]
        except Exception as e:
            print(f"Anthropic insights error: {e}")
            return []
    
    def _litellm_insights(self, text: str) -> List[str]:
        """Extract insights using LiteLLM with your specific format"""
        try:
            # Your specific format: Topic/headline extraction, Summary in 4-5 bullets ~100 words each, including notable quotes
            structured_prompt = """
You are a financial news analyst. For the given article, provide:

1. Topic/Headline: Extract the main economic topic and create a clear, focused headline
2. Summary: Create 4-5 bullet points, each approximately 100 words, covering:
   - Key economic developments and data points
   - Important quotes from officials, CEOs, or economists (include actual quotes)
   - Market implications and reactions
   - Policy or regulatory impacts
   - Future outlook or predictions

Format your response as:
TOPIC: [Clear headline]
SUMMARY:
• [Bullet point 1 - ~100 words with quotes if available]
• [Bullet point 2 - ~100 words with quotes if available]
• [Bullet point 3 - ~100 words with quotes if available]
• [Bullet point 4 - ~100 words with quotes if available]
• [Bullet point 5 - ~100 words with quotes if available] (if needed)

Article text: {text}
"""
            
            response = self.client.completion(
                model=self.model,
                messages=[
                    {"role": "user", "content": structured_prompt.format(text=text[:2500])}
                ],
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the structured response
            lines = content.split('\n')
            topic = ""
            summary_bullets = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('TOPIC:'):
                    topic = line.replace('TOPIC:', '').strip()
                elif line.startswith('SUMMARY:'):
                    current_section = 'summary'
                elif line.startswith('•') and current_section == 'summary':
                    bullet = line.lstrip('•').strip()
                    if bullet:
                        summary_bullets.append(bullet)
            
            # Return structured data as list for compatibility
            result = []
            if topic:
                result.append(f"📊 Topic: {topic}")
            
            for i, bullet in enumerate(summary_bullets[:5], 1):
                result.append(f"🔹 Point {i}: {bullet}")
            
            return result
            
        except Exception as e:
            print(f"LiteLLM insights error: {e}")
            return []
    
    def _rule_based_insights(self, text: str) -> List[str]:
        """Fallback rule-based insight extraction"""
        insights = []
        sentences = text.split('.')
        
        # Look for sentences with key economic indicators
        key_patterns = [
            r'(inflation|unemployment|gdp|interest rate|federal reserve|fed).{10,100}',
            r'(said|stated|announced|reported).{10,100}',
            r'(\d+\.?\d*%|\$\d+|\d+\s*(billion|million|trillion)).{10,100}',
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 50 <= len(sentence) <= 150:
                for pattern in key_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        insights.append(sentence)
                        break
                if len(insights) >= 4:
                    break
        
        return insights[:4]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and economic tone of the article"""
        if not text:
            return {"sentiment": "neutral", "confidence": 0.0, "economic_tone": "neutral"}
        
        try:
            if self.provider == "openai" and self.client:
                return self._openai_sentiment(text)
            elif self.provider == "anthropic" and self.client:
                return self._anthropic_sentiment(text)
            elif self.provider == "litellm" and self.client:
                return self._litellm_sentiment(text)
            else:
                return self._rule_based_sentiment(text)
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "economic_tone": "neutral"}
    
    def _openai_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI"""
        try:
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the economic sentiment of this article. Respond with JSON: {\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0, \"economic_tone\": \"bullish/bearish/neutral\", \"reasoning\": \"brief explanation\"}"},
                    {"role": "user", "content": f"Analyze sentiment: {text[:1000]}"}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"OpenAI sentiment error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "economic_tone": "neutral"}
    
    def _anthropic_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Anthropic Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": f"Analyze the economic sentiment of this article and respond with JSON format: {{\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0, \"economic_tone\": \"bullish/bearish/neutral\"}}. Article: {text[:1000]}"}
                ]
            )
            
            result = json.loads(response.content[0].text.strip())
            return result
        except Exception as e:
            print(f"Anthropic sentiment error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "economic_tone": "neutral"}
    
    def _litellm_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using LiteLLM"""
        try:
            response = self.client.completion(
                model=self.model,
                messages=[
                    {"role": "user", "content": f"Analyze the economic sentiment of this article and respond with JSON format: {{\"sentiment\": \"positive/negative/neutral\", \"confidence\": 0.0-1.0, \"economic_tone\": \"bullish/bearish/neutral\"}}. Article: {text[:1000]}"}
                ],
                max_tokens=100
            )
            
            content = response.choices[0].message.content.strip()
            # Try to extract JSON from the response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                sentiment = "neutral"
                confidence = 0.5
                economic_tone = "neutral"
                
                if "positive" in content.lower():
                    sentiment = "positive"
                    economic_tone = "bullish"
                elif "negative" in content.lower():
                    sentiment = "negative"
                    economic_tone = "bearish"
                
                return {"sentiment": sentiment, "confidence": confidence, "economic_tone": economic_tone}
                
        except Exception as e:
            print(f"LiteLLM sentiment error: {e}")
            return {"sentiment": "neutral", "confidence": 0.0, "economic_tone": "neutral"}
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ['growth', 'increase', 'rise', 'gain', 'improve', 'strong', 'robust', 'positive', 'optimistic']
        negative_words = ['decline', 'fall', 'drop', 'decrease', 'weak', 'concern', 'risk', 'negative', 'pessimistic']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            economic_tone = "bullish"
            confidence = min(0.8, (pos_count - neg_count) / 10)
        elif neg_count > pos_count:
            sentiment = "negative"
            economic_tone = "bearish"
            confidence = min(0.8, (neg_count - pos_count) / 10)
        else:
            sentiment = "neutral"
            economic_tone = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "economic_tone": economic_tone,
            "reasoning": f"Based on {pos_count} positive and {neg_count} negative indicators"
        }
    
    def generate_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Generate comprehensive structured analysis using the detailed prompt format"""
        if not self.available:
            return self._rule_based_structured_analysis(article, article_content)
        
        try:
            if self.provider == "openai":
                return self._openai_structured_analysis(article, article_content)
            elif self.provider == "anthropic":
                return self._anthropic_structured_analysis(article, article_content)
            elif self.provider == "litellm":
                return self._litellm_structured_analysis(article, article_content)
            elif self.provider == "local":
                return self._local_structured_analysis(article, article_content)
        except Exception as e:
            print(f"Error generating structured analysis: {e}")
            return self._rule_based_structured_analysis(article, article_content)
    
    def _openai_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Generate structured analysis using OpenAI with comprehensive prompt"""
        try:
            content = article_content or article.get('description', '') or article.get('title', '')
            
            structured_prompt = """
You are a financial news analyst. For the given article, provide a comprehensive structured analysis with:

Topic/Headline: Title of the news article or main focus of the story.

Summary Highlights (4 Bullet Points):
- Concisely summarize key points focusing on main developments, key data, and notable changes
- Include important quotes from influential figures (government officials, CEOs, economists)
- Highlight potential economic or political implications
- Mention market reactions or predictions (stock market, interest rates, public sentiment)

Notable Quotes:
- Include relevant quotes from major stakeholders (President, Federal Reserve Chair, CEOs, economists, market experts)
- Ensure quotes reflect differing perspectives or key insights

Context & Implications:
- Provide brief context on why this issue is important
- Highlight potential broader impact on economy, financial markets, or political landscape
- Mention potential consequences (policy shifts, market volatility, consumer behavior changes)

Format your response as JSON with keys: topic_headline, summary_highlights, notable_quotes, context_implications
"""
            
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": structured_prompt},
                    {"role": "user", "content": f"Article Title: {article.get('title', '')}\nContent: {content[:2000]}"}
                ],
                max_tokens=600,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except Exception as e:
            print(f"OpenAI structured analysis error: {e}")
            return self._rule_based_structured_analysis(article, article_content)
    
    def _anthropic_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Generate structured analysis using Anthropic Claude"""
        try:
            content = article_content or article.get('description', '') or article.get('title', '')
            
            prompt = f"""
Analyze this financial news article and provide a structured analysis in JSON format:

Article Title: {article.get('title', '')}
Content: {content[:2000]}

Provide analysis with these keys:
- topic_headline: Main focus of the story
- summary_highlights: Array of 4 bullet points covering key developments, quotes, implications, and market reactions
- notable_quotes: Array of relevant quotes from stakeholders
- context_implications: Brief context and potential broader impacts

Format as valid JSON.
"""
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text.strip())
            return result
        except Exception as e:
            print(f"Anthropic structured analysis error: {e}")
            return self._rule_based_structured_analysis(article, article_content)
    
    def _litellm_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Generate structured analysis using LiteLLM with your specific format requirements"""
        try:
            content = article_content or article.get('description', '') or article.get('title', '')
            
            # Your specific format: Topic/headline extraction, Summary in 4-5 bullets ~100 words each, including notable quotes
            prompt = f"""
Analyze this financial news article and provide a structured analysis in JSON format with your specific requirements:

Article Title: {article.get('title', '')}
Content: {content[:2500]}

Provide analysis with these exact keys:
- topic_headline: Extract the main economic topic and create a clear, focused headline
- summary_highlights: Array of exactly 4-5 bullet points, each approximately 100 words, covering:
  * Key economic developments and data points
  * Important quotes from officials, CEOs, or economists (include actual quotes)
  * Market implications and reactions
  * Policy or regulatory impacts
  * Future outlook or predictions
- notable_quotes: Array of actual quotes from the article with attribution
- context_implications: Analysis of broader economic impact and market sentiment
- market_sentiment: Object with sentiment (positive/negative/neutral), confidence (0.0-1.0), and economic_tone (bullish/bearish/neutral)

Each summary highlight should be substantial (~100 words) and include specific details, numbers, and quotes where available.

Format as valid JSON only.
"""
            
            response = self.client.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            content_response = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(content_response)
                
                # Ensure we have the required structure
                if not isinstance(result.get('summary_highlights'), list):
                    result['summary_highlights'] = []
                if not isinstance(result.get('notable_quotes'), list):
                    result['notable_quotes'] = []
                
                # Ensure we have 4-5 summary highlights as requested
                while len(result['summary_highlights']) < 4:
                    result['summary_highlights'].append("Additional analysis pending based on available information.")
                
                return result
                
            except json.JSONDecodeError:
                print("LiteLLM returned invalid JSON, using fallback structure")
                return self._rule_based_structured_analysis(article, article_content)
                
        except Exception as e:
            print(f"LiteLLM structured analysis error: {e}")
            return self._rule_based_structured_analysis(article, article_content)
    
    def _local_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Generate structured analysis using local model (simplified)"""
        # Local models are primarily for summarization, so provide a simplified structure
        content = article_content or article.get('description', '') or article.get('title', '')
        summary = self._local_summarize(content, max_length=200)
        
        return {
            "topic_headline": article.get('title', 'Economic News Update'),
            "summary_highlights": [
                f"Key development: {summary[:100]}...",
                "Economic implications under analysis",
                "Market impact being assessed",
                "Further developments expected"
            ],
            "notable_quotes": ["Analysis based on available information"],
            "context_implications": f"This development relates to ongoing economic trends. {summary}"
        }
    
    def _rule_based_structured_analysis(self, article: dict, article_content: str = None) -> dict:
        """Fallback rule-based structured analysis"""
        content = article_content or article.get('description', '') or article.get('title', '')
        
        # Extract key phrases and create structured response
        key_phrases = []
        economic_terms = ['federal reserve', 'interest rate', 'inflation', 'unemployment', 'gdp', 'market', 'economy']
        
        for term in economic_terms:
            if term in content.lower():
                key_phrases.append(term.title())
        
        return {
            "topic_headline": article.get('title', 'Economic News Update'),
            "summary_highlights": [
                f"Article covers: {', '.join(key_phrases[:3]) if key_phrases else 'economic developments'}",
                "Key economic indicators and trends discussed",
                "Policy implications and market impact analyzed", 
                "Ongoing monitoring of economic conditions"
            ],
            "notable_quotes": ["Detailed quotes available in full article"],
            "context_implications": f"This development is part of broader economic trends affecting {'key areas: ' + ', '.join(key_phrases) if key_phrases else 'the financial markets'}."
        }

class NewsAggregator:
    def __init__(self, config_file: Optional[str] = None, llm_provider: str = "litellm", llm_api_key: Optional[str] = None):
        self.keywords = [
            'unemployment', 'inflation', 'market risk', 'banking', 
            'federal reserve', 'interest rates', 'economic outlook',
            'GDP', 'recession', 'monetary policy', 'fiscal policy',
            'fed', 'jerome powell', 'fomc', 'federal open market committee',
            'fed chair', 'fed governor', 'fed official', 'fed policy',
            'fed meeting', 'fed minutes', 'fed speech', 'fed testimony'
        ]
        
        # Initialize LLM service for enhanced analysis
        self.llm_service = LLMService(provider=llm_provider, api_key=llm_api_key)
        self.use_llm = self.llm_service.client is not None or self.llm_service.local_model is not None
        
        if self.use_llm:
            print(f"[OK] LLM-powered analysis enabled using {self.llm_service.provider}")
        else:
            print("[WARNING] LLM not available, using rule-based analysis")
        
        # Initialize with default sources
        self.free_sources = self._get_default_free_sources()
        self.subscription_sources = self._get_default_subscription_sources()
        
        # Load custom configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_sources_config(config_file)
        
        self.articles = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _get_default_free_sources(self) -> List[NewsSource]:
        """Default free RSS feed sources"""
        return [
            NewsSource(
                name='Reuters Business',
                url='https://www.reuters.com/business/finance/rss',
                source_type='free_rss',
                category='free',
                max_articles=15
            ),
            NewsSource(
                name='AP Business',
                url='https://feeds.apnews.com/rss/apf-business',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='NBC Business',
                url='https://feeds.nbcnews.com/nbcnews/public/business',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='BBC Business',
                url='http://feeds.bbci.co.uk/news/business/rss.xml',
                source_type='free_rss',
                category='free',
                max_articles=12
            ),
            NewsSource(
                name='CNN Business',
                url='http://rss.cnn.com/rss/money_latest.rss',
                source_type='free_rss',
                category='free',
                max_articles=10
            ),
            NewsSource(
                name='MarketWatch',
                url='https://feeds.marketwatch.com/marketwatch/topstories/',
                source_type='free_rss',
                category='free',
                max_articles=8
            ),
            NewsSource(
                name='Federal Reserve News',
                url='https://www.federalreserve.gov/feeds/press_all.xml',
                source_type='free_rss',
                category='free',
                max_articles=20
            ),
            NewsSource(
                name='Fed Economic Data (FRED)',
                url='https://fred.stlouisfed.org/releases/rss',
                source_type='free_rss',
                category='free',
                max_articles=15
            )
        ]
    
    def _get_default_subscription_sources(self) -> List[NewsSource]:
        """Default subscription-based sources (require API keys or premium access)"""
        return [
            NewsSource(
                name='Wall Street Journal',
                url='https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
                source_type='subscription_rss',
                category='subscription',
                max_articles=15,
                active=False  # Requires subscription
            ),
            NewsSource(
                name='Financial Times',
                url='https://www.ft.com/rss/home/us',
                source_type='subscription_rss',
                category='subscription',
                max_articles=12,
                active=False  # Requires subscription
            ),
            NewsSource(
                name='Bloomberg Terminal',
                url='https://api.bloomberg.com/news',
                source_type='api',
                category='subscription',
                max_articles=20,
                active=False  # Requires Bloomberg Terminal access
            ),
            NewsSource(
                name='Yahoo Finance',
                url='https://feeds.finance.yahoo.com/rss/2.0/headline',
                source_type='free_rss',
                category='free',
                max_articles=10
            )
        ]
    
    def add_free_source(self, source: NewsSource) -> None:
        """Add a new free news source"""
        source.category = 'free'
        self.free_sources.append(source)
        print(f"Added free source: {source.name}")
    
    def add_subscription_source(self, source: NewsSource) -> None:
        """Add a new subscription-based news source"""
        source.category = 'subscription'
        self.subscription_sources.append(source)
        print(f"Added subscription source: {source.name}")
    
    def load_sources_config(self, config_file: str) -> None:
        """Load sources configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load free sources
            if 'free_sources' in config:
                for source_data in config['free_sources']:
                    source = NewsSource(**source_data)
                    self.free_sources.append(source)
            
            # Load subscription sources
            if 'subscription_sources' in config:
                for source_data in config['subscription_sources']:
                    source = NewsSource(**source_data)
                    self.subscription_sources.append(source)
                    
            print(f"Loaded configuration from {config_file}")
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
    
    def save_sources_config(self, config_file: str) -> None:
        """Save current sources configuration to JSON file"""
        config = {
            'free_sources': [source.__dict__ for source in self.free_sources],
            'subscription_sources': [source.__dict__ for source in self.subscription_sources]
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_file}")
    
    def fetch_article_content(self, url: str) -> str:
        """Fetch full article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Try common article content selectors
                content_selectors = [
                    'article', '.article-content', '.story-body', '.entry-content',
                    '.post-content', '.content', '.article-body', 'main'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Get text and clean it
                        text = content_elem.get_text(separator=' ', strip=True)
                        # Limit to first 2000 characters to avoid too much content
                        return text[:2000] if len(text) > 2000 else text
                
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                    return text[:2000] if len(text) > 2000 else text
                    
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")
        
        return ""

    def extract_quotes(self, text: str) -> List[str]:
        """Extract quotes from article text"""
        quotes = []
        
        # Find text in quotes
        import re
        quote_patterns = [
            r'"([^"]{20,200})"',  # Double quotes
            r"'([^']{20,200})'",  # Single quotes
            r'"([^"]{20,200})"',  # Curly quotes
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches[:3])  # Limit to 3 quotes per pattern
        
        return quotes[:5]  # Return max 5 quotes

    def generate_highlights(self, article: Dict[str, Any]) -> List[str]:
        """Generate 4-5 content-based highlights with LLM-powered analysis"""
        highlights = []
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        
        # Fetch full article content
        full_content = self.fetch_article_content(url)
        
        # Combine all available text
        all_text = f"{title} {description} {full_content}"
        
        # Use LLM for enhanced analysis if available
        if self.use_llm and len(all_text.strip()) > 100:
            try:
                # Get LLM-powered insights
                llm_insights = self.llm_service.extract_key_insights(all_text)
                
                # Add LLM insights as highlights
                for insight in llm_insights[:3]:  # Max 3 LLM insights
                    if insight and len(insight.strip()) > 20:
                        highlights.append(f'🧠 {insight.strip()}')
                
                # Get sentiment analysis
                sentiment_data = self.llm_service.analyze_sentiment(all_text)
                if sentiment_data.get('sentiment') != 'neutral':
                    sentiment_emoji = '📈' if sentiment_data.get('economic_tone') == 'bullish' else '📉' if sentiment_data.get('economic_tone') == 'bearish' else '📊'
                    highlights.append(f'{sentiment_emoji} Economic sentiment: {sentiment_data.get("sentiment", "neutral").title()} ({sentiment_data.get("confidence", 0):.1f} confidence)')
                
            except Exception as e:
                print(f"LLM analysis failed for article, falling back to rule-based: {e}")
                self.use_llm = False  # Temporarily disable for this session
        
        # Fallback to rule-based analysis or supplement LLM results
        if not self.use_llm or len(highlights) < 3:
            # Extract quotes from the content
            quotes = self.extract_quotes(all_text)
            
            # Add quotes as highlights (prioritize these)
            for quote in quotes[:2]:  # Max 2 quotes
                if len(highlights) < 5:
                    highlights.append(f'💬 "{quote}"')
            
            # Generate content-based highlights using rule-based approach
            sentences = all_text.split('.')
            key_sentences = []
            
            # Look for key economic indicators and statements
            economic_keywords = [
                'federal reserve', 'fed', 'inflation', 'unemployment', 'interest rate',
                'monetary policy', 'economic growth', 'gdp', 'market', 'banking'
            ]
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and len(sentence) < 150:  # Good length for highlights
                    if any(keyword in sentence.lower() for keyword in economic_keywords):
                        key_sentences.append(sentence)
            
            # Add key sentences as highlights
            for sentence in key_sentences[:2]:  # Max 2 key sentences to leave room for LLM insights
                if len(highlights) < 5:
                    # Clean up the sentence
                    clean_sentence = sentence.replace('\n', ' ').replace('\r', ' ')
                    clean_sentence = ' '.join(clean_sentence.split())  # Remove extra whitespace
                    if len(clean_sentence) > 20:
                        highlights.append(f'📊 {clean_sentence}')
        
        # If we still don't have enough highlights, add generic ones based on content analysis
        if len(highlights) < 4:
            content_lower = all_text.lower()
            
            if 'federal reserve' in content_lower or 'fed' in content_lower:
                highlights.append("🏛️ Federal Reserve policy developments discussed")
            
            if len(highlights) < 4 and ('inflation' in content_lower or 'price' in content_lower):
                highlights.append("💰 Inflation and pricing trends analyzed")
            
            if len(highlights) < 4 and ('employment' in content_lower or 'job' in content_lower):
                highlights.append("💼 Employment market conditions reported")
            
            if len(highlights) < 4 and ('market' in content_lower or 'economic' in content_lower):
                highlights.append("📈 Economic and market developments covered")
        
        # Remove duplicates while preserving order
        highlights = list(dict.fromkeys(highlights))
        
        # Ensure we have exactly 4-5 highlights
        if len(highlights) < 4:
            # Add more generic highlights if needed
            generic_highlights = [
                "📊 Economic indicators and market analysis",
                "🏛️ Policy implications and regulatory updates", 
                "🌍 Global economic impact assessment",
                "🔮 Economic outlook and forecasts"
            ]
            
            for generic in generic_highlights:
                if len(highlights) < 4 and generic not in highlights:
                    highlights.append(generic)
        
        # Limit to maximum 5 highlights
        return highlights[:5]
    
    def generate_llm_summary(self, article: Dict[str, Any]) -> str:
        """Generate an LLM-powered TL;DR summary for the article"""
        if not self.use_llm:
            # Fallback to simple truncation
            description = article.get('description', '')
            return description[:100] + "..." if len(description) > 100 else description
        
        title = article.get('title', '')
        description = article.get('description', '')
        url = article.get('url', '')
        
        # Fetch full article content for better summarization
        full_content = self.fetch_article_content(url)
        
        # Combine all available text
        all_text = f"{title} {description} {full_content}"
        
        if len(all_text.strip()) < 100:
            return description or title
        
        try:
            # Generate LLM-powered summary
            summary = self.llm_service.generate_summary(all_text, max_length=150)
            return summary if summary else (description[:100] + "..." if len(description) > 100 else description)
        except Exception as e:
            print(f"LLM summary generation failed: {e}")
            # Fallback to description
            return description[:100] + "..." if len(description) > 100 else description
    
    def enhance_article_with_llm(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance article with LLM-powered analysis"""
        enhanced_article = article.copy()
        
        if not self.use_llm:
            return enhanced_article
        
        try:
            # Get full content for analysis
            title = article.get('title', '')
            description = article.get('description', '')
            url = article.get('url', '')
            full_content = self.fetch_article_content(url)
            all_text = f"{title} {description} {full_content}"
            
            if len(all_text.strip()) > 100:
                # Add sentiment analysis
                sentiment_data = self.llm_service.analyze_sentiment(all_text)
                enhanced_article['sentiment_analysis'] = sentiment_data
                
                # Add LLM-generated summary
                enhanced_article['llm_summary'] = self.llm_service.generate_summary(all_text, max_length=200)
                
                # Add key insights
                insights = self.llm_service.extract_key_insights(all_text)
                enhanced_article['key_insights'] = insights
                
                # Mark as LLM-enhanced
                enhanced_article['llm_enhanced'] = True
            
        except Exception as e:
            print(f"Article enhancement failed: {e}")
            enhanced_article['llm_enhanced'] = False
        
        return enhanced_article
    
    def generate_structured_article_analysis(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive structured analysis for an article using the detailed prompt format"""
        enhanced_article = article.copy()
        
        if not self.use_llm:
            return self._generate_fallback_structured_analysis(article)
        
        try:
            # Get full content for analysis
            title = article.get('title', '')
            description = article.get('description', '')
            url = article.get('url', '')
            full_content = self.fetch_article_content(url)
            all_text = f"{title} {description} {full_content}"
            
            if len(all_text.strip()) > 100:
                # Generate structured analysis using the comprehensive prompt
                structured_analysis = self.llm_service.generate_structured_analysis(article, all_text)
                
                # Merge structured analysis into article
                enhanced_article.update({
                    'structured_analysis': structured_analysis,
                    'topic_headline': structured_analysis.get('topic_headline', title),
                    'summary_highlights': structured_analysis.get('summary_highlights', []),
                    'notable_quotes': structured_analysis.get('notable_quotes', []),
                    'context_implications': structured_analysis.get('context_implications', ''),
                    'llm_enhanced': True
                })
                
                # Also add traditional analysis for compatibility
                sentiment_data = self.llm_service.analyze_sentiment(all_text)
                enhanced_article['sentiment_analysis'] = sentiment_data
            
        except Exception as e:
            print(f"Structured article analysis failed: {e}")
            return self._generate_fallback_structured_analysis(article)
        
        return enhanced_article
    
    def _generate_fallback_structured_analysis(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback structured analysis when LLM is not available"""
        enhanced_article = article.copy()
        title = article.get('title', 'Economic News Update')
        description = article.get('description', '')
        
        # Create basic structured analysis
        enhanced_article.update({
            'structured_analysis': {
                'topic_headline': title,
                'summary_highlights': [
                    f"Article title: {title}",
                    f"Key content: {description[:100]}..." if description else "Economic development reported",
                    "Market implications under analysis",
                    "Further details available in full article"
                ],
                'notable_quotes': ["Full quotes available in original article"],
                'context_implications': f"This development relates to ongoing economic trends. {description[:200]}..." if description else "Economic significance being assessed."
            },
            'topic_headline': title,
            'summary_highlights': [
                f"📊 {title}",
                "💼 Economic implications discussed",
                "📈 Market impact being assessed",
                "🔍 Further analysis ongoing"
            ],
            'notable_quotes': ["Detailed analysis available in full article"],
            'context_implications': f"Economic development: {description[:150]}..." if description else "Ongoing economic situation requires monitoring.",
            'llm_enhanced': False
        })
        
        return enhanced_article
        
    def search_google_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """Search Google News for articles with specific keywords"""
        articles = []
        try:
            # Use Google News RSS feed for public access
            base_url = "https://news.google.com/rss/search"
            params = {
                'q': query,
                'hl': 'en-US',
                'gl': 'US',
                'ceid': 'US:en'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            if response.status_code == 200:
                # Parse RSS feed (simplified)
                content = response.text
                # Extract article information from RSS
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(content)
                    for item in root.findall('.//item')[:10]:  # Limit to 10 articles per query
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            articles.append({
                                'title': title.text,
                                'url': link.text,
                                'published': pub_date.text if pub_date is not None else '',
                                'description': description.text if description is not None else '',
                                'source': 'Google News',
                                'keyword': query
                            })
                except ET.ParseError:
                    print(f"Error parsing RSS for query: {query}")
                    
        except Exception as e:
            print(f"Error searching Google News for '{query}': {e}")
            
        return articles
    
    def fetch_from_source(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from a single news source"""
        articles = []
        
        if not source.active:
            print(f"Skipping inactive source: {source.name}")
            return articles
            
        try:
            print(f"Fetching from {source.name} ({source.source_type})...")
            
            if source.source_type in ['free_rss', 'subscription_rss']:
                articles = self._fetch_rss_feed(source)
            elif source.source_type == 'api':
                articles = self._fetch_api_source(source)
            elif source.source_type == 'web_scraping':
                articles = self._fetch_web_scraping(source)
            
            # Add highlights to each article
            for article in articles:
                article['highlights'] = self.generate_highlights(article)
                article['source_category'] = source.category
            
            time.sleep(source.rate_limit)  # Respect rate limiting
            
        except Exception as e:
            print(f"Error fetching from {source.name}: {e}")
            
        return articles[:source.max_articles]
    
    def _fetch_rss_feed(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from RSS feed"""
        articles = []
        
        try:
            headers = source.headers.copy()
            if source.api_key:
                headers['Authorization'] = f"Bearer {source.api_key}"
                
            response = self.session.get(source.url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(response.content)
                    
                    for item in root.findall('.//item'):
                        title = item.find('title')
                        link = item.find('link')
                        pub_date = item.find('pubDate')
                        description = item.find('description')
                        
                        if title is not None and link is not None:
                            title_text = title.text or ''
                            desc_text = (description.text or '') if description is not None else ''
                            
                            # Check if article is relevant to our keywords
                            content_lower = f"{title_text} {desc_text}".lower()
                            if any(keyword.lower() in content_lower for keyword in self.keywords):
                                articles.append({
                                    'title': title_text,
                                    'url': link.text,
                                    'published': pub_date.text if pub_date is not None else '',
                                    'description': desc_text,
                                    'source': source.name,
                                    'source_type': source.source_type,
                                    'keyword': 'RSS Feed'
                                })
                                
                except ET.ParseError as e:
                    print(f"Error parsing RSS feed from {source.name}: {e}")
            else:
                print(f"HTTP {response.status_code} error for {source.name}")
                
        except Exception as e:
            print(f"Error fetching RSS from {source.name}: {e}")
            
        return articles
    
    def _fetch_api_source(self, source: NewsSource) -> List[Dict]:
        """Fetch articles from API-based source"""
        articles = []
        
        if not source.api_key:
            print(f"API key required for {source.name}")
            return articles
            
        try:
            headers = source.headers.copy()
            headers['Authorization'] = f"Bearer {source.api_key}"
            
            # This is a placeholder for API-specific implementations
            # Each API would need its own implementation
            print(f"API fetching not yet implemented for {source.name}")
            
        except Exception as e:
            print(f"Error fetching from API {source.name}: {e}")
            
        return articles
    
    def _fetch_web_scraping(self, source: NewsSource) -> List[Dict]:
        """Fetch articles via web scraping (placeholder)"""
        print(f"Web scraping not yet implemented for {source.name}")
        return []
    
    def fetch_all_sources(self) -> List[Dict]:
        """Fetch articles from all active sources"""
        all_articles = []
        
        # Fetch from free sources
        print("Fetching from free sources...")
        for source in self.free_sources:
            if source.active:
                articles = self.fetch_from_source(source)
                all_articles.extend(articles)
        
        # Fetch from subscription sources
        print("Fetching from subscription sources...")
        for source in self.subscription_sources:
            if source.active:
                articles = self.fetch_from_source(source)
                all_articles.extend(articles)
        
        return all_articles
    
    def is_article_recent(self, article: Dict, target_date: datetime = None) -> bool:
        """Check if article was published on target date or day before"""
        if target_date is None:
            target_date = datetime.now()
        
        # Define the date range (target date and day before)
        day_before = target_date - timedelta(days=1)
        
        published_str = article.get('published', '')
        if not published_str:
            # If no publish date, assume it's recent
            return True
        
        try:
            # Try to parse various date formats
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %Z',  # RFC 2822 format
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822 with timezone
                '%Y-%m-%dT%H:%M:%S%z',       # ISO format
                '%Y-%m-%d %H:%M:%S',         # Simple format
                '%Y-%m-%d',                  # Date only
                '%d %b %Y',                  # Day Month Year
                '%b %d, %Y',                 # Month Day, Year
            ]
            
            article_date = None
            for fmt in date_formats:
                try:
                    article_date = datetime.strptime(published_str.strip(), fmt)
                    break
                except ValueError:
                    continue
            
            if article_date is None:
                # Try parsing partial dates (like "Thu, 06 No" from RSS feeds)
                import re
                date_match = re.search(r'(\w{3}),?\s*(\d{1,2})\s*(\w{2,3})', published_str)
                if date_match:
                    day_name, day_num, month_abbr = date_match.groups()
                    # Assume current year and try to match with target date range
                    current_year = target_date.year
                    
                    # Map month abbreviations
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
                        'ja': 1, 'fe': 2, 'mr': 3, 'ap': 4, 'my': 5, 'jn': 6,
                        'jl': 7, 'au': 8, 'se': 9, 'oc': 10, 'no': 11, 'de': 12
                    }
                    
                    month_num = month_map.get(month_abbr.lower()[:2])
                    if month_num:
                        try:
                            article_date = datetime(current_year, month_num, int(day_num))
                        except ValueError:
                            pass
            
            if article_date:
                # Remove timezone info for comparison
                if article_date.tzinfo:
                    article_date = article_date.replace(tzinfo=None)
                
                # Check if article date is within our range (target date or day before)
                target_date_only = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                day_before_only = day_before.replace(hour=0, minute=0, second=0, microsecond=0)
                article_date_only = article_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                return day_before_only <= article_date_only <= target_date_only
            
        except Exception as e:
            print(f"Error parsing date '{published_str}': {e}")
        
        # If we can't parse the date, assume it's recent
        return True

    def collect_articles(self, target_date: datetime = None) -> List[Dict]:
        """Collect articles from all sources, filtered by date"""
        if target_date is None:
            target_date = datetime.now()
            
        print("Collecting articles from various sources...")
        
        # Fetch from all configured sources
        source_articles = self.fetch_all_sources()
        
        # Filter articles by date before adding to collection
        recent_source_articles = []
        for article in source_articles:
            if self.is_article_recent(article, target_date):
                recent_source_articles.append(article)
        
        print(f"Filtered {len(source_articles)} source articles to {len(recent_source_articles)} recent articles")
        self.articles.extend(recent_source_articles)
        
        # Search Google News for each keyword (as backup/additional source)
        print("Searching Google News for additional coverage...")
        # Prioritize Fed-related searches
        priority_keywords = [
            'unemployment', 'inflation', 'market risk', 
            'federal reserve', 'jerome powell', 'fed policy'
        ]
        for keyword in priority_keywords:
            print(f"Searching for: {keyword}")
            articles = self.search_google_news(keyword, days_back=2)  # Search last 2 days
            
            # Filter Google News articles by date
            recent_google_articles = []
            for article in articles:
                if self.is_article_recent(article, target_date):
                    article['highlights'] = self.generate_highlights(article)
                    article['source_category'] = 'free'
                    recent_google_articles.append(article)
            
            self.articles.extend(recent_google_articles)
            time.sleep(1)  # Be respectful with requests
        
        # Remove duplicates based on title similarity
        self.articles = self.remove_duplicates(self.articles)
        
        print(f"Collected {len(self.articles)} unique recent articles")
        return self.articles
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = re.sub(r'[^\w\s]', '', article['title'].lower())[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
                
        return unique_articles
    
    def summarize_articles(self) -> Dict[str, Any]:
        """Create a summary of collected articles"""
        if not self.articles:
            return {"error": "No articles collected"}
        
        # Group articles by keyword/topic and apply structured analysis
        topics = {}
        processed_articles = []
        
        print(f"Applying structured analysis to {len(self.articles)} articles...")
        
        for i, article in enumerate(self.articles):
            # Apply structured analysis to each article
            try:
                enhanced_article = self.generate_structured_article_analysis(article)
                processed_articles.append(enhanced_article)
                
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(self.articles)} articles...")
                    
            except Exception as e:
                print(f"Error processing article {i+1}: {e}")
                processed_articles.append(article)  # Use original if processing fails
        
        # Now categorize the processed articles
        for article in processed_articles:
            title_lower = article['title'].lower()
            desc_lower = (article.get('description', '') or '').lower()
            content = f"{title_lower} {desc_lower}"
            
            # Fed-related keywords for comprehensive detection
            fed_keywords = [
                'federal reserve', 'fed', 'fomc', 'jerome powell', 'fed chair', 
                'fed governor', 'fed official', 'fed policy', 'fed meeting', 
                'fed minutes', 'fed speech', 'fed testimony', 'federal open market committee',
                'monetary policy', 'interest rate', 'rate cut', 'rate hike', 'rate decision',
                'powell says', 'fed says', 'central bank', 'fed fund', 'fed rate'
            ]
            
            # Categorize articles with Fed priority
            if any(keyword in content for keyword in fed_keywords):
                topic = 'Federal Reserve & Monetary Policy'
            elif any(word in content for word in ['unemployment', 'job', 'employment', 'jobless', 'labor']):
                topic = 'Unemployment & Employment'
            elif any(word in content for word in ['inflation', 'price', 'cpi', 'deflation', 'pce']):
                topic = 'Inflation'
            elif any(word in content for word in ['market risk', 'volatility', 'risk', 'market crash', 'correction']):
                topic = 'Market Risk'
            elif any(word in content for word in ['banking', 'bank', 'financial institution', 'credit']):
                topic = 'Banking & Finance'
            else:
                topic = 'General Economic News'
            
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(article)
        
        summary = {
            'collection_date': datetime.now().isoformat(),
            'total_articles': len(self.articles),
            'topics': topics,
            'sources_covered': list(set(article['source'] for article in self.articles))
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any]) -> str:
        """Generate a formatted report with highlights"""
        report = []
        report.append("# Economic and Financial News Summary")
        report.append(f"**Collection Date:** {summary['collection_date']}")
        report.append(f"**Total Articles:** {summary['total_articles']}")
        report.append(f"**Sources:** {', '.join(summary['sources_covered'])}")
        
        # Add source breakdown
        free_sources = [s for s in summary['sources_covered'] if any(article.get('source_category') == 'free' for article in self.articles if article['source'] == s)]
        subscription_sources = [s for s in summary['sources_covered'] if any(article.get('source_category') == 'subscription' for article in self.articles if article['source'] == s)]
        
        if free_sources:
            report.append(f"**Free Sources:** {', '.join(free_sources)}")
        if subscription_sources:
            report.append(f"**Subscription Sources:** {', '.join(subscription_sources)}")
        
        report.append("\n---\n")
        
        for topic, articles in summary['topics'].items():
            report.append(f"## {topic} ({len(articles)} articles)")
            report.append("")
            
            for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles per topic
                report.append(f"### {i}. {article['title']}")
                report.append(f"**Source:** {article['source']} ({article.get('source_category', 'unknown')})")
                report.append(f"**Published:** {article.get('published', 'N/A')}")
                report.append(f"**URL:** {article['url']}")
                
                # Add highlights
                if article.get('highlights'):
                    report.append("**Key Highlights:**")
                    for highlight in article['highlights']:
                        report.append(f"  • {highlight}")
                
                if article.get('description'):
                    # Clean up description
                    desc = re.sub(r'<[^>]+>', '', article['description'])[:200]
                    report.append(f"**Summary:** {desc}...")
                report.append("")
            
            if len(articles) > 5:
                report.append(f"*... and {len(articles) - 5} more articles in this category*")
            report.append("")
        
        return "\n".join(report)

    def list_sources(self) -> None:
        """List all configured sources"""
        print("\n=== FREE SOURCES ===")
        for i, source in enumerate(self.free_sources, 1):
            status = "[Active]" if source.active else "[Inactive]"
            print(f"{i}. {source.name} ({source.source_type}) - {status}")
            print(f"   URL: {source.url}")
            print(f"   Max Articles: {source.max_articles}")
        
        print("\n=== SUBSCRIPTION SOURCES ===")
        for i, source in enumerate(self.subscription_sources, 1):
            status = "[Active]" if source.active else "[Inactive]"
            api_status = "[API Key Set]" if source.api_key else "[No API Key]"
            print(f"{i}. {source.name} ({source.source_type}) - {status} - {api_status}")
            print(f"   URL: {source.url}")
            print(f"   Max Articles: {source.max_articles}")
    
    def activate_source(self, source_name: str) -> bool:
        """Activate a source by name"""
        for source in self.free_sources + self.subscription_sources:
            if source.name.lower() == source_name.lower():
                source.active = True
                print(f"Activated source: {source.name}")
                return True
        print(f"Source not found: {source_name}")
        return False
    
    def deactivate_source(self, source_name: str) -> bool:
        """Deactivate a source by name"""
        for source in self.free_sources + self.subscription_sources:
            if source.name.lower() == source_name.lower():
                source.active = False
                print(f"Deactivated source: {source.name}")
                return True
        print(f"Source not found: {source_name}")
        return False

def main():
    """Main function with enhanced functionality"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced News Aggregator')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--list-sources', action='store_true', help='List all sources')
    parser.add_argument('--activate', help='Activate a source by name')
    parser.add_argument('--deactivate', help='Deactivate a source by name')
    parser.add_argument('--save-config', help='Save current configuration to file')
    
    args = parser.parse_args()
    
    # Initialize aggregator
    aggregator = NewsAggregator(config_file=args.config)
    
    # Handle source management commands
    if args.list_sources:
        aggregator.list_sources()
        return
    
    if args.activate:
        aggregator.activate_source(args.activate)
        return
    
    if args.deactivate:
        aggregator.deactivate_source(args.deactivate)
        return
    
    if args.save_config:
        aggregator.save_sources_config(args.save_config)
        return
    
    # Run normal news collection
    print("Starting enhanced news collection...")
    print(f"Keywords: {', '.join(aggregator.keywords)}")
    
    articles = aggregator.collect_articles()
    
    if not articles:
        print("No articles were collected. This might be due to:")
        print("- Rate limiting or access restrictions")
        print("- Inactive sources (use --list-sources to check)")
        print("- Network connectivity issues")
        return
    
    print("Generating summary...")
    summary = aggregator.summarize_articles()
    
    print("Creating enhanced report...")
    report = aggregator.generate_report(summary)
    
    # Save report to file
    with open('economic_news_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save raw data as JSON
    with open('articles_data.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("[OK] Report saved to economic_news_report.md")
    print("[OK] Raw data saved to articles_data.json")
    print(f"[INFO] Collected {len(articles)} articles from {len(summary['sources_covered'])} sources")
    
    return report

def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "free_sources": [
            {
                "name": "Custom RSS Feed",
                "url": "https://example.com/rss",
                "source_type": "free_rss",
                "category": "free",
                "max_articles": 10,
                "active": False
            }
        ],
        "subscription_sources": [
            {
                "name": "Premium News API",
                "url": "https://api.example.com/news",
                "source_type": "api",
                "category": "subscription",
                "api_key": "your_api_key_here",
                "max_articles": 20,
                "active": False
            }
        ]
    }
    
    with open('news_sources_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration created: news_sources_config.json")

if __name__ == "__main__":
    main()
