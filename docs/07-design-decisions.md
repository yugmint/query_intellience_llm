# 07 — Design Decisions

Short ADR-style entries: the decision, the alternative considered, and why
the chosen option won. Not exhaustive — only decisions that would confuse a
reader if left unexplained.

---

### LangGraph node graph instead of one `RAGPipeline` class

**Decision:** `src/workflow/` — a compiled `StateGraph` with one node per
concern (guardrail, intent, rewrite, retrieve, generate, memory), routed by
`route_guardrail`/`route_by_intent`.

**Alternative considered:** the earlier, actual approach —
`src/retrieval/rag_pipeline_archived.py`'s `RAGPipeline` class, doing
retrieval + a combined intent/response prompt + memory update inside one
`.query()` method. Was dead code, not imported anywhere, non-importable as-is;
removed from the repo in a 2026-07-24 cleanup pass (recoverable via git
history: `git show <pre-2026-07-24 commit>:src/retrieval/rag_pipeline_archived.py`).

**Why:** the single-method version couldn't express "greetings skip
retrieval entirely" or "guardrail rejection skips everything downstream"
without nested conditionals accumulating inside one function. A graph makes
those branches structural (edges in `workflow.py`) instead of buried in
`if` statements, and each node stays independently testable/loggable
(`@log_node` wraps every one). The cost is more files and more indirection
for a simple case — judged worth it once intent-based branching and
guardrail short-circuiting were both real requirements, which they weren't
in the pre-LangGraph era.

---

### An ordered, short-circuiting guardrail chain

**Decision:** `InputGuardrail` runs 5 validators in a fixed order
(`EmptyQueryValidator` → `LengthValidator` → `CharacterValidator` →
`PromptInjectionValidator` → `QueryNormalizer`), stopping at the first
rejection.

**Why order matters here:** character stripping and normalization *mutate*
the query rather than reject it, and they run after the reject-capable
checks — so a query that would be rejected for being empty/too-long isn't
first silently mutated into something that passes. Reordering these (e.g.
normalizing before length-checking) would change what actually gets
rejected. If you add a new validator, decide deliberately where in this
order it belongs — don't just append it.

**A real cost of this ordering, found and fixed 2026-07-24:**
`PromptInjectionValidator` running before `QueryNormalizer` meant pattern
matching happened against un-normalized whitespace — `"ignore   previous
  instructions"` (extra internal spaces) evaded every pattern entirely,
since the regexes expect single spaces. Fixed *without* reordering the
chain (reordering would've shifted `LengthValidator`'s behavior too, since
it also runs before normalization today, deliberately): `PromptInjectionValidator`
now matches against a whitespace-collapsed copy of the query internally,
without writing it back to `state["query"]` — normalizing the actual query
is still `QueryNormalizer`'s job. Covered by
`tests/test_guardrail_validators.py::test_extra_whitespace_no_longer_bypasses_injection_detection`.

---

### Vector store: FAISS on a shared volume, not an embedded client-server DB

**Decision:** `VectorStoreFactory.load()` reads a FAISS index from a local
path (`FAISS_INDEX_PATH`); nothing in this repo builds one. The separate
`ingestion_fixed` project builds it; the two are meant to share a mounted
volume in deployment.

**Alternative considered:** a real client-server vector database (Qdrant,
pgvector), which would support genuine concurrent read/write across two
independently deployed services.

**Why FAISS-on-disk for now:** this matches the actual current usage
pattern — ingestion runs periodically, retrieval reads whatever the last
successful ingestion produced. `RAGService.reload_index()` plus a manual
`POST /reload` (see `01-architecture.md`) is enough for that pattern without
adding a database server. This was an explicit, discussed tradeoff (see
prior conversation / `ingestion_fixed/docs/07-design-decisions.md`'s
matching entry) — not an oversight. It stops being enough the moment you
need real-time freshness or true concurrent writers; `vectorstore.py` and
`retriever.py` are the two files that would need to change if that happens.

---

### Intent-based routing instead of always retrieving

**Decision:** every query is classified (`intent` node) into
`knowledge`/`greeting`/`chit_chat` before deciding whether to retrieve at
all; only `knowledge` goes through `process_query → retrieve → generate`.

**Alternative considered:** always retrieve context and let the generation
prompt decide whether it's relevant.

**Why:** "hi" doesn't need a FAISS similarity search — retrieving anyway
wastes a call and risks pulling in irrelevant context that could leak into
a greeting response. The cost is an extra LLM call for classification on
every request (mitigated: `detect_intent` falls back to `"knowledge"` on
JSON-parse failure rather than blocking, so a classifier hiccup degrades to
"just try to answer" instead of failing the request).

---

### Query rewriting is conditionally triggered, not automatic

**Decision:** `QueryRewriter._needs_rewrite()` only calls the LLM to
rewrite a query if there's chat history **and** the query contains a
pronoun/reference token (`it`, `this`, `that`, `they`, ...). Otherwise the
original query is used for retrieval unchanged.

**Why:** rewriting exists to resolve references like "what about *that*?"
against prior turns — most queries aren't referential and gain nothing from
an extra LLM round-trip before retrieval even starts. The heuristic is
deliberately cheap and conservative (a false negative — skipping a rewrite
that would have helped — just falls back to normal retrieval; a false
positive costs one extra LLM call). Not meant to be a complete coreference
resolver, just a cost/latency-aware gate on one.

---

### `RAGResources` is a mutable dataclass, not frozen

**Decision:** `@dataclass(slots=True)`, not `frozen=True`.

**Why this matters, not just a style note:** every workflow node's lambda
closes over the *same* `RAGResources` instance by reference. Because it's
mutable, `RAGService.reload_index()` can swap `resources.vectorstore` and
`resources.retriever` in place after a fresh FAISS index is available, and
every already-compiled node picks up the change immediately — no graph
rebuild needed. This is what makes `POST /reload` (added for the standalone
API deployment) a cheap in-process operation instead of requiring a service
restart. If this were frozen, reload would require rebuilding the whole
compiled graph on every index refresh.

---

### `GROQ_API_KEY` from environment, with `cred.json` as a local-dev fallback

**Decision (recent):** `LLMFactory._load_api_key()` now checks
`os.environ.get("GROQ_API_KEY")` first and only falls back to reading
`cred.json` if it's unset.

**Why:** `cred.json` is gitignored and holds a real secret — appropriate for
local dev, inappropriate to bake into a container image or expect mounted
into every deployment target. This change was needed specifically to make
the standalone `Dockerfile`/API deployment (§12 of `DOCUMENTATION.md`)
possible without either committing a secret or requiring every deployment
to carry a JSON file — env vars are the more standard container-native path.
Local dev via `cred.json` is unaffected.

---

### `RAGState.documents`, not `retrieved_documents`/`reranked_documents`

**Decision (2026-07-24):** `state.py` declares a single `documents: list[Document]`
field for retrieval output.

**What it replaced:** the state used to declare both
`retrieved_documents` and `reranked_documents` — but `retrieve_context.py`
had always written to a `documents` key that wasn't declared at all.
Harmless at runtime (`RAGState` is a `TypedDict`, so Python doesn't enforce
it), but the declared contract didn't describe reality, and
`reranked_documents` was speculative — declared for a reranking feature
(roadmap v0.2.0) that doesn't exist yet.

**Why fix it this way, not the other way (rename the write site to match
the old declared field):** `documents` is the accurate, current name for
what the field holds today — pre-rerank retrieval output. Keeping
`retrieved_documents` around would have meant either leaving
`reranked_documents` as dead, aspirational declaration, or writing to it
from code that doesn't rerank anything yet. Neither is better than just
declaring what's actually true now and adding `reranked_documents` for
real when reranking is actually implemented — see the "don't design for
hypothetical future requirements" instinct elsewhere in this codebase
(e.g. `ingestion_fixed`'s `DocumentChunk`/`EmbeddingRecord` are the
one deliberate exception, and even those are called out explicitly as
such in their own docstrings).
