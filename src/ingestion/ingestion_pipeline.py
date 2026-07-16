# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS

# from src.retrieval.embeddings import get_embeddings
# from src.retrieval.config import FAISS_PATH


# def build_vector_db(file_path: str):
#     print("🔄 Loading document...")
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()

#     print(f"Loaded {len(documents)} pages")

#     print("✂️ Splitting into chunks...")
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=100
#     )
#     chunks = splitter.split_documents(documents)

#     print(f"Created {len(chunks)} chunks")

#     print("🧠 Creating embeddings...")
#     embeddings = get_embeddings()

#     print("📦 Building FAISS index...")
#     vectorstore = FAISS.from_documents(chunks, embeddings)

#     vectorstore.save_local(FAISS_PATH)

#     print("✅ FAISS index created and saved!")


# if __name__ == "__main__":
#     path = input("Enter the path to your PDF file: ")
#     build_vector_db(path)