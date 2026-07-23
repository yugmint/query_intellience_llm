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

`tests/` (added 2026-07-24) currently covers the guardrail layer only —
`test_guardrail_validators.py` (each of the 5 validators in isolation) and
`test_input_guardrail.py` (chain ordering and short-circuit behavior). Pure
functions, no LLM/FAISS needed, fast enough to run on every change. One test
is an intentional `pytest.mark.xfail(strict=True)` documenting a real,
unfixed prompt-injection bypass (see `05-roadmap.md`) — if it ever starts
passing, that's a signal the bypass got fixed and the `xfail` should come
off, not a flake to ignore.

Individual workflow nodes (intent, retrieve, generate, process_query,
update_memory) still have no unit tests — the only thing exercising them is
`src/evaluation/runner.py` against
`src/evaluation/datasets/workflow_test_suite.json`, which runs the full
compiled workflow end to end (guardrails, intent routing, retrieval,
generation) and records latency/success per case, not unit-level
assertions. Treat a new category added to `workflow_test_suite.json` as the
way to pin down a node-level behavior you care about until real unit tests
exist for that node — see `05-roadmap.md`.

## Working on the workflow graph

- Node functions live in `src/workflow/nodes/`, one file per node, each
  taking `(state, resources)` and returning a partial state update.
- Routing logic (`route_guardrail`, `route_by_intent`) lives directly in
  `workflow.py` next to `build_workflow` — keep new conditional routing
  there rather than scattering `if` branches inside node functions.
- `RAGState` (`state.py`) is the contract every node reads/writes against.
  Note: it declares `retrieved_documents`/`reranked_documents`, but
  `retrieve_context.py` currently writes to `documents` instead — a known
  drift, not intentional design (see `07-design-decisions.md`). If you touch
  retrieval, reconcile this rather than adding a third key.

## Docker

```bash
docker build -t rag-api .
docker run -p 8001:8001 -e GROQ_API_KEY=... -v $(pwd)/data:/data rag-api
```

See the top-level `docker-compose.yml` (one directory up, alongside
`ingestion_fixed/`) to run this together with the ingestion API against a
shared volume. Bootstrap order matters — see that file's comments.
