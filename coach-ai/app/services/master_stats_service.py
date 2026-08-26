import asyncio
from datetime import datetime, timezone
import json
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import chess

from app.core.config import settings
from app.db.mongo import get_db
from app.services.position_key import canonical_position_fen, position_key


logger = logging.getLogger(__name__)


class MasterStatsService:
    """Read master opening statistics locally, filling missing positions from Lichess."""

    collection_name = "master_position_move_stats"

    @staticmethod
    def _fetch_remote(fen: str, limit: int) -> dict:
        query = urlencode(
            {
                "fen": canonical_position_fen(fen),
                "moves": limit,
                "topGames": 0,
            }
        )
        request = Request(
            f"{settings.master_explorer_url}?{query}",
            headers={"User-Agent": "Choco-Chess-Coach/1.0"},
        )
        with urlopen(request, timeout=settings.master_explorer_timeout_seconds) as response:
            return json.load(response)

    @staticmethod
    def _normalize(
        data: dict,
        side_to_move: str,
        limit: int,
        statistics_available: bool = True,
    ) -> dict:
        position_games = sum(int(data.get(key, 0) or 0) for key in ("white", "draws", "black"))
        moves = []

        for move in data.get("moves", [])[:limit]:
            white = int(move.get("white", 0) or 0)
            draws = int(move.get("draws", 0) or 0)
            black = int(move.get("black", 0) or 0)
            games = white + draws + black
            wins = white if side_to_move == "white" else black
            moves.append(
                {
                    "move_uci": move["uci"],
                    "move_san": move.get("san", move["uci"]),
                    "games": games,
                    "frequency": games / position_games if position_games else 0.0,
                    "win_rate": (wins + 0.5 * draws) / games if games else 0.0,
                }
            )

        return {
            "rating_bucket": "masters",
            "side_to_move": side_to_move,
            "total_games": position_games,
            "moves": moves,
            "statistics_source": "masters",
            "statistics_available": statistics_available,
        }

    async def get_move_stats(
        self,
        fen: str,
        rating: int | None,
        side_to_move: str,
        limit: int = 8,
    ) -> dict:
        del rating  # Master statistics are intentionally independent of the user's rating.
        key = position_key(fen)
        collection = get_db()[self.collection_name]
        data = None
        statistics_available = True

        try:
            cached = await collection.find_one({"_id": key})
            if cached is not None:
                data = cached.get("explorer", {})
                logger.debug("masters.local_cache_hit position=%s", key)
        except Exception:
            logger.warning("masters.local_cache_read_failed position=%s", key, exc_info=True)

        if data is None:
            try:
                data = await asyncio.to_thread(self._fetch_remote, fen, max(limit, 20))
                logger.info(
                    "masters.explorer_completed position=%s games=%d",
                    key,
                    sum(int(data.get(name, 0) or 0) for name in ("white", "draws", "black")),
                )
            except Exception:
                logger.warning("masters.explorer_failed position=%s", key, exc_info=True)
                data = {"white": 0, "draws": 0, "black": 0, "moves": []}
                statistics_available = False
            else:
                try:
                    await collection.replace_one(
                        {"_id": key},
                        {
                            "_id": key,
                            "fen": chess.Board(fen).fen(),
                            "explorer": data,
                            "fetched_at": datetime.now(timezone.utc),
                        },
                        upsert=True,
                    )
                    logger.debug("masters.local_cache_stored position=%s", key)
                except Exception:
                    logger.warning("masters.local_cache_write_failed position=%s", key, exc_info=True)

        return self._normalize(data, side_to_move, limit, statistics_available)
