from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PlayerUser(BaseModel):
    name: str
    id: str


class Player(BaseModel):
    user: PlayerUser
    rating: int
    ratingDiff: Optional[int] = None


class Players(BaseModel):
    white: Player
    black: Player


class Opening(BaseModel):
    eco: Optional[str]
    name: Optional[str]
    ply: Optional[int]


class Clock(BaseModel):
    initial: int
    increment: int
    totalTime: int


class Game(BaseModel):
    id: str
    rated: bool
    variant: str
    speed: str
    perf: str
    createdAt: str
    lastMoveAt: str
    status: str
    source: Optional[str] = None

    players: Players
    winner: Optional[str] = None

    opening: Optional[Opening] = None

    moves: str

    clocks: List[int] = []
    clock: Optional[Clock] = None