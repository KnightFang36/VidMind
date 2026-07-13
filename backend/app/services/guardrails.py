"""Hallucination guard + timestamped citation builder."""

from __future__ import annotations

from langchain_core.documents import Document

from app.services.embedding import get_embeddings

_RELEVANCE_THRESHOLD = 0.0

INSUFFICIENT_CONTEXT_MESSAGE = (
    "The transcript does not contain enough information to answer this question."
)


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def has_sufficient_evidence(question: str, documents: list[Document]) -> bool:
    """Check if evidence is relevant enough to answer."""
    if not documents:
        return False
    try:
        embeddings = get_embeddings()
        q_vec = embeddings.embed_query(question)
        doc_vecs = embeddings.embed_documents([d.page_content for d in documents])
        best = max((_cosine(q_vec, dv) for dv in doc_vecs), default=0.0)
        return best >= _RELEVANCE_THRESHOLD
    except Exception:
        return True


def _format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def build_citations(documents: list[Document]) -> list[dict]:
    """Convert documents into timestamped citation objects."""
    sources: list[dict] = []
    for doc in documents:
        meta = doc.metadata or {}
        start = float(meta.get("start", 0.0) or 0.0)
        video_id = meta.get("video_id")
        url = None
        if video_id:
            url = f"https://www.youtube.com/watch?v={video_id}&t={int(start)}s"

        content = doc.page_content
        snippet = content if len(content) <= 320 else content[:317] + "..."

        sources.append(
            {
                "video_id": video_id,
                "parent_id": meta.get("parent_id"),
                "chunk_index": meta.get("chunk_index"),
                "start_seconds": round(start, 2),
                "timestamp": _format_timestamp(start),
                "url": url,
                "snippet": snippet,
            }
        )
    return sources