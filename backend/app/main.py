import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.indexing import VideoIndexService
from app.services.rag import RagService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

video_index = VideoIndexService()
rag_service = RagService(video_index)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VidMind backend starting up")
    yield
    logger.info("VidMind backend shutting down")


app = FastAPI(
    title="VidMind",
    description="Chat with any YouTube video",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.video_index = video_index
app.state.rag = rag_service


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")