import os

MODEL_NAME = "llama-3.1-8b-instant"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
TOP_K = 3
pdf_path = "data\Grandma's Bag of Stories by Sudha Murthy.pdf"  ## Paste your pdf path here
