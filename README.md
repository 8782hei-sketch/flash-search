# 🚀 Flash-search

A fast, multi-source web search library with intelligent fallback and content extraction capabilities.

[![PyPI](https://img.shields.io/badge/PyPI-flash--search-blue)](https://pypi.org/project/flash-search)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Fast Web Search** - Search across multiple sources with intelligent fallback (Google + DuckDuckGo)  
🔄 **Auto Fallback** - Automatically uses DuckDuckGo if Google is blocked  
📄 **Content Extraction** - Extract clean, readable text from websites without HTML  
💾 **Save Results** - Export search results and website content to .txt files  
🌍 **Multi-language** - Support for 30+ languages and regions  
🔧 **Advanced Filtering** - Unique results, safe search, pagination support  
⚡ **Fast Performance** - Optimized with curl-cffi for speed and reliability

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

## How It Works

Flash-search uses a dual-source strategy:

1. **Primary Source**: Uses `curl-cffi` to impersonate a real browser and fetch Google results
2. **Fallback Source**: Automatically switches to DuckDuckGo if Google blocks the request

This ensures reliable search results even when one source is unavailable.

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
