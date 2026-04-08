from typing import List, Set
from prefect import flow, task, get_run_logger
from prefect.cache_policies import NO_CACHE
import time

from backend.constant import (
    GAME_TIME_CONTROL,
    IS_ANALYZED_GAME,
    IS_RATED,
    MAX_GAMES_PER_USER,
    RAPID_GAME_TIME_CONTROL,
)

from backend.utils.game_utils import get_black_from_game, get_white_from_game
from backend.utils.validation import is_valid_game


# =========================
# TASKS
# =========================

@task(retries=2, retry_delay_seconds=5)
def fetch_games_task(client, username: str, config: dict) -> List[dict]:
    logger = get_run_logger()

    logger.info(f"[FETCH] starting user={username}")

    
    time.sleep(1)
    
    games = client.games.export_by_player(
        username=username,
        as_pgn=False,
        max=config.get(MAX_GAMES_PER_USER, 10),
        rated=config.get(IS_RATED, True),
        perf_type=config.get(GAME_TIME_CONTROL, RAPID_GAME_TIME_CONTROL),
        analysed=config.get(IS_ANALYZED_GAME, False),
        moves=True,
        evals=True,
        opening=True,
        clocks=True,
    )

    games = list(games)

    logger.info(f"[FETCH] user={username} games_fetched={len(games)}")

    return games


@task
def filter_rapid_games_task(games: List[dict], config_dict: dict):
    logger = get_run_logger()

    logger.info(f"[FILTER] starting games={len(games)}")

    filtered_games = []
    new_users = set()

    for game in games:
        if not game:
            continue

        white = get_white_from_game(game)
        black = get_black_from_game(game)

        if config_dict.get("is_collect_opponents", False):
            if white:
                new_users.add(white.lower())
            if black:
                new_users.add(black.lower())

        if is_valid_game(game):
            filtered_games.append(game)
        logger.info(
        f"[FILTER] input={len(games)} "
        f"filtered={len(filtered_games)} "
        f"new_users={len(new_users)}")

    return filtered_games, new_users


@task
def persist_games_task(sink, username: str, games: List[dict]) -> int:
    logger = get_run_logger()

    logger.info(f"[PERSIST] user={username} games={len(games)}")
    
    count = 0

    for game in games:
        sink.save(username=username, game=game, logging=True)
        count += 1

        if count % 10 == 0:
            logger.info(f"[PERSIST] user={username} saved={count}/{len(games)}")

    logger.info(f"[PERSIST] done user={username} total_saved={count}")

    return count


@task(cache_policy=NO_CACHE)
def update_user_store_task(db_path: str, username: str, new_users: Set[str]):
    logger = get_run_logger()

    logger.info(
        f"[STORE] updating user={username} new_users={len(new_users)}"
    )
    
    from backend.scrape.UserStore import UserStore

    store = UserStore(db_path)

    store.mark_processed(username)

    pending_before = store.pending_count()

    if pending_before < 500:
        store.add_many_pending(new_users)

    pending_after = store.pending_count()

    logger.info(
        f"[STORE] user={username} "
        f"pending_before={pending_before} "
        f"pending_after={pending_after}"
    )

    return len(new_users)

@task(tags=["lichess"])
def scrape_user_task(client, username: str, config: dict, sink, db_path: str):

    from backend.scrape.UserStore import UserStore

    store = UserStore(db_path)

    username = username.lower().strip()

    games = fetch_games_task(client, username, config)

    filtered, new_users = filter_rapid_games_task(games, config)

    saved = persist_games_task(sink, username, filtered)

    store.mark_processed(username)

    if store.pending_count() < 500:
        store.add_many_pending(new_users)

    return {
        "user": username,
        "games": len(games),
        "saved": saved,
        "new_users": len(new_users),
    }


# =========================
# FLOW 1: SINGLE USER SCRAPE
# =========================

@flow(name="scrape-user")
def scrape_user_flow(client, username: str, config: dict, sink, user_store):

    logger = get_run_logger()

    username = username.lower().strip()

    logger.info(f"[FLOW] scrape_user start user={username}")

    # skip if already processed
    if user_store.is_processed(username):
        logger.info(f"[FLOW] skipped user={username} already processed")
        return {"status": "skipped", "user": username}

    games = fetch_games_task(client, username, config)

    filtered_games, new_users = filter_rapid_games_task(games, config)

    saved_count = persist_games_task(sink, username, filtered_games)

    # TODO: Manual handle for expanding.
    # ? Update this 
    new_discovered = update_user_store_task(user_store.db_path, username, new_users) if False else None

    logger.info(
        f"[FLOW] done user={username} "
        f"fetched={len(games)} "
        f"saved={saved_count} "
        f"new_users={new_discovered}"
        f"usernames_queue={user_store.pending_count()}"
    )

    return {
        "user": username,
        "games_fetched": len(games),
        "games_saved": saved_count,
        "new_users_found": new_discovered,
        "usernames_queue": user_store.pending_count()
    }


# =========================
# FLOW 2: CRAWLER LOOP
# =========================

@flow(name="lichess-crawler")
def crawler_flow(client, config, sink, user_store, batch_size=5, max_loops=50):

    logger = get_run_logger()

    logger.info(
        f"[CRAWLER] start batch_size={batch_size} max_loops={max_loops}"
    )

    for i in range(max_loops):

        users = user_store.get_pending_batch(batch_size)

        if not users:
            logger.info("[CRAWLER] no more users → stopping")
            break

        logger.info(f"[CRAWLER] batch={i+1} users={users}")

        results = []

        for username in users:

            logger.info(f"[CRAWLER] processing user={username}")

            result = scrape_user_flow(
                client=client,
                username=username,
                config=config,
                sink=sink,
                user_store=user_store
            )

            results.append(result)

            logger.info(f"[CRAWLER] finished user={username}")

            time.sleep(1.5)

        logger.info(f"[CRAWLER] batch={i+1} complete results={results}")

    logger.info(f"[CRAWLER] DONE")

    return "done"