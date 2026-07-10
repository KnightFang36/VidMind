"""Modern RAG pipeline services.

Pipeline stages:
  document_ingestion  — timestamped transcript fetching
  embedding           — bge-large embeddings + disk cache
  indexing            — hybrid (FAISS + BM25) + parent-document index
  retrieval           — adaptive top-k, MultiQuery, cross-encoder rerank, compression
  memory              — conversation memory + standalone question generation
  guardrails          — hallucination guard + timestamped citation builder
  cache               — TTL/LRU caches for retrieval + answers
  rag                 — end-to-end orchestration (sync + streaming)
"""

from backend.app.services.document_ingestion import (
    TranscriptSegment,
    fetch_transcript,
    fetch_transcript_segments,
)
from backend.app.services.embedding import get_embeddings
from backend.app.services.guardrails import build_citations, has_sufficient_evidence
from backend.app.services.indexing import VideoIndexService
from backend.app.services.memory import ConversationMemory, build_standalone_question
from backend.app.services.rag import RagAnswer, RagService

__all__ = [
    "TranscriptSegment",
    "fetch_transcript",
    "fetch_transcript_segments",
    "get_embeddings",
    "build_citations",
    "has_sufficient_evidence",
    "VideoIndexService",
    "ConversationMemory",
    "build_standalone_question",
    "RagAnswer",
    "RagService",
]