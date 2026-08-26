import chess
import asyncio
import logging

from app.services.master_stats_service import MasterStatsService
from app.services.peer_stats_service import PeerStatsService
from app.services.stockfish_service import StockfishService


logger = logging.getLogger(__name__)


class CandidateGenerator:
    def __init__(self):
        self.peer_stats = PeerStatsService()
        self.master_stats = MasterStatsService()
        self.stockfish = StockfishService()

    async def generate(
        self,
        fen: str,
        rating: int | None,
        max_candidates: int = 8,
        use_master_games: bool = False,
    ) -> dict:
        board = chess.Board(fen)
        side = "white" if board.turn == chess.WHITE else "black"
        logger.debug(
            "candidates.generation_started side=%s rating=%s max_candidates=%d",
            side,
            rating,
            max_candidates,
        )

        legal_moves = {move.uci(): move for move in board.legal_moves}

        statistics_service = self.master_stats if use_master_games else self.peer_stats
        peer_data, engine_moves = await asyncio.gather(
            statistics_service.get_move_stats(
                fen=fen,
                rating=rating,
                side_to_move=side,
                limit=max_candidates,
            ),
            self.stockfish.analyze_top_moves(fen, top_k=max_candidates),
        )
        statistics_source = peer_data.get(
            "statistics_source",
            "masters" if use_master_games else "peer",
        )

        candidates: dict[str, dict] = {}

        for move in peer_data["moves"]:
            if move["move_uci"] not in legal_moves:
                continue

            candidates[move["move_uci"]] = {
                "move_uci": move["move_uci"],
                "move_san": move["move_san"],
                "peer_frequency": move["frequency"],
                "peer_games": move["games"],
                "peer_win_rate": move["win_rate"],
                "engine_rank": None,
                "engine_eval_cp": None,
                "engine_loss_cp": None,
                "statistics_source": statistics_source,
            }

        for move in engine_moves:
            if move["move_uci"] not in legal_moves:
                continue

            try:
                san = board.san(legal_moves[move["move_uci"]])
            except Exception:
                san = move["move_uci"]

            existing = candidates.get(move["move_uci"], {})
            candidates[move["move_uci"]] = {
                "move_uci": move["move_uci"],
                "move_san": existing.get("move_san", san),
                "peer_frequency": existing.get("peer_frequency", 0.0),
                "peer_games": existing.get("peer_games", 0),
                "peer_win_rate": existing.get("peer_win_rate", 0.0),
                "engine_rank": move["rank"],
                "engine_eval_cp": move["cp"],
                "engine_loss_cp": move["loss_cp"],
                "statistics_source": existing.get("statistics_source", "engine"),
            }

        candidate_list = list(candidates.values())

        # deterministic ordering before ranking
        candidate_list.sort(
            key=lambda x: (
                x["peer_games"],
                -999999 if x["engine_rank"] is None else -x["engine_rank"],
                x["peer_frequency"],
            ),
            reverse=True,
        )

        result = {
            "fen": fen,
            "side_to_move": side,
            "rating_bucket": peer_data["rating_bucket"],
            "sample_size": peer_data["total_games"],
            "statistics_source": statistics_source,
            "statistics_available": peer_data.get("statistics_available", True),
            "candidates": candidate_list[:max_candidates],
        }
        logger.debug(
            "candidates.generation_completed peer_moves=%d engine_moves=%d candidates=%d",
            len(peer_data["moves"]),
            len(engine_moves),
            len(result["candidates"]),
        )
        return result
