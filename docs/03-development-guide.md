# 03 — Development Guide

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

`requirements.txt` was missing `langgraph` entirely despite `workflow.py`
importing it directly — added (unpinned) as part of the API deployment work.
Pin it to whatever version you've actually developed against
(`pip show langgraph` in a working environment) before relying on this file
for a clean install. See §12 of `DOCUMENTATION.md`.

Create `cred.json` at the repo root for local dev (or set `GROQ_API_KEY`
directly — see `07-design-decisions.md` for why both paths exist now):

```json
{ "grok_api_key": "YOUR_GROQ_API_KEY" }
```

## You need a FAISS index before anything works

This repo has **no working ingestion code of its own** (see §8 of
`DOCUMENTATION.md` for why). `src/retrieval/vectorstore.py` only loads an
existing index from `FAISS_INDEX_PATH` (default `faiss_index/`). Before
`python main.py` or the API will do anything useful:

1. Use the sibling [`ingestion_fixed`](../../ingestion_fixed/DOCUMENTATION.md)
   project to build an index from your documents.
2. Point `FAISS_INDEX_PATH` (env var) or `src/retrieval/config.py`'s
   `FAISS_PATH` at the resulting directory.

Be aware there are currently **three different FAISS index directories** on
disk from different points in this project's history (`faiss_index/`,
`vectorstore/`, `src/vectorstore/`) — and the one actually wired up
(`faiss_index/`) is the oldest, smallest one. See §8 of `DOCUMENTATION.md`
for the full timeline before assuming retrieval quality issues are a code
bug rather than a stale-index problem.

## Running

```bash
python main.py                       # interactive CLI chat
uvicorn src.api:app --reload --port 8001   # HTTP API (added for standalone deployment)
python -m src.evaluation.runner      # evaluation suite -> src/evaluation/results/
```

## Tests

```bash
pytest tests/ -v
```

`tests/` (added 2026-07-24) covers the guardrail layer
(`test_guardrail_validators.py`, `test_input_guardrail.py`) and every
workflow node (`test_node_*.py`, one file per node) — 56 tests, all pure
unit tests, no real LLM/FAISS/network call. `conftest.py` has the shared
fakes:

- `FakeLLM` — stand-in for `resources.llm`; records every prompt, returns
  a scripted response (or raises, to test a failure path).
- `FakeRetriever` — stand-in for `resources.retriever`.
- an autouse fixture resetting the `QueryRewriter` singleton between
  tests — it caches itself on the class (`QueryRewriter._instance`), so
  without this a `FakeLLM` from one test would leak into every later test
  that touches `process_query`.

`update_memory` tests use the real `InMemoryChatMessageHistory` rather than
a fake — it's a plain in-process object, nothing worth mocking.

A whitespace-based prompt-injection bypass found while writing these tests
(tracked as an `xfail` initially) is now fixed — see `07-design-decisions.md`
for what it was and how it was fixed without reordering the guardrail chain.

`src/evaluation/runner.py` against
`src/evaluation/datasets/workflow_test_suite.json` remains the only thing
exercising the full *compiled graph* end to end (guardrails, intent
routing, retrieval, generation) with latency/success recorded per case —
unit tests catch "this node's logic broke," the eval harness catches
"answer quality regressed." Keep using both.

## Working on the workflow graph

- Node functions live in `src/workflow/nodes/`, one file per node, each
  taking `(state, resources)` and returning a partial state update.
- Routing logic (`route_guardrail`, `route_by_intent`) lives directly in
  `workflow.py` next to `build_workflow` — keep new conditional routing
  there rather than scattering `if` branches inside node functions.
- `RAGState` (`state.py`) is the contract every node reads/writes against
  — declares `documents: list[Document]` for retrieval results (fixed
  2026-07-24; used to declare `retrieved_documents`/`reranked_documents`,
  which no node ever wrote — see `07-design-decisions.md`). If you add
  reranking (roadmap v0.2.0), add a real `reranked_documents` field then,
  not speculatively ahead of the implementation.

## Docker

```bash
docker build -t rag-api .
docker run -p 8001:8001 -e GROQ_API_KEY=... -v $(pwd)/data:/data rag-api
```

See the top-level `docker-compose.yml` (one directory up, alongside
`ingestion_fixed/`) to run this together with the ingestion API against a
shared volume. Bootstrap order matters — see that file's comments.
