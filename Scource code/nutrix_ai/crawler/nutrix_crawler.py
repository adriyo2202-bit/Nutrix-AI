import requests
from bs4 import BeautifulSoup
import urllib.robotparser
import time
from urllib.parse import urlparse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NutrixCrawler:
    def __init__(self, rate_limit_delay=1.0):
        self.rate_limit_delay = rate_limit_delay
        self.robot_parsers = {}
        self.last_request_time = 0
        
        # Simple headers to represent the crawler
        self.headers = {
            'User-Agent': 'NutrixBot/1.0 (Health and Nutrition Knowledge Retriever)'
        }
    
    def _check_robots_txt(self, url):
        """Check if the URL is allowed to be crawled according to robots.txt."""
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if domain not in self.robot_parsers:
            robots_url = f"{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                # Need to read the robots.txt file, but urllib.robotparser.read()
                # uses urllib.request which might not use our headers.
                # Let's fetch it with requests and parse.
                resp = requests.get(robots_url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
            except Exception as e:
                logger.warning(f"Could not fetch robots.txt for {domain}: {e}")
                # If we can't fetch it, we'll assume it's allowed but be cautious
                pass
            self.robot_parsers[domain] = rp
            
        rp = self.robot_parsers[domain]
        # If the parser has no rules (e.g. 404 on robots.txt), it allows everything by default.
        if not rp.default_entry and not rp.entries:
            return True
            
        return rp.can_fetch(self.headers['User-Agent'], url)

    def _rate_limit(self):
        """Ensure we don't hit the server too fast."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def fetch_page(self, url):
        """Fetch a page if allowed, extract content and metadata."""
        if not self._check_robots_txt(url):
            logger.info(f"Crawling disallowed by robots.txt for URL: {url}")
            return None

        self._rate_limit()

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return self._extract_content(response.text, url)
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None

    def _extract_content(self, html_content, url):
        """Extract main content and remove boilerplate using BeautifulSoup."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, header, footer, nav, aside elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside", "noscript", "iframe"]):
            element.decompose()

        # Extract Title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        if not title:
            h1 = soup.find('h1')
            title = h1.get_text().strip() if h1 else ""

        # Extract main text
        # A simple approach: grab paragraphs and lists
        content_elements = []
        # Usually main content is in <main>, <article>, or we just grab all paragraphs
        main_container = soup.find('main') or soup.find('article')
        
        if main_container:
            elements = main_container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table'])
        else:
            elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table'])

        for el in elements:
            text = el.get_text(separator=' ', strip=True)
            if text:
                content_elements.append(text)

        main_text = "\n\n".join(content_elements)

        # Basic metadata
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Try to find published date (often in meta tags)
        published_at = ""
        meta_date = soup.find('meta', property='article:published_time') or \
                    soup.find('meta', attrs={'name': 'publication_date'})
        if meta_date and meta_date.get('content'):
            published_at = meta_date['content']

        # Canonical URL
        canonical_link = soup.find('link', rel='canonical')
        canonical_url = canonical_link.get('href') if canonical_link else url

        # Author (often in meta tags)
        author = ""
        meta_author = soup.find('meta', attrs={'name': 'author'}) or \
                      soup.find('meta', property='article:author')
        if meta_author and meta_author.get('content'):
            author = meta_author['content']

        document = {
            "url": url,
            "canonical_url": canonical_url,
            "title": title,
            "domain": domain,
            "published_at": published_at,
            "crawled_at": datetime.utcnow().isoformat(),
            "content": main_text,
            "author": author
        }

        return document

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    crawler = NutrixCrawler()
    # Test with a generic accessible page, since this is just an example test
    doc = crawler.fetch_page("https://en.wikipedia.org/wiki/Nutrition")
    if doc:
        print(f"Title: {doc['title']}")
        print(f"Content Length: {len(doc['content'])}")
