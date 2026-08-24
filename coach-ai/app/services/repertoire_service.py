from app.db.mongo import get_db
from app.services.position_key import position_fen_pattern


class RepertoireService:
    async def get_move_fits(
        self,
        user_id: str,
        fen: str,
        move_ucis: list[str],
    ) -> dict[str, float]:
        if not move_ucis:
            return {}

        cursor = await get_db().position_events.aggregate(
            [
                {
                    "$match": {
                        "user_id": user_id.lower(),
                        "fen_before": {"$regex": position_fen_pattern(fen)},
                    }
                },
                {"$group": {"_id": "$move_played_uci", "count": {"$sum": 1}}},
            ]
        )
        move_counts = {document["_id"]: document["count"] async for document in cursor}
        total = sum(move_counts.values())
        if total == 0:
            return {move_uci: 0.0 for move_uci in move_ucis}

        return {
            move_uci: move_counts.get(move_uci, 0) / total
            for move_uci in move_ucis
        }

    async def get_move_fit(self, user_id: str, fen: str, move_uci: str) -> float:
        return (await self.get_move_fits(user_id, fen, [move_uci]))[move_uci]
