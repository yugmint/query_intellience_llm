# Intelligent Document AI

> A production-ready **Document Intelligence System** built with **LangGraph**, **LangChain**, and **FAISS** for intelligent document understanding, contextual retrieval, and conversational AI.

---

# Overview

Intelligent Document AI is designed to move beyond traditional Retrieval-Augmented Generation (RAG) systems by introducing an intelligent workflow layer capable of understanding user intent, validating requests, routing conversations, and retrieving the most relevant document context before generating responses.

The project follows a modular architecture where every stage of the workflow is isolated into reusable components, making it easy to extend, maintain, and scale.

Current implementation focuses on:

* Production-ready LangGraph workflow
* Modular node architecture
* Input Guardrails
* Intent Detection
* Conversational AI
* Contextual Retrieval
* Evaluation Framework
* Structured Logging
* GPU Accelerated Embeddings

The long-term goal is to evolve this project into a complete enterprise-grade Document Intelligence Platform.

---

# Features

## Current Features

* LangGraph Workflow Engine
* Modular Node Architecture
* FAISS Vector Database
* HuggingFace Embeddings
* Groq LLM Integration
* Conversation Memory
* Intent Detection
* Knowledge & Conversation Routing
* Input Guardrails
* Query Normalization
* Structured Logging
* Evaluation Pipeline
* GPU Support (CUDA)
* Production Ready Folder Structure

---

# Technology Stack

| Category        | Technology                             |
| --------------- | -------------------------------------- |
| Workflow        | LangGraph                              |
| LLM Framework   | LangChain                              |
| Embeddings      | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Database | FAISS                                  |
| LLM             | Groq                                   |
| Language        | Python                                 |
| Logging         | Python Logging                         |
| Evaluation      | Custom Evaluation Framework            |
| Hardware        | CUDA / CPU                             |

---

# High-Level Architecture

```text
                        User
                          │
                          ▼
                 Input Guardrails
                          │
                          ▼
                 Intent Detection
                  ┌────────┴────────┐
                  ▼                 ▼
          Knowledge Query    Conversation Query
                  │                 │
                  ▼                 ▼
          Document Retrieval      LLM
                  │
                  ▼
           Context Generation
                  │
                  ▼
           Response Generation
                  │
                  ▼
          Conversation Memory
                  │
                  ▼
                 Response
```

---

# LangGraph Workflow

```text
                    START
                      │
                      ▼
             Input Guardrail
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
 Guardrail Response           Intent Detection
         │                         │
         ▼                         ▼
        END                 Knowledge ?
                             ┌──────┴──────┐
                             ▼             ▼
                      Retrieve Context  Conversation
                             │             │
                             ▼             ▼
                      Generate Answer      │
                             │             │
                             └──────┬──────┘
                                    ▼
                              Update Memory
                                    │
                                    ▼
                                   END
```

---

# Current Directory Structure

```text
src/
│
├── evaluation/
│   ├── dataset/
│   ├── results/
│   ├── models.py
│   └── runner.py
│
├── guardrails/
│   ├── base.py
│   ├── input_guardrail.py
│   └── validators/
│       ├── empty_query.py
│       ├── length.py
│       ├── prompt_injection.py
│       ├── character.py
│       └── normalizer.py
│
├── prompts/
│   ├── generation.py
│   └── conversation.py
│
├── retrieval/
│   ├── config.py
│   ├── embeddings.py
│   ├── llm.py
│   ├── memory.py
│   ├── retriever.py
│   └── vectorstore.py
│
├── services/
│   └── rag_service.py
│
├── utils/
│   ├── decorators.py
│   └── logger.py
│
├── workflow/
│   ├── nodes/
│   │   ├── input_guardrail.py
│   │   ├── guardrail_response.py
│   │   ├── intent.py
│   │   ├── retrieve_context.py
│   │   ├── generate_knowledge.py
│   │   ├── generate_conversation.py
│   │   └── update_memory.py
│   │
│   ├── resources.py
│   ├── state.py
│   └── workflow.py
│
└── main.py
```

---

# Workflow Nodes

### Input Guardrail

Validates every incoming request before it enters the system.

Validators include:

* Empty Query Validation
* Length Validation
* Prompt Injection Detection
* Character Validation
* Query Normalization

---

### Intent Detection

Classifies the request into:

* Knowledge
* Greeting
* Chit Chat

This determines the execution path inside LangGraph.

---

### Retrieve Context

Responsible for

* Embedding Query
* FAISS Similarity Search
* Context Construction

---

### Generate Knowledge

Generates grounded answers using retrieved document context.

---

### Generate Conversation

Handles greetings and general conversational responses without document retrieval.

---

### Update Memory

Maintains conversation history for contextual interactions.

---

# Evaluation Framework

The project includes a custom evaluation framework capable of testing the complete workflow.

Current evaluation categories include:

* Knowledge Questions
* Greetings
* Chit Chat
* Out-of-Context Queries
* Empty Queries
* Whitespace Queries
* Prompt Injection
* Long Queries
* Query Normalization
* Rewrite Tests

Each evaluation records:

* Response
* Intent
* Latency
* Success Status
* Metadata

Results are automatically exported as CSV reports.

---

# Input Guardrails

Current Guardrails include:

* Empty Query Validator
* Length Validator
* Prompt Injection Validator
* Character Validator
* Query Normalizer

Future Guardrails:

* PII Detection
* Toxicity Detection
* Language Detection
* Sensitive Information Detection
* Role Validation

---

# Logging

Every workflow node provides structured logs including:

* Node Start
* Node Completion
* Execution Time
* Retrieval Statistics
* Intent Detection
* Context Length
* Guardrail Results

This significantly improves debugging and production observability.

---

# GPU Support

The embedding model automatically detects the available hardware.

Priority:

```text
CUDA GPU
    ↓
CPU
```

Tested on:

* NVIDIA GTX 1650
* CUDA 12.x
* PyTorch CUDA Build

---

# Current Project Status

## Completed

* Modular Project Structure
* LangGraph Workflow
* GPU Accelerated Embeddings
* Intent Classification
* Knowledge Routing
* Conversation Routing
* Input Guardrails
* Conversation Memory
* Evaluation Framework
* Structured Logging
* Production Resource Management

---

## Phase 2 — Intelligence Layer (In Progress)

* Query Rewriting
* Metadata-aware Retrieval
* Reranking
* Better Chunk Selection

---

## Phase 3 — Advanced Retrieval

* Hybrid Search
* BM25 + Dense Retrieval
* Metadata Filtering
* Parent-Child Retrieval
* Context Compression

---

## Phase 4 — Enterprise Features

* Source Citations
* Streaming Responses
* Multi-document Retrieval
* Observability
* Metrics Dashboard
* API Authentication
* Rate Limiting

---

## Phase 5 — Agentic Intelligence

* Multi-Agent Workflow
* Document Planning
* Tool Calling
* SQL + Document Routing
* Web Search Integration
* Autonomous Research

---

# Running the Project

## Clone Repository

```bash
git clone "https://github.com/yugmint/query_intellience_llm.git"

cd Intelligent-Document-AI
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Credentials

Create a `cred.json` file:

```json
{
    "grok_api_key": "YOUR_GROQ_API_KEY"
}
```

---

## Run Application

```bash
python main.py
```

---

## Run Evaluation

```bash
python -m src.evaluation.runner
```

Evaluation reports will be generated under:

```text
src/evaluation/results/
```

---

# Future Roadmap

```text
Phase 1
Production RAG Workflow
✔ Completed

Phase 2
Intelligence Layer
⏳ In Progress

Phase 3
Advanced Retrieval

Phase 4
Enterprise Features

Phase 5
Agentic AI Platform
```

---

# Design Philosophy

The architecture follows a modular design where each component has a single responsibility.

* Guardrails validate requests.
* Workflow nodes orchestrate execution.
* Retrieval components manage document search.
* Services coordinate application logic.
* Evaluation continuously validates system performance.

This separation of concerns enables maintainability, extensibility, and production scalability.

---

# License

This project is intended for educational, research, and production experimentation purposes. Licensing can be updated based on deployment requirements.
