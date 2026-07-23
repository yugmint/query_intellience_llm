# 02 — RAG Best Practices

Domain-specific practices for building/maintaining a retrieval-augmented
generation system — grounded in decisions already made in this codebase,
including a couple of gaps found while documenting it, not generic advice.

## Retrieval

- **Don't retrieve for every query.** Classifying intent first
  (`nodes/intent.py`) and only running `retrieve → generate` on the
  `knowledge` branch avoids wasting a similarity search — and avoids
  irrelevant context leaking into a greeting/chit-chat response — on
  queries that were never going to need document context.
- **Top-k alone is a blunt instrument.** `retriever.py` uses a fixed
  `k=3` similarity search with no score threshold — every query gets
  exactly 3 chunks forced into context, even if none of them are actually
  relevant. A similarity-score cutoff (drop matches below some threshold,
  even if that leaves fewer than k) is usually a better default than always
  filling k slots. Worth adding before/alongside reranking (§05-roadmap.md).
- **Know exactly which index you're querying before debugging retrieval
  logic.** This repo's own `FAISS_INDEX_PATH` currently points at the
  oldest, smallest index on disk, not the most recently built one (see §8
  of `DOCUMENTATION.md`) — a "the model gave a bad answer" symptom that
  isn't a prompt or retrieval-algorithm bug at all, just a stale-data bug
  wearing a different costume. Check index provenance before assuming the
  retrieval code is wrong.

## Grounding & prompting

- **Explicitly instruct the model to admit when it doesn't know**, and test
  that it actually does. `build_generation_prompt` already says "answer
  only from context... say 'I don't know.' if absent" — the
  `out_of_context` category in `workflow_test_suite.json` exists to catch a
  regression in this specific behavior. Treat that category's pass rate as
  a real signal, not decoration.
- **Never let the model reveal that it was given retrieved context or
  reasoning steps** — this is already in the prompt; watch for regressions
  whenever the prompt is edited, since it's an easy line to accidentally
  drop while "improving" the prompt for something else.
- **Keep generation prompts centralized, not scattered per node.**
  `src/prompts/generation.py` is the one place the knowledge-answer prompt
  lives — but `generate_conversation.py` currently has its own inline
  prompt instead. That's a real inconsistency worth fixing (move it into
  `src/prompts/`) before adding a third or fourth prompt somewhere else;
  scattered prompts are much harder to audit or version than centralized
  ones.

## Guardrails

- **Order matters between reject-capable and mutating validators.**
  `EmptyQueryValidator`/`LengthValidator`/`PromptInjectionValidator` run
  before `CharacterValidator`/`QueryNormalizer` specifically so a query
  that should be rejected isn't first silently cleaned up into something
  that passes. If you add a validator, decide deliberately where in the
  chain it belongs — don't just append it.
- **Fail closed on genuinely adversarial input, fail open on ambiguous
  input.** The prompt-injection validator blocks specific known patterns
  rather than trying to be maximally aggressive — a guardrail that's too
  eager to reject legitimate questions is its own kind of failure, just a
  quieter one (it shows up as "the bot is annoyingly unhelpful," not as an
  incident).
- **Keep guardrail decisions observable.** `guardrail_reason` flows into
  the rejection response and into logs — when you add a new validator,
  make sure its rejection reason is just as specific, not a generic
  "invalid query."

## Conversation memory

- **Decide session/user scoping before going multi-user — don't let it
  default silently to global.** Right now `RAGResources.memory` is one
  shared history for the entire process; every concurrent user on the API
  currently reads and writes the same conversation. This is fine for a
  single-user demo and a real correctness bug the moment there's more than
  one concurrent user. Flagged as a hard blocker in `05-roadmap.md`, not a
  nice-to-have.
- **Unbounded memory growth is a latent bug, not just an inefficiency.**
  There's currently no truncation/summarization of `InMemoryChatMessageHistory`
  — a long-running conversation will eventually exceed the LLM's context
  window. Worth a cap or summarization strategy before conversations are
  expected to run long.

## Evaluation-driven iteration

- **Don't tune prompts or retrieval settings "by feel."** Run
  `python -m src.evaluation.runner` before and after a change and diff the
  resulting CSV against the previous one in `src/evaluation/results/` —
  this repo already has the harness; the discipline is using it as a gate
  on every retrieval/prompt/guardrail change, not just running it
  occasionally as a report.
- **Cover adversarial and edge categories, not just the happy path.**
  `workflow_test_suite.json` already includes guardrail/injection/
  out-of-context/rewrite categories alongside plain knowledge questions —
  keep growing this set every time a real failure surfaces in dev or
  production, so it doesn't reappear silently later.

## Latency & cost awareness

- **Gate expensive calls behind cheap heuristics wherever possible.**
  `QueryRewriter._needs_rewrite()` — skip the LLM rewrite call unless chat
  history exists *and* the query has a pronoun/reference token — is the
  model to follow for future features like reranking: don't call an
  LLM/cross-encoder on every single query if a cheap check can filter out
  most of the cases that don't need it.
- **Build shared resources once, not per request.** `RAGResources` (llm,
  embeddings, vectorstore, retriever) is built once in `RAGService.__init__`
  and reused across every query — keep this pattern for any new expensive
  resource; constructing it per-request would silently reintroduce the
  latency this design already avoided.

## Observability

- **Log enough structured fields per turn to debug a bad answer after the
  fact**, not just "request received" / "response sent": intent, whether
  retrieval fired, context length, retrieved doc sources, latency per node.
  `@log_node` plus the evaluation CSVs already capture much of this —
  keep it consistent as new nodes are added, since inconsistent logging
  across nodes is what makes debugging a specific bad answer painful later.

## Index freshness

- **A RAG system is only as good as the index it's reading.** Before
  debugging "the model gave a bad/outdated answer" as a prompt or
  retrieval-logic problem, confirm which index is actually live and how it
  was built — see the ingestion-freshness note above and §8 of
  `DOCUMENTATION.md`. This is the single most likely root cause of
  "retrieval quality regressed" reports on this specific project right now.
