from langchain_community.vectorstores import FAISS
from src.retrieval.embeddings import get_embeddings
from src.retrieval.config import FAISS_PATH

def load_vectorstore():
    embeddings = get_embeddings()
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )