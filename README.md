
# Daily News Brief - Economic & Financial News Aggregator

An automated tool for collecting, analyzing, and curating economic and financial news from major sources including Bloomberg, Reuters, Fox News, NBC, AP News, WSJ, and LinkedIn.

## 🚀 Features

- **Automated News Collection**: Aggregates articles from multiple RSS feeds and Google News
- **Smart Categorization**: Automatically categorizes articles by topic (Unemployment, Inflation, Market Risk, Banking)
- **Multiple Output Formats**: Generates HTML reports, Markdown summaries, and JSON data
- **Web Dashboard**: Interactive HTML dashboard for viewing curated news
- **Executive Summary**: Comprehensive analysis with key insights and recommendations

## 📊 Latest Report Summary

**Collection Period**: October 17-24, 2025 (Past 7 Days)  
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

### 1. Collect News Articles
```bash
python3 news_aggregator.py
```
This script:
- Searches Google News for economic keywords
- Fetches from RSS feeds (Reuters, AP, NBC Business)
- Removes duplicates and categorizes articles
- Saves data to `articles_data.json`

### 2. Generate Reports
```bash
python3 generate_html_report.py
```
Creates:
- Interactive HTML dashboard (`economic_news_report.html`)
- Formatted with responsive design and categorized sections

### 3. Start Web Dashboard
```bash
python3 dashboard.py
```
- Launches Flask web server on port 51487
- Provides interactive web interface
- API endpoints for data access

## 📈 Data Sources

### Primary Sources
- **Google News RSS**: Aggregated news from multiple outlets
- **Reuters Business**: Direct RSS feed
- **NBC Business**: Direct RSS feed  
- **AP Business**: RSS feed (when available)

### Covered Outlets
- Bloomberg (via Google News)
- Reuters (direct + Google News)
- Fox News (via Google News)
- NBC News (direct + Google News)
- AP News (RSS + Google News)
- Wall Street Journal (via Google News)
- LinkedIn (via Google News)

## 🎯 Key Features

### Automated Categorization
Articles are automatically sorted into:
- **Unemployment & Employment**: Job market trends, claims data
- **Inflation**: CPI reports, price pressures, policy impacts
- **Market Risk**: Volatility, concentration risks, investment strategies
- **Banking & Finance**: Regulatory changes, stress tests, digital currencies
- **General Economic News**: Broader economic indicators and analysis

### Multiple Output Formats
1. **JSON Data** (`articles_data.json`): Raw structured data
2. **HTML Report** (`economic_news_report.html`): Interactive web report
3. **Markdown Report** (`economic_news_report.md`): Text-based summary
4. **Executive Summary** (`executive_summary.md`): Strategic analysis
5. **Curated List** (`curated_articles_list.md`): Prioritized articles

### Smart Filtering
- Removes duplicate articles based on title similarity
- Filters by economic keywords and relevance
- Prioritizes articles by source reliability and impact

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

## 🚀 Future Enhancements

- [ ] Real-time news streaming
- [ ] Sentiment analysis integration
- [ ] Email/SMS alert system
- [ ] Historical trend analysis
- [ ] Machine learning categorization
- [ ] Social media integration (Twitter/X)
- [ ] Mobile app development

## 📝 Sample Output

### Executive Summary Extract
```
## Key Findings & Trends

### 🔴 UNEMPLOYMENT & EMPLOYMENT (11 Articles)
- US Weekly Jobless Claims Increase (Reuters)
- Australia's Unemployment Spike (The Guardian)
- China's Graduate Unemployment Crisis (NBC News)

### 📈 INFLATION (15 Articles)  
- CPI Report Shows September Inflation Rise (NYT)
- Social Security COLA Set at 2.8% (USA Today)
- Government Shutdown Risk (Fox News)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool aggregates publicly available news for analysis purposes. The information should be supplemented with official economic data and professional financial analysis for investment decisions. News sources retain all rights to their content.

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review the generated reports for data quality
- Check RSS feed availability for source connectivity

---

**Last Updated**: October 24, 2025  
**Version**: 1.0.0  
**Maintainer**: Economic Analysis Team

