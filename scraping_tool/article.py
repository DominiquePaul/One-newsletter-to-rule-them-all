from pydantic import BaseModel
from datetime import datetime
from pydantic import field_validator


class Article(BaseModel):
    heading: str
    subheading: str
    date: datetime
    url: str
    content: str


class ArticleChunk(BaseModel):
    article_url: str
    embedding: list[float]
    content: str
    num_characters: int
