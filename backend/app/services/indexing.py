# services/indexing.py
#
# Upgrades implemented here:
#   #3  Hybrid Retrieval      -> FAISS (dense) + BM25 (sparse) EnsembleRetriever
#   #8  Parent Document Retr. -> small child chunks are indexed for precision,
#                                large parent chunks are returned for context
#   Timestamps                -> every chunk carries a `start` (seconds) so the
#                                Citation Builder can deep-link into the video
#   FAISS disk persistence    -> save_local / load_local  (+ pickled BM25/parents)
#   Path-traversal guard      -> video_id character validation

from __future__ import annotations

import pickle
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from langchain.retrievers import EnsembleRetriever
    from langchain_community.retrievers import BM25Retriever
except ImportError:
    from langchain_core.retrievers import EnsembleRetriever  # type: ignore
    try:
        from langchain_community.retrievers import BM25Retriever
    except ImportError:
        from langchain_text_splitters import BM25Retriever  # type: ignore


from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.services.document_ingestion import (
    TranscriptSegment,
    fetch_transcript_segments,
)
from backend.app.services.embedding import get_embeddings

# ---------------------------------------------------------------------------
# Storage layout
#   data/faiss_indexes/<video_id>/index.faiss  — FAISS dense index (children)
#   data/faiss_indexes/<video_id>/bm25.pkl     — BM25 retriever   (children)
#   data/faiss_indexes/<video_id>/parents.pkl  — parent_id -> parent Document
# ---------------------------------------------------------------------------
INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "faiss_indexes"
_SAFE_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]+$")

# Parent / child chunking (Parent Document Retrieval)
_PARENT_SIZE = 2000
_PARENT_OVERLAP = 200
_CHILD_SIZE = 400
_CHILD_OVERLAP = 80

# Hybrid weighting: 60% semantic, 40% keyword
_FAISS_WEIGHT = 0.6
_BM25_WEIGHT = 0.4

# Candidates each sub-retriever fetches before Reciprocal Rank Fusion.
_K_SUB = 12


@dataclass
class _VideoArtifacts:
    faiss: FAISS
    bm25: BM25Retriever
    parents: dict[str, Document]
    child_count: int


class VideoIndexService:
    """Build and retain a hybrid + parent-document index per video."""

    def __init__(self) -> None:
        self._cache: dict[str, _VideoArtifacts] = {}
        self._parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=_PARENT_SIZE,
            chunk_overlap=_PARENT_OVERLAP,
        )
        self._child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=_CHILD_SIZE,
            chunk_overlap=_CHILD_OVERLAP,
        )
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------
    def _dir(self, video_id: str) -> Path:
        if not _SAFE_VIDEO_ID.match(video_id):
            raise ValueError(f"video_id '{video_id}' contains unsupported characters.")
        return INDEX_DIR / video_id

    def _parents_path(self, video_id: str) -> Path:
        return self._dir(video_id) / "parents.pkl"

    def _bm25_path(self, video_id: str) -> Path:
        return self._dir(video_id) / "bm25.pkl"

    # ------------------------------------------------------------------
    # Chunk construction with timestamp propagation
    # ------------------------------------------------------------------
    def _build_documents(
        self, video_id: str, segments: list[TranscriptSegment]
    ) -> tuple[list[Document], dict[str, Document]]:
        """
        Turn timestamped segments into:
          • child docs  (small, indexed for retrieval)
          • parents map (large, returned for context)

        Timestamps are propagated by tracking each segment's character offset
        in the concatenated transcript and mapping chunk offsets back to a time.
        """
        # Concatenate while recording (char_offset -> start_seconds) checkpoints.
        offsets: list[tuple[int, float]] = []
        cursor = 0
        pieces: list[str] = []
        for seg in segments:
            offsets.append((cursor, seg.start))
            pieces.append(seg.text)
            cursor += len(seg.text) + 1  # +1 for the join space
        full_text = " ".join(pieces)

        def time_at(offset: int) -> float:
            """Nearest segment start time at or before a character offset."""
            best = 0.0
            for off, start in offsets:
                if off <= offset:
                    best = start
                else:
                    break
            return best

        parents: dict[str, Document] = {}
        child_docs: list[Document] = []
        child_index = 0
        search_from = 0

        parent_texts = self._parent_splitter.split_text(full_text)
        for p_i, p_text in enumerate(parent_texts):
            # locate this parent's offset to derive its timestamp
            p_offset = full_text.find(p_text, search_from)
            if p_offset == -1:
                p_offset = search_from
            search_from = max(search_from, p_offset + 1)
            p_start = time_at(p_offset)
            parent_id = f"{video_id}-p{p_i}"

            parents[parent_id] = Document(
                page_content=p_text,
                metadata={
                    "parent_id": parent_id,
                    "video_id": video_id,
                    "start": round(p_start, 2),
                },
            )

            # split the parent into children
            local_from = 0
            for c_text in self._child_splitter.split_text(p_text):
                c_local = p_text.find(c_text, local_from)
                if c_local == -1:
                    c_local = local_from
                local_from = max(local_from, c_local + 1)
                c_start = time_at(p_offset + c_local)

                child_docs.append(
                    Document(
                        page_content=c_text,
                        metadata={
                            "chunk_index": child_index,
                            "parent_id": parent_id,
                            "video_id": video_id,
                            "start": round(c_start, 2),
                        },
                    )
                )
                child_index += 1

        return child_docs, parents

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load_from_disk(self, video_id: str) -> _VideoArtifacts | None:
        d = self._dir(video_id)
        faiss_file = d / "index.faiss"
        if not (faiss_file.exists() and self._bm25_path(video_id).exists()
                and self._parents_path(video_id).exists()):
            return None

        faiss = FAISS.load_local(
            str(d), get_embeddings(), allow_dangerous_deserialization=True
        )
        with self._bm25_path(video_id).open("rb") as fh:
            bm25 = pickle.load(fh)  # noqa: S301 — trusted local artifact
        with self._parents_path(video_id).open("rb") as fh:
            parents = pickle.load(fh)  # noqa: S301
        return _VideoArtifacts(faiss, bm25, parents, faiss.index.ntotal)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def index_video(self, video_id: str, *, force: bool = False) -> int:
        video_id = video_id.strip()
        if not video_id:
            raise ValueError("video_id cannot be blank.")

        if not force:
            if video_id in self._cache:
                return self._cache[video_id].child_count
            disk = self._load_from_disk(video_id)
            if disk:
                self._cache[video_id] = disk
                return disk.child_count

        segments = fetch_transcript_segments(video_id)
        child_docs, parents = self._build_documents(video_id, segments)
        if not child_docs:
            raise ValueError("Transcript produced zero chunks after splitting.")

        # Dense index (FAISS) over children
        faiss = FAISS.from_documents(child_docs, get_embeddings())
        d = self._dir(video_id)
        d.mkdir(parents=True, exist_ok=True)
        faiss.save_local(str(d))

        # Sparse index (BM25) over children
        bm25 = BM25Retriever.from_documents(child_docs)
        bm25.k = _K_SUB
        with self._bm25_path(video_id).open("wb") as fh:
            pickle.dump(bm25, fh)

        # Parent store
        with self._parents_path(video_id).open("wb") as fh:
            pickle.dump(parents, fh)

        self._cache[video_id] = _VideoArtifacts(faiss, bm25, parents, len(child_docs))
        return len(child_docs)

    def ensure_indexed(self, video_id: str) -> int:
        video_id = video_id.strip()
        if not video_id:
            raise ValueError("video_id cannot be blank.")
        if video_id in self._cache:
            return self._cache[video_id].child_count
        disk = self._load_from_disk(video_id)
        if disk:
            self._cache[video_id] = disk
            return disk.child_count
        return self.index_video(video_id)

    def _artifacts(self, video_id: str) -> _VideoArtifacts:
        if video_id not in self._cache:
            self.ensure_indexed(video_id)
        return self._cache[video_id]

    def get_hybrid_retriever(self, video_id: str, k_sub: int = _K_SUB) -> EnsembleRetriever:
        """Return the FAISS + BM25 EnsembleRetriever (Reciprocal Rank Fusion)."""
        art = self._artifacts(video_id)

        faiss_retriever = art.faiss.as_retriever(
            search_type="similarity", search_kwargs={"k": k_sub}
        )
        art.bm25.k = k_sub

        return EnsembleRetriever(
            retrievers=[faiss_retriever, art.bm25],
            weights=[_FAISS_WEIGHT, _BM25_WEIGHT],
        )

    def get_parents(self, video_id: str, documents: list[Document]) -> list[Document]:
        """
        Parent Document Retrieval: map retrieved child chunks back to their
        (larger) parent documents, de-duplicated and order-preserving.
        """
        art = self._artifacts(video_id)
        seen: set[str] = set()
        parents: list[Document] = []
        for doc in documents:
            pid = doc.metadata.get("parent_id")
            if pid and pid not in seen and pid in art.parents:
                seen.add(pid)
                parents.append(art.parents[pid])
        return parents