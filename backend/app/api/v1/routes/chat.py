"""Chat endpoint with sync + streaming support."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import RagService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Answer a question about a video (non-streaming)."""
    service: RagService = request.app.state.rag
    
    try:
        result = service.answer(
            payload.video_id, 
            payload.query, 
            history=payload.history
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    
    return ChatResponse(
        video_id=payload.video_id,
        query=payload.query,
        answer=result.answer,
        sources=result.sources,
        standalone_question=result.standalone_question,
        grounded=result.grounded,
    )


@router.post("/stream")
def chat_stream(payload: ChatRequest, request: Request):
    """Stream answer tokens in real-time (Server-Sent Events)."""
    service: RagService = request.app.state.rag
    
    def generate():
        try:
            for event in service.answer_stream(
                payload.video_id, 
                payload.query, 
                history=payload.history
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except ValueError as exc:
            yield f"data: {json.dumps({'type': 'error', 'data': str(exc)})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'data': 'Internal server error'})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")