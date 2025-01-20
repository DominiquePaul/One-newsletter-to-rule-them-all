# This file is used to scrape the NZZ articles
from datetime import datetime

from feedparser import parse as parse_feed
from trafilatura import extract, fetch_url
import requests
from bs4 import BeautifulSoup

from src.db.supa import add_article_to_supabase
from src.models import Article

def main():

    nzz_feed_link = "https://www.nzz.ch/technologie.rss"
    nzz_feed = parse_feed(nzz_feed_link)

    for article in nzz_feed.entries:
        page_title = article.title
        page_description = article.description
        page_link = article.link
        page_timestamp = datetime(*article.published_parsed[:6])
        # Stop at only one article
        raw_article = fetch_url(page_link)
        article_content_xml = extract(raw_article, output_format="xml", include_formatting=True, include_links=True, include_images=True)
        article_full = extract(raw_article, output_format="txt", include_comments=False)
    # Fetch the page to get the hero image

    try:
        response = requests.get(page_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        hero_image = soup.find('img')
        hero_image_url = hero_image['src'] if hero_image else None # type: ignore
    except Exception as e:
        print(f"Error fetching hero image: {e}")
        hero_image_url = None

    article = Article(
        heading=page_title,
        subheading=page_description,
        date=page_timestamp,
        url=page_link,
        hero_image_url=hero_image_url, # type: ignore
        article_xml=article_content_xml,# type: ignore
        article_full=article_full# type: ignore
    )

    add_article_to_supabase(article)

if __name__ == "__main__":
    main()
