# services/embedding.py
#
# Upgrade — stronger embeddings + embedding cache (suggestion #15 & #18)
#   • Default model: BAAI/bge-large-en-v1.5  (override via EMBEDDING_MODEL)
#   • normalize_embeddings=True  -> clean cosine similarity
#   • CacheBackedEmbeddings persists vectors to disk so re-indexing the same
#     text never recomputes an embedding (big cost / latency win).

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_huggingface import HuggingFaceEmbeddings

from backend.app.core.config import get_settings

# Recommended production-grade models (set via EMBEDDING_MODEL env var):
#   BAAI/bge-large-en-v1.5        — strong English retrieval (default)
#   BAAI/bge-m3                   — multilingual
#   nomic-ai/nomic-embed-text-v1  — long context
_DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"

# Where cached embedding vectors live on disk.
_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "embedding_cache"


@lru_cache(maxsize=1)
def _base_embeddings() -> HuggingFaceEmbeddings:
    settings = get_settings()
    model_name = getattr(settings, "embedding_model", None) or _DEFAULT_MODEL
    device = getattr(settings, "embedding_device", None) or "cpu"
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},          # set "cuda" if a GPU is available
        encode_kwargs={"normalize_embeddings": True},
    )


@lru_cache(maxsize=1)
def get_embeddings() -> CacheBackedEmbeddings:
    """
    Return a cached, disk-backed embeddings instance.

    Documents that were embedded before are read straight from the local
    file store instead of being recomputed.
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    store = LocalFileStore(str(_CACHE_DIR))
    base = _base_embeddings()
    model_name = getattr(get_settings(), "embedding_model", None) or _DEFAULT_MODEL
    return CacheBackedEmbeddings.from_bytes_store(
        base,
        store,
        namespace=model_name,          # namespacing avoids cross-model collisions
        query_embedding_cache=True,    # also cache query vectors
    )