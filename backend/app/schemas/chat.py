from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    video_id: str = Field(min_length=1, max_length=32)
    query: str = Field(min_length=1, max_length=4000)


class SourceChunk(BaseModel):
    content: str
    chunk_index: int | None = None


class ChatResponse(BaseModel):
    video_id: str
    query: str
    answer: str
    sources: list[SourceChunk] = []