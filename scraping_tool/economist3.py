fcx_user = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDMzejAwMDAycE1VSjRBQU8iLCJlbnRpdGxlbWVudHMiOlsiVEUuUE9EQ0FTVCIsIlRFLkFQUCIsIlRFLldFQiIsIlRFLk5FV1NMRVRURVIiXSwidXNlclR5cGUiOiJzdWJzY3JpYmVyIiwiZXhwIjoxNzQ1MDA4MTI3LCJpYXQiOjE3MzcyMjg1Mjd9.CnXNEWJYzsRxS4hebZIPGryg7IirdvjoK_CJExOVQKU"


import requests
import trafilatura
import json
import re


def fetch_economist_article(url):
    headers = {
        'authority': 'www.economist.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    cookies = {
        'fcx_user': fcx_user
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None
        
    article_content = trafilatura.extract(response.text, output_format='xml', include_comments=False)
    return article_content


def fetch_weekly_edition_urls(edition_url):
    headers = {
        'authority': 'www.economist.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    cookies = {
        'fcx_user': fcx_user
    }
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None

    # Use trafilatura to extract all links
    downloaded = requests.get(edition_url, headers=headers, cookies=cookies).text
    links = []
    # Look for JSON-LD script tags containing article URLs
    json_pattern = re.compile(r'{"@type":"ListItem","position":\d+,"url":"(https://www\.economist\.com/[^"]+)"}')
    matches = json_pattern.finditer(downloaded)
    for match in matches:
        url = match.group(1)
        links.append(url)

    
    # Filter for article URLs
    article_urls = []
    for link in links:
        if link.startswith('https://www.economist.com/') and '/2025/' in link:
            article_urls.append(link)
            
    return list(set(article_urls))  # Remove duplicates

# Example usage:
edition_url = 'https://www.economist.com/weeklyedition/2025-01-18'
urls = fetch_weekly_edition_urls(edition_url)
for url in urls:
    fetch_economist_article()
    print(url)
