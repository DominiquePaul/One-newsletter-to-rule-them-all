from dataclasses import dataclass

@dataclass
class Article():
    headline: str
    description: str
    date: str
    link_url: str
    content: str