# This file is used to scrape the NZZ articles
from trafilatura import fetch_url, extract
from feedparser import parse as parse_feed


def main():

    nzz_feed_link = "https://www.nzz.ch/technologie.rss"
    nzz_feed = parse_feed(nzz_feed_link)
    
    for article in nzz_feed.entries:
        page_title = article.title
        page_description = article.description
        page_link = article.link
        # Stop at only one article
        raw_article = fetch_url(page_link)
        article = extract(raw_article, output_format="xml")
        print(article)
        
        # From here push each individual piece to the weviate databse
        break



if __name__ == "__main__":
    main()