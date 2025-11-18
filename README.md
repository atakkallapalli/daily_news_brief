
# Daily News Brief - Economic & Financial News Aggregator

A powerful and easy-to-use automated tool for collecting, analyzing, and curating economic and financial news from major sources including Bloomberg, Reuters, Fox News, NBC, AP News, WSJ, and LinkedIn.

## 🚀 Features

### Core Features
- **Flexible Source Management**: Configurable free and subscription-based news sources
- **Automated News Collection**: Aggregates articles from multiple RSS feeds, APIs, and Google News
- **Smart Categorization**: Automatically categorizes articles by topic (Unemployment, Inflation, Market Risk, Banking)
- **Article Highlights**: Generates 4-5 key bullet points for each article automatically
- **Multiple Output Formats**: Generates HTML reports, Markdown summaries, and JSON data
- **Web Dashboard**: Interactive HTML dashboard for viewing curated news
- **Executive Summary**: Comprehensive analysis with key insights and recommendations
- **Dynamic Source Control**: Add, remove, activate/deactivate sources on the fly
- **Configuration Management**: Save and load source configurations from JSON files

### 🤖 LLM-Powered Analysis (NEW!)
- **AI-Enhanced Summaries**: Generate intelligent TL;DR summaries using multiple LLM providers
- **Smart Insights Extraction**: Automatically identify key economic insights and quotes from articles
- **Sentiment Analysis**: Analyze economic sentiment and market tone (bullish/bearish/neutral)
- **Enhanced Highlights**: LLM-generated bullet points with deeper content understanding
- **Multi-Provider Support**: Works with OpenAI GPT, Anthropic Claude, LiteLLM proxy, or local Transformers models
- **LiteLLM Integration**: Support for Claude Sonnet 4 and other models via LiteLLM proxy
- **Structured Analysis**: Comprehensive analysis with topic extraction, 4-5 detailed bullet points (~100 words each), notable quotes, and market sentiment
- **Fallback Protection**: Gracefully falls back to rule-based analysis if LLM is unavailable

## 📊 Latest Report Summary

**Collection Period**: October 17-24, 2024 (Past 7 Days)  
**Total Articles**: 70  
**Categories**: 5 topic areas  
**Sources**: Major news outlets and RSS feeds

### Key Findings
- **Unemployment**: Rising US jobless claims, international labor market concerns
- **Inflation**: September CPI increase, Social Security COLA adjustments
- **Market Risk**: High concentration warnings, alternative investment trends  
- **Banking**: Fed stress test changes, digital currency adoption
- **Policy**: Government shutdown risks, regulatory modifications

## 🛠 Installation & Setup

### Prerequisites
Make sure you have Python 3.8+ installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### Basic Installation
```bash
# Clone the repository
git clone https://github.com/atakkallapalli/daily_news_brief.git
cd daily_news_brief

# Install core dependencies
pip install requests lxml beautifulsoup4 flask schedule

# Run the news aggregator (one-time)
python3 news_aggregator.py
```

### 🤖 LLM Integration Setup (Optional)

For enhanced AI-powered analysis, install LLM dependencies:

```bash
# Install LLM packages (choose one or more)
pip install openai>=1.0.0          # For OpenAI GPT models
pip install anthropic>=0.7.0       # For Anthropic Claude models
pip install litellm>=1.0.0         # For LiteLLM proxy (supports Claude Sonnet 4)
pip install transformers torch     # For local models
```

#### API Key Configuration

Set your API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# For LiteLLM proxy (supports Claude Sonnet 4)
export LITELLM_API_KEY="your-litellm-api-key"

# Or set in your shell profile for persistence
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
echo 'export LITELLM_API_KEY="your-litellm-key"' >> ~/.bashrc
```

#### LLM Configuration Options

Create or modify `scheduler_config.json` to configure LLM settings:

```json
{
  "llm_settings": {
    "provider": "auto",           // auto, openai, anthropic, litellm, local
    "model": "claude-3-5-sonnet-20241022",  // for litellm provider
    "api_key": null,             // or set directly (not recommended)
    "enabled": true,
    "fallback_to_rule_based": true,
    "features": {
      "sentiment_analysis": true,
      "key_insights": true,
      "enhanced_summaries": true,
      "economic_tone_analysis": true,
      "structured_analysis": true
    }
  }
}
```

#### Test LLM Integration

```bash
# Test basic LLM functionality
python3 test_llm_integration.py

# Test structured analysis with comprehensive prompt
python3 test_structured_analysis.py

# Test LiteLLM integration with Claude Sonnet 4
python3 test_litellm_integration.py
```

#### LiteLLM Usage Examples

```python
# Initialize with LiteLLM and Claude Sonnet 4
from news_aggregator import LLMService

llm = LLMService(
    provider="litellm",
    model="claude-3-5-sonnet-20241022",
    api_key="your-litellm-api-key"
)

# Generate structured analysis with your specific format
analysis = llm.generate_structured_analysis(article)
# Returns: topic_headline, 4-5 bullet points (~100 words each), notable_quotes, context_implications

# Generate summary with enhanced insights
summary = llm.extract_key_insights(article_content)
# Returns: 4-5 detailed bullet points with quotes and market implications
```

#### Structured Analysis Format

The LLM integration now uses a comprehensive prompt format that generates:

**For each major news article:**
- **Topic/Headline**: Enhanced title extraction and focus identification
- **Summary Highlights (4 Bullet Points)**:
  - Key developments, data, and notable changes
  - Important quotes from influential figures (officials, CEOs, economists)
  - Economic or political implications
  - Market reactions and predictions
- **Notable Quotes**: Relevant quotes from major stakeholders
- **Context & Implications**: Broader economic and market impact analysis
- **Market Sentiment**: AI-powered sentiment analysis with confidence scores

**Topic Categories Covered:**
- Generative AI (GenAI): Innovations, launches, regulatory updates, industry trends
- Tariffs & International Trade: Trade negotiations, supply chain impacts
- Presidential Administration: Executive actions, policy moves, economic impact
- Federal Reserve & Monetary Policy: Interest rates, economic outlook, inflation policy
- Economic Policies & Stimulus: Fiscal policy, government spending, recovery impact
- Unemployment & Labor Market: Employment data, job trends, wage analysis
- Housing Market: Price trends, affordability, mortgage rates, market conditions
- Financial Markets: Market movements, earnings reports, investment outlooks
- Inflation: CPI data, sector-specific prices, central bank responses

# Generate daily digest (recommended)
python3 daily_scheduler.py --run-once

# Start automated daily scheduling
python3 daily_scheduler.py --schedule

# Generate HTML report (optional)
python3 generate_html_report.py

# Start web dashboard (optional)
python3 dashboard.py
```

## 📁 Project Structure

```
daily_news_brief/
├── news_aggregator.py          # Main news collection script
├── daily_scheduler.py          # Daily digest scheduler
├── scheduler_config.json       # Scheduler configuration
├── dashboard.py                # Web dashboard application
├── generate_html_report.py     # HTML report generator
├── daily-news-digest.service   # Systemd service file
├── crontab_example.txt         # Cron job examples
├── daily_digests/              # Generated daily digests
│   ├── daily_digest_YYYY-MM-DD_HH-MM.md
│   └── latest_digest.markdown
├── economic_news_report.html   # Generated HTML report
├── economic_news_report.md     # Markdown report
├── executive_summary.md        # Executive summary with insights
├── curated_articles_list.md    # Prioritized article list
├── articles_data.json          # Raw collected data
├── daily_digest.log            # Scheduler log file
└── README.md                   # This file
```

## 🔧 Usage

### 1. Basic News Collection
```bash
python3 news_aggregator.py
```
This enhanced script:
- Fetches from all active free and subscription sources
- Searches Google News for additional coverage
- Generates 4-5 key highlights for each article
- Removes duplicates and categorizes articles
- Saves data to [`articles_data.json`](articles_data.json)

### 2. Source Management
```bash
# List all configured sources
python3 news_aggregator.py --list-sources

# Activate/deactivate sources
python3 news_aggregator.py --activate "Reuters Business"
python3 news_aggregator.py --deactivate "BBC Business"

# Use custom configuration
python3 news_aggregator.py --config news_sources_config.json

# Save current configuration
python3 news_aggregator.py --save-config my_config.json
```

### 3. Generate Reports
```bash
python3 generate_html_report.py
```
Creates:
- Interactive HTML dashboard ([`economic_news_report.html`](economic_news_report.html))
- Formatted with responsive design and categorized sections

### 4. Start Web Dashboard
```bash
python3 dashboard.py
```
- Launches Flask web server on port 5000 (configurable)
- Provides interactive web interface
- API endpoints for data access

### 5. Adding Custom Sources
```python
from news_aggregator import NewsAggregator, NewsSource

# Initialize aggregator
aggregator = NewsAggregator()

# Add a free RSS source
new_source = NewsSource(
    name="Custom Financial News",
    url="https://example.com/rss",
    source_type="free_rss",
    category="free",
    max_articles=15,
    active=True
)
aggregator.add_free_source(new_source)

# Add a subscription API source
api_source = NewsSource(
    name="Premium News API",
    url="https://api.example.com/news",
    source_type="api",
    category="subscription",
    api_key="your_api_key",
    max_articles=25,
    active=True
)
aggregator.add_subscription_source(api_source)
```

## 📈 Data Sources

### Federal Reserve Sources
- **Federal Reserve News**: Official Fed press releases and announcements
- **Fed Economic Data (FRED)**: St. Louis Fed economic data releases
- **FOMC Meeting Coverage**: Via major news outlets and Google News

### Primary Financial News Sources
- **Google News RSS**: Aggregated news from multiple outlets
- **Reuters Business**: Direct RSS feed
- **NBC Business**: Direct RSS feed  
- **BBC Business**: Direct RSS feed
- **CNN Business**: Direct RSS feed
- **MarketWatch**: Direct RSS feed

### Additional Covered Outlets
- Bloomberg (via Google News)
- Wall Street Journal (via Google News)
- AP News (RSS + Google News)
- Financial Times (subscription)
- CNBC (via configuration)
- Forbes Business (via configuration)

## 🎯 Key Features

### Flexible Source Management
- **Free Sources**: Reuters, BBC, NBC, CNN, MarketWatch, and more
- **Subscription Sources**: Bloomberg Terminal, Financial Times, WSJ (with API keys)
- **Dynamic Control**: Activate/deactivate sources without code changes
- **Custom Sources**: Easily add new RSS feeds, APIs, or web scraping sources
- **Configuration Files**: Save and load source configurations as JSON

### Article Highlights Generation
Each article automatically gets exactly 4 key highlights:
- 🎙️ **Fed Officials**: Quotes and statements from Jerome Powell and Fed personnel
- 📋 **FOMC Decisions**: Meeting outcomes, rate decisions, and policy changes
- 💼 **Monetary Policy**: Strategy implementation and economic outlook
- 📈 **Employment Trends**: Unemployment metrics and job market indicators
- 💰 **Inflation Signals**: Price pressures and monetary policy impacts  
- 🏦 **Banking Sector**: Financial institution news and regulatory changes

## 📅 Daily Digest & Scheduling

### Automated Daily Digests
The system generates comprehensive daily digests with:
- **Executive Summary**: Article counts by category and top sources
- **Categorized Articles**: Fed-priority organization with exactly 4 highlights each
- **Multiple Formats**: Markdown, HTML, and JSON outputs
- **Archive Management**: Automatic cleanup of old digests (30-day retention)

### Scheduling Options

#### 1. One-Time Generation
```bash
# Generate digest immediately
python3 daily_scheduler.py --run-once

# Custom schedule times
python3 daily_scheduler.py --run-once --times "08:00" "14:00" "20:00"
```

#### 2. Continuous Scheduler
```bash
# Start continuous scheduler (default: 7:00, 12:00, 18:00)
python3 daily_scheduler.py --schedule

# View current configuration
python3 daily_scheduler.py
```

#### 3. Cron Jobs (Linux/Mac)
```bash
# Add to crontab (crontab -e)
0 7 * * * cd /path/to/daily_news_brief && python3 daily_scheduler.py --run-once
0 12 * * * cd /path/to/daily_news_brief && python3 daily_scheduler.py --run-once  
0 18 * * * cd /path/to/daily_news_brief && python3 daily_scheduler.py --run-once
```

#### 4. System Service (Linux)
```bash
# Copy service file
sudo cp daily-news-digest.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable daily-news-digest
sudo systemctl start daily-news-digest
```

### Configuration
Edit `scheduler_config.json` to customize:
```json
{
  "schedule_times": ["07:00", "12:00", "18:00"],
  "output_directory": "daily_digests",
  "archive_days": 30,
  "digest_settings": {
    "max_articles_per_category": 10,
    "include_highlights": true,
    "generate_summary": true,
    "format": "markdown"
  }
}
```

### Output Files
- `daily_digests/daily_digest_YYYY-MM-DD_HH-MM.md` - Timestamped digest
- `daily_digests/latest_digest.markdown` - Always points to latest
- `daily_digest.log` - Scheduler activity log
- 📊 **Economic Indicators**: GDP, market conditions, and forecasts

### Automated Categorization
Articles are automatically sorted into:
- **Federal Reserve & Monetary Policy**: Fed speeches, FOMC meetings, policy decisions, official statements
- **Unemployment & Employment**: Job market trends, claims data, labor statistics
- **Inflation**: CPI reports, price pressures, policy impacts, PCE data
- **Market Risk**: Volatility, concentration risks, investment strategies
- **Banking & Finance**: Regulatory changes, stress tests, digital currencies
- **General Economic News**: Broader economic indicators and analysis

### Multiple Output Formats
1. **JSON Data** ([`articles_data.json`](articles_data.json)): Raw structured data with highlights
2. **HTML Report** ([`economic_news_report.html`](economic_news_report.html)): Interactive web report
3. **Markdown Report** ([`economic_news_report.md`](economic_news_report.md)): Text-based summary with highlights
4. **Executive Summary** ([`executive_summary.md`](executive_summary.md)): Strategic analysis
5. **Curated List** ([`curated_articles_list.md`](curated_articles_list.md)): Prioritized articles

### Smart Filtering
- Removes duplicate articles based on title similarity
- Filters by economic keywords and relevance
- Prioritizes articles by source reliability and impact
- Rate limiting and respectful API usage

## 🔍 API Endpoints

When running the dashboard (`python3 dashboard.py`):

- `GET /` - Main dashboard interface
- `GET /api/data` - Raw JSON data
- `GET /api/summary` - Summary statistics

## 📊 Analysis Capabilities

### Trend Identification
- Labor market indicators
- Inflation pressures and policy responses
- Market concentration risks
- Banking sector developments
- International economic impacts

### Risk Assessment
- **High Impact**: Fed policy changes, major economic indicators
- **Medium Impact**: Regional trends, sector-specific developments  
- **Low Impact**: Local news with systemic implications

### Source Reliability Scoring
- **Tier 1**: Reuters, NYT, WSJ, BBC, NBC (Highest reliability)
- **Tier 2**: USA Today, Washington Post, Fox News, Guardian
- **Tier 3**: Specialized/Regional outlets

## ⚙️ Configuration File Format

The news aggregator uses JSON configuration files to manage sources. Here's the structure:

```json
{
  "free_sources": [
    {
      "name": "Source Name",
      "url": "https://example.com/rss",
      "source_type": "free_rss",
      "category": "free",
      "max_articles": 10,
      "rate_limit": 1.0,
      "active": true
    }
  ],
  "subscription_sources": [
    {
      "name": "Premium Source",
      "url": "https://api.example.com/news",
      "source_type": "api",
      "category": "subscription",
      "api_key": "your_api_key_here",
      "headers": {
        "Authorization": "Bearer TOKEN"
      },
      "max_articles": 20,
      "rate_limit": 0.5,
      "active": false
    }
  ]
}
```

### Source Types
- **`free_rss`**: Public RSS feeds (no authentication required)
- **`subscription_rss`**: Premium RSS feeds (may require API keys/headers)
- **`api`**: REST API endpoints (requires API key)
- **`web_scraping`**: Web scraping sources (placeholder for future implementation)

## 🚀 Future Enhancements

- [ ] Real-time news streaming
- [ ] Sentiment analysis integration
- [ ] Email/SMS alert system
- [ ] Historical trend analysis
- [ ] Machine learning categorization
- [ ] Social media integration (Twitter/X)
- [ ] Mobile app development
- [ ] Advanced web scraping capabilities
- [ ] Custom highlight templates
- [ ] Multi-language support

## 📝 Sample Output

### Executive Summary Extract with Highlights
```markdown
## Key Findings & Trends

### 🏛️ FEDERAL RESERVE & MONETARY POLICY (45 Articles)

#### 1. Federal Reserve Board issues enforcement actions with Belt Valley Bank
**Source:** Federal Reserve News (free)
**Key Highlights:**
  • 🎙️ Federal Reserve official statements and quotes
  • 🏦 Banking sector and financial institution news
  • 🏛️ Federal Reserve interest rate policy developments
  • 📰 Economic and financial news update

#### 2. Bank says inflation has 'peaked' as it holds interest rates
**Source:** BBC Business (free)
**Key Highlights:**
  • 📋 FOMC meeting outcomes and policy decisions
  • 💰 Inflationary pressures intensifying
  • 🏛️ Federal Reserve interest rate policy developments
  • 📊 Economic indicators and trends

### 📈 INFLATION (7 Articles)  

#### 1. Why is UK inflation still high?
**Source:** BBC Business (free)
**Key Highlights:**
  • 💲 Price pressures showing signs of easing
  • 🏦 Banking sector and financial institution news
  • 📊 Inflation data and price trends updated
  • 📰 Economic and financial news update
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/enhancement
   ```
3. Commit your changes:
   ```bash
   git commit -am 'Add new feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/enhancement
   ```
5. Create a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool aggregates publicly available news for analysis purposes. The information should be supplemented with official economic data and professional financial analysis for investment decisions. News sources retain all rights to their content.

## 📞 Support

Need help or have questions? We're here to assist:
- **Issues & Bug Reports**: [Open an issue on GitHub](../../issues)
- **Data Quality**: Review the generated reports and let us know if you notice any inconsistencies
- **Connectivity Problems**: Check RSS feed availability if you're experiencing source connectivity issues
- **Feature Requests**: We welcome suggestions for new features and improvements!

---

**Last Updated**: October 24, 2024  
**Version**: 1.0.0  
**Maintainer**: Economic Analysis Team

**prompt**
Generate today’s **San Francisco Federal Reserve Executive Daily News Digest**.

Audience: SF Fed Executive Leadership Team.
Purpose: Provide a high-signal, low-noise briefing to inform monetary policy, supervision, financial stability, 
technology readiness, payments evolution, and regional economic conditions.

Include the following sections in order:

1. **Top 5 Headlines Relevant to the Federal Reserve**
   - Short summaries (2–3 lines each)
   - Must relate to macroeconomics, financial markets, banking, technology, cyber, or policy.

2. **12th District Regional Economic & Labor Signals**
   - California, Washington, Oregon, Arizona, Utah, Alaska, Hawaii, Idaho, Nevada.
   - Housing, labor, consumer spending, tech sector conditions, logistics/supply chain.

3. **National Macroeconomic & Monetary Policy Developments**
   - Inflation, labor markets, GDP, productivity.
   - Key indicators that matter for FOMC outlook.
   - Market-implied rate expectations & yield curve movements.

4. **Financial System & Banking Stability Watch**
   - Bank liquidity/capital trends, CRE exposures, funding markets, credit spreads.
   - Notable supervisory signals or emerging vulnerabilities.

5. **Global & Pacific Rim Insights (SF Fed priority)**
   - China, Japan, Korea, ASEAN.
   - International central bank actions, global demand shifts, supply chain/geopolitical risks.

6. **Technology, Cyber, and Payments Developments**
   - Major cyber threats, cloud/AI risks, fintech, payments modernization, digital assets.
   - Implications for FedNow, payment resilience, or financial system risk.

7. **Regulatory, Legislative, and Federal Government Updates**
   - Congress, Treasury, CFPB, FDIC, OCC.
   - Only items with real supervisory or policy implications.

8. **Implications for SF Fed**
   - 5–7 bullets.
   - Clearly translate news into potential impacts on:
       • Monetary policy
       • Bank supervision
       • Regional economic monitoring
       • Payments & technology operations
       • Financial stability

9. **Executive Summary (<150 words)**
   - A concise, board-ready overview of the most important signals.

Constraints:
- Tone: analytical, factual, policy-relevant. No sensationalism.
- Exclude consumer lifestyle news, political commentary, and unrelated media stories.
- Prioritize accuracy, brevity, and decision-readiness.


