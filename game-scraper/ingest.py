import os
import json
import logging
from db_sync import games_collection


logger = logging.getLogger(__name__)


def ingest(folder="../data/raw/chocoroku"):
    logger.info("ingest.scan_started folder=%s", folder)
    inserted = 0
    updated = 0

    for root, _, files in os.walk(folder):
        for file in files:
            if not file.endswith(".json"):
                continue

            path = os.path.join(root, file)

            with open(path, "r") as f:
                game = json.load(f)

            result = games_collection.update_one(
                {"id": game["id"]},
                {"$set": game},
                upsert=True
            )

            if result.upserted_id:
                inserted += 1
            else:
                updated += 1

    logger.info("ingest.scan_completed inserted=%d updated=%d", inserted, updated)


if __name__ == "__main__":
    ingest()
