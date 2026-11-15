from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def today():
    """Data de hoje no fuso do jogador (o servidor na nuvem roda em UTC)."""
    return datetime.now(ZoneInfo(current_app.config["TIMEZONE"])).date()
