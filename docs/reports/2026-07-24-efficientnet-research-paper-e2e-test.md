# End-to-End Test Report — Genuine Research Paper (Third Document)

> **Update (2026-07-24, later same day):** Q5/Q6/Q8 below are **fixed**
> via reranking. Q1 (the confidently-wrong answer) is **no longer wrong**
> — it now safely refuses instead — but is still not fully correct; see
> [2026-07-24-reranking-validation.md](2026-07-24-reranking-validation.md) §4
> for why that one specific case is more nuanced. Left this report's
> original findings intact below for the record.

**Date:** 2026-07-24
**Document:** `Computer Vision_2.pdf` — actually **"EfficientNet: Rethinking
Model Scaling for Convolutional Neural Networks"** (Tan & Le, Google
Research/Brain Team, *ICML 2019*), 11 pages, real Abstract/Introduction/
Method/Experiments/Conclusion/References structure.
**Pipeline versions:** `ingestion_fixed` `v0.1.0`, `RAG_Project_1` `v0.1.0`
**Why this document:** the [2026-07-24 Factor Analysis
report](2026-07-24-academic-document-e2e-test.md) never actually exercised
the `research_paper` classification path natively — that document got
classified `book` and `research_paper` behavior was only reached by
force-overriding it in code (see that report's §5). This is the first
document to hit `research_paper` for real. It's also topically and
structurally different again from both prior documents (ML benchmarks,
figures, dense citation list, no narrative prose).

**Method:** same standard as both prior reports — every number below is
real, captured output; ground-truth answers were extracted and written
down from the actual PDF text *before* running the questions. Isolated
index at `local/test_reports/efficientnet_index/` (gitignored), separate
from production and from the other two test indexes.

---

## 1. Ingestion — classification and chunk quality

```bash
INGESTION_INDEX_PATH=".../efficientnet_index" \
    python -m src.ingestion.pipeline "Computer Vision_2.pdf"
```

```
Detected Document Type : research_paper
Confidence              : 0.90
Recommended Chunker     : structure
Chunk Size/Overlap      : 630/126
Rationale               : base profile for document_type='research_paper';
                          avg paragraph length (43767 chars) is large
                          relative to the base window; growing chunk_size to 630
Pages: 11 | Chunks: 79 | Avg chunk size: 662 chars
```

**Classification worked correctly this time** — a real `"Abstract"`
heading plus a genuine references section gave `_classify_document` what
it needed (see the prior report's §1 for the exact code path). Confidence
0.90, the highest of any document tested so far.

**One odd number worth flagging:** `average_paragraph_length` of **43,767
characters** is implausible for an 11-page paper — `_extract_statistics`
splits on `"\n\n"` across the whole joined document text, and dense
multi-column academic PDF layouts often don't reproduce blank-line
paragraph breaks reliably through `pypdf` extraction. The practical effect
here was benign (the recommendation logic's "paragraph too large" branch
correctly grew `chunk_size` from 450→630), but the *input number* feeding
that decision is close to meaningless for this document type. Worth a
roadmap note: `average_paragraph_length` as computed may not be a
reliable signal for academic-paper-style PDFs specifically.

**Chunk quality** (`scripts/validate_chunks.py`):

| Metric | Value | (Factor Analysis, for comparison) |
|---|---|---|
| Chunk count | 79 | 54 |
| Within 0.5x–1.5x target | 75/79 (95%) | 49/54 (91%) |
| Near-empty / duplicate chunks | 0 / 0 | 0 / 0 |
| Not ending on sentence punctuation | 56/79 (71%) | 37/54 (69%) |

Structurally the *best*-scoring ingestion of the three documents tested so
far — correct classification, higher target-range compliance, no
empty/duplicate chunks.

**Embedding quality** (`scripts/validate_embeddings.py`): 79 vectors,
dimension 384, 0 NaN/zero vectors, norm exactly 1.000 throughout, pairwise
similarity mean/std 0.495/0.135 (no near-duplicates). Clean, same as both
prior documents.

## 2. RAG — question/answer suite

Ten questions through the compiled `RAGService`, fresh session per
question. Question 10 is a deliberate **cross-document leakage test** —
asking about `Factor_Analysis.pdf`'s subject matter against an index that
only contains this paper, to check for contamination between separate
indexes or reliance on the model's general training knowledge instead of
the retrieved context.

| # | Question | Expected (source) | Actual answer | Retrieved pages | Verdict |
|---|---|---|---|---|---|
| 1 | Title and authors? | *"EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks"*, Mingxing Tan & Quoc V. Le (p.1) | *"Squeezenet: Alexnet-level accuracy with 50x fewer parameters and <0.5 mb model size. The authors are Iandola, F. N., Han, S., Moskewicz, M. W., Ashraf, K., Dally, W. J., and Keutzer, K."* | 9, 1, 11 | ❌ **Seriously wrong** — see §3, not a minor slip |
| 2 | B7 accuracy vs. previous best? | Surpasses GPipe accuracy, 8.4x fewer params, 6.1x faster inference (p.1–2) | Matches, correct | 2, 2, 2 | ✅ Correct |
| 3 | B4 vs. ResNet-50 improvement? | 76.3% → 83.0% (+6.7%) (p.2) | Exact match | 2, 2, 2 | ✅ Correct |
| 4 | What is compound scaling? | Uniformly scales width/depth/resolution with fixed coefficients (p.2) | Correct core mechanism, terse | 8, 1, 2 | ✅ Correct |
| 5 | How was the baseline network designed? | Neural architecture search (p.2) | *"I don't know."* | 4, 3, 1 | ❌ False refusal — p.2 missing from top-3 |
| 6 | What is "Observation 1"? | *"Scaling up any dimension of network width, depth, or resolution improves accuracy, but the accuracy gain diminishes for bigger models."* (p.4) | *"I don't know."* | 6, 1, 1 | ❌ False refusal — p.4 missing |
| 7 | Transfer-learning accuracy on CIFAR-100/Flowers? | 91.7% / 98.8% (p.1) | Exact match | 7, 1, 8 | ✅ Correct |
| 8 | Where is the source code? | GitHub URL, on p.1 (wraps across 3 lines in raw extracted text) | *"I don't know."* | 9, 1, 5 | ❌ False refusal — p.1 retrieved, but likely lost in the line-wrapped URL extraction |
| 9 | What other networks was the method applied to? | MobileNets and ResNet (p.1) | Correct | 3, 5, 3 | ✅ Correct |
| 10 | What is factor analysis? *(cross-document leakage test)* | Not in this document/index at all | *"I don't know."* | 5, 5, 1 | ✅ **Correct refusal — no cross-index contamination** |

**Score: 5/10 fully correct, 1/10 seriously wrong, 3/10 false refusals,
1/10 correct refusal.**

## 3. The Q1 failure — a materially different and more serious problem

Every failure in the Factor Analysis report (and Q5/Q6/Q8 here) was a
**safe** failure: the model said "I don't know" when the true answer
wasn't retrieved. Q1 is not that — it's a **confident, wrong answer**,
and it happened *while the correct source (page 1) was sitting in the
same retrieved context*.

Root cause, confirmed by reading page 9 directly (§1's index, not this
report's numbering — see the raw text below):

```
References
Berg, T., Liu, J., ...
...
Iandola, F. N., Han, S., Moskewicz, M. W., Ashraf, K.,
Dally, W. J., and Keutzer, K. Squeezenet: Alexnet-level
accuracy with 50x fewer parameters and <0.5 mb model
size. arXiv preprint arXiv:1602.07360, 2016.
```

Page 9 is the start of the References section — a long, essentially
unbroken bibliography (matches §1's `average_paragraph_length` anomaly:
no blank-line breaks between citations for the chunker to split on). Each
entry reads exactly like `Authors. Title. Venue, Year.` — structurally
identical to how a paper's own title/author line reads. When asked "what
is the title of this paper," the retriever surfaced both the real title
page (page 1) *and* a References chunk (page 9) containing someone else's
citation in that same title-like format, and the LLM picked the wrong
one — despite the generation prompt's explicit instruction to answer only
from context and not fabricate.

**This is not a hallucination in the usual sense** — every word in the
answer is real text that was actually in the retrieved context. It's a
**source-attribution failure**: nothing in the current pipeline
distinguishes "this chunk is the document describing itself" from "this
chunk is the document citing someone else." For an identity-type question
("what is this called," "who wrote this"), that distinction matters a lot
more than it does for a content question.

## 4. Comparison across all three documents tested so far

| | Fiction book (README) | Factor Analysis (stats manual) | EfficientNet (this report) |
|---|---|---|---|
| Classification | `book` (correct) | `book` (**wrong** — should be closer to `research_paper`) | `research_paper` (correct, 0.90 confidence) |
| Chunk quality | not measured this rigorously | 91% in target range | 95% in target range |
| Q&A tested | narrative recall only (guardrails/memory focus) | 10 fact questions | 10 fact questions + 1 cross-index leakage check |
| Fully correct | — | 6/10 | 5/10 |
| False refusals | — | 2/10 | 3/10 |
| **Confidently wrong** | — | 0/10 | **1/10 (new)** |

**Correct classification and better chunk-quality metrics did not produce
better retrieval accuracy** — if anything, this run has *more* false
refusals than the misclassified Factor Analysis document, despite scoring
better on every ingestion-side quality metric. This is a third,
independent data point supporting the [prior report's controlled
finding](2026-07-24-academic-document-e2e-test.md#5-follow-up--testing-the-chunking-size-hypothesis-directly-2026-07-24-later-same-day):
the bottleneck is the retrieval/ranking layer (`k=3`, no reranking, no
source-type awareness), not chunking or classification quality. Those
remain worth fixing for their own reasons, just not as the fix for
retrieval accuracy.

## 5. Recommendations

| Finding | Action | Where it belongs |
|---|---|---|
| Confident wrong answer from a References-section chunk mistaken for the document's own identity (Q1) | Tag chunks originating from a references/bibliography section (layout detection already has `has_references`; could extend to per-chunk, not just document-level) and either exclude them from identity-type queries or let the generation prompt know a chunk's structural role | New — real, higher-severity finding. Belongs in `RAG_Project_1` roadmap (generation/grounding) *and* `ingestion_fixed` (metadata could carry a `section` hint) |
| `average_paragraph_length` is unreliable for dense academic PDF layouts (43,767 chars from one document) | Investigate whether `pypdf` extraction is losing paragraph breaks for this layout style, or whether the statistic needs a sentence-based fallback when paragraph count is implausibly low | New — `ingestion_fixed` roadmap |
| 3/10 false refusals despite correct classification and best-yet chunk quality | Further confirms reranking / better retrieval is the real lever, not ingestion-side tuning | Reinforces existing `RAG_Project_1` `v0.2.0` items — no new action, just more evidence |
| Cross-document leakage test passed cleanly | None needed | Good news, not a gap — worth keeping this kind of check in future reports as a standing sanity check |

**Overall:** this is the most concerning of the three test documents so
far — not because the numbers are much worse (5/10 vs. 6/10 is noise at
this sample size), but because it surfaced a **new failure category**
that neither prior test caught: a confidently wrong, source-misattributed
answer. That's a more serious problem for a real deployment than a safe
"I don't know," and it's exactly the kind of thing that N=1-document
testing was always going to eventually surface. Good argument for testing
a fourth and fifth document before treating the failure-mode inventory as
complete.
