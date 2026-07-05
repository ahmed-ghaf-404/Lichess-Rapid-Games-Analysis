from typing import Any, Literal

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    fen: str
    user_id: str
    rating: int | None = None
    color: Literal["white", "black"] | None = None
    max_candidates: int = Field(default=8, ge=1, le=20)

    use_cache: bool = True
    refresh_cache: bool = False
    force_recompute: bool = False

class CandidateMove(BaseModel):
    move_uci: str
    move_san: str
    score: float
    peer_frequency: float
    peer_games: int
    peer_win_rate: float
    engine_rank: int | None = None
    engine_eval_cp: int | None = None
    engine_loss_cp: int | None = None
    repertoire_fit: float = 0.0
    reasons: list[str] = []


class RecommendResponse(BaseModel):
    fen: str
    recommended_move: str | None
    candidates: list[CandidateMove]
    metadata: dict[str, Any]