import argparse
from backend.jobs.scrape_job import run_scrape_lichess

# sample configs
# TODO: Update this to have it passed via the CLI
DEFAULT_CONFIG = {
    "games_per_user": 10,
    "perf": "rapid",
    "rated": True,
    "analysed": True,
}


##
# USAGE: 
# ===========
# cli.py --users ericrosen ChocoRoku <other usernames> --output data/raw_games
##

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Lichess scraping job")
    parser.add_argument("--users", nargs="+", required=True, help="Usernames to scrape")
    parser.add_argument("--output", default="data/raw", help="Output path")
    args = parser.parse_args()

    run_scrape_lichess(args.users, DEFAULT_CONFIG, args.output)
