from datetime import datetime

from pydantic import BaseModel, field_validator


class Article(BaseModel):
    heading: str
    subheading: str
    date: datetime
    url: str
    content: str
    hero_image_url: str|None
    full_article: str


class ArticleChunk(BaseModel):
    article_url: str
    embedding: list[float]
    content: str
    num_characters: int

