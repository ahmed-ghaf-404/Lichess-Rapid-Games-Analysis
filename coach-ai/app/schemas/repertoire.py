from typing import Literal

from pydantic import BaseModel, Field


class RepertoireLineCreate(BaseModel):
    user_id: str = Field(min_length=2, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(min_length=3, max_length=100)
    opening_name: str = Field(min_length=2, max_length=150)
    parent_line_id: str | None = None


class RepertoireMoveCreate(BaseModel):
    user_id: str = Field(min_length=2, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    fen_before: str = Field(min_length=10, max_length=150)
    move_uci: str = Field(min_length=4, max_length=5, pattern=r"^[a-h][1-8][a-h][1-8][qrbn]?$")
    move_san: str | None = Field(default=None, max_length=20)
    source: Literal["recommendation", "manual"] = "recommendation"


class RepertoireMoveResponse(BaseModel):
    id: str
    position_key: str
    fen_before: str
    fen_after: str
    move_uci: str
    move_san: str
    source: str
    approved_at: str


class RepertoireLineResponse(BaseModel):
    id: str
    user_id: str
    name: str
    opening_name: str
    parent_line_id: str | None
    moves: list[RepertoireMoveResponse]
    created_at: str
    updated_at: str
