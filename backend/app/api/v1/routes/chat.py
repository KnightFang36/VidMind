from fastapi import APIRouter, HTTPException, Request
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import RagService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    service: RagService = request.app.state.rag
    try:
        result = service.answer(
            payload.video_id,
            payload.query,
            history=getattr(payload, "history", None),  # enables memory if sent
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ChatResponse(
        video_id=payload.video_id,
        query=payload.query,
        answer=result.answer,
        sources=result.sources,
        standalone_question=result.standalone_question,  # optional new field
        grounded=result.grounded,                          # optional new field
    )