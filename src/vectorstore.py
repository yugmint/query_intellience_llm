from langchain_community.vectorstores import FAISS
from src.embeddings import get_embeddings
from src.config import FAISS_PATH

def load_vectorstore():
    embeddings = get_embeddings()
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )