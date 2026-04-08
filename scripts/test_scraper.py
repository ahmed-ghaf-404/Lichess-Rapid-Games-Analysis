from backend.scrape.UserStore import UserStore
from backend.scrape.FileSystemSink import FileSystemSink
from backend.scrape.LichessRapidGameScraper import crawler_flow
from backend.utils.client import get_client


if __name__ == "__main__":
    client = get_client()
    sink = FileSystemSink('data/raw')
    user_store = UserStore()

    config = {
    "games_per_user": 100,
    "perf": "rapid",
    "rated": True,
    "is_collect_opponents": True
    }

    user_store.add_pending("ChocoRoku")

    crawler_flow(
        client=client,
        config={
            "games_per_user": 50,
            "rated": True,
            "perf": "rapid",
            "is_collect_opponents": True
        },
        sink=sink,
        user_store=user_store,
        batch_size=3
    )