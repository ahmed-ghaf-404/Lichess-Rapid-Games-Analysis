from datetime import datetime, timezone
import uuid

import chess
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.db.mongo import get_db
from app.schemas.repertoire import RepertoireLineCreate, RepertoireMoveCreate
from app.services.position_key import position_key


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def serialize_line(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "user_id": document["user_id"],
        "name": document["name"],
        "opening_name": document["opening_name"],
        "parent_line_id": (
            str(document["parent_line_id"]) if document.get("parent_line_id") else None
        ),
        "moves": [
            {
                **move,
                "approved_at": move["approved_at"].isoformat(),
            }
            for move in document.get("moves", [])
        ],
        "created_at": document["created_at"].isoformat(),
        "updated_at": document["updated_at"].isoformat(),
    }


async def ensure_repertoire_indexes() -> None:
    collection = get_db().repertoire_lines
    await collection.create_index(
        [("user_id", 1), ("name", 1)],
        unique=True,
        name="unique_user_repertoire_line_name",
    )
    await collection.create_index(
        [("user_id", 1), ("moves.position_key", 1)],
        name="repertoire_position_lookup",
    )


async def list_lines(user_id: str) -> list[dict]:
    cursor = get_db().repertoire_lines.find({"user_id": user_id}).sort(
        [("opening_name", 1), ("name", 1)]
    )
    return [serialize_line(document) async for document in cursor]


async def create_line(payload: RepertoireLineCreate) -> dict:
    collection = get_db().repertoire_lines
    parent_id = None

    if payload.parent_line_id:
        if not ObjectId.is_valid(payload.parent_line_id):
            raise ValueError("Invalid parent repertoire line.")
        parent_id = ObjectId(payload.parent_line_id)
        parent = await collection.find_one(
            {"_id": parent_id, "user_id": payload.user_id.lower()}
        )
        if parent is None:
            raise ValueError("The parent repertoire line was not found.")

    now = utc_now()
    document = {
        "user_id": payload.user_id.lower(),
        "name": payload.name.strip(),
        "opening_name": payload.opening_name.strip(),
        "parent_line_id": parent_id,
        "moves": [],
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = await collection.insert_one(document)
    except DuplicateKeyError as exc:
        raise FileExistsError("A repertoire line with this name already exists.") from exc

    document["_id"] = result.inserted_id
    return serialize_line(document)


async def add_move(line_id: str, payload: RepertoireMoveCreate) -> dict:
    if not ObjectId.is_valid(line_id):
        raise ValueError("Invalid repertoire line.")

    collection = get_db().repertoire_lines
    object_id = ObjectId(line_id)
    user_id = payload.user_id.lower()
    line = await collection.find_one({"_id": object_id, "user_id": user_id})
    if line is None:
        raise LookupError("The repertoire line was not found.")

    board = chess.Board(payload.fen_before)
    move = chess.Move.from_uci(payload.move_uci)
    if move not in board.legal_moves:
        raise ValueError("The selected move is not legal in this position.")

    normalized_fen = board.fen()
    key = position_key(normalized_fen)
    san = board.san(move)
    board.push(move)

    existing = next(
        (
            item
            for item in line.get("moves", [])
            if item["position_key"] == key and item["move_uci"] == payload.move_uci
        ),
        None,
    )
    if existing:
        raise FileExistsError("This move is already saved in the selected line.")

    repertoire_move = {
        "id": str(uuid.uuid4()),
        "position_key": key,
        "fen_before": normalized_fen,
        "fen_after": board.fen(),
        "move_uci": payload.move_uci,
        "move_san": san,
        "source": payload.source,
        "approved_at": utc_now(),
    }

    await collection.update_one(
        {"_id": object_id, "user_id": user_id},
        {"$push": {"moves": repertoire_move}, "$set": {"updated_at": utc_now()}},
    )
    return {
        **repertoire_move,
        "approved_at": repertoire_move["approved_at"].isoformat(),
    }


async def remove_move(line_id: str, move_id: str, user_id: str) -> bool:
    if not ObjectId.is_valid(line_id):
        raise ValueError("Invalid repertoire line.")
    result = await get_db().repertoire_lines.update_one(
        {"_id": ObjectId(line_id), "user_id": user_id.lower()},
        {"$pull": {"moves": {"id": move_id}}, "$set": {"updated_at": utc_now()}},
    )
    return result.modified_count > 0


async def delete_line(line_id: str, user_id: str) -> bool:
    if not ObjectId.is_valid(line_id):
        raise ValueError("Invalid repertoire line.")
    object_id = ObjectId(line_id)
    collection = get_db().repertoire_lines
    child = await collection.find_one(
        {"user_id": user_id.lower(), "parent_line_id": object_id}
    )
    if child:
        raise RuntimeError("Delete nested lines before deleting their parent line.")
    result = await collection.delete_one({"_id": object_id, "user_id": user_id.lower()})
    return result.deleted_count > 0
