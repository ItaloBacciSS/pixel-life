from flask import Blueprint, Response, g, jsonify, render_template, request

from ..services import clock, home, journal, room
from .auth import login_required

bp = Blueprint("room", __name__)
HEADERS = {"Cache-Control": "no-cache"}


def _choice():
    """Escolha salva; parâmetros na URL servem para pré-visualizar (como no personagem)."""
    choice = home.current(g.user)
    choice.update({k: v for k, v in request.args.items() if k in home.FIELDS})
    return home.validate(choice)


@bp.get("/quarto")
@login_required
def page():
    return render_template("home.html")


@bp.get("/cenario.svg")
@login_required
def background():
    return Response(room.background(_choice()["tema"]), mimetype="image/svg+xml", headers=HEADERS)


@bp.get("/quarto.svg")
@login_required
def svg():
    """Objetos do quarto e mascote, de acordo com o progresso de hoje."""
    today = clock.today()
    snap = journal.snapshot(g.user, today)
    humor = request.args.get("humor")
    if humor not in room.HUMORS:
        humor = room.mood(snap, today)["humor"]
    return Response(room.render(snap["levels"], humor, _choice()), mimetype="image/svg+xml", headers=HEADERS)


@bp.get("/api/quarto")
@login_required
def get_home():
    return jsonify(home.overview(g.user))


@bp.put("/api/quarto")
@login_required
def save_home():
    return jsonify(home.save(g.user, request.get_json(silent=True) or {}))
