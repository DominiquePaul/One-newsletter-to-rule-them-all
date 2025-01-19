import os
from embedding.rag_query import RAGQueryEngine
from interface.mail import send_scandinavian_newsletter
from openai import OpenAI
from tqdm import tqdm

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Example usage
rag = RAGQueryEngine(verbose=True)

topics=["German politics", "Stock markets", "Machine learning, AI, Programming"]

image_url = None
news = {}
for topic in tqdm(topics, desc="Generating summaries"):
    image, bullets = rag.query(topic, model="openai")
    if image_url is None:
        image_url = image
    news[topic] = [bullet for bullet in bullets.split("\n") if bullet.strip()]

from pprint import pprint
pprint(news)

# Generate email subject from content
all_news = "\n".join([item for items in news.values() for item in items])
subject_prompt = f"""Write a compelling email subject line (max 10 words) that summarizes these key points:

{all_news}

The subject should help readers immediately grasp the key content. Format as a newspaper headline."""

subject_response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": subject_prompt}]
)
subject = subject_response.choices[0].message.content.strip('"')

send_scandinavian_newsletter(subject=subject, 
                             recipients=["dominique.paul.info@gmail.com"], 
                                        #  "york@schlabrendorff.de"], 
                             news_categories=news,
                             header_image_url=image_url)

rag.pipeline.client.close()
