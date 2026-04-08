
def is_standard_chess(game):
    return game.get("variant") == "standard"

def is_valid_game(game: dict) -> bool:

    if not is_standard_chess(game):
        return False

    if "opening" not in game:
        return False

    white = game["players"]["white"]
    black = game["players"]["black"]

    if "provisional" in white or "provisional" in black:
        return False

    if abs(white["rating"] - black["rating"]) > 100:
        return False

    if len(game.get("moves", "").split()) < 10:
        return False

    if "ratingDiff" in white and "ratingDiff" in black:
        if white["ratingDiff"] + black["ratingDiff"] > 2:
            return False

    return True
