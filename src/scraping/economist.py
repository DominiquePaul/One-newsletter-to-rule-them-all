import os
import re
import time
import logging
from datetime import datetime, timezone
from typing import Optional, List
from urllib.parse import urljoin

import requests
import trafilatura
from tqdm import tqdm
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from src.models import Article
from src.db.supa import add_article_to_supabase

# Constants
BASE_URL = "https://www.economist.com"
HEADERS = {
    "authority": "www.economist.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 10

def extract_economist_article(text: str, url: str) -> Optional[Article]:
    """Extract an article from The Economist website."""
    soup = BeautifulSoup(text, 'html.parser')
    heading = soup.find('h1')
    subheading = soup.find('h2')
    
    if not heading or not subheading:
        return None
        
    # Extract hero image with fallback
    hero_image_patterns = [
        r'(https://www\.economist\.com/content-assets[^"]+)',
        r'(https://[^"]+(?:\.jpg|\.jpeg|\.webp))'
    ]
    hero_image_url = None
    for pattern in hero_image_patterns:
        if match := re.search(pattern, text):
            hero_image_url = match.group(1)
            break

    article_text = trafilatura.extract(
        text,
        output_format="txt",
        include_comments=False
    )
    
    if not article_text:
        return None

    date_match = re.search(r"/(\d{4}/\d{2}/\d{2})/", url)
    if not date_match:
        return None

    article_date = datetime.strptime(date_match.group(1), "%Y/%m/%d").replace(tzinfo=timezone.utc)

    return Article(
        heading=heading.text.strip(),
        subheading=subheading.text.strip(),
        date=article_date,
        url=url,
        article_xml=article_text,
        hero_image_url=hero_image_url,
        article_full=article_text,
    )


def fetch_economist_article(url: str) -> Optional[Article]:
    """Fetch and parse an article from The Economist website."""
    cookies = {"fcx_user": os.environ.get("ECONOMIST_FCX_USER")}
    
    for attempt in range(MAX_RETRIES):
        fcx_user = os.environ.get("ECONOMIST_FCX_USER")
        cookies = {"fcx_user": fcx_user} if fcx_user else None
        try:
            response = requests.get(url, headers=HEADERS, cookies=cookies, timeout=30)
            response.raise_for_status()
        
            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    logging.error(f"Max retries reached for {url}")
                    return None
                logging.warning(f"Rate limited, waiting {RATE_LIMIT_DELAY} seconds... (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RATE_LIMIT_DELAY)
                continue

            return extract_economist_article(response.text, url)

        except RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return None
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            logging.error(f"Unexpected error processing {url}: {str(e)}")
            return None

def fetch_weekly_edition_urls(edition_url: str) -> Optional[list[str]]:
    """Fetch article URLs from a weekly edition page."""
    cookies = {"fcx_user": os.environ["ECONOMIST_FCX_USER"]}
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(edition_url, headers=HEADERS, cookies=cookies, timeout=30)
            response.raise_for_status()

            if response.status_code == 429:
                if attempt == MAX_RETRIES - 1:
                    logging.error(f"Max retries reached for {edition_url}")
                    return []
                logging.warning(f"Rate limited, waiting {RATE_LIMIT_DELAY} seconds... (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(RATE_LIMIT_DELAY)
                continue

            json_pattern = re.compile(
                r'{"@type":"ListItem","position":\d+,"url":"(https://www\.economist\.com/[^"]+)"}'
            )
            urls = {match.group(1) for match in json_pattern.finditer(response.text)}
            return [url for url in urls if "/2025/" in url]

        except RequestException as e:
            logging.error(f"Error fetching {edition_url}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return []
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            logging.error(f"Unexpected error processing {edition_url}: {str(e)}")
            return []

def get_all_weekly_editions_urls(
    from_year: int = datetime.now().year - 1,
    to_year: int = datetime.now().year + 1
) -> List[str]:
    """Fetch all weekly edition URLs within the specified year range."""
    all_links = []
    
    for year in range(from_year, to_year + 1):
        try:
            archive_url = f"{BASE_URL}/weeklyedition/archive?year={year}"
            response = requests.get(archive_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', attrs={"data-test-id": "edition-link"})
            
            for link in links:
                if href := link.get('href'):
                    full_url = urljoin(BASE_URL, href)
                    all_links.append(full_url)
                    
        except Exception as e:
            logging.error(f"Error fetching archive for year {year}: {str(e)}")
            
    return all_links

def main():
    """Main execution function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        all_weekly_editions_urls = get_all_weekly_editions_urls()
        article_urls = []
        
        for edition_url in tqdm(all_weekly_editions_urls, desc="Fetching article URLs"):
            if edition_urls := fetch_weekly_edition_urls(edition_url):
                article_urls.extend(edition_urls)
            time.sleep(1)  # Rate limiting
        
        for article_url in tqdm(article_urls, desc="Fetching articles"):
            if article := fetch_economist_article(article_url):
                add_article_to_supabase(article)
            time.sleep(1)  # Rate limiting
            
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
