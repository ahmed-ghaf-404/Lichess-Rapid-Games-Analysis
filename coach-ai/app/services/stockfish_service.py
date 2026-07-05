import chess
import chess.engine

from app.core.config import settings


class StockfishService:
    def __init__(self, engine_path: str | None = None, depth: int | None = None):
        self.engine_path = engine_path or settings.stockfish_path
        self.depth = depth or settings.engine_depth

    async def analyze_top_moves(self, fen: str, top_k: int = 5) -> list[dict]:
        board = chess.Board(fen)

        transport, engine = await chess.engine.popen_uci(self.engine_path)
        try:
            info = await engine.analyse(
                board,
                chess.engine.Limit(depth=self.depth),
                multipv=top_k,
            )

            if not isinstance(info, list):
                info = [info]

            moves: list[dict] = []
            best_cp: int | None = None

            for idx, entry in enumerate(info, start=1):
                pv = entry.get("pv", [])
                if not pv:
                    continue

                move = pv[0]

                # score from the side-to-move perspective
                score = entry["score"].pov(board.turn).score(mate_score=100000)
                if score is None:
                    score = 0

                if best_cp is None:
                    best_cp = score

                moves.append(
                    {
                        "rank": idx,
                        "move_uci": move.uci(),
                        "cp": int(score),
                        "loss_cp": int(max(0, best_cp - score)),
                        "pv": [m.uci() for m in pv[:6]],
                    }
                )

            return moves
        finally:
            await engine.quit()
            transport.close()