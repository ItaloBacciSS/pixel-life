from flask import Blueprint, g, jsonify, render_template, request

from ..services import clock, journal, wealth
from .auth import login_required

bp = Blueprint("wealth", __name__)


def _overview(status=200):
    return jsonify(wealth.overview(g.user, clock.today())), status


@bp.get("/riqueza")
@login_required
def page():
    return render_template("wealth.html")


@bp.get("/api/riqueza")
@login_required
def get_wealth():
    return _overview()


@bp.post("/api/riqueza")
@login_required
def add_move():
    data = request.get_json(silent=True) or {}
    wealth.add(g.user, data.get("centavos"), journal.parse_day(data.get("dia"), clock.today()), data.get("nota"))
    return _overview(201)


@bp.post("/api/riqueza/saldo")
@login_required
def set_balance():
    data = request.get_json(silent=True) or {}
    wealth.set_balance(g.user, data.get("saldo"), journal.parse_day(data.get("dia"), clock.today()))
    return _overview(201)


@bp.delete("/api/riqueza/<int:move_id>")
@login_required
def delete_move(move_id):
    wealth.remove(g.user, move_id)
    return _overview()
