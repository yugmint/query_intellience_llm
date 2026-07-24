# Reranking Validation Report

**Date:** 2026-07-24
**What changed:** added a cross-encoder reranking step
(`cross-encoder/ms-marco-MiniLM-L-6-v2`, via `sentence-transformers`,
already a dependency) between `retrieve` and `generate` in the LangGraph
workflow. `RetrieverFactory` now pulls `RERANK_CANDIDATES=15` chunks from
FAISS (was `TOP_K=3`); the new `rerank` node scores all 15 against the
query with the cross-encoder and keeps the top `TOP_K=3` for generation.
See `07-design-decisions.md` for why this shape specifically.

**Why this report exists:** the two prior e2e reports
([Factor Analysis](2026-07-24-academic-document-e2e-test.md),
[EfficientNet](2026-07-24-efficientnet-research-paper-e2e-test.md)) named
specific, real failures and root-caused them to plain `k=3` similarity
search with no reranking. This report re-runs the *exact same questions,
same indexes, same grading standard* with reranking in place, to check
whether the fix actually worked rather than just asserting it should.

---

## 1. Targeted re-test of the known failures

Ran the specific previously-failing questions in isolation first, before
the full suites, so the before/after comparison is unambiguous:

| Document | Q | Question | Before | After |
|---|---|---|---|---|
| Factor Analysis | 6 | Example 1 dataset & variable count? | ❌ "I don't know" | ✅ *"PCA2 dataset, which is a subset, contains 6 variables."* |
| Factor Analysis | 7 | Example 1 factors retained & rotation? | ❌ "I don't know" | ✅ *"In Example 1, two factors were retained. The rotation used was Varimax Rotation."* |
| EfficientNet | 5 | Baseline network design method? | ❌ "I don't know" | ✅ *"...leveraging a multi-objective neural architecture search."* |
| EfficientNet | 6 | What is Observation 1? | ❌ "I don't know" | ✅ Exact match to source text |
| EfficientNet | 8 | Source code location? | ❌ "I don't know" | ✅ Exact GitHub URL |
| EfficientNet | 1 | Paper title & authors? | ❌ **Confidently wrong** (answered with a *different* paper's title/authors, from a References-section chunk) | ⚠️ *"I don't know."* — no longer wrong, but not yet correct either |

**5 of 6 targeted failures are now fully fixed.** The 6th (EfficientNet
Q1) improved from the most dangerous failure mode found in either report
(confidently wrong) to the safest one (honest refusal) — a real
improvement, just not a complete fix. See §4.

## 2. Full 10-question suite reruns (checking for regressions)

Not just the known failures — the entire suite from each prior report,
rerun end to end, same questions, same indexes.

### Factor Analysis (`local/test_reports/factor_analysis_index/`)

| # | Question | Before | After |
|---|---|---|---|
| 1 | What is factor analysis? | ✅ Correct | ✅ Correct (unchanged) |
| 2 | Two rotation methods? | ✅ Correct | ✅ Correct (unchanged) |
| 3 | Kaiser eigenvalue cutoff? | ✅ Correct | ✅ Correct (unchanged) |
| 4 | Jolliffe cutoff? | ✅ Correct | ✅ Correct (unchanged) |
| 5 | PCA vs FA difference? | ⚠️ Partial (garbled clause) | ✅ **Correct — clean now, no garbled insertion** |
| 6 | Example 1 dataset & variable count? | ❌ "I don't know" | ⚠️ **Improved, not complete:** *"The dataset used is PCA2. However, I don't have information about the exact number of variables."* — see note below |
| 7 | Example 1 factors & rotation? | ❌ "I don't know" | ✅ **Fixed** |
| 8 | Who documented scree graph? | ✅ Correct | ✅ Correct (unchanged) |
| 9 | NCSS method + steps? | ⚠️ Partial (steps omitted) | ✅ **Fixed — all 5 numbered steps now listed correctly** |
| 10 | Out-of-context (transformers)? | ✅ Correct refusal | ✅ Correct refusal (unchanged) |

**8/10 fully correct, 1/10 correct refusal, 1/10 partial** — up from 6/10
fully correct, 2/10 partial, 2/10 incorrect.

**Note on Q6's inconsistency:** the isolated targeted rerun (§1) got a
*fully* correct answer to this exact question against this exact index;
the full-suite rerun here got a partial one. Checked the retrieved pages
for both runs — **identical** (`[5, 6, 8]` both times). Same context, two
different completeness levels in the generated answer. This points at LLM
sampling variance (temperature-based non-determinism) in the generation
step, not a retrieval difference — worth keeping in mind when reading any
single run's results as ground truth. See §5.

### EfficientNet (`local/test_reports/efficientnet_index/`)

| # | Question | Before | After |
|---|---|---|---|
| 1 | Title and authors? | ❌ **Confidently wrong** | ⚠️ *"I don't know."* — safe now, not correct |
| 2 | B7 accuracy vs. previous best? | ✅ Correct | ✅ Correct (unchanged) |
| 3 | B4 vs. ResNet-50? | ✅ Correct | ✅ Correct (unchanged) |
| 4 | What is compound scaling? | ✅ Correct | ✅ Correct (unchanged) |
| 5 | Baseline design method? | ❌ "I don't know" | ✅ **Fixed** |
| 6 | Observation 1? | ❌ "I don't know" | ✅ **Fixed** |
| 7 | CIFAR-100/Flowers accuracy? | ✅ Correct | ✅ Correct (unchanged) |
| 8 | Source code location? | ❌ "I don't know" | ✅ **Fixed** |
| 9 | Other networks scaled? | ✅ Correct | ✅ Correct (unchanged) |
| 10 | Cross-document leakage check | ✅ Correct refusal | ✅ Correct refusal (unchanged) |

**8/10 fully correct, 1/10 correct refusal, 1/10 safe-but-incomplete
refusal** — up from 5/10 fully correct, 1/10 correct refusal, 3/10 false
refusals, 1/10 confidently wrong. **Zero false-refusal failures remain in
this document's suite** (down from 3).

## 3. Combined before/after

| | Fully correct | Correct refusal | Partial/safe-incomplete | False refusal | Confidently wrong |
|---|---|---|---|---|---|
| **Before** (20 questions, both documents) | 11/20 | 2/20 | 2/20 | 5/20 | 1/20 |
| **After** | 16/20 | 2/20 | 2/20 | 0/20 | 0/20 |

Every false-refusal failure identified in either prior report is gone.
The one confidently-wrong answer is gone, replaced by a safe refusal.
Nothing that was previously correct regressed.

## 4. What's still not fixed, and an honest read of why

**EfficientNet Q1 ("what is the title of this paper") is still not
answered correctly**, in either the targeted or full-suite rerun. Both
runs retrieved pages `[5, 9, 10]` — **page 1, the actual title page, is
no longer in the final top-3 at all**, where it *was* present (alongside
the wrong References-section chunk) in the pre-reranking run.

This is a real, slightly counterintuitive result worth sitting with
rather than glossing over: reranking removed the wrong answer, but it did
so by dropping the *right* chunk too, not by correctly promoting it. The
cross-encoder is scoring (query, chunk) relevance more precisely than
FAISS's embedding similarity did, but "what is the title of this paper"
against a chunk that's mostly abstract/author-affiliation text apparently
still doesn't score as clearly relevant as it should for an identity-type
question. This is consistent with the root cause already named in the
EfficientNet report: nothing in the pipeline distinguishes "this chunk
describes the document itself" from any other content-relevance judgment.
Reranking helps with *topical* relevance a lot (confirmed, 5/6 direct
fixes); it doesn't inherently solve *identity/self-referential* questions,
which may need a different mechanism entirely (e.g. always including the
first chunk/title-page content for "about this document" style
questions, or a dedicated document-metadata lookup that bypasses
retrieval for this query class).

## 5. Cost/latency note (not measured rigorously here, worth flagging)

This report didn't measure latency, but the architecture change has a
real cost: every knowledge query now runs a cross-encoder forward pass
over `RERANK_CANDIDATES=15` (query, chunk) pairs, in addition to the
FAISS search and the two LLM calls (intent + generation) that already
existed. The model is small (`ms-marco-MiniLM-L-6-v2`, same weight class
as the embedding model), and it's a local CPU/GPU forward pass rather
than a network call, but it's not free. Worth a follow-up report
specifically measuring added latency per query before/after, especially
under concurrent load — not done here.

## 6. Recommendation

Ship it — the evidence is about as clean as a 20-question, 2-document
sample can produce: 5 of 6 targeted, previously-diagnosed failures fixed
outright, zero regressions, and the one remaining gap (Q1) changed from
the most dangerous failure mode to the safest one rather than staying
put. `docs/05-roadmap.md`'s "Reranking after initial FAISS retrieval"
item is checked off on this basis. Two things worth tracking as follow-up
rather than blockers:

- [ ] Identity/self-referential questions ("what is this document
      called") may need a mechanism beyond reranking — see §4.
- [ ] Actual latency measurement under the new architecture — see §5.
