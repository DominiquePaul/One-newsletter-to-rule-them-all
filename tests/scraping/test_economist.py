from datetime import datetime, timezone

from src.models import Article
from src.scraping.economist import extract_economist_article

def test_extract_economist_article(example_economist_article):
    
    # Test URL with date
    test_url = 'https://www.economist.com/middle-east-and-africa/2025/01/16/first-the-ceasefire-next-the-trump-effect-could-upend-the-middle-east'
    
    # Extract article
    article = extract_economist_article(example_economist_article, test_url)
    
    # Assertions
    assert isinstance(article, Article)
    assert article.heading == "First, the ceasefire. Next the Trump effect could upend the Middle East"
    assert article.subheading == "Will Israel and Donald Trump use the threat of annexation to secure a new grand bargain?"
    assert article.url == test_url
    assert article.hero_image_url == "https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/content-assets/images/20250118_MAP001.jpg"
    assert "Article content goes here." in article.article_full
    assert article.date == datetime(2024, 1, 15, tzinfo=timezone.utc)

def test_extract_economist_article_missing_required_fields():
    # HTML without required fields
    html_content = """
    <html>
        <body>
            <p>Article with no heading or subheading</p>
        </body>
    </html>
    """
    
    test_url = "https://www.economist.com/leaders/2024/01/15/test-article"
    
    # Should return None when required fields are missing
    article = extract_economist_article(html_content, test_url)
    assert article is None

def test_extract_economist_article_invalid_date():
    html_content = """
    <html>
        <body>
            <h1>Test Headline</h1>
            <h2>Test Subheading</h2>
        </body>
    </html>
    """
    
    # URL with invalid date format
    test_url = "https://www.economist.com/leaders/invalid-date/test-article"
    
    # Should return None when date is invalid
    article = extract_economist_article(html_content, test_url)
    assert article is None
