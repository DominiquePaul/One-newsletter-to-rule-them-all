import os
from typing import List
import dotenv
from mistralai import Mistral, UserMessage
from embedding.pipeline import Pipeline
from weaviate_init import init_weaviate_client

dotenv.load_dotenv()

class RAGQueryEngine:
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_APIKEY"))
        self.pipeline = Pipeline(init_weaviate_client())
        
    def query(self, topic: str, user_question: str, num_chunks: int = 5) -> str:
        # 1. Retrieve relevant chunks from Weaviate
        chunks = self.pipeline.retrieve_articles(
            topics=[topic],
            top_k=num_chunks
        )
        
        # 2. Format context from retrieved chunks
        context = "\n\n".join([chunk.properties["content"] for chunk in chunks])
        
        # 3. Create prompt with context
        prompt = f"""You are presented with news snippets. Based on the following context, please answer the question. 
        If the answer cannot be found in the context, say so.

        Context:
        {context}

        Question: {user_question}"""
        
        # 4. Get response from Mistral
        messages = [
            UserMessage(content=prompt)
        ]
        
        response = self.mistral_client.chat.complete(
            model="mistral-medium",
            messages=messages
        )
        
        return response.choices[0].message.content


if __name__ == "__main__":
    # Example usage
    rag = RAGQueryEngine()
    
    topic = "Donald Trump"
    # Fixed the string formatting
    question = f"What do articles about {topic} report about?"
    
    print("Querying with Mistral:")
    mistral_answer = rag.query(topic, question)
    print(mistral_answer)
    
    