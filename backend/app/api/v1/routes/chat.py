from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag import RagService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    service: RagService = request.app.state.rag
    try:
        answer = service.answer(payload.video_id, payload.query)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ChatResponse(video_id=payload.video_id, query=payload.query, answer=answer)
