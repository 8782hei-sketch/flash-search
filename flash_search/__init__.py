"""Flash-search: A fast, multi-source web search library with content extraction."""
from time import sleep
from bs4 import BeautifulSoup
from curl_cffi.requests import Session, get
from requests.exceptions import RequestException
from urllib.parse import unquote
from .user_agents import get_useragent

__version__ = "2.0.0"
__author__ = "https://www.tiktok.com/@vibecoding_pemula"

_session = Session()

try:
    from ddgs import DDGS
    _ddgs_available = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        _ddgs_available = True
    except ImportError:
        _ddgs_available = False


def _req_google(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    """Request Google search results with curl-cffi"""
    try:
        resp = _session.get(
            url="https://www.google.com/search",
            headers={
                "User-Agent": get_useragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
            },
            params={
                "q": term,
                "num": results + 2,
                "hl": lang,
                "start": start,
                "safe": safe,
                "gl": region,
            },
            proxies=proxies,
            timeout=timeout,
            verify=ssl_verify,
            allow_redirects=True,
            impersonate="chrome124"
        )
        resp.raise_for_status()
        return resp
    except Exception as e:
        raise RequestException(f"Google search request failed: {e}") from e


def _req_duckduckgo(term, results, lang, start):
    """Fallback to DuckDuckGo search"""
    if not _ddgs_available:
        raise RequestException("DuckDuckGo fallback not available. Install with: pip install ddgs")
    try:
        ddgs = DDGS()
        search_results = ddgs.text(term, region=lang, timelimit='y', max_results=results)
        return search_results
    except Exception as e:
        raise RequestException(f"DuckDuckGo search failed: {e}") from e


class SearchResult:
    """Represents a single search result."""
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False):
    """
    Search the web for a given term.
    
    Args:
        term: Search query
        num_results: Number of results (default: 10)
        lang: Language code (default: "en")
        proxy: Proxy URL if needed
        advanced: Return SearchResult objects (default: False)
        sleep_interval: Sleep between requests
        timeout: Request timeout in seconds
        safe: Safe search mode
        ssl_verify: Verify SSL certificates
        region: Country code for results
        start_num: Starting result number
        unique: Return only unique URLs
        
    Yields:
        URLs or SearchResult objects
    """
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http") or proxy.startswith("socks5")) else None

    start = start_num
    fetched_results = 0
    fetched_links = set()
    use_duckduckgo = False
    
    while fetched_results < num_results:
        try:
            if not use_duckduckgo:
                resp = _req_google(term, num_results - start, lang, start, proxies, timeout, safe, ssl_verify, region)
                soup = BeautifulSoup(resp.text, "html.parser")
                result_block = soup.find_all("div", class_="ezO2md")
                
                if len(result_block) == 0 and _ddgs_available:
                    use_duckduckgo = True
                    continue
                
                new_results = 0
                for result in result_block:
                    link_tag = result.find("a", href=True)
                    title_tag = link_tag.find("span", class_="CVA68e") if link_tag else None
                    description_tag = result.find("span", class_="FrIlee")

                    if not (link_tag and title_tag and description_tag):
                        continue

                    link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", ""))
                    if link in fetched_links and unique:
                        continue
                    fetched_links.add(link)
                    title = title_tag.text
                    description = description_tag.text
                    fetched_results += 1
                    new_results += 1
                    
                    if advanced:
                        yield SearchResult(link, title, description)
                    else:
                        yield link

                    if fetched_results >= num_results:
                        return

                if new_results == 0:
                    break

                start += 10
                sleep(sleep_interval)
            else:
                ddg_results = _req_duckduckgo(term, num_results - fetched_results, lang, start)
                for result in ddg_results:
                    url = result.get('href', '')
                    title = result.get('title', '')
                    desc = result.get('body', '')
                    
                    if url in fetched_links and unique:
                        continue
                    fetched_links.add(url)
                    fetched_results += 1
                    
                    if advanced:
                        yield SearchResult(url, title, desc)
                    else:
                        yield url
                    
                    if fetched_results >= num_results:
                        return
                break
                
        except RequestException:
            if not use_duckduckgo and _ddgs_available:
                use_duckduckgo = True
                continue
            else:
                raise


def extract_website_content(url):
    """Extract clean text content from a website."""
    try:
        resp = get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        return f"Error extracting content: {e}"


def save_results_to_file(results, filename="search_results.txt"):
    """Save search results to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, result in enumerate(results, 1):
            if isinstance(result, SearchResult):
                f.write(f"\n{'='*80}\n")
                f.write(f"Result #{i}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Title: {result.title}\n")
                f.write(f"URL: {result.url}\n")
                f.write(f"Description: {result.description}\n\n")
            else:
                f.write(f"{i}. {result}\n")
    return f"Results saved to {filename}"


def save_website_content(url, filename=None):
    """Extract and save website content to a file."""
    if not filename:
        filename = url.split("//")[-1].split("/")[0] + ".txt"
    content = extract_website_content(url)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Content saved to {filename}"


__all__ = ['search', 'SearchResult', 'extract_website_content', 'save_results_to_file', 'save_website_content', '__version__']
