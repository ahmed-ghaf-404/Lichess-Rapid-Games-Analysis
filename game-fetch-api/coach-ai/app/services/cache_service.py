import hashlib
import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


def make_cache_key(*parts: object) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"chess-coach:{digest}"


async def get_json(key: str) -> Any | None:
    value = await redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def set_json(key: str, value: Any, ttl_seconds: int) -> None:
    await redis_client.set(key, json.dumps(value), ex=ttl_seconds)