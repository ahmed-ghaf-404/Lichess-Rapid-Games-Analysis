import re

import chess


def position_key(fen: str) -> str:
    """Return the rule-relevant FEN fields used to identify a position."""
    board = chess.Board(fen)
    return " ".join(board.fen().split(" ")[:4])


def canonical_position_fen(fen: str) -> str:
    return f"{position_key(fen)} 0 1"


def position_fen_pattern(fen: str) -> str:
    return rf"^{re.escape(position_key(fen))} "
