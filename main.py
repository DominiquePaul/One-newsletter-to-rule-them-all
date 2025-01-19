from embedding.rag_query import RAGQueryEngine

# Example usage
rag = RAGQueryEngine(verbose=False)

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



def create_and_send_newsletter():
    pass


if __name__ == "__main__":
    topics=["German politics", "European stock markets", "Machine learning, AI, Programming"]
    create_and_send_newsletter(topics=topics)