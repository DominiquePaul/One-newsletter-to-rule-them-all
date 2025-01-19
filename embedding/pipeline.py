import pickle
from tqdm import tqdm
from datetime import datetime, timezone
from pprint import pprint

import dotenv
from models import Article
import weaviate
from weaviate.util import generate_uuid5
from weaviate.classes.query import MetadataQuery

from weaviate_init import init_weaviate_client

dotenv.load_dotenv()


class Pipeline:

    def __init__(self, client: weaviate.Client, collection_name: str = "Articles"):
        self.client = client
        self.collection = self.client.collections.get(collection_name)
        self.chunk_size = 1000
        self.chunk_overlap = 50

    def ingest_article(self, article: Article):
        chunks = self._create_chunks(article.content)
        base_uuid = generate_uuid5(article.url)
        
        for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc="Ingesting chunks", leave=False):
            # Create a unique UUID for each chunk based on the article URL and chunk index
            chunk_uuid = generate_uuid5(f"{article.url}_chunk_{i}")
            
            # Create chunk object with original metadata plus chunk-specific fields
            chunk_object = dict(article)
            chunk_object.update({
                "content": chunk,
                "full_article": article.content,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "parent_uuid": str(base_uuid),
                "is_chunk": True
            })
            
            # Delete existing object with this UUID if it exists
            try:
                self.collection.data.delete_by_id(chunk_uuid)
            except:
                pass
                
            # Insert the new object
            self.collection.data.insert(chunk_object, uuid=chunk_uuid)

    def _create_chunks(self, text: str) -> list[str]:
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the chunk
            end = start + self.chunk_size
            
            # If we're not at the end of the text, try to find a sentence boundary
            if end < len(text):
                # Look for the last period, question mark, or exclamation mark
                for punct in ['. ', '? ', '! ']:
                    last_punct = text[start:end].rfind(punct)
                    if last_punct != -1:
                        # Skip if the punctuation is too close to the start
                        if last_punct < self.chunk_overlap:
                            continue
                        end = start + last_punct + 2  # +2 to include the punctuation and space
                        break
            
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
        
        return chunks

    def delete_article(self, url):
        self.collection.data.delete_by_id(generate_uuid5(url))

    def retrieve(
        self,
        query: str,
        from_date: datetime = None,
        to_date: datetime = None,
        top_k: int = 10,
    ) -> list[Article]:
        # Add timezone info if missing, with a warning
        if from_date and not from_date.tzinfo:
            print(f"Warning: from_date {from_date} has no timezone info. Assuming UTC.")
            from_date = from_date.replace(tzinfo=timezone.utc)
        if to_date and not to_date.tzinfo:
            print(f"Warning: to_date {to_date} has no timezone info. Assuming UTC.")
            to_date = to_date.replace(tzinfo=timezone.utc)

        # Add date filtering to the query if dates are provided
        where_filter = None
        if from_date or to_date:
            date_filter = {}
            if from_date:
                date_filter["gte"] = from_date.isoformat()
            if to_date:
                date_filter["lte"] = to_date.isoformat()
            where_filter = {"path": ["date"], "operator": "And", "valueDate": date_filter}

        response = self.collection.query.hybrid(
            query=query,
            limit=top_k,
            target_vector=["heading_vector"],
            return_metadata=MetadataQuery(
                distance=True, score=True, explain_score=True
            ),
            filters=where_filter,
        )

        output = []
        for obj in response.objects:
            output.append(Article(
                heading=obj.properties["heading"],
                subheading=obj.properties["subheading"], 
                date=obj.properties["date"],
                url=obj.properties["url"],
                content=obj.properties["content"],
                hero_image_url=obj.properties["hero_image_url"],
                full_article=obj.properties["full_article"]
            ))

        return output
    
    

if __name__ == "__main__":
    try:
        client = init_weaviate_client()

        pipeline = Pipeline(client)

        # test_article = Article(
        #     heading="Test Article",
        #     subheading="This is a test article",
        #     date="2021-01-01T00:00:00-02:00",
        #     url="https://www.example.com",
        #     content="This is a test article content",
        # )

        # pprint(test_article)

        # Load articles from pickle file
        with open("economist_articles.pkl", "rb") as f:
            articles = pickle.load(f)
        
        print(f"Loaded {len(articles)} articles from pickle file")
        
        # Ingest all articles
        for article in tqdm(articles, desc="Ingesting articles"):
            print(f"Ingesting article: {article.heading}")
            pipeline.ingest_article(article)

        # retrieved_articles = pipeline.retrieve_articles(["test"])
        # pprint(retrieved_articles)
    finally:
        client.close()
