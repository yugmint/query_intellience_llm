# 04 — Contributing

Single-contributor project today. Written for future-you or a future
collaborator, not as if there's already a team.

## Before opening a PR / making a change

1. **Run the evaluation suite** (`python -m src.evaluation.runner`) if you
   touched guardrails, intent detection, retrieval, or generation — it's
   currently the only thing exercising the full compiled workflow, across
   the categories in `src/evaluation/datasets/workflow_test_suite.json`
   (knowledge, greeting, chit_chat, guardrail_*, normalization,
   out_of_context, rewrite). Compare the new CSV in
   `src/evaluation/results/` against a recent prior run before assuming
   nothing regressed.
2. **Commit working-tree state deliberately**, including deletions — see
   "Git hygiene" below. Don't leave `src/ingestion` (or whatever you're
   removing next) in a deleted-but-uncommitted state.
3. **If you're changing what the vector index consumers expect**
   (`FAISS_INDEX_PATH`, chunk metadata shape), check both this repo and
   `ingestion_fixed` — they're separate repos, but the contract between
   them (a FAISS index at a shared path) is real and not enforced by either
   codebase automatically.

## Scope discipline

This repo is retrieval + generation + orchestration. It is **not** where
ingestion logic lives anymore (see §8 of `DOCUMENTATION.md`) — if you find
yourself writing a PDF loader or a chunker here, that almost certainly
belongs in `ingestion_fixed` instead, not a reintroduction of the pattern
that was already spun out once.

Per the current phased roadmap (`README.md`, `05-roadmap.md`): this repo is
still pre-MVP. Don't block a working change on making it "enterprise-ready"
(auth, rate limiting, citations) — those are explicitly later phases, not
missing requirements for every PR.

## Code style

- Node functions: `(state, resources) -> partial state dict`, wrapped with
  `@log_node(...)` from `src/utils/decorators.py`.
- Singletons/factories follow the existing `XFactory.get()` /
  `XFactory.build()` pattern (`EmbeddingFactory`, `LLMFactory`,
  `RetrieverFactory`, `VectorStoreFactory`) — match it for new resource
  types rather than introducing a different construction style.
- Logging via `src.utils.logger.logger`, not `print()`.
- No linter/formatter currently enforced. Match existing style over
  introducing a new one mid-file.

## Git hygiene

Concrete lessons from this repo's own history — not abstract advice:

- **A large chunk of work is currently uncommitted, including deletions.**
  16 files under `src/ingestion/` were deleted from the working tree after
  being committed in `5e12446`, but that removal was never committed —
  `git log` and the actual working tree currently disagree about whether
  this repo has ingestion code. Commit deletions as deliberately as
  additions: `git add -u src/ingestion test/cuda_test.py test/exp_notebook.ipynb`.
- **`73c59e0` committed a fully commented-out placeholder file** as if it
  were a real deliverable. If something's a sketch, don't commit it as
  working code — mark it with a `# TODO` and a tracking note instead.
- **Commit messages have typos that break `git log --grep` searches** —
  "seperated"/"retiveal" (`73c59e0`), "langgrapgh" (`c04f0c7`). Proofread
  library/concept names specifically, since those are exactly what you'll
  search for later.
- **Author identity is split** between `Yugendra` and `Yugendra Salunke` —
  standardize `git config user.name` so `git shortlog`/`git log --author`
  searches don't split across two identities.
- **No tags exist**, despite the README declaring "Phase 1 completion" —
  tag phase boundaries as they happen
  (`git tag -a v0.1.0-phase1 -m "..."`).

One commit per logical change, a message that says *why* if it's not
obvious from the diff, and commit deletions as deliberately as additions.
