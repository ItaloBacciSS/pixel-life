from flask import Blueprint, render_template

from .auth import login_required

bp = Blueprint("game", __name__)


@bp.route("/")
@login_required
def home():
    return render_template("game.html")
