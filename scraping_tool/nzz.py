# This file is used to scrape the NZZ articles
from time import strftime

from article import Article
from feedparser import parse as parse_feed
from trafilatura import extract, fetch_url


def main():

    nzz_feed_link = "https://www.nzz.ch/technologie.rss"
    nzz_feed = parse_feed(nzz_feed_link)

    for article in nzz_feed.entries:
        page_title = article.title
        page_description = article.description
        page_link = article.link
        page_timestamp = article.published_parsed
        page_timestamp = strftime("%Y-%m-%d %H:%M:%S", page_timestamp)
        # Stop at only one article
        raw_article = fetch_url(page_link)
        article_content = extract(raw_article, output_format="xml")

        article = Article(
            page_title, page_description, page_timestamp, page_link, article_content
        )
        print(article)

        # From here push each individual piece to the weviate databse
        break


if __name__ == "__main__":
    main()
