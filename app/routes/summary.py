from flask import Blueprint, g, jsonify, render_template

from ..services import clock, summary
from .auth import login_required

bp = Blueprint("summary", __name__)


@bp.get("/progresso")
@login_required
def page():
    return render_template("progress.html")


@bp.get("/api/progresso")
@login_required
def get_summary():
    return jsonify(summary.build(g.user, clock.today()))
