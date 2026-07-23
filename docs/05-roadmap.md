# 05 — Roadmap

The root `README.md` already lays out a 5-phase roadmap (Production RAG
Workflow → Intelligence Layer → Advanced Retrieval → Enterprise Features →
Agentic Intelligence). This page doesn't repeat that in full — it's the more
concrete, closer-in list: specific gaps found while documenting the current
codebase, in rough priority order. Current overall status: **pre-MVP**, per
project status — `ingestion_fixed` is considered done; this repo is still
actively changing.

## Now / next (fix before building more on top)

- [x] **Repoint `FAISS_INDEX_PATH` at a real, current index** — fixed
      2026-07-24. Turned out the "obvious" fix (point at the newer-looking
      `vectorstore/` build) would have made things worse — that build had
      the exact pre-fix chunking/metadata bugs `ingestion_fixed` was written
      to fix. Rebuilt with the current `ingestion_fixed` pipeline instead.
      Full story in §8 of `DOCUMENTATION.md`.
- [x] **Commit the uncommitted `src/ingestion` deletion** — done in
      `aa19c6c` (2026-07-24).
- [x] **Pin `langgraph` in `requirements.txt`** — pinned to `0.2.76`
      (2026-07-24); `>=0.3` conflicts with the rest of the `langchain-*`
      stack (`langchain-core<1.0.0` required by every other pin here).
- [ ] **Reconcile `RAGState`'s `retrieved_documents`/`reranked_documents`
      fields with what `retrieve_context.py` actually writes (`documents`)**
      — harmless today since nothing downstream reads the declared keys, but
      it means the state contract doesn't describe reality.
- [x] **Fixed a `StateGraph` node/state-key naming collision** discovered
      2026-07-24 while actually running the workflow for the first time in
      this dev environment (`langgraph` had never been installed here
      before — see the `langgraph` pin item above). The graph node named
      `"intent"` collided with `RAGState`'s `intent` field, which the
      installed `langgraph` version rejects outright at graph-build time.
      Renamed the node id to `"detect_intent"` in `workflow.py`; the state
      field and everything reading `state["intent"]` is untouched. Worth
      flagging: this means the current LangGraph workflow may not have been
      successfully executed end-to-end in *any* environment before this —
      worth double-checking whatever environment was previously used to
      generate the `src/evaluation/results/*.csv` files actually had a
      compatible `langgraph` version, not a coincidentally-different one.

## Intelligence layer (README Phase 2 — in progress)

- [x] Query rewriting — `QueryRewriter` / `process_query` node, landed
      alongside the (now-removed) modular ingestion pipeline in `5e12446`.
- [ ] Metadata-aware retrieval (filter by `document_type`, source, etc. —
      the ingestion side already attaches this metadata per chunk; nothing
      here queries on it yet).
- [ ] Reranking after initial FAISS retrieval.
- [ ] Better chunk selection / dedup at the `retrieve` node.

## Advanced retrieval (README Phase 3)

- [ ] Hybrid search (BM25 + dense).
- [ ] Parent-child retrieval, context compression.

## Multi-user / production readiness (not in README's phases, found during API work)

- [x] **Per-session conversation memory** — fixed 2026-07-24.
      `RAGService` now keys memory by `session_id`; the memory object flows
      through `RAGState["session_memory"]`, not `resources`, so concurrent
      requests for different sessions can't race on the same object. While
      fixing this, found and fixed a bigger, previously-hidden bug:
      `chat_history` was hardcoded to `""` on every call and never actually
      populated from memory, so conversation context had **zero effect** on
      query rewriting or generation regardless of session scoping. See §12
      of `DOCUMENTATION.md`. Still not a complete answer for real
      production scale: the session store is an in-memory dict, no
      persistence, no eviction/TTL — fine for moderate traffic, not for
      long-running high-volume multi-user use.
- [x] **Basic auth on `POST /query`, `/reload`, `/reset-memory`** (and on
      `ingestion_fixed`'s `POST /ingest`, since it shares a vector store with
      this API) — fixed 2026-07-24. Single shared-secret `X-API-Key` header
      checked against `RAG_API_KEY`/`INGESTION_API_KEY` env vars
      (`src/utils/auth.py`). Deliberately minimal: no per-client identity,
      no key rotation, **no rate limiting** — rate limiting is still
      outstanding and worth adding before any real external exposure.
- [ ] Auto-trigger `/reload` from the ingestion side after a successful
      `/ingest`, instead of requiring a manual call (see the shared
      `docker-compose.yml`'s comments — deliberately not built yet).
- [ ] Make `RAGService` tolerate "no index yet" at startup instead of
      crash-looping against an empty shared volume (see
      `docker-compose.yml` "BOOTSTRAP ORDER MATTERS" note).

## Enterprise features (README Phase 4)

- [ ] Source citations in generated answers.
- [ ] Streaming responses.
- [ ] Observability / metrics dashboard beyond the current structured logs
      and evaluation CSVs.

## Testing

- [x] **Unit tests for the guardrail validators** — added 2026-07-24,
      `tests/test_guardrail_validators.py` (per-validator) and
      `tests/test_input_guardrail.py` (chain ordering/short-circuit
      behavior), 22 passing + 1 intentional `xfail`. First `tests/` +
      `pyproject.toml`/pytest config this repo has ever had.
- [x] **Unit tests for individual workflow nodes** — added 2026-07-24.
      All 7 nodes covered (`intent`, `retrieve_context`, `generate_knowledge`,
      `generate_conversation`, `process_query`, `update_memory`,
      `input_guardrail`/`guardrail_response`), 56 tests total (with the
      guardrail-layer tests). `tests/conftest.py` provides `FakeLLM`/
      `FakeRetriever` (record calls, return scripted responses, no real
      network/FAISS call) and an autouse fixture resetting the
      `QueryRewriter` singleton between tests (it caches itself on the
      class, so tests would otherwise leak a stale `FakeLLM` into later
      ones). `update_memory` tests use the real `InMemoryChatMessageHistory`
      rather than a fake, since it's a plain in-process object with
      nothing worth mocking. Found and pinned down a real asymmetry while
      writing `test_node_generate_conversation.py`: on a JSON-parse
      failure, the node falls back to the original, un-stripped
      `response.content` rather than the fence-stripped `content` it just
      computed — cosmetic today, but now a change there won't happen
      silently.
      `src/evaluation/runner.py` remains the only thing exercising the
      *compiled graph* end to end; these are unit-level, not a replacement.
- [ ] **Fix the whitespace-based prompt-injection bypass** found while
      writing the guardrail tests: `PromptInjectionValidator` runs before
      `QueryNormalizer` in the chain, so `"ignore   previous   instructions"`
      (extra internal spaces) currently evades every pattern in `PATTERNS`
      entirely — pinned down by the `xfail`'d
      `test_extra_whitespace_bypasses_injection_detection`. Likely fix:
      match against a whitespace-collapsed copy of the query for detection
      purposes, without changing what actually reaches the LLM/normalizer
      order for other validators.

## Guardrails (README's own "Future Guardrails" list, unchanged)

- [ ] PII detection, toxicity detection, language detection, sensitive-info
      detection, role validation — none implemented yet; current guardrail
      chain is empty/length/character/prompt-injection/normalization only.

## Cleanup

- [ ] `openai` is listed in `requirements.txt` but no active code path uses
      it (Groq via `langchain-groq` is the actual LLM provider) — remove it
      unless there's a near-term plan to use it, to stop it looking like a
      real dependency.
