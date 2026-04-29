import asyncio
from pprint import pprint

from app.db.mongo import get_db


async def main() -> None:
    db = get_db()
    collection = db.position_events

    print("\n=== BASIC COUNTS ===")
    total = await collection.count_documents({})
    print("total position_events:", total)

    distinct_users = await collection.distinct("user_id")
    print("distinct user_id count:", len(distinct_users))
    print("distinct user_ids:", distinct_users[:20])

    print("\n=== SAMPLE DOCUMENTS ===")
    samples = await collection.find({}).limit(3).to_list(length=3)
    for i, doc in enumerate(samples, start=1):
        print(f"\n--- sample {i} ---")
        pprint(doc)

    print("\n=== ROWS PER USER ===")
    pipeline = [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    cursor = await collection.aggregate(pipeline)
    rows_per_user = await cursor.to_list(length=1000)
    for row in rows_per_user[:20]:
        print(f'{row["_id"]}: {row["count"]}')

    print("\n=== MISSING REQUIRED FIELDS ===")
    required_fields = [
        "move_played_san",
        "move_played_uci",
        "fen_before",
        "user_rating",
        "game_result_for_user",
    ]

    for field in required_fields:
        missing_count = await collection.count_documents(
            {
                "$or": [
                    {field: {"$exists": False}},
                    {field: None},
                    {field: ""},
                ]
            }
        )
        print(f"missing {field}: {missing_count}")

    print("\n=== SPECIFIC CHECKS ===")
    missing_fen = await collection.count_documents(
        {
            "$or": [
                {"fen_before": {"$exists": False}},
                {"fen_before": None},
                {"fen_before": ""},
            ]
        }
    )
    missing_move_uci = await collection.count_documents(
        {
            "$or": [
                {"move_played_uci": {"$exists": False}},
                {"move_played_uci": None},
                {"move_played_uci": ""},
            ]
        }
    )
    print("missing fen_before:", missing_fen)
    print("missing move_played_uci:", missing_move_uci)

    print("\n=== SAMPLE ROWS FOR ONE USER ===")
    one_user = distinct_users[0] if distinct_users else None
    if one_user:
        user_rows = await collection.find({"user_id": one_user}).limit(5).to_list(length=5)
        print("user_id:", one_user)
        for doc in user_rows:
            pprint(doc)

    print("\n=== SAMPLE ROWS FOR ONE FEN ===")
    one_fen_doc = await collection.find_one({"fen_before": {"$exists": True, "$ne": ""}})
    if one_fen_doc:
        one_fen = one_fen_doc["fen_before"]
        fen_rows = await collection.find({"fen_before": one_fen}).limit(10).to_list(length=10)
        print("fen_before:", one_fen)
        print("rows for this fen:", len(fen_rows))
        for doc in fen_rows:
            pprint(
                {
                    "user_id": doc.get("user_id"),
                    "move_played_san": doc.get("move_played_san"),
                    "move_played_uci": doc.get("move_played_uci"),
                    "user_rating": doc.get("user_rating"),
                    "game_result_for_user": doc.get("game_result_for_user"),
                    "ply": doc.get("ply"),
                }
            )

    print("\n=== DUPLICATE CHECK ===")
    duplicate_pipeline = [
        {
            "$group": {
                "_id": {
                    "game_id": "$game_id",
                    "user_id": "$user_id",
                    "ply": "$ply",
                },
                "count": {"$sum": 1},
            }
        },
        {"$match": {"count": {"$gt": 1}}},
        {"$limit": 20},
    ]
    cursor = await collection.aggregate(duplicate_pipeline)
    duplicates = await cursor.to_list(length=20)
    print("duplicate key groups found:", len(duplicates))
    for dup in duplicates:
        pprint(dup)

    print("\n=== RESULT VALUE CHECK ===")
    result_pipeline = [
        {"$group": {"_id": "$game_result_for_user", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    cursor = await collection.aggregate(result_pipeline)
    result_counts = await cursor.to_list(length=20)
    for row in result_counts:
        print(f'{row["_id"]}: {row["count"]}')


if __name__ == "__main__":
    asyncio.run(main())