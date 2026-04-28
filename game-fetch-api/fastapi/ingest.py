import os
import json
from db_sync import games_collection


def ingest(folder="../data/raw/chocoroku"):
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

    print(f"Inserted: {inserted}, Updated: {updated}")


if __name__ == "__main__":
    ingest()