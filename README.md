
# Daily News Brief - Economic & Financial News Aggregator

A powerful and easy-to-use automated tool for collecting, analyzing, and curating economic and financial news from major sources including Bloomberg, Reuters, Fox News, NBC, AP News, WSJ, and LinkedIn.

## 🚀 Features

- **Flexible Source Management**: Configurable free and subscription-based news sources
- **Automated News Collection**: Aggregates articles from multiple RSS feeds, APIs, and Google News
- **Smart Categorization**: Automatically categorizes articles by topic (Unemployment, Inflation, Market Risk, Banking)
- **Article Highlights**: Generates 4-5 key bullet points for each article automatically
- **Multiple Output Formats**: Generates HTML reports, Markdown summaries, and JSON data
- **Web Dashboard**: Interactive HTML dashboard for viewing curated news
- **Executive Summary**: Comprehensive analysis with key insights and recommendations
- **Dynamic Source Control**: Add, remove, activate/deactivate sources on the fly
- **Configuration Management**: Save and load source configurations from JSON files

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
Make sure you have Python 3.6+ installed, then install the required packages:
```bash
pip install requests lxml beautifulsoup4 flask
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/atakkallapalli/daily_news_brief.git
cd daily_news_brief

# Run the news aggregator
python3 news_aggregator.py

# Generate HTML report
python3 generate_html_report.py

# Start web dashboard (optional)
python3 dashboard.py
```

## 📁 Project Structure

```
daily_news_brief/
├── news_aggregator.py          # Main news collection script
├── dashboard.py                # Web dashboard application
├── generate_html_report.py     # HTML report generator
├── economic_news_report.html   # Generated HTML report
├── economic_news_report.md     # Markdown report
├── executive_summary.md        # Executive summary with insights
├── curated_articles_list.md    # Prioritized article list
├── articles_data.json          # Raw collected data
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
Each article automatically gets 4-5 key highlights:
- 🎙️ **Fed Officials**: Quotes and statements from Jerome Powell and Fed personnel
- 📋 **FOMC Decisions**: Meeting outcomes, rate decisions, and policy changes
- 💼 **Monetary Policy**: Strategy implementation and economic outlook
- 📈 **Employment Trends**: Unemployment metrics and job market indicators
- 💰 **Inflation Signals**: Price pressures and monetary policy impacts  
- 🏦 **Banking Sector**: Financial institution news and regulatory changes
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

