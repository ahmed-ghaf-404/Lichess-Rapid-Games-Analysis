import asyncio
from collections import defaultdict
from typing import Any

from pymongo import ReplaceOne

from app.db.mongo import get_db


BATCH_SIZE = 500


def get_rating_bucket(rating: int | None) -> str:
    if rating is None:
        return "unknown"
    if rating < 1200:
        return "0-1199"
    if rating < 1400:
        return "1200-1399"
    if rating < 1600:
        return "1400-1599"
    if rating < 1800:
        return "1600-1799"
    if rating < 2000:
        return "1800-1999"
    if rating < 2200:
        return "2000-2199"
    return "2200+"


def normalize_result_value(result: str | None) -> tuple[int, int, int]:
    if result == "win":
        return 1, 0, 0
    if result == "draw":
        return 0, 1, 0
    return 0, 0, 1


async def main() -> None:
    db = get_db()
    source = db.position_events
    target = db.position_move_stats

    total = await source.count_documents({})
    print(f"position_events count: {total}")

    cursor = source.find(
        {},
        projection={
            "_id": 0,
            "fen_before": 1,
            "side_to_move": 1,
            "user_rating": 1,
            "move_played_uci": 1,
            "move_played_san": 1,
            "game_result_for_user": 1,
            "ply": 1,
            "move_number": 1,
            "opening_eco": 1,
            "opening_name": 1,
        },
    )

    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

    processed = 0
    async for row in cursor:
        processed += 1
        if processed % 50000 == 0:
            print(f"processed {processed}/{total}")

        fen_before = row.get("fen_before")
        side_to_move = row.get("side_to_move")
        move_uci = row.get("move_played_uci")
        move_san = row.get("move_played_san")

        if not fen_before or not side_to_move or not move_uci or not move_san:
            continue

        rating_bucket = get_rating_bucket(row.get("user_rating"))
        key = (fen_before, side_to_move, rating_bucket)

        if key not in grouped:
            grouped[key] = {
                "fen_before": fen_before,
                "side_to_move": side_to_move,
                "rating_bucket": rating_bucket,
                "ply": row.get("ply"),
                "move_number": row.get("move_number"),
                "opening_eco": row.get("opening_eco"),
                "opening_name": row.get("opening_name"),
                "total_games": 0,
                "moves": defaultdict(
                    lambda: {
                        "move_uci": None,
                        "move_san": None,
                        "games": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,
                    }
                ),
            }

        group = grouped[key]
        group["total_games"] += 1

        move_bucket = group["moves"][move_uci]
        move_bucket["move_uci"] = move_uci
        move_bucket["move_san"] = move_san
        move_bucket["games"] += 1

        wins, draws, losses = normalize_result_value(row.get("game_result_for_user"))
        move_bucket["wins"] += wins
        move_bucket["draws"] += draws
        move_bucket["losses"] += losses

    print(f"built in-memory groups: {len(grouped)}")

    operations = []

    for (_, _, _), group in grouped.items():
        total_games = group["total_games"]
        move_docs = []

        for move_data in group["moves"].values():
            games = move_data["games"]
            wins = move_data["wins"]
            draws = move_data["draws"]
            losses = move_data["losses"]

            frequency = games / total_games if total_games else 0.0
            win_rate = (wins + 0.5 * draws) / games if games else 0.0

            move_docs.append(
                {
                    "move_uci": move_data["move_uci"],
                    "move_san": move_data["move_san"],
                    "games": games,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "frequency": round(frequency, 6),
                    "win_rate": round(win_rate, 6),
                }
            )

        move_docs.sort(
            key=lambda m: (m["frequency"], m["win_rate"], m["games"]),
            reverse=True,
        )

        doc_id = f'{group["fen_before"]}|{group["side_to_move"]}|{group["rating_bucket"]}'

        out_doc = {
            "_id": doc_id,
            "fen_before": group["fen_before"],
            "side_to_move": group["side_to_move"],
            "rating_bucket": group["rating_bucket"],
            "ply": group["ply"],
            "move_number": group["move_number"],
            "opening_eco": group["opening_eco"],
            "opening_name": group["opening_name"],
            "total_games": total_games,
            "moves": move_docs,
        }

        operations.append(
            ReplaceOne(
                {"_id": doc_id},
                out_doc,
                upsert=True,
            )
        )

    print(f"prepared upserts: {len(operations)}")

    for i in range(0, len(operations), BATCH_SIZE):
        batch = operations[i:i + BATCH_SIZE]
        await target.bulk_write(batch, ordered=False)
        print(f"upserted batch {i // BATCH_SIZE + 1} ({len(batch)} docs)")

    await target.create_index([("fen_before", 1), ("side_to_move", 1), ("rating_bucket", 1)])
    await target.create_index([("opening_eco", 1), ("rating_bucket", 1)])
    await target.create_index([("opening_name", 1), ("rating_bucket", 1)])

    print("done building position_move_stats")


if __name__ == "__main__":
    asyncio.run(main())