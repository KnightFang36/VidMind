from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.index import IndexRequest, IndexResponse
from app.services.indexing import VideoIndexService

router = APIRouter(prefix="/index", tags=["index"])


@router.post("", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
def index_video(payload: IndexRequest, request: Request) -> IndexResponse:
    service: VideoIndexService = request.app.state.video_index
    try:
        chunk_count = service.index_video(payload.video_id, force=payload.force)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return IndexResponse(video_id=payload.video_id, chunks_indexed=chunk_count)
