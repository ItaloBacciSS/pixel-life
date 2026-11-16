from flask import Blueprint, g, jsonify, render_template, request, session

from ..services import accounts
from .auth import login_required

bp = Blueprint("profile", __name__)


@bp.get("/perfil")
@login_required
def page():
    return render_template("profile.html")


@bp.post("/api/senha")
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    accounts.change_password(g.user, data.get("atual"), data.get("nova"))
    return jsonify(ok=True)


@bp.delete("/api/conta")
@login_required
def delete_account():
    data = request.get_json(silent=True) or {}
    accounts.delete_account(g.user, data.get("senha"))
    session.clear()
    return jsonify(ok=True)


@bp.post("/api/recuperacao")
@login_required
def recovery_code():
    data = request.get_json(silent=True) or {}
    return jsonify(codigo=accounts.regenerate_recovery_code(g.user, data.get("senha")))
