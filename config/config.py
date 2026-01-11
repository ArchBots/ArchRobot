from __future__ import annotations

import os
from typing import List, Optional
from dotenv import load_dotenv


load_dotenv()


def _env(name: str, default=None, required: bool = False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def _env_int(name: str, required: bool = False) -> Optional[int]:
    value = _env(name, required=required)
    return int(value) if value is not None else None


def _normalize(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.replace("https://t.me/", "").lstrip("@")


API_ID: int = _env_int("API_ID", required=True)
API_HASH: str = _env("API_HASH", required=True)
BOT_TOKEN: str = _env("BOT_TOKEN", required=True)

STRING_SESSIONS: List[str] = [
    s.strip() for s in _env("STRING_SESSIONS", "").split(",") if s.strip()
]

MONGO_URI: str = _env("MONGO_URI", required=True)
DB_NAME: str = _env("DB_NAME", required=True)

LOG_FILE_NAME: str = _env("LOG_FILE_NAME", required=True)

OWNER_ID: int = _env_int("OWNER_ID", required=True)

SUPPORT_CHANNEL: Optional[str] = _normalize(_env("SUPPORT_CHANNEL"))
SUPPORT_GROUP: Optional[str] = _normalize(_env("SUPPORT_GROUP"))
LOG_GROUP: Optional[int] = _env_int("LOG_GROUP")
LOG_GROUP_ID: Optional[int] = LOG_GROUP # Alias for backward compatibility - both names reference the same value

SET_CMDS: str = _env("SET_CMDS", "True")
