import functools
import os

import dotenv
import weaviate
import weaviate.classes.config as wc
from weaviate.classes.init import Auth

dotenv.load_dotenv()

# Instantiate your client (not shown). e.g.:
# headers = {"X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY")}  # Replace with your OpenAI API key
# client = weaviate.connect_to_weaviate_cloud(..., headers=headers) or
# client = weaviate.connect_to_local(..., headers=headers)

@functools.cache
def init_weaviate_client():
    jinaai_key = os.getenv("JINAAI_APIKEY")
    headers = {
        "X-JinaAI-Api-Key": jinaai_key,
    }

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.environ['WEAVIATE_ENDPOINT'],  # Replace with your Weaviate Cloud URL
        auth_credentials=Auth.api_key(os.environ['WEAVIATE_ADMIN_KEY']),  # Replace with your Weaviate Cloud key
        headers=headers
    )
    return client


if __name__ == '__main__':
    try:
        client = init_weaviate_client()

        # !!!client.collections.delete('Articles')
        client.collections.create(
            name="Articles",
            properties=[
                wc.Property(name="heading", data_type=wc.DataType.TEXT),
                wc.Property(name="subheading", data_type=wc.DataType.TEXT),
                wc.Property(name="date", data_type=wc.DataType.DATE, indexRangeFilters=True),
                wc.Property(name="url", data_type=wc.DataType.TEXT),
                wc.Property(name="content", data_type=wc.DataType.TEXT, indexSearchable=True),
            ],
            # Define the vectorizer module
            vectorizer_config=[
                wc.Configure.NamedVectors.text2vec_jinaai(name="heading_vector", source_properties=["heading", "subheading"]),
                wc.Configure.NamedVectors.text2vec_jinaai(name="content_vector", source_properties=["content"]),
            ]

        )
    finally:
        client.close()
