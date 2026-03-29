# 🚀 Flash-search

A fast, multi-source web search library with intelligent fallback and content extraction capabilities.

[![PyPI](https://img.shields.io/badge/PyPI-flash--search-blue)](https://pypi.org/project/flash-search)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Core Features
✨ **Fast Web Search** - Search across multiple sources with intelligent fallback (Google + DuckDuckGo)  
🔄 **Auto Fallback** - Automatically uses DuckDuckGo if Google is blocked  
📄 **Content Extraction** - Extract clean, readable text from websites without HTML  
💾 **Save Results** - Export search results and website content to .txt files  
🌍 **Multi-language** - Support for 30+ languages and regions  
🔧 **Advanced Filtering** - Unique results, safe search, pagination support  
⚡ **Fast Performance** - Optimized with curl-cffi for speed and reliability

### Advanced Features
🎯 **Query Intent Detection** - Automatically detect search intent (Informational, Navigational, Transactional, Local) for better result ranking  
🏆 **Smart Ranking Algorithm** - Advanced ranking engine that scores results based on keyword matching, URL quality, and domain authority  
✅ **Content Quality Assessment** - Evaluate content quality based on title optimization, description comprehensiveness, and URL structure  
🌈 **Result Diversification** - Smart result diversification to provide varied and comprehensive search results

## Installation

```bash
pip install flash-search
```

## Quick Start

### Basic Search
```python
from flash_search import search

# Get search result URLs
for url in search("Python programming", num_results=5):
    print(url)
```

### Advanced Search
```python
from flash_search import search

# Get detailed results with title and description
for result in search("Machine Learning", num_results=5, advanced=True):
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Description: {result.description}\n")
```

### Extract Website Content
```python
from flash_search import extract_website_content

# Get clean text from a website
content = extract_website_content("https://example.com")
print(content)
```

### Save Results to File
```python
from flash_search import search, save_results_to_file

# Search and save results
results = list(search("Python", num_results=10, advanced=True))
save_results_to_file(results, "results.txt")
```

### Save Website Content
```python
from flash_search import save_website_content

# Extract and save website content
save_website_content("https://python.org", "python_org.txt")
```

## API Reference

### `search(term, **kwargs)`
Search the web for a query.

**Parameters:**
- `term` (str): Search query
- `num_results` (int): Number of results to return (default: 10)
- `lang` (str): Language code (default: "en")
- `advanced` (bool): Return SearchResult objects instead of URLs (default: False)
- `timeout` (int): Request timeout in seconds (default: 5)
- `unique` (bool): Return only unique results (default: False)
- `proxy` (str): Proxy URL if needed
- `safe` (str): Safe search ("active" or None)
- `region` (str): Country code for region-specific results

**Returns:** Generator yielding URLs or SearchResult objects

### `extract_website_content(url)`
Extract clean text from a website.

**Parameters:**
- `url` (str): Website URL

**Returns:** Clean text content

### `save_results_to_file(results, filename)`
Save search results to a file.

**Parameters:**
- `results` (list): Search results to save
- `filename` (str): Output filename

### `save_website_content(url, filename=None)`
Extract and save website content.

**Parameters:**
- `url` (str): Website URL
- `filename` (str): Output filename (auto-generated if None)

## Advanced Features Documentation

### Query Intent Detection
Automatically detect the intent behind a search query to improve result ranking.

```python
from Query_Intent_Detection import detect_intent, SearchIntent

# Detect search intent
intent = detect_intent("How to learn Python")
print(intent)  # SearchIntent.INFORMATIONAL

# Supported intents:
# - INFORMATIONAL: "How to...", "What is...", "Explain"
# - NAVIGATIONAL: Brand or site-specific searches
# - TRANSACTIONAL: "Buy...", "Price...", "Download"
# - LOCAL: "Near me", location-based searches
```

### Smart Ranking Algorithm
Score and rank search results based on relevance factors.

```python
from Ranking_Algorithm import SearchRanker

ranker = SearchRanker()

# Score a single result
score = ranker.score_result("Python tutorial", search_result)
print(f"Relevance Score: {score}")

# Ranking considers:
# - Keyword matching in title (100 points)
# - Keyword matching in description (50 points)
# - URL quality check (30 points)
# - Domain authority (up to 20 points)
```

### Content Quality Assessment
Evaluate the quality of search results based on various metrics.

```python
from Content_Quality_Assessment import assess_content_quality

# Assess quality of a result
quality_score = assess_content_quality(
    title="Complete Python Programming Guide",
    description="A comprehensive guide covering Python basics...",
    url="https://example.com/python-guide"
)
print(f"Quality Score: {quality_score}")  # 0-100

# Factors considered:
# - Title length optimization (20 points)
# - Description comprehensiveness (20 points)
# - Content validity check (20 points)
# - URL readability (20 points)
# - Content freshness (20 points)
```

### Result Diversification
Get diverse search results covering multiple aspects of your query.

```python
from Result_Diversification import diversify_results

# Diversify results to cover different aspects
diverse_results = diversify_results(results, max_per_domain=2)
print(f"Original results: {len(results)}")
print(f"Diversified results: {len(diverse_results)}")
```

## How It Works

Flash-search uses a comprehensive multi-layered approach:

1. **Primary Source**: Uses `curl-cffi` to impersonate a real browser and fetch Google results
2. **Fallback Source**: Automatically switches to DuckDuckGo if Google blocks the request
3. **Intent Detection**: Analyzes the search query to understand user intent and optimize ranking
4. **Smart Ranking**: Scores results based on keyword relevance, URL quality, and domain authority
5. **Quality Assessment**: Evaluates content quality using multiple factors
6. **Result Diversification**: Ensures varied results from different sources and domains

This multi-layered approach ensures reliable, relevant, and diverse search results.

## Requirements

- Python 3.6+
- beautifulsoup4 >= 4.9
- requests >= 2.20
- curl-cffi >= 0.5.0
- ddgs >= 9.0.0
- fake-useragent >= 1.0.0

## Troubleshooting

**Search returns no results:**
- Check your internet connection
- Try increasing `sleep_interval` to avoid rate-limiting
- The website structure may have changed

**"DuckDuckGo fallback not available":**
```bash
pip install ddgs
```

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational and research purposes. Please respect website terms of service and robots.txt when scraping.
# - description
```
If requesting more than 100 results, googlesearch will send multiple requests to go through the pages. To increase the time between these requests, use `sleep_interval`:
```python
from googlesearch import search
search("Google", sleep_interval=5, num_results=200)
```

```
If requesting more than 10 results, but want to manage the batching yourself? 
Use `start_num` to specify the start number of the results you want to get:
```python
from googlesearch import search
search("Google", sleep_interval=5, num_results=200, start_num=10)
```

If you are using a HTTP Rotating Proxy which requires you to install their CA Certificate, you can simply add `ssl_verify=False` in the `search()` method to avoid SSL Verification.
```python
from googlesearch import search


proxy = 'http://username:password@proxy.host.com:8080/'
# or for socks5
# proxy = 'socks5://username:password@proxy.host.com:1080/'

j = search("proxy test", num_results=100, lang="en", proxy=proxy, ssl_verify=False)
for i in j:
    print(i)
```
