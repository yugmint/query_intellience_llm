from src.services.rag_services import RAGService


def main():

    rag = RAGService()

    print("=" * 60)
    print("Production RAG System")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:

        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        answer = rag.ask(query)

        print(f"\nAssistant: {answer}")


if __name__ == "__main__":
    main()