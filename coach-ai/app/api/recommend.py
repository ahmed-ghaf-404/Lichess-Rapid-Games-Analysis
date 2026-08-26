import chess
import logging
import logging
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.recommend import CandidateMove, RecommendRequest, RecommendResponse
from app.services.cache_service import get_json, make_cache_key, set_json
from app.services.candidate_generator import CandidateGenerator
from app.services.feature_builder import FeatureBuilder
from app.services.heuristic_ranker import HeuristicRanker
from app.services.position_key import canonical_position_fen, position_key
from app.services.rating_bucket import get_rating_bucket
from app.services.singleflight import run_singleflight
from app.services.position_key import canonical_position_fen, position_key
from app.services.rating_bucket import get_rating_bucket
from app.services.singleflight import run_singleflight

router = APIRouter(prefix="/recommend", tags=["recommend"])

candidate_generator = CandidateGenerator()
feature_builder = FeatureBuilder()
ranker = HeuristicRanker()
logger = logging.getLogger(__name__)


def recommendation_cache_key(payload: RecommendRequest, normalized_position: str) -> str:
    statistics_bucket = "masters" if payload.use_master_games else get_rating_bucket(payload.rating)
    return make_cache_key(
        "recommend-position",
        settings.recommender_version,
        normalized_position,
        payload.user_id.strip().lower(),
        statistics_bucket,
        payload.max_candidates,
        settings.engine_depth,
        "masters" if payload.use_master_games else "peer",
    )


def base_analysis_cache_key(payload: RecommendRequest, normalized_position: str) -> str:
    statistics_bucket = "masters" if payload.use_master_games else get_rating_bucket(payload.rating)
    return make_cache_key(
        "recommend-base",
        settings.recommender_version,
        normalized_position,
        statistics_bucket,
        payload.max_candidates,
        settings.engine_depth,
        "masters" if payload.use_master_games else "peer",
    )


async def load_base_analysis(
    payload: RecommendRequest,
    normalized_position: str,
    analysis_fen: str,
) -> dict:
    cache_key = base_analysis_cache_key(payload, normalized_position)

    if payload.use_cache and not payload.force_recompute and not payload.refresh_cache:
        cached = await get_json(cache_key)
        if cached is not None:
            logger.debug("recommendation.base_cache_hit cache_key=%s", cache_key)
            return cached

    async def generate() -> dict:
        generated = await candidate_generator.generate(
            fen=analysis_fen,
            rating=payload.rating,
            max_candidates=payload.max_candidates,
            use_master_games=payload.use_master_games,
        )
        if (payload.use_cache or payload.refresh_cache) and generated.get(
            "statistics_available",
            True,
        ):
            await set_json(cache_key, generated, settings.cache_ttl_seconds)
        return generated

    mode = f"{payload.use_cache}:{payload.refresh_cache}:{payload.force_recompute}"
    return await run_singleflight(f"base:{cache_key}:{mode}", generate)


@router.post("/position", response_model=RecommendResponse)
async def recommend_position(payload: RecommendRequest) -> RecommendResponse:
    logger.debug(
        "recommendation.started user_id=%s rating=%s max_candidates=%d use_cache=%s",
        payload.user_id,
        payload.rating,
        payload.max_candidates,
        payload.use_cache,
    )
    logger.debug(
        "recommendation.started user_id=%s rating=%s max_candidates=%d use_cache=%s",
        payload.user_id,
        payload.rating,
        payload.max_candidates,
        payload.use_cache,
    )
    try:
        board = chess.Board(payload.fen)
        normalized_fen = board.fen()
        normalized_position = position_key(normalized_fen)
        analysis_fen = canonical_position_fen(normalized_fen)
        normalized_position = position_key(normalized_fen)
        analysis_fen = canonical_position_fen(normalized_fen)
    except Exception as exc:
        logger.warning("recommendation.invalid_fen error=%s", exc)
        logger.warning("recommendation.invalid_fen error=%s", exc)
        raise HTTPException(status_code=400, detail=f"Invalid FEN: {exc}") from exc

    cache_key = recommendation_cache_key(payload, normalized_position)
    cache_key = recommendation_cache_key(payload, normalized_position)

    if payload.use_cache and not payload.force_recompute and not payload.refresh_cache:
        cached = await get_json(cache_key)
        if cached is not None:
            logger.debug("recommendation.cache_hit cache_key=%s", cache_key)
            logger.debug("recommendation.cache_hit cache_key=%s", cache_key)
            cached["metadata"]["cache"] = "hit"
            return RecommendResponse(**cached)
        logger.debug("recommendation.cache_miss cache_key=%s", cache_key)
        logger.debug("recommendation.cache_miss cache_key=%s", cache_key)

    async def compute_response() -> RecommendResponse:
        generated = await load_base_analysis(
            payload,
            normalized_position,
            analysis_fen,
    async def compute_response() -> RecommendResponse:
        generated = await load_base_analysis(
            payload,
            normalized_position,
            analysis_fen,
        )

        candidates = generated["candidates"]

        if not candidates:
            logger.warning(
                "recommendation.no_candidates user_id=%s rating_bucket=%s",
                payload.user_id,
                generated["rating_bucket"],
            )
            logger.warning(
                "recommendation.no_candidates user_id=%s rating_bucket=%s",
                payload.user_id,
                generated["rating_bucket"],
            )
            response = RecommendResponse(
                fen=analysis_fen,
                fen=analysis_fen,
                recommended_move=None,
                candidates=[],
                metadata={
                    "sample_size": 0,
                    "model": settings.recommender_version,
                    "rating_bucket": generated["rating_bucket"],
                    "side_to_move": generated["side_to_move"],
                    "source": f'{generated["statistics_source"]}+engine',
                    "cache": "miss",
                },
            )
        else:
            enriched = await feature_builder.enrich(
                user_id=payload.user_id,
                fen=analysis_fen,
                fen=analysis_fen,
                candidates=candidates,
            )

            ranked = ranker.rank(enriched)

            response = RecommendResponse(
                fen=analysis_fen,
                fen=analysis_fen,
                recommended_move=ranked[0]["move_uci"] if ranked else None,
                candidates=[CandidateMove(**item) for item in ranked],
                metadata={
                    "sample_size": generated["sample_size"],
                    "model": settings.recommender_version,
                    "rating_bucket": generated["rating_bucket"],
                    "side_to_move": generated["side_to_move"],
                    "source": f'{generated["statistics_source"]}+engine',
                    "cache": "miss",
                },
            )

        if (payload.use_cache or payload.refresh_cache) and generated.get(
            "statistics_available",
            True,
        ):
            await set_json(
                cache_key,
                response.model_dump(),
                settings.cache_ttl_seconds,
            )

        return response

    try:
        mode = f"{payload.use_cache}:{payload.refresh_cache}:{payload.force_recompute}"
        response = await run_singleflight(
            f"recommendation:{cache_key}:{mode}",
            compute_response,
        )
        logger.info(
            "recommendation.completed user_id=%s recommended_move=%s candidate_count=%d sample_size=%d",
            payload.user_id,
            response.recommended_move,
            len(response.candidates),
            response.metadata.get("sample_size", 0),
        )
        return response

    try:
        mode = f"{payload.use_cache}:{payload.refresh_cache}:{payload.force_recompute}"
        response = await run_singleflight(
            f"recommendation:{cache_key}:{mode}",
            compute_response,
        )
        logger.info(
            "recommendation.completed user_id=%s recommended_move=%s candidate_count=%d sample_size=%d",
            payload.user_id,
            response.recommended_move,
            len(response.candidates),
            response.metadata.get("sample_size", 0),
        )
        return response

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "recommendation.failed user_id=%s stockfish_path=%s",
            payload.user_id,
            settings.stockfish_path,
        )
        logger.exception(
            "recommendation.failed user_id=%s stockfish_path=%s",
            payload.user_id,
            settings.stockfish_path,
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc

