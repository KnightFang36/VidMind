"""Embeddings service using Hugging Face BGE models."""

from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings

_DEFAULT_MODEL = "BAAI/bge-large-en-v1.5"


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a Hugging Face embeddings instance.

    Models are cached in-memory and downloaded to HuggingFace cache on first use.
    The FAISS indexes themselves provide on-disk persistence for embeddings.
    """
    settings = get_settings()
    model_name = getattr(settings, "embedding_model", None) or _DEFAULT_MODEL
    device = getattr(settings, "embedding_device", None) or "cpu"

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )