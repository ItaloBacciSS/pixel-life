from flask import Blueprint, g, jsonify, request

from ..services import clock, journal
from .auth import login_required

bp = Blueprint("api", __name__, url_prefix="/api")


def _state(day):
    return jsonify(journal.state(g.user, day, clock.today()))


@bp.get("/estado")
@login_required
def get_state():
    return _state(journal.parse_day(request.args.get("dia"), clock.today()))


@bp.post("/registros")
@login_required
def create_entry():
    data = request.get_json(silent=True) or {}
    day = journal.parse_day(data.get("dia"), clock.today())
    journal.record(g.user, data.get("action_key"), day, data.get("nota"))
    return _state(day), 201


@bp.delete("/registros/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    return _state(journal.remove(g.user, entry_id))


@bp.post("/acoes")
@login_required
def create_action():
    data = request.get_json(silent=True) or {}
    journal.create_action(g.user, data.get("nome"), data.get("atributo"),
                          data.get("intensidade"), data.get("tropeco"))
    return _state(clock.today()), 201
