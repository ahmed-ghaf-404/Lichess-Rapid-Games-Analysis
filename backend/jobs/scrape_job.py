from backend.utils.client import get_client
from backend.scrape.lichess import LichessGameScraper
from backend.scrape.sink import FileSystemSink

##
# Job: Scrapes games for a list of usernames
##
# Define: List<usernames>, Dict<scrape_configurations>
##

# TODO: Add Rate limiter AND/OR MULTI-THREADING SOLUTIONS. 
# ! Bandwith is NOT INFINITE or <something>

def run_scrape_lichess(usernames: list[str], config: dict, base_path: str = "data/raw"):
    client = get_client()
    scraper = LichessGameScraper(client, config)
    sink = FileSystemSink(base_path)

    for username in usernames:
        print(f"Scraping games for {username}")
        try:
            for game in scraper.fetch_games(username):
                sink.save(username, game)
        except Exception as e:
            print(f"Failed for {username}: {e}")
