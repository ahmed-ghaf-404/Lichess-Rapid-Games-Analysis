import asyncio
from pprint import pprint
from app.db.mongo import get_db


async def main():
    db = get_db()
    col = db.position_move_stats

    print("count:", await col.count_documents({}))

    sample = await col.find_one({})
    pprint(sample)

    top_dense = await col.find({"total_games": {"$gte": 5}}).limit(5).to_list(length=5)
    print("\nSample dense docs:")
    for doc in top_dense:
        pprint({
            "fen_before": doc["fen_before"],
            "side_to_move": doc["side_to_move"],
            "rating_bucket": doc["rating_bucket"],
            "total_games": doc["total_games"],
            "top_moves": doc["moves"][:3],
        })


if __name__ == "__main__":
    asyncio.run(main())