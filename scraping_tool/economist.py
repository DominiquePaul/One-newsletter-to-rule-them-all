fcx_user = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDMzejAwMDAycE1VSjRBQU8iLCJlbnRpdGxlbWVudHMiOlsiVEUuUE9EQ0FTVCIsIlRFLkFQUCIsIlRFLldFQiIsIlRFLk5FV1NMRVRURVIiXSwidXNlclR5cGUiOiJzdWJzY3JpYmVyIiwiZXhwIjoxNzQ1MDA4MTI3LCJpYXQiOjE3MzcyMjg1Mjd9.CnXNEWJYzsRxS4hebZIPGryg7IirdvjoK_CJExOVQKU"

import json
import pickle
import re
import time
from datetime import datetime

import requests
import trafilatura
from tqdm import tqdm

from models import Article

def fetch_economist_article(url):
    headers = {
        "authority": "www.economist.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    retries = 0
    while retries < 3:
        response = requests.get(url, headers=headers, cookies={"fcx_user": fcx_user})

        if response.status_code == 429:
            retries += 1
            if retries == 3:
                print(f"Error: Max retries reached for {url}")
                return None
            print(f"Rate limited, waiting 10 seconds... (attempt {retries}/3)")
            time.sleep(10)
            continue

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return None

        article_content = trafilatura.extract(
            response.text, output_format="xml", include_comments=False
        )
        return Article(
            heading=response.text.split("<h1")[1].split("</h1>")[0].split(">")[1],
            subheading=response.text.split("<h2")[1].split("</h2>")[0].split(">")[1],
            date=datetime.strptime(
                re.search(r"/(\d{4}/\d{2}/\d{2})/", url).group(1), "%Y/%m/%d"
            ),
            url=url,
            content=trafilatura.extract(response.text, output_format="txt", include_comments=False),
            hero_image_url=(
                re.search(r'(https://www\.economist\.com/content-assets[^"]+)', response.text) or 
                re.search(r'(https://[^"]+(?:\.jpg|\.jpeg|\.webp))', response.text)
            ).group(1) if (
                re.search(r'(https://www\.economist\.com/content-assets[^"]+)', response.text) or
                re.search(r'(https://[^"]+(?:\.jpg|\.jpeg|\.webp))', response.text)
            ) else None,
        )


def fetch_weekly_edition_urls(edition_url):
    headers = {
        "authority": "www.economist.com",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    cookies = {"fcx_user": fcx_user}

    retries = 0
    while retries < 3:
        response = requests.get(edition_url, headers=headers, cookies=cookies)

        if response.status_code == 429:
            retries += 1
            if retries == 3:
                print(f"Error: Max retries reached for {edition_url}")
                return []
            print(f"Rate limited, waiting 10 seconds... (attempt {retries}/3)")
            time.sleep(10)
            continue

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return []

        downloaded = response.text
        links = []
        # Look for JSON-LD script tags containing article URLs
        json_pattern = re.compile(
            r'{"@type":"ListItem","position":\d+,"url":"(https://www\.economist\.com/[^"]+)"}'
        )
        matches = json_pattern.finditer(downloaded)
        for match in matches:
            url = match.group(1)
            links.append(url)

        # Filter for article URLs
        article_urls = []
        for link in links:
            if link.startswith("https://www.economist.com/") and "/2025/" in link:
                article_urls.append(link)

        return list(set(article_urls))


# Example usage:
edition_url = "https://www.economist.com/weeklyedition/2025-01-18"
urls = fetch_weekly_edition_urls(edition_url)
articles = []
for url in tqdm(urls, desc="Fetching articles"):
    article = fetch_economist_article(url)
    if article:
        articles.append(article)

# Save articles to pickle file
with open("economist_articles.pkl", "wb") as f:
    pickle.dump(articles, f)
