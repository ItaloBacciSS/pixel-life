import json
from functools import lru_cache
from pathlib import Path

from ..extensions import db
from ..errors import ApiError

STYLES_FILE = Path(__file__).resolve().parent.parent / "data" / "estilos.json"
DEFAULT = "classico"


@lru_cache
def catalog():
    return json.loads(STYLES_FILE.read_text(encoding="utf-8"))


def choose(user, style_id):
    if style_id not in {style["id"] for style in catalog()}:
        raise ApiError("Estilo desconhecido.")
    user.estilo = style_id
    db.session.commit()
