from pydantic import BaseModel
from datetime import datetime
from pydantic import field_validator

class Article(BaseModel):
    heading: str
    subheading: str
    date: datetime
    url: str
    content: str

    # @field_validator('date')
    # def validate_date(cls, v):
    #     try:
    #         # Try to parse the date string to verify it's valid
    #         datetime.strptime(v, '%Y-%m-%d')
    #         return v
    #     except ValueError:
    #         raise ValueError('Date must be in YYYY-MM-DD format')
    #

class ArticleChunk(BaseModel):
    article_url: str
    embedding: list[float]
    content: str
    num_characters: int