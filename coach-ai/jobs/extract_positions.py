import asyncio
from datetime import datetime
from typing import Any
from pymongo import ReplaceOne

import chess
from app.db.mongo import get_db


def parse_user_context(game: dict[str, Any], target_user_id: str) -> tuple[str, int | None, int | None]:
    white_id = game["players"]["white"]["user"]["id"]
    black_id = game["players"]["black"]["user"]["id"]

    if target_user_id == white_id:
        color = "white"
        user_rating = game["players"]["white"].get("rating")
        opp_rating = game["players"]["black"].get("rating")
    else:
        color = "black"
        user_rating = game["players"]["black"].get("rating")
        opp_rating = game["players"]["white"].get("rating")

    return color, user_rating, opp_rating


def normalize_result(game: dict[str, Any], user_color: str) -> str:
    winner = game.get("winner")
    if not winner:
        return "draw"
    return "win" if winner == user_color else "loss"


async def extract_game(game: dict[str, Any], target_user_id: str) -> list[dict]:
    board = chess.Board()
    rows: list[dict] = []

    user_color, user_rating, opp_rating = parse_user_context(game, target_user_id)
    result = normalize_result(game, user_color)
    moves = game.get("moves", "").split()

    for ply_index, san in enumerate(moves[:20], start=1):
        side_to_move = "white" if board.turn == chess.WHITE else "black"
        fen_before = board.fen()

        try:
            move = board.parse_san(san)
        except ValueError:
            break

        move_uci = move.uci()
        is_user_turn = side_to_move == user_color

        if is_user_turn:
            rows.append(
                {
                    "game_id": game["id"],
                    "user_id": target_user_id,
                    "fen_before": fen_before,
                    "ply": ply_index,
                    "move_number": (ply_index + 1) // 2,
                    "side_to_move": side_to_move,
                    "user_color": user_color,
                    "move_played_san": san,
                    "move_played_uci": move_uci,
                    "user_rating": user_rating,
                    "opponent_rating": opp_rating,
                    "speed": game.get("speed"),
                    "opening_eco": (game.get("opening") or {}).get("eco"),
                    "opening_name": (game.get("opening") or {}).get("name"),
                    "opening_declared_ply": (game.get("opening") or {}).get("ply"),
                    "game_result_for_user": result,
                    "created_at": game.get("createdAt"),
                    "last_move_at": game.get("lastMoveAt"),
                }
            )

        board.push(move)

    return rows


async def main() -> None:
    db = get_db()

    games = await db.games.find({}).to_list(length=100000)
    operations = []

    for game in games:
        white_id = game["players"]["white"]["user"]["id"]
        black_id = game["players"]["black"]["user"]["id"]

        for user_id in [white_id, black_id]:
            extracted = await extract_game(game, user_id)

            for doc in extracted:
                doc["_id"] = f'{doc["game_id"]}:{doc["user_id"]}:{doc["ply"]}'
                operations.append(
                    ReplaceOne(
                        {"_id": doc["_id"]},
                        doc,
                        upsert=True,
                    )
                )

    print("operations prepared:", len(operations))

    if operations:
        BATCH_SIZE = 500

        for i in range(0, len(operations), BATCH_SIZE):
            batch = operations[i:i + BATCH_SIZE]
            await db.position_events.bulk_write(batch, ordered=False)
            print(f"Upserted batch {i // BATCH_SIZE + 1} ({len(batch)} ops)")

        await db.position_events.create_index(
            [("fen_before", 1), ("side_to_move", 1), ("user_rating", 1)]
        )

        await db.position_events.create_index([("user_id", 1), ("created_at", -1)])
        

    print(f"Processed {len(operations)} position_events")


if __name__ == "__main__":
    asyncio.run(main())