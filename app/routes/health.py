import os
import time

from flask import Blueprint, g, jsonify
from sqlalchemy import text

from ..extensions import db

bp = Blueprint("health", __name__)

STARTED = time.time()
served = 0


def _ms(since):
    return round((time.perf_counter() - since) * 1000, 1)


@bp.before_app_request
def start_timer():
    g.started = time.perf_counter()


@bp.after_app_request
def add_timing(response):
    global served
    served += 1
    started = g.get("started")
    if started is not None:
        response.headers["Server-Timing"] = f"app;dur={_ms(started)}"
    return response


@bp.get("/saude")
def health():
    """Diagnóstico de velocidade: início a frio, conexão com o banco e uma consulta já conectada."""
    first = time.perf_counter()
    db.session.execute(text("select 1"))
    connect_ms = _ms(first)
    second = time.perf_counter()
    db.session.execute(text("select 1"))
    return jsonify(
        instancia_ligada_ha_s=round(time.time() - STARTED, 1),
        requisicoes_nesta_instancia=served,
        primeira_consulta_ms=connect_ms,
        segunda_consulta_ms=_ms(second),
        regiao=os.environ.get("VERCEL_REGION", "local"),
    )
