import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("MONEYHUB_SECRET_KEY", "change-me-to-a-secure-key")
    BASE_DIR = Path(__file__).resolve().parent
    DATABASE = os.environ.get("MONEYHUB_DATABASE") or str(BASE_DIR / "instance" / "moneyhub.db")
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https"
