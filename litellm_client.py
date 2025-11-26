#!/usr/bin/env python3
"""
Minimal LiteLLM Integration Client for Daily News Brief
"""

import os
import json
from typing import Dict, List, Optional

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

class LiteLLMClient:
    """Minimal LiteLLM client for news analysis"""
    
    def __init__(self, config_file: str = "llm_config_example.json"):
        if not LITELLM_AVAILABLE:
            raise ImportError("litellm package not installed. Run: pip install litellm")
        
        self.config = self._load_config(config_file)
        llm_settings = self.config.get('llm_settings', {})
        
        self.model = llm_settings.get('models', {}).get('litellm', 'claude-3-5-sonnet-20241022')
        self.api_key = llm_settings.get('api_key') or os.getenv('LITELLM_API_KEY') or os.getenv('ANTHROPIC_API_KEY')
        self.max_tokens = llm_settings.get('max_tokens', 1000)
        self.temperature = llm_settings.get('temperature', 0.3)
        
        if not self.api_key:
            raise ValueError("API key required in config file or environment variable")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'llm_settings': {}}
    
    def _call_llm(self, messages: List[Dict], max_tokens: Optional[int] = None) -> str:
        """Make LLM API call"""
        try:
            # Use provider URL as base_url if it's a URL
            llm_settings = self.config.get('llm_settings', {})
            provider = llm_settings.get('provider', '')
            
            if provider.startswith('http'):
                response = litellm.completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=self.temperature,
                    api_key=self.api_key,
                    base_url=provider
                )
            else:
                response = litellm.completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=self.temperature,
                    api_key=self.api_key
                )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LiteLLM API call failed: {e}")
    
    def generate_summary(self, article_text: str, max_length: int = 150) -> str:
        """Generate article summary"""
        messages = [
            {"role": "user", "content": f"Summarize this news article in {max_length} words or less:\n\n{article_text}"}
        ]
        return self._call_llm(messages, max_tokens=200)
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze market sentiment"""
        messages = [
            {"role": "user", "content": f"Analyze the economic/market sentiment of this text. Return only: bullish, bearish, or neutral:\n\n{text}"}
        ]
        sentiment = self._call_llm(messages, max_tokens=50).lower()
        
        # Normalize response
        if "bullish" in sentiment:
            return {"sentiment": "bullish", "confidence": 0.8}
        elif "bearish" in sentiment:
            return {"sentiment": "bearish", "confidence": 0.8}
        else:
            return {"sentiment": "neutral", "confidence": 0.7}
    
    def generate_structured_analysis(self, article: Dict) -> Dict:
        """Generate structured analysis for SF Fed digest"""
        prompt = f"""
Analyze this news article for a Federal Reserve executive briefing. Return JSON format:

Article: {article.get('title', '')}
Content: {article.get('description', '')}

Provide:
1. topic_headline: Enhanced title focusing on Fed relevance
2. summary_highlights: 4 bullet points (50-75 words each) covering key developments, quotes, implications, market reactions
3. notable_quotes: Important quotes from officials/experts
4. context_implications: Broader economic/policy impact (100 words)
5. market_sentiment: bullish/bearish/neutral

Format as valid JSON.
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self._call_llm(messages, max_tokens=1500)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback structure
            return {
                "topic_headline": article.get('title', 'Economic Development'),
                "summary_highlights": [
                    f"Key development: {article.get('description', '')[:100]}...",
                    "Market implications under analysis",
                    "Policy considerations being evaluated", 
                    "Economic indicators showing mixed signals"
                ],
                "notable_quotes": [],
                "context_implications": "Monitoring for potential economic impact and policy implications.",
                "market_sentiment": "neutral"
            }
    
    def extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights as bullet points"""
        messages = [
            {"role": "user", "content": f"Extract 4-5 key insights from this economic news as bullet points:\n\n{content}"}
        ]
        response = self._call_llm(messages, max_tokens=800)
        
        # Parse bullet points
        lines = response.split('\n')
        insights = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                insights.append(line.lstrip('•-* '))
        
        return insights[:5] if insights else [content[:200] + "..."]

# Usage example
if __name__ == "__main__":
    client = LiteLLMClient("llm_config_example.json")
    
    test_article = {
        'title': 'Fed Raises Rates 0.25% Amid Inflation Concerns',
        'description': 'The Federal Reserve raised interest rates by 0.25% today, with Chair Powell citing persistent inflation. Markets gained 1.2% on the news.'
    }
    
    # Test functionality
    summary = client.generate_summary(test_article['description'])
    sentiment = client.analyze_sentiment(test_article['description'])
    analysis = client.generate_structured_analysis(test_article)
    
    print(f"Model: {client.model}")
    print(f"Summary: {summary}")
    print(f"Sentiment: {sentiment}")
    print(f"Analysis: {json.dumps(analysis, indent=2)}")