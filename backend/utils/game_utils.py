def get_white_from_game(game):
    return game.get("players", {}).get("white", {}).get("user", {}).get("name")

def get_black_from_game(game):
    return game.get("players", {}).get("black", {}).get("user", {}).get("name")