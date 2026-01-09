from typing import Iterable
import berserk

from backend.constant import GAME_TIME_CONTROL, IS_ANALYZED_GAME, IS_RATED, MAX_GAMES_PER_USER, RAPID_GAME_TIME_CONTROL

# Lichess Scraper Implementation  
class LichessGameScraper:
    def __init__(self, client: berserk.Client, config_dict: dict):
        self.client = client
        self.config_dict = config_dict

    def fetch_games(self, username: str) -> Iterable[dict]:
        return self.client.games.export_by_player(
            username=username,
            as_pgn=False,
            max=self.config_dict[MAX_GAMES_PER_USER],
            rated=self.config_dict.get(IS_RATED, True),
            perf_type=self.config_dict.get(GAME_TIME_CONTROL, RAPID_GAME_TIME_CONTROL),
            analysed=self.config_dict.get(IS_ANALYZED_GAME, True),
            moves=True,
            evals=True,
            opening=True,
        )
