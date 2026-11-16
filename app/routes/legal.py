from flask import Blueprint, render_template

bp = Blueprint("legal", __name__)


@bp.get("/privacidade")
def privacy():
    return render_template("privacy.html")
