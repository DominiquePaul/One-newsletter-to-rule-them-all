from datetime import datetime

from pydantic import BaseModel

class Article(BaseModel):
    heading: str
    subheading: str
    date: datetime
    url: str
    hero_image_url: str|None
    article_xml: str
    article_full: str
    last_embedding_date: datetime|None = None
