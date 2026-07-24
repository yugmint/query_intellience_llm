from src.retrieval.config import TOP_K
from src.workflow.resources import RAGResources
from src.workflow.state import RAGState

from src.utils.decorators import log_node
from src.utils.logger import logger


@log_node("Rerank")
def rerank_documents(
    state: RAGState,
    resources: RAGResources,
):
    """
    Narrows the wider FAISS candidate pool (RERANK_CANDIDATES, from
    nodes/retrieve_context.py) down to TOP_K using a cross-encoder, which
    scores (query, chunk) pairs jointly -- much more precise than the
    bi-encoder similarity search FAISS already did to produce the
    candidate pool in the first place. This is what plain top-k similarity
    search alone couldn't do: recover a genuinely relevant chunk that
    ranked outside the old un-reranked top-3 (confirmed happening in
    practice -- see docs/reports/2026-07-24-*.md).

    Rebuilds `context` from the reranked, trimmed set -- the wider
    candidate pool's un-reranked context (built in retrieve_context.py)
    is not what should reach the generation prompt.
    """

    # ------------------------
    # Prepare
    # ------------------------

    query = state.get("rewritten_query") or state["query"]
    candidates = state.get("documents", [])

    if not candidates:
        logger.info("No candidates to rerank.")
        return {"documents": [], "context": ""}

    # ------------------------
    # Execute
    # ------------------------

    pairs = [(query, document.page_content) for document in candidates]
    scores = resources.reranker.predict(pairs)

    ranked = sorted(
        zip(scores, candidates),
        key=lambda pair: pair[0],
        reverse=True,
    )

    top_documents = [document for _score, document in ranked[:TOP_K]]

    context = "\n\n".join(
        document.page_content
        for document in top_documents
    )

    # ------------------------
    # Business Metrics
    # ------------------------

    logger.info(f"Reranked {len(candidates)} candidates -> kept top {len(top_documents)}")
    logger.info(f"Top scores: {[round(float(s), 3) for s, _ in ranked[:TOP_K]]}")
    logger.info(f"Context Length : {len(context)} chars")

    # ------------------------
    # Return
    # ------------------------

    return {
        "documents": top_documents,
        "context": context,
    }
