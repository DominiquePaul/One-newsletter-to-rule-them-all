from datetime import datetime
from pprint import pprint

import dotenv
from article import Article
from weaviate import WeaviateClient
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.util import generate_uuid5

from weaviate_init import init_weaviate_client

dotenv.load_dotenv()


class Pipeline:

    def __init__(self, client: WeaviateClient, collection_name: str = "Articles"):
        self.client = client
        self.collection = self.client.collections.get(collection_name)

    def ingest_article(self, article: Article):
        # TODO: chunking (here? or is chunking done somewhere else in the weaviate pipeline?)
        uuid = generate_uuid5(article.url)
        self.collection.data.insert(dict(article), uuid=uuid)

    def delete_article(self, url):
        self.collection.data.delete_by_id(generate_uuid5(url))

    def retrieve_articles(
        self,
        topics: list[str],
        from_date: datetime = None,
        to_date: datetime = None,
        top_k: int = 10,
    ) -> list[Article]:
        if from_date or to_date:
            raise NotImplementedError("Filtering by date is not yet implemented")

        response_agg = []
        for topic in topics:
            response = self.collection.query.hybrid(
                query=topic,
                limit=top_k,
                target_vector=["heading_vector"],
                return_metadata=MetadataQuery(
                    distance=True, score=True, explain_score=True
                ),
                # filters=Filter..
            )

            response_agg.extend(response.objects)

        return response_agg


if __name__ == "__main__":
    try:
        client = init_weaviate_client()

        pipeline = Pipeline(client)

        test_article = Article(
            heading="Test Article",
            subheading="This is a test article",
            date="2021-01-01T00:00:00-02:00",
            url="https://www.example.com",
            content="This is a test article content",
        )

        pprint(test_article)

        # pipeline.ingest_article(test_article)
        # print('Article ingested')

        retrieved_articles = pipeline.retrieve_articles(["test"])

        pprint(retrieved_articles)
    finally:
        client.close()
