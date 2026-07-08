from fastapi import APIRouter

from backend.app.api.v1.routes import chat, index

api_router = APIRouter(prefix="/v1")
api_router.include_router(index.router)
api_router.include_router(chat.router)
