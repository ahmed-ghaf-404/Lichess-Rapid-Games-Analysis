import chess

from app.db.mongo import get_db
from app.services.rating_bucket import get_rating_bucket


class PeerStatsService:
    async def get_move_stats(
        self,
        fen: str,
        rating: int | None,
        side_to_move: str,
        limit: int = 8,
    ) -> dict:
        rating_bucket = get_rating_bucket(rating)
        db = get_db()

        doc = await db.position_move_stats.find_one(
            {
                "fen_before": fen,
                "side_to_move": side_to_move,
                "rating_bucket": rating_bucket,
            }
        )

        if not doc:
            return {
                "rating_bucket": rating_bucket,
                "side_to_move": side_to_move,
                "total_games": 0,
                "moves": [],
            }

        moves = doc.get("moves", [])[:limit]

        return {
            "rating_bucket": rating_bucket,
            "side_to_move": side_to_move,
            "total_games": doc.get("total_games", 0),
            "moves": moves,
        }