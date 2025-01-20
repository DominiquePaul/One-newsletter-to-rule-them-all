import os
from pprint import pprint

import dotenv
from mistralai import Mistral, UserMessage
from openai import OpenAI

from src.embedding.pipeline import Pipeline
from src.weaviate_init import init_weaviate_client

dotenv.load_dotenv()

class RAGQueryEngine:
    def __init__(self, verbose=True):
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_APIKEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pipeline = Pipeline(init_weaviate_client())
        self.verbose = verbose
        
    def query(self, topic: str, num_articles: int = 15, model: str = "mistral") -> tuple[str, str]:
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
{article.subheading} {article.url}

{article.article_full}
------
"""
        prompt += (f"Please summarize the relevant news to the topic: {topic} as bullets. One article should be at most one bullet point. If two articles are related, they can be in the same bullet point. If there are multiple relevant stories to the topic then there should be multiple bullets. "
                   "Each bullet point should start with a bold mini-headline (<b>Mini headline</b>) followed by 2-4 sentences explaining the story. Separate bullets by a new line (backslash n). "
                   "Do not output any other text besides the bullet points. Write in the style of the economist's 'The world in brief' newsletter."
                   "Behind each bullet point, write the source of the information and a link to the article as anchor tag. Use HTML NOT Markdown. If there are multiple sources to a bullet link to both: ({News outlet}: {Article headline 1}, {News outlet (if different from first one)}: {Article headline 2}). Include the parentheses around the links. "
                   "The mini-headline should be 5-8 words and capture the key point. Make it attention-grabbing but factual.")

        if self.verbose:
            print(f"""### DEBUG ####\n\n{prompt}\n\n### ###""")

        # 3. Get response from selected model
        if model == "mistral":
            messages = [
                UserMessage(content=prompt)
            ]
            
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=messages, # type: ignore
            )
            content = response.choices[0].message.content # type: ignore
        else:  # OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                # response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
        
        hero_image_url = articles[0].hero_image_url or ""  # Fallback to empty string if None
        content = content or ""  # Fallback to empty string if None
        return hero_image_url, content


if __name__ == "__main__":
    # Example usage
    rag = RAGQueryEngine()
    
    topic = "Greenland"
    
    # Fixed the string formatting
    # question = f"What do articles about {topic} report about?"
    
    # print("Querying with Mistral:")
    # mistral_answer = rag.query(topic, model="mistral")
    # pprint(mistral_answer)
    
    print("\nQuerying with OpenAI:")
    openai_answer = rag.query(topic, model="openai")
    pprint(openai_answer)
    
    rag.pipeline.client.close()
