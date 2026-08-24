import asyncio

import pytest
from fastapi import HTTPException

from routes import games as games_route


class FakeCursor:
    def __init__(self, games):
        self.games = games
        self.index = 0

    def sort(self, *_args):
        return self

    def limit(self, limit):
        self.games = self.games[:limit]
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.games):
            raise StopAsyncIteration

        game = self.games[self.index]
        self.index += 1
        return game


class FakeCollection:
    def __init__(self, games):
        self.games = games
        self.query = None

    def find(self, query=None):
        self.query = query
        return FakeCursor(self.games.copy())


def test_normalize_username_rejects_invalid_input():
    with pytest.raises(HTTPException) as error:
        games_route.normalize_username("bad user!")

    assert error.value.status_code == 422


def test_user_games_are_returned_newest_first_query(monkeypatch):
    collection = FakeCollection(
        [
            {
                "_id": "mongo-id",
                "id": "game-1",
                "createdAt": 20,
                "moves": "e4 e5",
            }
        ]
    )
    monkeypatch.setattr(games_route, "games_collection", collection)

    result = asyncio.run(games_route.get_games_by_user("EricRosen", 50))

    assert result[0]["_id"] == "mongo-id"
    white_query = collection.query["$or"][0]["players.white.user.id"]
    assert white_query["$regex"] == "^ericrosen$"
    assert white_query["$options"] == "i"


def test_unknown_user_returns_not_found(monkeypatch):
    monkeypatch.setattr(games_route, "games_collection", FakeCollection([]))

    with pytest.raises(HTTPException) as error:
        asyncio.run(games_route.get_games_by_user("unknown-player", 50))

    assert error.value.status_code == 404
    assert "@unknown-player" in error.value.detail
