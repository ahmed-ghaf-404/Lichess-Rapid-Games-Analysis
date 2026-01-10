
import os
import json
from pathlib import Path
from datetime import datetime
import berserk

from backend.scrape.lichess import LichessGameScraper
from backend.constant import BERSERK_ACCESS_TOKEN, GAME_TIME_CONTROL, MAX_GAMES_PER_USER, RAPID_GAME_TIME_CONTROL, IS_RATED, IS_ANALYZED_GAME

DEFAULT_CONFIG = {
    MAX_GAMES_PER_USER: 1000,
    IS_RATED: True,
    GAME_TIME_CONTROL: RAPID_GAME_TIME_CONTROL,
    IS_ANALYZED_GAME: True,
}

def main():
    usernames = ["ericrosen"]
    token = os.environ[BERSERK_ACCESS_TOKEN]
    client = berserk.Client(berserk.TokenSession(token))
    scraper = LichessGameScraper(client, DEFAULT_CONFIG)

    now = datetime.utcnow()
    out_dir = Path("data/monthly_games") / str(now.year) / f"{now.month:02}"
    out_dir.mkdir(parents=True, exist_ok=True)

    for username in usernames:
        games = list(scraper.fetch_games(username))
        print(f"Fetched {len(games)} games for {username}")

        out_path = out_dir / f"{username}_games.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(games, f, indent=2, default=str)
        print(f"Saved games to {out_path}")

if __name__ == "__main__":
    main()