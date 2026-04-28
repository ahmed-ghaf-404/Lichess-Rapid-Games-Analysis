from fastapi import APIRouter
from db import games_collection

router = APIRouter(prefix="/games", tags=["games"])


def clean_game(game):
    game["_id"] = str(game["_id"])  # important
    return game


@router.get("/")
async def get_games(limit: int = 50):
    cursor = games_collection.find().limit(limit)

    games = []
    async for game in cursor:
        games.append(clean_game(game))

    return games

@router.get("/user/{username}")
async def get_games_by_user(username: str, limit: int = 50):
    cursor = games_collection.find({
        "$or": [
            {"players.white.user.id": username},
            {"players.black.user.id": username}
        ]
    }).limit(limit)

    games = []
    async for game in cursor:
        games.append(clean_game(game))

    return games


@router.get("/user/{username}")
async def get_games_by_user(username: str, limit: int = 50):
    cursor = games_collection.find({
        "$or": [
            {"players.white.user.id": username},
            {"players.black.user.id": username}
        ]
    }).limit(limit)

    games = []
    async for game in cursor:
        games.append(clean_game(game))

    return games


@router.post("/ingest")
async def ingest_games():
    from ingest import ingest
    await ingest() if callable(ingest) else ingest()
    return {"status": "ingested"}