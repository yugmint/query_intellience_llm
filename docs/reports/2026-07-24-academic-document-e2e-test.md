# End-to-End Test Report — Academic/Technical Document

> **Update (2026-07-24, later same day):** the Q6/Q7 failures below are
> **fixed** — reranking was added and both were re-tested and confirmed
> working. See [2026-07-24-reranking-validation.md](2026-07-24-reranking-validation.md).
> Left this report's original findings intact below for the record.

**Date:** 2026-07-24
**Document:** `Factor_Analysis.pdf` (NCSS Statistical Software, Chapter 420 — a 16-page
technical reference chapter on factor analysis: definitions, math, a worked
example, procedure/UI documentation)
**Pipeline versions:** `ingestion_fixed` `v0.1.0`, `RAG_Project_1` `v0.1.0`
**Why this document:** both repos had so far only been validated against one
document — a narrative fiction book ("Grandma's Bag of Stories"). This
report is the second, structurally different data point: dense technical
prose, citations, mathematical notation, tables, and a numbered worked
example — closer to what "academic/technical PDF" usually means in practice.
Sourced from the `rag_test_files/` folders already sitting in both repos
(untracked, never previously run through either pipeline).

**Method:** everything below is real, captured output — no numbers are
estimated or hand-written. Two dedicated, isolated indexes were used
(`local/test_reports/factor_analysis_index/` and, for the §5 follow-up,
`..._research_paper/`, both gitignored), separate from the production index
the README's "Proof It Works" section and the running app use, so this
test doesn't disturb either. Reproduction commands are included per
section. **Update:** §1's original hypothesis about *why* Q6/Q7 failed was
tested directly in §5 and turned out to be wrong — see there before reading
§1/§4 as settled conclusions.

---

## 1. Ingestion — classification

```bash
cd ingestion_fixed
INGESTION_INDEX_PATH="../RAG_Project_1/local/test_reports/factor_analysis_index" \
    python -m src.ingestion.pipeline "../RAG_Project_1/local/data/rag_test_files/Factor_Analysis.pdf"
```

```
Detected Document Type : book
Confidence              : 0.85
Recommended Chunker     : recursive
Chunk Size/Overlap      : 800/160
Rationale               : base profile for document_type='book'
Pages: 16 | Chunks: 54 | Avg chunk size: 727 chars
```

**Finding: this is a misclassification, and the exact mechanism is
traceable in `PDFAnalyzer._classify_document`** (`src/ingestion/analysers/pdf_analyzer.py`):

```python
def _classify_document(self, documents, layout) -> str:
    text = "\n".join(d.page_content.lower() for d in documents[:5])
    if "abstract" in text and layout.has_references:
        return "research_paper"
    if "invoice" in text:
        return "invoice"
    if "chapter" in text or "table of contents" in text:
        return "book"
    if "agreement" in text:
        return "legal"
    return "general"
```

This document has no literal `"Abstract"` heading (it's a software-manual
chapter, not a formatted academic paper), so the `research_paper` branch is
unreachable regardless of its citations (`Kaiser (1960)`, `Tabachnick
(1989)`, etc.) or references. It falls through to the `book` check, which
fires the instant the literal word `"chapter"` appears anywhere in the
first 5 pages — and page 1 opens with `"Chapter 420"`. One keyword, checked
in a fixed priority order, decided the classification.

**Tested as a possible cause of the retrieval failures in §3 — refuted, not
confirmed.** The original version of this report speculated that `book`'s
coarser chunking profile (`chunk_size=800, split_large_chunks=False` vs.
`research_paper`'s `450`/`True`) plausibly diluted the pinpoint facts Q6/Q7
needed. That was a hypothesis, stated as one, and it turned out to be
wrong — §6 reruns the exact same questions against a controlled variant of
this document forced to classify as `research_paper`, and the same two
questions fail the same way regardless of chunk size. Read §6 before
treating the paragraph above as settled; it isn't. The misclassification
itself is still real and still worth fixing (see recommendation below and
§5) — it's just not the explanation for Q6/Q7.

**Recommendation for `ingestion_fixed`'s roadmap:** the `chapter` keyword
check is too blunt on its own. Corroborate it against `layout.has_equations`
/ `layout.has_tables` (both already computed, already available) before
committing to `book` — a chapter-numbered document that's *also*
equation/table-dense reads more like a technical reference than a
narrative book. Worth fixing for classification correctness and
predictability on its own merits, independent of §6's finding. Not fixed
as part of this report (see §5).

## 2. Ingestion — chunk & embedding quality

```bash
python scripts/validate_chunks.py "<path>/Factor_Analysis.pdf"
python scripts/validate_embeddings.py "<path>/Factor_Analysis.pdf"
```

**Chunk size distribution:**

| Metric | Value |
|---|---|
| Chunk count | 54 |
| Target size / overlap | 800 / 160 |
| Min / max | 202 / 959 |
| Mean / median | 727 / 748 |
| Within 0.5x–1.5x target | 49/54 (91%) |
| Near-empty chunks (<20 chars) | 0 |
| Exact duplicate chunks | 0 |
| Avg overlap between consecutive chunks | 117 chars (target ~160) |
| Chunks not ending on sentence punctuation | 37/54 (69%) |

Structurally healthy (no empty/duplicate chunks, size distribution
reasonable), but the 69% non-sentence-ending rate is well above the
script's own "worth a manual look" threshold (~30–40%). Manual spot-check
(`--dump-samples`) confirms why: a meaningful fraction of chunks are
formula/table fragments, not prose —

```
--- sample | 696 chars | page 3 ---
( )
ii ii
k =1
p
over j k
jk
k =1
p
kk
c = 1 - 1
R
r
1 - 1
R
∑
∑
≠
max
where Rii is the ith diagonal element of R-1 and rjk is an element of R...
```

This is `pypdf`'s text extraction doing its best with an embedded
mathematical equation — the result is barely-readable to a human and low
signal for an embedding model. `ingestion_fixed`'s loader has no
equation-aware handling (`layout.has_equations` is *detected* but nothing
currently *does* anything differently for equation-heavy content). This is
a real, current limitation, not a bug — but it's the direct explanation for
some of the boundary-quality and retrieval numbers in this report.

**Embedding sanity** (`validate_embeddings.py`):

| Metric | Value |
|---|---|
| Vectors | 54, dimension 384 |
| NaN / zero vectors | 0 / 0 |
| Norm mean/std/min/max | 1.000 / 0.000 / 1.000 / 1.000 |
| Pairwise similarity mean/std | 0.394 / 0.156 |
| Near-duplicate pairs (cosine > 0.999) | 0 |

Clean — normalized correctly, healthy discriminative spread, no degenerate
vectors. Embedding quality itself is not implicated in the retrieval
failures below; chunk granularity and content noise are the more likely
causes.

**Bug found:** `scripts/validate_chunks.py --dump-samples` crashes on
Windows with `UnicodeEncodeError: 'charmap' codec can't encode character
'χ'` the moment a sampled chunk contains a character outside cp1252
(here, the Greek χ from "Bartlett Test... uses a Chi-square distribution").
`print()` inherits the console's default encoding, which on Windows is
cp1252, not UTF-8. Workaround used for this report: `PYTHONIOENCODING=utf-8`
env var. Real fix belongs in the script (wrap stdout or force UTF-8) — see
§5.

## 3. RAG — question/answer suite

Ten questions run through the actual compiled `RAGService`, one real turn
each (fresh `session_id` per question — no shared history), pointed at the
isolated index above. Full raw output (including retrieved page numbers) in
`local/test_reports/qa_results.json`. Expected answers below are quoted or
directly paraphrased from the source PDF, established *before* running the
questions.

```bash
FAISS_INDEX_PATH="local/test_reports/factor_analysis_index" python -c "
from src.services.rag_service import RAGService
rag = RAGService()
print(rag.ask('<question>', session_id='test'))
"
```

| # | Question | Expected (source page) | Actual answer | Retrieved pages | Verdict |
|---|---|---|---|---|---|
| 1 | What is factor analysis? | Exploratory technique finding underlying factors from observed variables (p.1) | *"Factor analysis is an exploratory technique applied to a set of observed variables that seeks to find underlying factors (subsets of variables) from which the observed variables were generated."* | 1, 1, 5 | ✅ Correct |
| 2 | What two rotation methods does NCSS provide? | Varimax and Quartimax (p.1, 3) | *"NCSS provides two orthogonal rotation options: varimax and quartimax."* | 3, 1, 2 | ✅ Correct |
| 3 | Who proposed dropping factors whose eigenvalues are less than one? | Kaiser (1960) (p.3) | *"Kaiser (1960) proposed dropping factors whose eigenvalues are less than one."* | 3, 3, 12 | ✅ Correct |
| 4 | What eigenvalue cutoff does Jolliffe suggest? | 0.7 (p.3) | *"Jolliffe suggests using a cutoff on the eigenvalues of 0.7..."* | 3, 11, 12 | ✅ Correct |
| 5 | Main difference between PCA and factor analysis? | PCA = total variation (diagonal of R); FA = common portion (off-diagonal) (p.5) | *"...PCA is concerned with the total variation... PCA models the total variation, whereas FA is concerned with a correlation in a partition of the total variation called the common portion."* | 5, 5, 1 | ⚠️ Partially correct — core distinction right, but "PCA models the total variation" is an inserted clause not stated that way in the source (the source says FA models the *common* portion, `Rc`; it doesn't say PCA "models" anything). Mildly garbled, not factually wrong. |
| 6 | What dataset was used in Example 1, and how many variables does it contain? | PCA2 dataset, 6 variables X1–X6 (p.5, 9) | *"I don't know."* | 8, 6, 8 | ❌ **Incorrect** — false refusal. The answer exists in the corpus (p.5, p.9) but none of it made top-3 retrieval. |
| 7 | In Example 1, how many factors were retained, and what rotation was used? | 2 factors, Varimax (p.9, 12) | *"I don't know."* | 3, 3, 3 | ❌ **Incorrect** — false refusal, and notably all 3 retrieved chunks came from the same page (3), which discusses factor-count methodology in general, not the specific worked example. The actual answer (p.9, p.12) never surfaced. |
| 8 | Who documented the scree graph? | Cattell (1966) (p.3) | *"Cattell (1966)."* | 12, 8, 2 | ✅ Correct |
| 9 | What method does NCSS use to solve the factor analysis problem, and what are its main steps? | Principal-axis method; 5 steps (estimate U → eigen-decompose R-U → loading matrix → score matrix → factor scores) (p.2) | *"NCSS uses the principal axis method of factor analysis. It may be rotated using varimax or quartimax rotation."* | 1, 2, 6 | ⚠️ Partially correct — method name right, but the actual numbered steps (present on p.2, in the retrieved set) were never surfaced in the answer, and the response substitutes rotation info instead. Plausibly related to p.2's steps sitting adjacent to the garbled equation text seen in §2. |
| 10 | Explain how transformer neural networks and attention mechanisms work. *(deliberately out-of-context)* | Not covered by this document at all | *"I don't know."* | 3, 4, 1 | ✅ **Correct refusal** — no hallucination on a topic totally absent from the corpus, despite 3 chunks being retrieved anyway (`retriever.invoke` always returns k=3 regardless of relevance; grounding is enforced by the generation prompt, not by retrieval declining to return anything). |

**Score: 6/10 fully correct, 2/10 partially correct, 2/10 incorrect
(both false refusals from retrieval misses).**

## 4. Analysis

**The two real failures (Q6, Q7) share a pattern:** both needed a
*specific numeric detail tied to "Example 1"* (a dataset name + variable
count; a factor count + rotation choice used in that worked example) rather
than a general conceptual fact. Both times, the top-3 FAISS results were
dominated by conceptually-adjacent-but-wrong content (general "how many
factors" methodology discussion on page 3, procedure-tab UI documentation
on page 6/8) rather than the actual worked-example content on pages 9/12.
Q7 is the more telling case — all three retrieved chunks came from the
*same page*, meaning the top-k had zero diversity and no chance of
surfacing the right answer even probabilistically.

This is exactly the failure mode `RAG_Project_1`'s own roadmap already
names for `v0.2.0`: **reranking** and **better chunk selection/dedup at the
`retrieve` node** — plain top-k similarity search with `k=3` and no
relevance threshold or diversity constraint. §6 confirms this directly:
forcing smaller, more granular chunks (the `research_paper` profile) did
**not** fix Q6/Q7 — the same two questions failed the same way regardless
of chunk size, which points at the retrieval/ranking layer as the actual
cause, not chunk granularity. This report is real evidence the reranking
and dedup items are correctly prioritized, not speculative nice-to-haves.

**The `"book"` misclassification (§1) is real and worth fixing, but §6
shows it is *not* the cause of Q6/Q7.** It's precisely explained (one
keyword, fixed priority order) and narrowly fixable — see §5 — but its
value is classification correctness/predictability on its own terms, not
as a fix for the retrieval failures in this report. Keeping the original
(wrong) hypothesis crossed out rather than deleted, in §1, so the
correction is visible.

**Compared to the existing fiction-book baseline** (README "Proof It
Works"): that test exercised intent routing, session memory, and guardrails
successfully but only asked narrative-recall questions from one short,
prose-only book. This report is a genuinely different stress case —
citation/fact lookup against dense technical content — and it's the first
time either pipeline's behavior on *retrieval precision under ambiguity*
has been measured with real pass/fail numbers instead of a single anecdote.

## 5. Follow-up — testing the chunking-size hypothesis directly (2026-07-24, later same day)

§1/§4's first version claimed the `"book"` misclassification "plausibly"
caused Q6/Q7 via coarser chunking. That's a correlational claim dressed as
a finding, and it deserved an actual test rather than staying a hunch —
this section is that test.

**Method:** rebuilt the same document into a second, isolated index, with
one deliberate change — after running the real analyzer (which still
classifies it `book`), the classification and its derived
`ChunkingRecommendation` were overridden in code to force `research_paper`,
using the analyzer's own `_recommend_chunking("research_paper", statistics)`
— same statistics, same document, only the profile differs. Not a config
flag (none exists for this yet); done directly against the pipeline
internals for this one-off test.

```
book profile:           chunk_size=800, split_large_chunks=False -> 54 chunks, avg 727 chars, range 202-959
research_paper profile: chunk_size=450, split_large_chunks=True  -> 89 chunks, avg 446 chars, range 172-541
```

Confirmed genuinely different chunking (89 vs. 54 chunks, ~40% smaller on
average, much narrower range) — a real manipulation, not a no-op. Same 10
questions, same method, run against this new index.

| # | Question | Book-profile verdict | Research-paper-profile verdict | Changed? |
|---|---|---|---|---|
| 1 | What is factor analysis? | ✅ Correct | ✅ Correct (identical answer) | No |
| 2 | Two rotation methods? | ✅ Correct | ✅ Correct | No |
| 3 | Kaiser eigenvalue cutoff? | ✅ Correct | ✅ Correct | No |
| 4 | Jolliffe cutoff? | ✅ Correct | ✅ Correct | No |
| 5 | PCA vs FA difference? | ⚠️ Partial (garbled clause) | ⚠️ Partial (different wording, still not a direct quote, but cleaner) | Marginal |
| 6 | Example 1 dataset & variable count? | ❌ "I don't know" (retrieved 8,6,8) | ❌ **Still "I don't know"** (retrieved 10,6,8 — different chunks, same failure) | **No — hypothesis fails here** |
| 7 | Example 1 factors & rotation? | ❌ "I don't know" (retrieved 3,3,3) | ❌ **Still "I don't know"** (retrieved 3,7,3 — still mostly page 3) | **No — hypothesis fails here** |
| 8 | Who documented scree graph? | ✅ Correct | ✅ Correct | No |
| 9 | NCSS method + steps? | ⚠️ Partial (method right, steps missing, mentions rotation) | ⚠️ Partial (method right, steps missing, doesn't mention rotation either — slightly less complete) | Marginal, slightly worse |
| 10 | Out-of-context (transformers)? | ✅ Correct refusal | ✅ Correct refusal | No |

**Conclusion: the hypothesis is refuted.** Q6 and Q7 — the two questions it
was supposed to explain — fail identically under both chunking profiles.
Smaller, more granular, force-split chunks did not surface the right
content for either question; in both cases the top-3 retrieved pages
changed slightly but still missed pages 9/12 (where the actual "Example 1"
answers live) entirely. This rules out chunk granularity as the
explanation and points more specifically at the retrieval/ranking layer:
plain `k=3` cosine similarity search apparently can't distinguish "content
*about* the general concept of factor counting" (page 3) from "the answer
*for this specific worked example*" (pages 9/12) regardless of how the
source text is sliced. That's a stronger, more specific justification for
reranking than the original report had — a reranker (or a cross-encoder
second pass) is designed to fix exactly this class of problem; a
chunking-strategy change was never going to.

**Honest caveat on this follow-up itself:** still N=1 document, still the
same two questions, still manually graded by the same person who wrote
both the questions and the original hypothesis. It's a real controlled
comparison, not a large-scale one — treat "refuted" as "refuted for this
document and these two questions," not as a general law.

## 6. Recommendations (mapped to existing roadmap items where possible)

| Finding | Action | Where it belongs |
|---|---|---|
| `"book"` misclassification via a single `"chapter"` keyword | Corroborate against `layout.has_equations`/`has_tables` before committing to `book` over `research_paper`. **Note (§5): tested and confirmed this is *not* the cause of the Q6/Q7 retrieval failures** — worth fixing for classification correctness on its own merits, not as a retrieval fix. | New — `ingestion_fixed` `v0.2.0` roadmap (classification robustness), not yet listed |
| Retrieval misses on specific-example questions (Q6/Q7), confirmed independent of chunk size (§5) | Reranking; chunk dedup/diversity at `retrieve` — §5's controlled test makes this the primary suspect, not a secondary guess | Already listed — `RAG_Project_1` `v0.2.0` |
| Formula/equation text extracted as low-signal noise | Equation-aware cleaning or exclusion — `layout.has_equations` is detected but unused downstream | New — `ingestion_fixed` roadmap, adjacent to the existing `TextCleaner` table/header-footer item (`v0.3.0`) |
| `validate_chunks.py --dump-samples` crashes on non-cp1252 output (Windows) | Force UTF-8 on stdout, or write samples to a file instead of `print()` | New — small, should land in `ingestion_fixed` `v0.1.1` (patch-level fix, no feature change) |
| Answer occasionally omits retrieved facts even when present (Q9) | Not a retrieval problem this time — the right chunk *was* in context under both chunking profiles (§5), and the answer stayed incomplete both times. Possibly a generation-prompt following-instructions gap on multi-part questions ("what method, and what are its steps"). Worth a few more test cases before concluding a fix is needed. | Watch — not enough evidence yet for a specific roadmap item |

None of these are blockers on their own — the 60% fully-correct / 20%
partial / 20% false-refusal split on a deliberately harder document type is
a reasonable result for the current architecture, and the false refusals
are the *safe* failure mode (no hallucination occurred anywhere in this
suite, including the deliberate out-of-context question). But this is
concrete, second-document evidence for exactly the "needs more real-world
mileage before a 1.0 claim" reasoning already written into both repos'
`v0.1.0` tags.
