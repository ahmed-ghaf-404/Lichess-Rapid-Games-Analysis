def is_valid_game(game: dict) -> bool:
    if game.get("variant") != "standard":
        return False

    if "opening" not in game:
        return False

    white = game["players"]["white"]
    black = game["players"]["black"]

    if "provisional" in white or "provisional" in black:
        return False

    if abs(white["rating"] - black["rating"]) > 100:
        return False

    if len(game.get("moves", "").split()) < 40:
        return False

    if "ratingDiff" in white and "ratingDiff" in black:
        if white["ratingDiff"] + black["ratingDiff"] > 2:
            return False

    return True
