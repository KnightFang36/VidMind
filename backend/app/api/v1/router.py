
from fastapi import APIRouter

from backend.app.api.v1.routes.chat import router as chat_router
from backend.app.api.v1.routes.index import router as index_router

api_router = APIRouter(prefix="/v1")
api_router.include_router(chat_router)
api_router.include_router(index_router)