import re
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.services.document_ingestion import fetch_transcript
from backend.app.services.embedding import get_embeddings

#
INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "faiss_indexes"

_SAFE_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]+$")


class VideoIndexService:
    """Build and retain one FAISS vector store per video, persisted to disk."""

    def __init__(self) -> None:
        self._stores: dict[str, FAISS] = {}
        self._chunk_counts: dict[str, int] = {}
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

    def _index_path(self, video_id: str) -> Path:
        if not _SAFE_VIDEO_ID.match(video_id):
            raise ValueError("video_id contains unsupported characters.")
        return INDEX_DIR / video_id

    def _load_from_disk(self, video_id: str) -> bool:
        path = self._index_path(video_id)
        if not (path / "index.faiss").exists():
            return False

        store = FAISS.load_local(
            str(path),
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
        self._stores[video_id] = store
        self._chunk_counts[video_id] = store.index.ntotal
        return True

    def index_video(self, video_id: str, *, force: bool = False) -> int:
        video_id = video_id.strip()
        if not video_id:
            raise ValueError("video_id cannot be blank.")

        if not force:
            if video_id in self._stores:
                return self._chunk_counts[video_id]
            if self._load_from_disk(video_id):
                return self._chunk_counts[video_id]

        transcript = fetch_transcript(video_id)
        texts = self._splitter.split_text(transcript)
        chunks = [
            Document(page_content=text, metadata={"chunk_index": i})
            for i, text in enumerate(texts)
        ]
        store = FAISS.from_documents(chunks, get_embeddings())
        store.save_local(str(self._index_path(video_id)))

        self._stores[video_id] = store
        self._chunk_counts[video_id] = len(chunks)
        return len(chunks)

    def ensure_indexed(self, video_id: str) -> int:
        video_id = video_id.strip()
        if not video_id:
            raise ValueError("video_id cannot be blank.")

        if video_id in self._stores:
            return self._chunk_counts[video_id]

        if self._load_from_disk(video_id):
            return self._chunk_counts[video_id]

        return self.index_video(video_id)

    def get_retriever(self, video_id: str):
        if video_id not in self._stores:
            self.ensure_indexed(video_id)

        store = self._stores[video_id]
        return store.as_retriever(search_type="similarity", search_kwargs={"k": 4})