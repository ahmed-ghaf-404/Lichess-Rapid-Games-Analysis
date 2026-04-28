import chess
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.recommend import CandidateMove, RecommendRequest, RecommendResponse
from app.services.cache_service import get_json, make_cache_key, set_json
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
        board = chess.Board(payload.fen)
        normalized_fen = board.fen()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    cache_key = make_cache_key(
        "recommend-position",
        settings.recommender_version,
        normalized_fen,
        payload.user_id,
        payload.rating,
        payload.max_candidates,
        settings.engine_depth,
    )

    if payload.use_cache and not payload.force_recompute and not payload.refresh_cache:
        cached = await get_json(cache_key)
        if cached is not None:
            cached["metadata"]["cache"] = "hit"
            return RecommendResponse(**cached)

    try:
        generated = await candidate_generator.generate(
            fen=normalized_fen,
            rating=payload.rating,
            max_candidates=payload.max_candidates,
        )

        candidates = generated["candidates"]

        if not candidates:
            response = RecommendResponse(
                fen=normalized_fen,
                recommended_move=None,
                candidates=[],
                metadata={
                    "sample_size": 0,
                    "model": settings.recommender_version,
                    "rating_bucket": generated["rating_bucket"],
                    "side_to_move": generated["side_to_move"],
                    "source": "peer+engine",
                    "cache": "miss",
                },
            )
        else:
            enriched = await feature_builder.enrich(
                user_id=payload.user_id,
                fen=normalized_fen,
                candidates=candidates,
            )

            ranked = ranker.rank(enriched)

            response = RecommendResponse(
                fen=normalized_fen,
                recommended_move=ranked[0]["move_uci"] if ranked else None,
                candidates=[CandidateMove(**item) for item in ranked],
                metadata={
                    "sample_size": generated["sample_size"],
                    "model": settings.recommender_version,
                    "rating_bucket": generated["rating_bucket"],
                    "side_to_move": generated["side_to_move"],
                    "source": "peer+engine",
                    "cache": "miss",
                },
            )

        if payload.use_cache or payload.refresh_cache:
            await set_json(
                cache_key,
                response.model_dump(),
                settings.cache_ttl_seconds,
            )

        return response

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc