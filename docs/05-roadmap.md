# 05 — Roadmap

Versioned by milestone (semver, pre-1.0 — `0.MINOR.0` for a meaningful
batch of work, `0.0.PATCH` for small fixes between them). First tag is
`v0.0.1`, not `v1.0.0`: unlike the sibling `ingestion_fixed` (already
considered stable, tagged `v1.0.0`), this repo is still actively changing
and hasn't earned a 1.0 claim yet. See `06-release-notes.md` for the
per-version changelog this file's "Shipped" sections are summarized from.

The root `README.md`'s 5-phase roadmap (Production RAG Workflow →
Intelligence Layer → Advanced Retrieval → Enterprise Features → Agentic
Intelligence) is the long-arc framing; the versions below are how that
actually gets delivered incrementally.

---

## v0.0.1 — Stable baseline (2026-07-24)

First tagged version. Everything here was broken, missing, or undocumented
before this session; all of it is now fixed and covered by tests.

**Shipped:**
- Fixed the stale FAISS index (was serving from a May-era build; the
  newer-looking alternative was actually worse — pre-fix chunking/metadata
  bugs). Rebuilt with the current `ingestion_fixed` pipeline.
  `FAISS_PATH` is now configurable via `FAISS_INDEX_PATH` instead of
  hardcoded.
- Per-session conversation memory, plus a much bigger bug found in the
  process: `chat_history` was hardcoded to `""` on every call and never
  actually populated from memory — conversation context had **zero
  effect** on behavior, in any session configuration, before this fix.
- Fixed a `StateGraph` node/state-key collision (`"intent"` used as both a
  node id and a state field) that made the graph fail to *build* under the
  `langgraph` version actually installed here — first time this workflow
  had been run end-to-end in this dev environment.
- Standalone FastAPI service (`src/api.py`) with `X-API-Key` auth,
  deployable alongside `ingestion_fixed`'s own API over a shared FAISS
  volume (see the top-level `docker-compose.yml`).
- Removed the in-tree ingestion pipeline for good (`aa19c6c`) — superseded
  by the standalone `ingestion_fixed` project.
- Full pytest suite: 57 tests — all 5 guardrail validators, the chain's
  ordering/short-circuit behavior, and all 7 workflow nodes, with fake
  LLM/retriever (no real network calls).
- Fixed a real security gap found while writing those tests: whitespace
  padding inside a blocked phrase (`"ignore   previous   instructions"`)
  was bypassing prompt-injection detection entirely.
- Full documentation set: `DOCUMENTATION.md` + numbered `docs/`
  (architecture, RAG-specific best practices, development guide,
  contributing, roadmap, release notes, design decisions).

**Known limitations carried into v0.1.0+** (not blockers for calling this
a stable baseline, just not yet done):
- Session memory has no persistence or eviction/TTL — an in-memory dict,
  fine for moderate traffic, not for long-running high-volume use.
- No rate limiting on the API.
- `openai` is listed in `requirements.txt` but nothing uses it (Groq via
  `langchain-groq` is the actual provider).

---

## v0.1.0 — Presentation & correctness polish (2026-07-24)

Small, high-leverage fixes to make what's already true legible — not new
features. All three shipped in the same session as `v0.0.1`.

- [x] A real example conversation/transcript in the README — captured
      live against `v0.0.1` (greeting → knowledge → pronoun follow-up →
      guardrail rejection), not hand-written. See "Proof It Works" in
      `README.md`.
- [x] Reconcile `RAGState`'s `retrieved_documents`/`reranked_documents`
      vs. what `retrieve_context.py` actually writes — renamed the
      declared field to `documents`. See `07-design-decisions.md`.
- [x] Removed the unused `openai` dependency — confirmed unreferenced
      anywhere in `src/` (Groq via `langchain-groq` is the actual provider).

## v0.2.0 — Intelligence layer (README Phase 2)

- [ ] Metadata-aware retrieval — filter by `document_type`, source, etc.
      The ingestion side already attaches this metadata per chunk;
      nothing here queries on it yet.
- [ ] Reranking after initial FAISS retrieval.
- [ ] Better chunk selection / dedup at the `retrieve` node. **Now backed
      by real evidence, not just intuition:** `docs/reports/2026-07-24-academic-document-e2e-test.md`
      found a 10-question Q&A suite against a dense technical PDF scored
      6/10 fully correct, with both failures caused by `k=3` top-k
      retrieval returning zero-diversity results (one question's top-3
      were all from the same page) that crowded out the actually relevant
      chunks. The report's §5 ruled out a competing explanation (chunk
      size from a document misclassification) via a controlled rerun —
      the same two questions failed identically with much smaller,
      more granular chunks — which narrows the cause down to the
      retrieval/ranking layer specifically, strengthening the case for
      these two items over a chunking-side fix.

(Query rewriting — `QueryRewriter` / `process_query` — already shipped,
landed in commit `5e12446`.)

## v0.3.0 — Advanced retrieval (README Phase 3)

- [ ] Hybrid search (BM25 + dense).
- [ ] Parent-child retrieval, context compression.

## v0.4.0 — Multi-user & production hardening

- [ ] Persistent, bounded session memory (replace the in-memory dict; cap
      or summarize long conversations).
- [ ] Rate limiting on the API.
- [ ] Auto-trigger `/reload` from the ingestion side after a successful
      `/ingest`, instead of requiring a manual call (see the shared
      `docker-compose.yml`'s comments — deliberately not built yet).
- [ ] Make `RAGService` tolerate "no index yet" at startup instead of
      crash-looping against an empty shared volume.

## v0.5.0 — Enterprise features (README Phase 4)

- [ ] Source citations in generated answers.
- [ ] Streaming responses.
- [ ] Observability / metrics dashboard beyond structured logs and
      evaluation CSVs.
- [ ] Expanded guardrails: PII detection, toxicity detection, language
      detection, sensitive-info detection, role validation (current chain
      is empty/length/character/prompt-injection/normalization only).

## Unscheduled

- [ ] CI (GitHub Actions): run `pytest tests/ -v` on every push.
- [ ] Agentic Intelligence (README Phase 5) — multi-agent, tool calling,
      web search. Deliberately not scheduled into a version yet; too far
      out to commit to a shape.
