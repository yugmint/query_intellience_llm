import os
import json
from langchain.chat_models import init_chat_model
from src.config import MODEL_NAME

def load_api_key():
    with open("cred.json") as f:
        data = json.load(f)
        os.environ["GROQ_API_KEY"] = data["grok_api_key"]

def get_llm():
    load_api_key()
    return init_chat_model(MODEL_NAME, model_provider="groq")