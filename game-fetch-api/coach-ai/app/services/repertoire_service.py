from app.db.mongo import get_db


class RepertoireService:
    async def get_move_fit(self, user_id: str, fen: str, move_uci: str) -> float:
        db = get_db()

        total = await db.position_events.count_documents(
            {
                "user_id": user_id,
                "fen_before": fen,
            }
        )
        if total == 0:
            return 0.0

        count = await db.position_events.count_documents(
            {
                "user_id": user_id,
                "fen_before": fen,
                "move_played_uci": move_uci,
            }
        )
        return count / total