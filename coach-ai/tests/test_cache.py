import asyncio
import os


os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.api.recommend import (  # noqa: E402
    base_analysis_cache_key,
    recommendation_cache_key,
)
from app.schemas.recommend import RecommendRequest  # noqa: E402
from app.services.feature_builder import FeatureBuilder  # noqa: E402
from app.services.position_key import position_key  # noqa: E402
from app.services.singleflight import run_singleflight  # noqa: E402


START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
START_FEN_LATER = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 18 42"


def request(user_id: str, rating: int, fen: str = START_FEN) -> RecommendRequest:
    return RecommendRequest(
        fen=fen,
        user_id=user_id,
        rating=rating,
        color="white",
        max_candidates=6,
    )


def test_cache_keys_reuse_equivalent_positions_and_rating_buckets():
    first = request("ChocoRoku", 1601)
    equivalent = request("chocoroku", 1799, START_FEN_LATER)

    assert recommendation_cache_key(first, position_key(first.fen)) == (
        recommendation_cache_key(equivalent, position_key(equivalent.fen))
    )


def test_base_analysis_is_shared_but_final_result_remains_account_specific():
    choco = request("chocoroku", 1682)
    eric = request("ericrosen", 1750)
    normalized = position_key(START_FEN)

    assert base_analysis_cache_key(choco, normalized) == base_analysis_cache_key(
        eric,
        normalized,
    )
    assert recommendation_cache_key(choco, normalized) != recommendation_cache_key(
        eric,
        normalized,
    )


def test_singleflight_runs_concurrent_factory_once():
    async def exercise():
        calls = 0
        release = asyncio.Event()

        async def factory():
            nonlocal calls
            calls += 1
            await release.wait()
            return "ready"

        first = asyncio.create_task(run_singleflight("same-work", factory))
        second = asyncio.create_task(run_singleflight("same-work", factory))
        await asyncio.sleep(0)
        release.set()
        assert await asyncio.gather(first, second) == ["ready", "ready"]
        assert calls == 1

    asyncio.run(exercise())


def test_feature_builder_fetches_all_move_fits_in_one_batch():
    class FakeRepertoire:
        calls = 0

        async def get_move_fits(self, user_id, fen, move_ucis):
            self.calls += 1
            assert user_id == "chocoroku"
            assert fen == START_FEN
            assert move_ucis == ["e2e4", "d2d4"]
            return {"e2e4": 0.75, "d2d4": 0.25}

    builder = FeatureBuilder()
    builder.repertoire = FakeRepertoire()
    candidates = [{"move_uci": "e2e4"}, {"move_uci": "d2d4"}]

    result = asyncio.run(builder.enrich("chocoroku", START_FEN, candidates))

    assert builder.repertoire.calls == 1
    assert [item["repertoire_fit"] for item in result] == [0.75, 0.25]
