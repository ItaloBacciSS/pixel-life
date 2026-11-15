import os
import re

DEV_SECRET = "dev-only-troque-em-producao"


def _database_url():
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or "sqlite:///jogo.db"
    )
    return re.sub(r"^postgres(ql)?(\+\w+)?://", "postgresql+psycopg2://", url)


def _secret_key():
    key = os.environ.get("SECRET_KEY", DEV_SECRET)
    if os.environ.get("VERCEL") and key == DEV_SECRET:
        raise RuntimeError("Defina SECRET_KEY nas variáveis de ambiente da Vercel.")
    return key


class Config:
    SECRET_KEY = _secret_key()
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    TIMEZONE = os.environ.get("TIMEZONE", "America/Sao_Paulo")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = bool(os.environ.get("VERCEL"))
    REGISTRATION_OPEN = os.environ.get("REGISTRATION_OPEN", "1") == "1"


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "teste"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SESSION_COOKIE_SECURE = False
