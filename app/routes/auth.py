from functools import wraps

from flask import (Blueprint, abort, current_app, flash, g, redirect,
                   render_template, request, session, url_for)

from ..extensions import db
from ..models import User
from ..services import accounts, throttle

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                abort(401)
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def _start_session(user, endpoint="game.home", **values):
    session.clear()
    session["user_id"] = user.id
    return redirect(url_for(endpoint, **values))


def _validate(username, password):
    if not 3 <= len(username) <= 40:
        return "O usuário precisa ter de 3 a 40 caracteres."
    error = accounts.validate_password(password)
    if error:
        return error
    if User.query.filter_by(username=username).first():
        return "Esse usuário já existe."


@bp.route("/registro", methods=("GET", "POST"))
def register():
    if not current_app.config["REGISTRATION_OPEN"]:
        abort(404)
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        error = _validate(username, password)
        if error is None:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return _start_session(user, "character.page", primeiro=1)
        flash(error)
    return render_template("auth.html", registro=True)


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        if throttle.blocked(username):
            flash("Muitas tentativas. Aguarde 15 minutos e tente de novo.")
            return render_template("auth.html", registro=False), 429
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(request.form.get("password", "")):
            throttle.clear(username)
            return _start_session(user)
        throttle.record_failure(username)
        flash("Usuário ou senha incorretos.")
    return render_template("auth.html", registro=False)


@bp.post("/sair")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
