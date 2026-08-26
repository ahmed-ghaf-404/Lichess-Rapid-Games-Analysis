from app.db.mongo import get_db
from app.services.position_key import position_fen_pattern
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

        cursor = db.position_move_stats.find(
            {
                "fen_before": {"$regex": position_fen_pattern(fen)},
                "side_to_move": side_to_move,
                "rating_bucket": rating_bucket,
            }
        )
        documents = [document async for document in cursor]

        if not documents:
            return {
                "rating_bucket": rating_bucket,
                "side_to_move": side_to_move,
                "total_games": 0,
                "moves": [],
                "statistics_source": "peer",
                "statistics_available": True,
            }

        total_games = sum(document.get("total_games", 0) for document in documents)
        aggregated_moves: dict[str, dict] = {}
        for document in documents:
            for move in document.get("moves", []):
                games = move.get("games", 0)
                current = aggregated_moves.setdefault(
                    move["move_uci"],
                    {
                        "move_uci": move["move_uci"],
                        "move_san": move.get("move_san", move["move_uci"]),
                        "games": 0,
                        "weighted_score": 0.0,
                    },
                )
                current["games"] += games
                current["weighted_score"] += move.get("win_rate", 0.0) * games

        moves = []
        for move in aggregated_moves.values():
            games = move["games"]
            moves.append(
                {
                    "move_uci": move["move_uci"],
                    "move_san": move["move_san"],
                    "games": games,
                    "frequency": games / total_games if total_games else 0.0,
                    "win_rate": move["weighted_score"] / games if games else 0.0,
                }
            )
        moves.sort(key=lambda move: move["games"], reverse=True)

        return {
            "rating_bucket": rating_bucket,
            "side_to_move": side_to_move,
            "total_games": total_games,
            "moves": moves[:limit],
            "statistics_source": "peer",
            "statistics_available": True,
        }
