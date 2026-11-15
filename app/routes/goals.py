from flask import Blueprint, g, jsonify, render_template, request

from ..services import clock, goals, journal, rules
from .auth import login_required

bp = Blueprint("goals", __name__)


def _view():
    today = clock.today()
    snap = journal.snapshot(g.user, today)
    return jsonify(**goals.view(g.user, snap, today), acoes=goals.options(snap["actions"], rules.attributes()))


@bp.get("/metas")
@login_required
def page():
    return render_template("goals.html")


@bp.get("/api/metas")
@login_required
def get_goals():
    return _view()


@bp.post("/api/metas")
@login_required
def create_goal():
    data = request.get_json(silent=True) or {}
    goals.create(g.user, data.get("action_key"), data.get("vezes"), journal.available_actions(g.user))
    response = _view()
    response.status_code = 201
    return response


@bp.delete("/api/metas/<int:goal_id>")
@login_required
def delete_goal(goal_id):
    goals.remove(g.user, goal_id)
    return _view()
