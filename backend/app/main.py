from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings
from backend.app.services.indexing import VideoIndexService
from backend.app.services.rag import RagService


@asynccontextmanager
async def lifespan(app: FastAPI):
    video_index = VideoIndexService()
    app.state.video_index = video_index
    app.state.rag = RagService(video_index)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}