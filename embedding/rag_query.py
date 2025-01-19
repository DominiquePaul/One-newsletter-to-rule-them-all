import json
import os
from pprint import pprint

import dotenv
from mistralai import Mistral, UserMessage

from embedding.pipeline import Pipeline
from models import Article, Summary
from weaviate_init import init_weaviate_client

dotenv.load_dotenv()

class RAGQueryEngine:
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_APIKEY"))
        self.pipeline = Pipeline(init_weaviate_client())
        
    def query(self, topic: str, num_articles: int = 5) -> tuple[str, str]:
        # 1. Retrieve relevant chunks from Weaviate
        articles = self.pipeline.retrieve(
            query=topic,
            top_k=num_articles
        )

        # 2. Create prompt with context
        prompt = f"""You are presented with news articles for the topic "{topic}". Based on the following context, please answer the question. 
If the answer cannot be found in the context, say so.

"""
        for article in articles:
            prompt += f"""Article: {article.heading}
{article.subheading}

{article.full_article}
------
"""
        prompt += ("Please summarize the articles to five bullet points. "
                   "Each bullet point should have between two to four sentences. "
                   "Format the bullet points with dashes `-`. "
                   "Do not output any other text besides the bullet points.")

        print(f"""### DEBUG ####\n\n{prompt}\n\n### ###""")

        # 3. Get response from Mistral
        messages = [
            UserMessage(content=prompt)
        ]
        
        response = self.mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            response_format={
                "type": "json_object",
            }
        )
        
        return articles[0].hero_image_url, response.choices[0].message.content


if __name__ == "__main__":
    # Example usage
    rag = RAGQueryEngine()
    
    topic = "Greenland"
    # Fixed the string formatting
    # question = f"What do articles about {topic} report about?"
    
    print("Querying with Mistral:")
    mistral_answer = rag.query(topic)
    pprint(mistral_answer)
    
    rag.pipeline.client.close()
