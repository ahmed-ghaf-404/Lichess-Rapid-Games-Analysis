def get_rating_bucket(rating: int | None) -> str:
    if rating is None:
        return "unknown"
    if rating < 1200:
        return "0-1199"
    if rating < 1400:
        return "1200-1399"
    if rating < 1600:
        return "1400-1599"
    if rating < 1800:
        return "1600-1799"
    if rating < 2000:
        return "1800-1999"
    if rating < 2200:
        return "2000-2199"
    return "2200+"