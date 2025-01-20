import os
from supabase import create_client, Client

def add_article_to_supabase(article):
    """Add an article to the Supabase articles table"""
    supabase: Client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

    # Convert article to dict and format date
    article_data = {
        "heading": article.heading,
        "subheading": article.subheading,
        "date": article.date.isoformat(),
        "url": article.url,
        "hero_image_url": article.hero_image_url,
        "article_xml": article.article_xml,
        "article_full": article.article_full,
        "last_embedding_date": article.last_embedding_date.isoformat() if article.last_embedding_date else None
    }

    # Insert into articles table
    data = supabase.table("articles").insert(article_data).execute()
    return data
