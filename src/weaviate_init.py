import functools
import os

import dotenv
import weaviate
import weaviate.classes.config as wc
from weaviate.classes.init import Auth

dotenv.load_dotenv()

@functools.cache
def init_weaviate_client() -> weaviate.WeaviateClient:
    jinaai_key = os.getenv("JINAAI_APIKEY")
    headers = {"X-JinaAI-Api-Key": jinaai_key} if jinaai_key else None
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ[
            "WEAVIATE_ENDPOINT"
        ],
        auth_credentials=Auth.api_key(
            os.environ["WEAVIATE_ADMIN_KEY"]
        ),
        headers=headers,
    )
    return client


if __name__ == "__main__":
    try:
        client = init_weaviate_client()

        # Delete collection if it exists
        if client.collections.exists("Articles"):
            client.collections.delete("Articles")

        client.collections.create(
            name="Articles",
            properties=[
                wc.Property(name="heading", data_type=wc.DataType.TEXT),
                wc.Property(name="subheading", data_type=wc.DataType.TEXT),
                wc.Property(name="hero_image_url", data_type=wc.DataType.TEXT),
                wc.Property(
                    name="date", data_type=wc.DataType.DATE, indexRangeFilters=True # type: ignore
                ),
                wc.Property(name="url", data_type=wc.DataType.TEXT),
                wc.Property(
                    name="content", data_type=wc.DataType.TEXT, indexSearchable=True # type: ignore
                ),
                wc.Property(
                    name="full_article", data_type=wc.DataType.TEXT, indexSearchable=True # type: ignore
                ),
            ],
            # Define the vectorizer module
            vectorizer_config=[
                wc.Configure.NamedVectors.text2vec_jinaai(
                    name="heading_vector", source_properties=["heading", "subheading"]
                ),
                wc.Configure.NamedVectors.text2vec_jinaai(
                    name="content_vector", source_properties=["content"]
                ),
            ],
        )
    finally:
        client.close()
