from typing import TypedDict

# TBA: pgn, times, tiemcontrol, etc
class RawGame(TypedDict):
    id: str
    players: dict
    moves: str
    rated: bool
    perf: str
    createdAt: int