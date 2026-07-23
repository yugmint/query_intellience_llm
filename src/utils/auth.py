# src/utils/auth.py

import os

from fastapi import Header, HTTPException

from src.utils.logger import logger

_API_KEY = os.getenv("RAG_API_KEY")

if not _API_KEY:
    logger.warning(
        "RAG_API_KEY is not set -- /query, /reload, and /reset-memory are "
        "running UNAUTHENTICATED. Fine for local dev; set RAG_API_KEY "
        "before exposing this service beyond localhost."
    )


def require_api_key(x_api_key: str | None = Header(default=None)):
    """
    FastAPI dependency enforcing a shared-secret API key via the
    X-API-Key header. A no-op (allows everything) if RAG_API_KEY isn't
    configured -- see the module-level warning above.

    Intentionally minimal: one shared key, no per-client identity, no
    rotation, no rate limiting. Enough to stop casual/accidental
    unauthenticated access; not a substitute for a real auth layer
    (OAuth, per-user keys, a gateway) before this is exposed to
    untrusted traffic. See docs/05-roadmap.md.
    """

    if _API_KEY is None:
        return

    if x_api_key != _API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing API key")
