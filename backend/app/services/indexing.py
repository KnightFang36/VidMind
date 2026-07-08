from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.services.document_ingestion import fetch_transcript
from backend.app.services.embedding import get_embeddings


class VideoIndexService:
    """Build and retain one FAISS vector store per video."""

    def __init__(self) -> None:
        self._stores: dict[str, FAISS] = {}
        self._chunk_counts: dict[str, int] = {}
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def index_video(self, video_id: str, *, force: bool = False) -> int:
        video_id = video_id.strip()
        if not video_id:
            raise ValueError("video_id cannot be blank.")
        if not force and video_id in self._stores:
            return self._chunk_counts[video_id]

        transcript = fetch_transcript(video_id)
        chunks = self._splitter.create_documents([transcript])
        self._stores[video_id] = FAISS.from_documents(chunks, get_embeddings())
        self._chunk_counts[video_id] = len(chunks)
        return len(chunks)

    def get_retriever(self, video_id: str):
        try:
            store = self._stores[video_id]
        except KeyError:
            raise KeyError(video_id) from None
        return store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
