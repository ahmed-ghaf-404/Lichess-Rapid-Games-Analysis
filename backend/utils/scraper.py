from typing import Set
from .filesystem import ensure_dir, save_json
from .validation import is_valid_game
import os

def scrape_rapid_games(
    client,
    output_path: str,
    username: str,
    num_games: int = 1,
    allow_duplicate: bool = False,
    scraped_usernames: Set[str] = None,
    collect_opponents: bool = False
) -> Set[str]:

    if scraped_usernames and not allow_duplicate and username in scraped_usernames:
        return set()

    new_users = set()
    user_dir = f"{output_path}/{username}"
    ensure_dir(user_dir)

    games = client.games.export_by_player(
        username=username,
        as_pgn=False,
        max=num_games,
        rated=True,
        perf_type="rapid",
        analysed=True,
        moves=True,
        evals=True,
        opening=True,
    )

    added = 0
    for game in games:
        game_path = f"{user_dir}/{game['id']}.json"

        if os.path.exists(game_path):
            continue

        if collect_opponents:
            white = game["players"]["white"]["user"]["name"]
            black = game["players"]["black"]["user"]["name"]
            new_users.add(black if white.lower() == username.lower() else white)

        if is_valid_game(game):
            save_json(game, game_path)
            added += 1

    print(f"Added {added}/{num_games} games for {username}")
    return new_users
