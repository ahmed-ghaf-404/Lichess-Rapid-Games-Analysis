from app.services.master_stats_service import MasterStatsService


def test_master_statistics_are_normalized_for_side_to_move():
    data = {
        "white": 50,
        "draws": 30,
        "black": 20,
        "moves": [
            {
                "uci": "e2e4",
                "san": "e4",
                "white": 30,
                "draws": 15,
                "black": 5,
            },
            {
                "uci": "d2d4",
                "san": "d4",
                "white": 20,
                "draws": 15,
                "black": 15,
            },
        ],
    }

    result = MasterStatsService._normalize(data, "white", 8)

    assert result["statistics_source"] == "masters"
    assert result["statistics_available"] is True
    assert result["rating_bucket"] == "masters"
    assert result["total_games"] == 100
    assert result["moves"][0]["frequency"] == 0.5
    assert result["moves"][0]["win_rate"] == 0.75


def test_master_statistics_use_black_results_when_black_is_to_move():
    data = {
        "white": 4,
        "draws": 2,
        "black": 4,
        "moves": [
            {
                "uci": "e7e5",
                "san": "e5",
                "white": 1,
                "draws": 2,
                "black": 3,
            }
        ],
    }

    result = MasterStatsService._normalize(data, "black", 8)

    assert result["moves"][0]["games"] == 6
    assert result["moves"][0]["win_rate"] == 4 / 6
