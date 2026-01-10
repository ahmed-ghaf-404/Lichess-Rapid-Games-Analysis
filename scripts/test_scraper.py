from backend.scrape.lichess import LichessGameScraper
from backend.scrape.sink import FileSystemSink
from backend.utils.client import get_client


config = {
    "games_per_user": 3,
    "perf": "rapid",
    "rated": True,
    "analysed": True,
}

client = get_client()
scraper = LichessGameScraper(client, config)
sink = FileSystemSink("data/raw")

username = "ericrosen"

for game in scraper.fetch_games(username):
    sink.save(username, game)