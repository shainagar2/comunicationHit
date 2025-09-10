import os
from dataclasses import dataclass
from functools import lru_cache

@dataclass(frozen=True)
class Settings:
    # Scratchy config values you can later inject/use anywhere
    app_name: str = os.getenv("APP_NAME", "TinyFastAPI")
    scratch_value: str = os.getenv("SCRATCH_VALUE", "not-important")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    db_connection_string: str = os.getenv("DB_CONN", "mydbconnectionstring")

@lru_cache
def get_settings() -> Settings:
    # Cached so it's cheap to inject in handlers via Depends()
    return Settings()