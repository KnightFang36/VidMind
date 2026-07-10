# services/retrieval.py
#
# Advanced retrieval stack layered on top of the hybrid base retriever:
#
#   #11 Adaptive Top-K   -> easy questions fetch fewer chunks, hard ones fetch more
#   MultiQueryRetriever  -> LLM rewrites the query into several variations to
#                           improve recall
#   Cross-Encoder Rerank -> re-scores candidates with a cross-encoder for precision
#   #7  Context Compress. -> redundant-filter + rerank trims ~20 chunks down to ~5
#
# All heavy models are lazy + cached, and every optional stage degrades
# gracefully (if a model can't load, retrieval still works, just less fancy).

from __future__ import annotations

import re
from functools import lru_cache

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
)
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.document_transformers import EmbeddingsRedundantFilter

from backend.app.core.config import get_settings
from backend.app.services.embedding import get_embeddings

# Cross-encoder reranker model (override via RERANKER_MODEL).
#   BAAI/bge-reranker-base                     — strong, a bit heavier
#   cross-encoder/ms-marco-MiniLM-L-6-v2       — fast, light (default)
_DEFAULT_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# ---------------------------------------------------------------------------
# #11 Adaptive Top-K
# ---------------------------------------------------------------------------
_HARD_HINTS = re.compile(
    r"\b(compare|difference|why|how|explain|list|all|every|steps?|"
    r"pros?\s+and\s+cons?|summar|relationship|versus|vs)\b",
    re.IGNORECASE,
)


def adaptive_top_k(question: str) -> tuple[int, int]:
    """
    Decide how many candidates to fetch (k_sub) and how many to keep after
    compression (k_final) based on the apparent difficulty of the question.

    Returns (k_sub, k_final).
    """
    q = question.strip()
    words = len(q.split())
    hard = bool(_HARD_HINTS.search(q)) or words > 18

    if hard:
        return 16, 8          # hard  -> cast a wide net
    if words <= 6:
        return 6, 2           # easy  -> minimal retrieval
    return 12, 5              # medium


# ---------------------------------------------------------------------------
# Cross-encoder reranker (lazy + cached, degrades gracefully)
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _cross_encoder():
    try:
        from langchain_community.cross_encoders import HuggingFaceCrossEncoder

        model_name = (
            getattr(get_settings(), "reranker_model", None) or _DEFAULT_RERANKER
        )
        return HuggingFaceCrossEncoder(model_name=model_name)
    except Exception:
        # Reranking is optional — if the model can't load, we skip it.
        return None


def _build_compressor(k_final: int):
    """
    #7 Context Compression pipeline:
      1. EmbeddingsRedundantFilter  -> drop near-duplicate chunks
      2. CrossEncoderReranker       -> keep the top-k most relevant chunks
    """
    transformers = [EmbeddingsRedundantFilter(embeddings=get_embeddings())]

    encoder = _cross_encoder()
    if encoder is not None:
        from langchain.retrievers.document_compressors import CrossEncoderReranker

        transformers.append(CrossEncoderReranker(model=encoder, top_n=k_final))

    return DocumentCompressorPipeline(transformers=transformers)


# ---------------------------------------------------------------------------
# Public assembly
# ---------------------------------------------------------------------------
def build_advanced_retriever(base_retriever, llm, k_final: int, *, use_multi_query: bool = True):
    """
    Wrap a base (hybrid) retriever with MultiQuery + compression/rerank.

    base_retriever : the FAISS+BM25 EnsembleRetriever
    llm            : chat model used to generate query variations
    k_final        : number of chunks to keep after compression
    """
    retriever = base_retriever

    # MultiQuery: generate several phrasings to boost recall.
    if use_multi_query:
        try:
            retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)
        except Exception:
            retriever = base_retriever  # degrade gracefully

    # Contextual compression: redundancy filter + cross-encoder rerank.
    compressor = _build_compressor(k_final)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=retriever,
    )