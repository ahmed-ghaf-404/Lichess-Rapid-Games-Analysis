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


settings = Settings()