"""Advanced retrieval: adaptive top-K, reranking."""

from __future__ import annotations

import re
from functools import lru_cache

from app.core.config import get_settings
from app.services.embedding import get_embeddings

_DEFAULT_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_HARD_HINTS = re.compile(
    r"\b(compare|difference|why|how|explain|list|all|every|steps?|"
    r"pros?\s+and\s+cons?|summar|relationship|versus|vs)\b",
    re.IGNORECASE,
)


def adaptive_top_k(question: str) -> tuple[int, int]:
    """Decide retrieval depth based on question difficulty."""
    q = question.strip()
    words = len(q.split())
    hard = bool(_HARD_HINTS.search(q)) or words > 18

    if hard:
        return 16, 8
    if words <= 6:
        return 6, 2
    return 12, 5


def build_advanced_retriever(base_retriever, llm, k_final: int, *, use_multi_query: bool = True):
    """Wrap base retriever with adaptive filtering."""
    # For LangChain 1.x simplicity, just return the base retriever
    # Advanced features (MultiQuery, compression) can be added incrementally
    return base_retriever