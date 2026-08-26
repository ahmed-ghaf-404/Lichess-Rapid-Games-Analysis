import re
import logging

from fastapi import APIRouter, HTTPException, Query, status

from db import games_collection


router = APIRouter(prefix="/games", tags=["games"])
LICHESS_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{2,30}$")
logger = logging.getLogger(__name__)


def normalize_username(username: str) -> str:
    normalized = username.strip().lower()

    if not LICHESS_USERNAME_PATTERN.fullmatch(normalized):
        logger.warning("games.invalid_username username=%r", username)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Use 2–30 letters, numbers, underscores, or hyphens.",
        )

    return normalized


def clean_game(game: dict) -> dict:
    cleaned = dict(game)
    cleaned["_id"] = str(cleaned["_id"])
    return cleaned


async def collect_games(cursor) -> list[dict]:
    return [clean_game(game) async for game in cursor]


@router.get("/")
async def get_games(limit: int = Query(default=50, ge=1, le=200)):
    logger.debug("games.list_started limit=%d", limit)
    cursor = games_collection.find().limit(limit)
    games = await collect_games(cursor)
    logger.info("games.list_completed count=%d limit=%d", len(games), limit)
    return games


@router.get("/user/{username}")
async def get_games_by_user(
    username: str,
    limit: int = Query(default=50, ge=1, le=200),
):
    normalized_username = normalize_username(username)
    logger.debug("games.user_lookup_started username=%s limit=%d", normalized_username, limit)
    exact_username = {
        "$regex": f"^{re.escape(normalized_username)}$",
        "$options": "i",
    }
    cursor = games_collection.find(
        {
            "$or": [
                {"players.white.user.id": exact_username},
                {"players.black.user.id": exact_username},
            ]
        }
    ).sort("createdAt", -1).limit(limit)

    games = await collect_games(cursor)

    if not games:
        logger.info("games.user_fallback_to_masters username=%s", normalized_username)
        return []

    logger.info("games.user_lookup_completed username=%s count=%d", normalized_username, len(games))
    return games


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_games():
    from ingest import ingest

    logger.info("games.ingest_started")
    try:
        result = ingest()
        if hasattr(result, "__await__"):
            await result
    except Exception:
        logger.exception("games.ingest_failed")
        raise

    logger.info("games.ingest_completed")
    return {"status": "ingested"}
