
---

# 📚 RAG Chatbot (LangChain-Based)

A modular **Retrieval-Augmented Generation (RAG)** system built using LangChain, FAISS, and Groq.
This project enables document-based question answering with conversational memory and LLM-based intent routing.

---

## 🚀 Features

* 🔍 Semantic search using FAISS vector database
* 🧠 LLM-powered responses via Groq (LLaMA3)
* 💬 Conversational memory (multi-turn chat)
* 🧭 LLM-based intent classification (greeting, chit-chat, knowledge)
* 🧱 Modular architecture for scalability
* ⚡ Fully open-source + API-based hybrid setup

---

## 🏗️ Architecture

```text
User Query
   ↓
Intent Classifier (LLM)
   ↓
 ┌───────────────┬───────────────┐
 │ Chat Response │ RAG Pipeline  │
 ↓               ↓
Direct LLM      Retriever (FAISS)
                  ↓
              Context Injection
                  ↓
                 LLM
                  ↓
              Final Answer
```

---

## 📂 Project Structure

```bash
rag-project/
│── data/                 # Input documents (PDFs)
│── faiss_index/          # Stored vector database
│
│── src/
│    ├── config.py        # Configurations
│    ├── llm.py           # LLM initialization (Groq)
│    ├── embeddings.py    # Embedding model
│    ├── vectorstore.py   # FAISS loading
│    ├── retriever.py     # Retrieval logic
│    ├── intent_classifier.py
│    ├── memory.py        # Chat history
│    ├── rag_pipeline.py  # Core pipeline
│
│── main.py               # Entry point
│── cred.json             # API keys (ignored in Git)
```

---

## ⚙️ Tech Stack

* **Framework:** LangChain
* **Vector DB:** FAISS
* **Embeddings:** sentence-transformers
* **LLM API:** Groq
* **Language:** Python

---

## 🧪 Setup Instructions

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add API key

Create `cred.json`:

```json
{
  "grok_api_key": "your_api_key_here"
}
```

### 4. Run the system

```bash
python main.py
```

---

## 💡 Example Queries

* "What is this document about?"
* "Summarize the key points"
* "Hi"
* "Thanks"

---

## 🔥 Key Highlights

* Uses **LLM-based intent routing** instead of rule-based logic
* Supports **context-aware multi-turn conversations**
* Designed for **easy extension** (LangGraph, reranking, UI)

---

## 🚀 Future Improvements

* 📊 Add source citations
* 🔁 Implement reranking
* 🧠 LangGraph-based workflows
* 🌐 Streamlit UI
* 📚 Multi-document support

---

## 📌 Notes

* This project currently uses **LangChain-based orchestration**
* Designed as a **foundation for production-grade RAG systems**

---

