import os

import pytest
from fastapi import HTTPException


os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.api import repertoire as repertoire_api  # noqa: E402
from app.services.repertoire_store import position_key  # noqa: E402


def test_position_key_ignores_move_clocks():
    first = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    later = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 18 42"

    assert position_key(first) == position_key(later)


def test_repertoire_is_limited_to_selected_users(monkeypatch):
    monkeypatch.setattr(
        repertoire_api.settings,
        "repertoire_users",
        "ericrosen,chocoroku",
    )

    assert repertoire_api.require_allowed_user("EricRosen") == "ericrosen"

    with pytest.raises(HTTPException) as error:
        repertoire_api.require_allowed_user("another-player")

    assert error.value.status_code == 403


def test_repertoire_writes_require_private_management_key(monkeypatch):
    monkeypatch.setattr(
        repertoire_api.settings,
        "repertoire_write_key",
        "a-private-test-management-key",
    )

    repertoire_api.require_write_key("a-private-test-management-key")

    with pytest.raises(HTTPException) as error:
        repertoire_api.require_write_key("wrong-key")

    assert error.value.status_code == 401
