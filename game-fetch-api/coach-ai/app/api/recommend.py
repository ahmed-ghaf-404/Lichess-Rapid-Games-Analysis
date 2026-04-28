import chess
from fastapi import APIRouter, HTTPException

from app.schemas.recommend import CandidateMove, RecommendRequest, RecommendResponse
from app.services.candidate_generator import CandidateGenerator
from app.services.feature_builder import FeatureBuilder
from app.services.heuristic_ranker import HeuristicRanker

router = APIRouter(prefix="/recommend", tags=["recommend"])

candidate_generator = CandidateGenerator()
feature_builder = FeatureBuilder()
ranker = HeuristicRanker()


@router.post("/position", response_model=RecommendResponse)
async def recommend_position(payload: RecommendRequest) -> RecommendResponse:
    try:
        chess.Board(payload.fen)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    try:
        generated = await candidate_generator.generate(
            fen=payload.fen,
            rating=payload.rating,
            max_candidates=payload.max_candidates,
        )

        candidates = generated["candidates"]
        if not candidates:
            return RecommendResponse(
                fen=payload.fen,
                recommended_move=None,
                candidates=[],
                metadata={
                    "sample_size": 0,
                    "model": "heuristic_v1",
                    "rating_bucket": generated["rating_bucket"],
                    "side_to_move": generated["side_to_move"],
                    "source": "peer+engine",
                },
            )

        enriched = await feature_builder.enrich(
            user_id=payload.user_id,
            fen=payload.fen,
            candidates=candidates,
        )

        ranked = ranker.rank(enriched)

        return RecommendResponse(
            fen=payload.fen,
            recommended_move=ranked[0]["move_uci"] if ranked else None,
            candidates=[CandidateMove(**item) for item in ranked],
            metadata={
                "sample_size": generated["sample_size"],
                "model": "heuristic_v1",
                "rating_bucket": generated["rating_bucket"],
                "side_to_move": generated["side_to_move"],
                "source": "peer+engine",
            },
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc