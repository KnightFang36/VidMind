from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    video_id: str = Field(min_length=1, max_length=32)
    query: str = Field(min_length=1, max_length=4000)
    # Optional prior conversation turns to enable conversation memory (#10).
    # Each item: {"role": "user" | "assistant", "content": "..."}
    history: list[dict] | None = None


class SourceChunk(BaseModel):
    # New richer citation shape emitted by guardrails.build_citations().
    video_id: str | None = None
    parent_id: str | None = None
    chunk_index: int | None = None
    start_seconds: float | None = None
    timestamp: str | None = None          # e.g. "2:05" or "1:02:05"
    url: str | None = None                # deep link: ...watch?v=<id>&t=<sec>s
    snippet: str | None = None            # was previously "content"


class ChatResponse(BaseModel):
    video_id: str
    query: str
    answer: str
    sources: list[SourceChunk] = []
    standalone_question: str | None = None   # rewritten question used for retrieval
    grounded: bool = True                    # False when the hallucination guard refused