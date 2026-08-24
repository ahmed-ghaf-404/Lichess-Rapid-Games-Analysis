from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from routes.games import router as games_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from logging_config import configure_logging, request_logging_middleware

load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)


def get_allowed_origins() -> list[str]:
    configured = os.getenv("CHESS_UI_URL", "http://localhost:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(
        "service.startup log_level=%s database_configured=%s",
        os.getenv("LOG_LEVEL", "INFO").upper(),
        bool(os.getenv("MONGO_URL")),
    )
    if not os.getenv("MONGO_URL"):
        logger.critical("dependency.missing name=mongodb_configuration variable=MONGO_URL")
    yield
    logger.info("service.shutdown")


app = FastAPI(title="Choco Chess Coach Games API", lifespan=lifespan)

app.middleware("http")(request_logging_middleware)

app.include_router(games_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

@app.get("/")
def root():
    logger.debug("root.checked")
    return {"status": "ok", "message": "Chess API running"}


@app.get("/health", tags=["health"])
def health():
    logger.debug("health.checked")
    return {"status": "healthy"}
