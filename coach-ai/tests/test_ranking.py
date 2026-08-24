from app.services.heuristic_ranker import HeuristicRanker
from app.services.rating_bucket import get_rating_bucket


def test_rating_buckets_cover_boundaries():
    assert get_rating_bucket(None) == "unknown"
    assert get_rating_bucket(1199) == "0-1199"
    assert get_rating_bucket(1200) == "1200-1399"
    assert get_rating_bucket(2199) == "2000-2199"
    assert get_rating_bucket(2200) == "2200+"


def test_ranker_prefers_stronger_supported_candidate():
    ranker = HeuristicRanker()
    candidates = [
        {
            "move_uci": "e2e4",
            "peer_frequency": 0.35,
            "peer_win_rate": 0.58,
            "peer_games": 80,
            "engine_eval_cp": 45,
            "engine_loss_cp": 0,
            "engine_rank": 1,
            "repertoire_fit": 0.7,
        },
        {
            "move_uci": "a2a3",
            "peer_frequency": 0.02,
            "peer_win_rate": 0.4,
            "peer_games": 2,
            "engine_eval_cp": -80,
            "engine_loss_cp": 120,
            "engine_rank": 6,
            "repertoire_fit": 0,
        },
    ]

    ranked = ranker.rank(candidates)

    assert ranked[0]["move_uci"] == "e2e4"
    assert "top engine move" in ranked[0]["reasons"]
    assert ranked[0]["score"] > ranked[1]["score"]
