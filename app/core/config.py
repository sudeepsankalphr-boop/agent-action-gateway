from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent


class Settings:
    DB_PATH: str = str(_ROOT / "gateway.db")
    POLICIES_DIR: str = str(_ROOT / "policies")


settings = Settings()
