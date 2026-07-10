# services/guardrails.py
#
# #12 Hallucination Guard  -> before answering, verify the retrieved evidence
#                             is actually relevant to the question. If it is
#                             not, we refuse instead of making something up.
# Citation Builder         -> turn parent chunks + timestamps into clean,
#                             deep-linkable sources (?t=<seconds>).

from __future__ import annotations

from langchain_core.documents import Document

from backend.app.services.embedding import get_embeddings

# Cosine-similarity floor for "is this evidence good enough to answer?"
# Embeddings are normalized, so dot product == cosine similarity.
_RELEVANCE_THRESHOLD = 0.28

INSUFFICIENT_CONTEXT_MESSAGE = (
    "The transcript does not contain enough information to answer this question."
)


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def has_sufficient_evidence(question: str, documents: list[Document]) -> bool:
    """
    Return True if at least one retrieved chunk is semantically close enough
    to the question to justify answering.
    """
    if not documents:
        return False
    try:
        embeddings = get_embeddings()
        q_vec = embeddings.embed_query(question)
        doc_vecs = embeddings.embed_documents([d.page_content for d in documents])
        best = max((_cosine(q_vec, dv) for dv in doc_vecs), default=0.0)
        return best >= _RELEVANCE_THRESHOLD
    except Exception:
        # If the check itself fails, don't block the answer.
        return True


def _format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def build_citations(documents: list[Document]) -> list[dict]:
    """
    Convert (parent) documents into API-friendly source objects with a
    human-readable timestamp and a deep link into the YouTube video.
    """
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