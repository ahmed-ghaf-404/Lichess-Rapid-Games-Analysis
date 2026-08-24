from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.recommend import router as recommend_router
from app.core.config import settings
from app.core.logging import configure_logging, request_logging_middleware

from dotenv import load_dotenv
import os

load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)


def get_allowed_origins() -> list[str]:
    configured = os.getenv("CHESS_UI_URL", "http://localhost:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(
        "service.startup log_level=%s engine_depth=%d",
        os.getenv("LOG_LEVEL", "INFO").upper(),
        settings.engine_depth,
    )
    if os.path.isfile(settings.stockfish_path) and os.access(settings.stockfish_path, os.X_OK):
        logger.info("dependency.ready name=stockfish path=%s", settings.stockfish_path)
    else:
        logger.critical(
            "dependency.missing name=stockfish path=%s hint=install_stockfish_or_set_STOCKFISH_PATH",
            settings.stockfish_path,
        )
    yield
    logger.info("service.shutdown")


app = FastAPI(title="Choco Chess Coach AI", version="0.1.0", lifespan=lifespan)

app.middleware("http")(request_logging_middleware)

app.include_router(recommend_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

@app.get("/health")
async def health():
    logger.debug("health.checked")
    return {"ok": True}
