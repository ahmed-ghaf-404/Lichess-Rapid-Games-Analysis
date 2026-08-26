from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    mongo_uri: str
    mongo_db: str = "chess-games"
    stockfish_path: str = "/usr/local/bin/stockfish"
    engine_depth: int = 14

    redis_url: str
    cache_ttl_seconds: int = 60 * 60 * 24 * 30  # one month
    recommender_version: str = "heuristic_v1"
    repertoire_users: str = "ericrosen,chocoroku"
    repertoire_write_key: str = ""
    master_explorer_url: str = "https://explorer.lichess.org/masters"
    master_explorer_timeout_seconds: float = 6.0


settings = Settings()
