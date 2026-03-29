"""Flash-search: A fast, multi-source web search library with content extraction."""
from time import sleep
from bs4 import BeautifulSoup
from curl_cffi.requests import Session, get
from requests.exceptions import RequestException
from urllib.parse import unquote
from .user_agents import get_useragent
from enum import Enum

__version__ = "2.5.0"
__author__ = "https://www.tiktok.com/@vibecoding_pemula"

_session = Session()


class SearchIntent(Enum):
    """Enum untuk intent deteksi query"""
    INFORMATIONAL = "informational"  # "How to...", "What is..."
    NAVIGATIONAL = "navigational"     # Brand/site specific
    TRANSACTIONAL = "transactional"   # "Buy", "Download"
    LOCAL = "local"                   # "Near me", location-based


def detect_intent(query):
    """Deteksi intent dari query untuk ranking yang lebih baik"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['how', 'what', 'why', 'explain']):
        return SearchIntent.INFORMATIONAL
    elif any(word in query_lower for word in ['buy', 'price', 'download']):
        return SearchIntent.TRANSACTIONAL
    elif any(word in query_lower for word in ['near', 'near me', 'location']):
        return SearchIntent.LOCAL
    else:
        return SearchIntent.INFORMATIONAL


def is_mostly_ads(text):
    """Deteksi apakah teks kemungkinan adalah iklan atau spam"""
    if not text:
        return True
    
    ad_keywords = {
        'ad', 'ads', 'sponsored', 'promotion', 'promo', 'discount', 'sale', 
        'limited offer', 'click here', 'buy now', 'sign up', 'register now',
        'click', 'free trial', 'offer'
    }
    
    text_lower = text.lower()
    ad_count = sum(1 for keyword in ad_keywords if keyword in text_lower)
    
    # Jika lebih dari 30% text adalah ad keywords, dianggap mostly ads
    return ad_count > (len(ad_keywords) * 0.3)


def is_readable_url(url):
    """Cek apakah URL memiliki struktur yang readable dan bukan spam"""
    if not url:
        return False
    
    # URL terlalu pendek kemungkinan shortened/suspicious
    if len(url) < 10:
        return False
    
    # Cek domain yang terindikasi spam
    spam_patterns = {
        'bit.ly', 'tinyurl', 'short.link', 'goo.gl', 
        'adf.ly', 'linkvertise', 'link.click', 'click.pay'
    }
    
    url_lower = url.lower()
    if any(pattern in url_lower for pattern in spam_patterns):
        return False
    
    # URL yang readable biasanya memiliki path yang jelas
    parts = url.split('/')
    if len(parts) < 4:  # min: https://domain.com/
        return False
    
    return True


def assess_content_quality(title, description, url):
    """Nilai kualitas konten berdasarkan berbagai faktor (0-100)"""
    quality_score = 0
    
    # 1. Title length (optimal: 40-70 chars untuk readability)
    if title:
        title_len = len(title)
        if 40 <= title_len <= 70:
            quality_score += 20
        elif 30 <= title_len <= 80:
            quality_score += 15  # Acceptable tapi tidak optimal
        elif title_len > 20:
            quality_score += 5   # Minimal points
    
    # 2. Description comprehensiveness (descriptive > 100 chars)
    if description:
        desc_len = len(description)
        if desc_len > 150:
            quality_score += 20
        elif desc_len > 100:
            quality_score += 15
        elif desc_len > 50:
            quality_score += 5
    
    # 3. Check if content has actual information (not just ads)
    if not is_mostly_ads(description):
        quality_score += 20
    
    # 4. URL structure readability
    if is_readable_url(url):
        quality_score += 20
    
    # 5. Domain authority bonus (official domains)
    if url:
        url_lower = url.lower()
        official_domains = {'.edu', '.gov', '.org', 'wikipedia', 'github', 'stackoverflow', 'medium.com', 'dev.to'}
        if any(domain in url_lower for domain in official_domains):
            quality_score += 5
    
    return min(quality_score, 100)  # Cap at 100


def extract_domain(url):
    """Extract domain dari URL untuk diversification check"""
    if not url:
        return None
    try:
        # Extract domain dari URL
        # https://www.example.com/path -> example.com
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix untuk konsistensi
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.split('/')[0] if domain else None
    except:
        return None


class ResultDiversifier:
    """Engine untuk diversifikasi hasil pencarian berdasarkan domain dan konten type"""
    
    def __init__(self, max_per_domain=2, diversity_weight=0.3):
        """
        Args:
            max_per_domain: Max hasil dari domain yang sama
            diversity_weight: Bobot diversifikasi vs relevansi (0-1, default 0.3)
        """
        self.max_per_domain = max_per_domain
        self.diversity_weight = diversity_weight
    
    def diversify(self, scored_results):
        """
        Diversifikasi hasil sambil mempertahankan ranking quality
        Input: [(score, SearchResult), ...]
        Output: [(score, SearchResult, diversity_adjusted_score), ...]
        """
        if not scored_results:
            return []
        
        diversified = []
        domain_count = {}
        selected_domains = set()
        
        # Sort by original score descending
        sorted_results = sorted(scored_results, key=lambda x: x[0], reverse=True)
        
        for score, result in sorted_results:
            domain = extract_domain(result.url)
            
            if domain is None:
                # Jika tidak bisa extract domain, tetap include
                diversified.append((score, result, score))
                continue
            
            # Track domain count
            domain_count[domain] = domain_count.get(domain, 0) + 1
            
            # Diversifikasi score: kurangi score jika domain sudah banyak
            diversity_penalty = 0
            if domain_count[domain] > self.max_per_domain:
                # Penalty meningkat untuk setiap result tambahan dari domain sama
                excess_count = domain_count[domain] - self.max_per_domain
                diversity_penalty = (excess_count * 10) * self.diversity_weight
            
            # Adjusted score: pertahankan score tapi dengan diversity penalty
            adjusted_score = score - diversity_penalty
            
            # Track domains yang sudah dipilih
            if adjusted_score > 0:
                selected_domains.add(domain)
                diversified.append((score, result, adjusted_score))
        
        return diversified
    
    def select_diverse_results(self, scored_results, num_results):
        """
        Select hasil yang diverse berdasarkan adjusted scores
        Input: [(score, SearchResult, adjusted_score), ...]
        Output: [SearchResult, ...] dalam urutan diversity-optimized
        """
        if not scored_results:
            return []
        
        # Sort by adjusted score
        sorted_by_adjusted = sorted(scored_results, key=lambda x: x[2], reverse=True)
        
        # Take top N results
        diverse_results = [result for _, result, _ in sorted_by_adjusted[:num_results]]
        
        return diverse_results
    
    def get_content_type(self, result):
        """Deteksi tipe konten dari title dan description"""
        content_type = "general"
        
        title_lower = result.title.lower()
        desc_lower = result.description.lower()
        text = title_lower + " " + desc_lower
        
        # Deteksi tipe konten
        if any(kw in text for kw in {'tutorial', 'how to', 'guide', 'learn', 'documentation'}):
            content_type = "tutorial"
        elif any(kw in text for kw in {'forum', 'discussion', 'reddit', 'ycombinator'}):
            content_type = "discussion"
        elif any(kw in text for kw in {'research', 'paper', 'study', 'academic', '.edu'}):
            content_type = "academic"
        elif any(kw in text for kw in {'news', 'article', 'blog'}) or 'wikipedia' in result.url.lower():
            content_type = "article"
        elif any(kw in text for kw in {'video', 'youtube', 'tutorial video'}):
            content_type = "video"
        elif any(kw in text for kw in {'official', 'documentation', '.org', '.gov'}):
            content_type = "official"
        
        return content_type
    
    def diversify_by_content_type(self, scored_results):
        """Balance hasil berdasarkan content type untuk lebih variatif"""
        content_types = {}
        diversified = []
        
        for score, result, adjusted_score in scored_results:
            content_type = self.get_content_type(result)
            
            if content_type not in content_types:
                content_types[content_type] = 0
            
            # Boost score untuk content types yang kurang represented
            type_penalty = content_types[content_type] * 2
            final_score = adjusted_score - type_penalty
            
            content_types[content_type] += 1
            diversified.append((final_score, result, content_type))
        
        return diversified


class SearchRanker:
    """Ranking engine dengan intent detection dan content quality assessment"""
    
    def score_result(self, query, result):
        """
        Hitung score relevance berdasarkan multiple factors:
        - Keyword matching
        - Intent alignment
        - Content quality assessment
        """
        score = 0
        
        # Deteksi intent dari query
        intent = detect_intent(query)
        
        # === RELEVANCE SCORING (200 points max) ===
        # Keyword matching di title (bobot tinggi)
        if self._keyword_match(query, result.title):
            score += 100
            
        # Keyword matching di description
        if self._keyword_match(query, result.description):
            score += 50
            
        # URL quality check
        if self._is_quality_url(result.url):
            score += 30
            
        # Domain authority check
        domain_score = self._get_domain_authority(result.url)
        score += domain_score * 20
        
        # === CONTENT QUALITY SCORING (100 points max) ===
        quality_score = assess_content_quality(result.title, result.description, result.url)
        score += quality_score
        
        # === INTENT-AWARE SCORING (60 points max) ===
        intent_boost = self._calculate_intent_boost(intent, result, query)
        score += intent_boost
        
        return score
    
    def _keyword_match(self, query, text):
        """Multi-keyword matching dengan exact dan partial match"""
        keywords = query.lower().split()
        text_lower = text.lower()
        return all(kw in text_lower for kw in keywords)
    
    def _is_quality_url(self, url):
        """Filter domain berkualitas rendah atau spam"""
        spam_domains = {'pinterest.com', 'facebook.com', 'reddit.com'}
        return not any(domain in url for domain in spam_domains)
    
    def _get_domain_authority(self, url):
        """Score domain authority (bisa cache dari external API)"""
        # Implementasi sederhana, bisa integrate dengan Moz/Ahrefs API
        return 0.8  # Default score
    
    def _calculate_intent_boost(self, intent, result, query):
        """Boost score berdasarkan intent dan karakteristik result"""
        boost = 0
        url_lower = result.url.lower()
        title_lower = result.title.lower()
        description_lower = result.description.lower()
        
        if intent == SearchIntent.INFORMATIONAL:
            # Untuk informational: boost hasil yang educational/explanatory
            educational_keywords = {'tutorial', 'guide', 'how to', 'explanation', 'learn', 'documentation', 'article', 'blog'}
            if any(kw in title_lower or kw in description_lower for kw in educational_keywords):
                boost += 40
            # Boost official docs/educational domains
            if any(domain in url_lower for domain in {'edu', 'wikipedia', 'docs.', 'documentation'}):
                boost += 30
                
        elif intent == SearchIntent.TRANSACTIONAL:
            # Untuk transactional: boost hasil dengan ecommerce/product intent
            ecommerce_keywords = {'buy', 'price', 'shop', 'download', 'order', 'product', 'add to cart', 'amazon', 'ebay'}
            if any(kw in title_lower or kw in description_lower for kw in ecommerce_keywords):
                boost += 50
            # Boost official retailer domains
            if any(domain in url_lower for domain in {'amazon', 'ebay', 'store', 'shop', 'buy'}):
                boost += 35
                
        elif intent == SearchIntent.LOCAL:
            # Untuk local: boost hasil dengan location keywords
            local_keywords = {'near', 'near me', 'location', 'local', 'address', 'hours', 'phone', 'google maps'}
            if any(kw in title_lower or kw in description_lower for kw in local_keywords):
                boost += 45
            # Boost maps dan local business directories
            if any(domain in url_lower for domain in {'maps.google', 'yelp', 'foursquare', 'google.com/maps'}):
                boost += 40
                
        elif intent == SearchIntent.NAVIGATIONAL:
            # Untuk navigational: boost hasil yang official/brand name match
            if self._keyword_match(query, title_lower):
                boost += 60
            # Boost official brand domains
            official_domain_indicators = {'.com', '.org', '.io'}
            if any(url_lower.endswith(ind) for ind in official_domain_indicators):
                boost += 25
        
        return boost

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
        URLs or SearchResult objects (ranked if advanced mode)
    """
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http") or proxy.startswith("socks5")) else None

    start = start_num
    fetched_results = 0
    fetched_links = set()
    use_duckduckgo = False
    collected_results = []  # Kumpulkan semua hasil terlebih dahulu
    ranker = SearchRanker()  # Inisialisasi ranker
    
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
                    
                    search_result = SearchResult(link, title, description)
                    collected_results.append(search_result)
                    
                    if fetched_results >= num_results:
                        break

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
                    
                    search_result = SearchResult(url, title, desc)
                    collected_results.append(search_result)
                    
                    if fetched_results >= num_results:
                        break
                break
                
        except RequestException:
            if not use_duckduckgo and _ddgs_available:
                use_duckduckgo = True
                continue
            else:
                raise
    
    # Terapkan ranking jika ada hasil
    if collected_results:
        # Hitung score untuk setiap hasil
        scored_results = [(ranker.score_result(term, r), r) for r in collected_results]
        # Sort berdasarkan score (tertinggi duluan)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # === DIVERSIFIKASI HASIL ===
        diversifier = ResultDiversifier(max_per_domain=2, diversity_weight=0.3)
        diversified_results = diversifier.diversify(scored_results)
        
        # Apply content type diversification untuk lebih variatif
        final_results = diversifier.diversify_by_content_type(diversified_results)
        
        # Sort final results berdasarkan adjusted score
        final_results.sort(key=lambda x: x[0], reverse=True)
        
        # Yield hasil yang sudah di-ranking dan di-diversify
        for adjusted_score, result, content_type in final_results:
            if advanced:
                yield result
            else:
                yield result.url
    


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


__all__ = [
    'search', 'SearchResult', 'SearchRanker', 'SearchIntent', 'detect_intent',
    'assess_content_quality', 'is_mostly_ads', 'is_readable_url',
    'extract_domain', 'ResultDiversifier',
    'extract_website_content', 'save_results_to_file', 'save_website_content', 
    '__version__'
]
