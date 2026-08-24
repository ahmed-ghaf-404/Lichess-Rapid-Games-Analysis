import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.core.config import settings
from app.schemas.repertoire import (
    RepertoireLineCreate,
    RepertoireLineResponse,
    RepertoireMoveCreate,
    RepertoireMoveResponse,
)
from app.services.repertoire_store import (
    add_move,
    create_line,
    delete_line,
    list_lines,
    remove_move,
)


router = APIRouter(prefix="/repertoire", tags=["repertoire"])
logger = logging.getLogger(__name__)


def allowed_users() -> set[str]:
    return {
        user.strip().lower()
        for user in settings.repertoire_users.split(",")
        if user.strip()
    }


def require_allowed_user(user_id: str) -> str:
    normalized = user_id.strip().lower()
    if normalized not in allowed_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Repertoire access is not enabled for this player.",
        )
    return normalized


def require_write_key(supplied_key: str | None) -> None:
    configured_key = settings.repertoire_write_key
    if len(configured_key) < 16:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repertoire editing is not configured.",
        )
    if not supplied_key or not hmac.compare_digest(configured_key, supplied_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid repertoire management key is required.",
        )


@router.get("/{user_id}", response_model=list[RepertoireLineResponse])
async def get_repertoire(user_id: str) -> list[dict]:
    normalized = require_allowed_user(user_id)
    return await list_lines(normalized)


@router.post(
    "/lines",
    response_model=RepertoireLineResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_repertoire_line(
    payload: RepertoireLineCreate,
    repertoire_key: str | None = Header(default=None, alias="X-Repertoire-Key"),
) -> dict:
    require_write_key(repertoire_key)
    payload.user_id = require_allowed_user(payload.user_id)
    try:
        line = await create_line(payload)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    logger.info("repertoire.line_created user_id=%s line_id=%s", payload.user_id, line["id"])
    return line


@router.post(
    "/lines/{line_id}/moves",
    response_model=RepertoireMoveResponse,
    status_code=status.HTTP_201_CREATED,
)
async def approve_repertoire_move(
    line_id: str,
    payload: RepertoireMoveCreate,
    repertoire_key: str | None = Header(default=None, alias="X-Repertoire-Key"),
) -> dict:
    require_write_key(repertoire_key)
    payload.user_id = require_allowed_user(payload.user_id)
    try:
        move = await add_move(line_id, payload)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    logger.info(
        "repertoire.move_approved user_id=%s line_id=%s move=%s",
        payload.user_id,
        line_id,
        move["move_uci"],
    )
    return move


@router.delete("/lines/{line_id}/moves/{move_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repertoire_move(
    line_id: str,
    move_id: str,
    user_id: str = Query(...),
    repertoire_key: str | None = Header(default=None, alias="X-Repertoire-Key"),
) -> None:
    require_write_key(repertoire_key)
    normalized = require_allowed_user(user_id)
    try:
        removed = await remove_move(line_id, move_id, normalized)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not removed:
        raise HTTPException(status_code=404, detail="The saved move was not found.")


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repertoire_line(
    line_id: str,
    user_id: str = Query(...),
    repertoire_key: str | None = Header(default=None, alias="X-Repertoire-Key"),
) -> None:
    require_write_key(repertoire_key)
    normalized = require_allowed_user(user_id)
    try:
        removed = await delete_line(line_id, normalized)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not removed:
        raise HTTPException(status_code=404, detail="The repertoire line was not found.")
