# 06 — Release Notes

No git tags exist yet (see `04-contributing.md`'s Git hygiene section). Organized by commit
and grouped into the same phases as §10 of `DOCUMENTATION.md`. Once a phase
boundary is tagged, switch this file to standard
[Keep a Changelog](https://keepachangelog.com/) format anchored on tags.

## Unreleased (working tree, not yet committed)

**Prod-readiness pass (2026-07-24)** — a direct answer to "is this
prod-level yet" (no) turned into four fixes, two of which uncovered bigger
pre-existing bugs than expected:

- **Fixed the stale-index problem for real, not just cosmetically.**
  Rebuilt the FAISS index with the current `ingestion_fixed` pipeline
  rather than repointing at the newer-looking `vectorstore/` build, which
  turned out to have the exact pre-fix chunking/metadata bugs
  `ingestion_fixed` exists to fix (confirmed by direct `index.pkl`
  inspection: avg 64-char chunks, `document_type: 'pdf'` everywhere). Old
  index directories renamed to `*.stale-*` rather than deleted. Full story
  in §8 of `DOCUMENTATION.md`.
- **Per-session conversation memory** — `RAGResources` no longer holds
  `memory`; it's now keyed by `session_id` in `RAGService` and carried
  through `RAGState["session_memory"]` per request. Uncovered a much bigger
  bug while fixing this: `chat_history` was hardcoded to `""` on every call
  and never actually populated from memory — conversation context had
  **zero effect** on behavior before this fix, in any session configuration.
  `src/utils/chat_history.py::format_chat_history` existed but was never
  called from the live workflow. Verified fixed end-to-end. See §12 of
  `DOCUMENTATION.md`.
- **Basic API key auth** on `/query`, `/reload`, `/reset-memory` (and
  `ingestion_fixed`'s `/ingest`) — `X-API-Key` header against
  `RAG_API_KEY`/`INGESTION_API_KEY`. Minimal (no rotation, no rate
  limiting) but real; verified 401 without/with-wrong key, 200 with the
  right one.
- **Fixed a `StateGraph` node/state-key collision** (`"intent"` used as
  both a node id and a state field) that made the graph fail to even
  *build* under the `langgraph` version actually installed here — see
  `05-roadmap.md` for why this suggests the workflow may never have run
  successfully in this exact dependency configuration before.
- `requirements.txt` — `langgraph` pinned to `0.2.76` (previously
  unpinned/missing; `>=0.3` conflicts with this project's `langchain-core`
  pin); `fastapi`/`uvicorn` corrected to the versions actually verified
  working (`0.139.2`/`0.51.0`).
- `src/api.py` — FastAPI service (`GET /health`, `POST /query`,
  `POST /reload`, `POST /reset-memory`), now with auth + session support.
- `RAGService.reload_index()` — in-place FAISS reload without a process
  restart.
- `src/retrieval/config.py` — `FAISS_PATH` now reads `FAISS_INDEX_PATH` env
  var instead of being hardcoded.
- `src/retrieval/llm.py` — `LLMFactory` now accepts `GROQ_API_KEY` from the
  environment directly, without requiring `cred.json` (needed for
  container deployment — `cred.json` is gitignored and holds a secret).
- `Dockerfile` — new (none existed before).
- `DOCUMENTATION.md`, `docs/` — this documentation set.

## `aa19c6c` (2026-07-24) — Remove in-tree ingestion pipeline

Committed the `src/ingestion/` deletion (16 files) and
`test/cuda_test.py`/`test/exp_notebook.ipynb` that had sat uncommitted for a
while — see `04-contributing.md`'s Git hygiene section for why that was a
problem in its own right. `git log` and the working tree now agree that
this repo has no ingestion code.

## 2026-07-16 — New ingestion pipeline (later removed from this repo)

- `5e12446` (HEAD as of last commit) — Added a full modular ingestion
  package under `src/ingestion/` (loaders, cleaners, chunkers, embedders,
  indexers, metadata) plus validation/benchmark scripts, and landed query
  rewriting (`src/processing/query_rewriter.py`,
  `src/workflow/nodes/process_query.py`) in the same commit. This ingestion
  code was later removed from the working tree (see Unreleased, above) and
  spun off into the standalone `ingestion_fixed` project — see §8 of
  `DOCUMENTATION.md` for the full history.

## 2026-07-15 — Guardrails + full modular LangGraph workflow (Phase 1 complete)

- `bd797f6` — README updated to mark Phase 1 (production RAG workflow)
  complete. Natural tag point that was never tagged.
- `dbcc9fd` — **feat:** modular LangGraph workflow with input guardrails —
  the node/routing architecture described in `01-architecture.md`, largely
  as it exists today.
- `27e969e` — Refactored factories, debugging improvements, CUDA support
  for the embedding model.

## 2026-07-14 — LangGraph hardening, testing, observability

- `b642bde` — Fixed intent node for greeting/chit-chat routing.
- `a65328c` — Logger function updated.
- `422151c` — Codebase cleanup.
- `1e5ed5d` — Added a test runner for unit testing and reporting (the
  ancestor of today's `src/evaluation/runner.py`).
- `c04f0c7` — Workflow updated for "LangGraph phase-1" (commit message has
  a typo — see `04-contributing.md`'s Git hygiene section).
- `34c4714` — `requirements.txt` updated alongside nodes/graph directory
  restructuring.

## 2026-07-08 — LangGraph foundation

- `46137e0` — Merge remote changes.
- `9719177` — Added LangGraph foundation: shared `RAGState` and
  `RAGResources` container — the point where this stopped being a single
  `RAGPipeline` class (`rag_pipeline_archived.py` — dead code by this point;
  removed entirely in the 2026-07-24 cleanup pass, recoverable via git
  history if ever needed) and became a graph of nodes.

## 2026-05-07 — Ingestion/retrieval split, iterative hardening (pre-LangGraph era)

- `cb1b1ee`, `5cd05ef`, `4ab18d5`, `74bd882`, `97bcde1`, `644b461`,
  `081367a` — reference fixes, `main.py` fixes, removing a redundant LLM
  call in intent classification, JSON-structured response format.
- `73c59e0` — "seperated the ingestion and retiveal pipelines" — flat `src/`
  reorganized into `src/ingestion/` (a placeholder, committed fully
  commented out — see `04-contributing.md`'s Git hygiene section) and
  `src/retrieval/` (the working LangChain pieces, still the retrieval
  layer's structure today).
- `0851534` — Resolved a `.gitignore` merge conflict.
- `552be68`, `eea561b` — README revisions, removed promotional content.
- `9b117d5` — `.gitignore` updated to ignore `cred.json` (before any secret
  had a chance to leak).
- `e5eef3f` — `venv_rag` ignored.
- `69f534a` — Initial commit.

## Documented but not in this repo's git history

The pre-`73c59e0` "monolithic script era" (a single flat `src/` with
`ingestion_pipeline.py` and `rag_pipeline.py`) isn't reconstructable from
`git log` — it predates or was squashed into the initial commit. It used to
be described in `local/project_history/README_v3.md`, an untracked local
file that was permanently deleted in a 2026-07-24 cleanup pass (not
git-recoverable — it was gitignored, never committed). What's written about
that era in `DOCUMENTATION.md` §1/§8 is a paraphrase from a reading of that
file earlier the same session, not a verbatim record.
