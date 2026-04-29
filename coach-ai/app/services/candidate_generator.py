import chess

from app.services.peer_stats_service import PeerStatsService
from app.services.stockfish_service import StockfishService


class CandidateGenerator:
    def __init__(self):
        self.peer_stats = PeerStatsService()
        self.stockfish = StockfishService()

    async def generate(
        self,
        fen: str,
        rating: int | None,
        max_candidates: int = 8,
    ) -> dict:
        board = chess.Board(fen)
        side = "white" if board.turn == chess.WHITE else "black"

        legal_moves = {move.uci(): move for move in board.legal_moves}

        peer_data = await self.peer_stats.get_move_stats(
            fen=fen,
            rating=rating,
            side_to_move=side,
            limit=max_candidates,
        )
        engine_moves = await self.stockfish.analyze_top_moves(fen, top_k=max_candidates)

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

        return {
            "fen": fen,
            "side_to_move": side,
            "rating_bucket": peer_data["rating_bucket"],
            "sample_size": peer_data["total_games"],
            "candidates": candidate_list[:max_candidates],
        }