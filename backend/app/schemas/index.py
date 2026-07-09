
from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    video_id: str = Field(min_length=1, max_length=32)
    force: bool = False


class IndexResponse(BaseModel):
    video_id: str
    chunks_indexed: int