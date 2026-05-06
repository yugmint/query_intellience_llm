from src.memory import get_memory
from src.rag_pipeline import RAGPipeline

def main():
    memory = get_memory()
    rag = RAGPipeline(memory)

    print("RAG Chatbot Ready! Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        response = rag.query(query)
        print("Bot:", response)

if __name__ == "__main__":
    main()