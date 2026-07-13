"""Advanced retrieval with reduced token size for LangChain 1.x."""

from __future__ import annotations


def adaptive_top_k(question: str) -> tuple[int, int]:
    """Fixed top-K values - reduced to avoid token limits."""
    return 5, 3  # Retrieve 5, return top 3 (down from 12, 5)


def build_advanced_retriever(base_retriever, llm, k_final: int, *, use_multi_query: bool = True):
    """Return base retriever as-is for LangChain 1.x."""
    return base_retriever
