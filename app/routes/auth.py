from functools import wraps

from flask import (Blueprint, abort, current_app, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from ..services import accounts, network, throttle

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


def _validate(username, password, accepted):
    error = accounts.validate_username(username) or accounts.validate_password(password, username)
    if error:
        return error
    if not accepted:
        return "Para criar a conta, aceite a política de privacidade."
    if User.query.filter_by(username=username).first():
        return "Esse usuário já existe."


def _too_many(message, template, **context):
    flash(message)
    return render_template(template, **context), 429


def _throttle_keys(username):
    # Nomes fora do padrão não viram chave (evita lixo no banco e colisão com as chaves de IP).
    return (username if accounts.USERNAME.fullmatch(username) else "invalido"), network.fingerprint("ip")


def _locked(user_key, ip_key):
    return throttle.blocked(user_key) or throttle.blocked(ip_key, throttle.MAX_FAILURES_IP)


@bp.route("/registro", methods=("GET", "POST"))
def register():
    if not current_app.config["REGISTRATION_OPEN"]:
        abort(404)
    if request.method == "POST":
        signup_key = network.fingerprint("reg")
        if throttle.blocked(signup_key, throttle.MAX_SIGNUPS, throttle.SIGNUP_WINDOW):
            return _too_many("Muitas contas criadas por aqui. Tente de novo mais tarde.", "auth.html", registro=True)
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        error = _validate(username, password, request.form.get("aceito"))
        if error is None:
            user = User(username=username)
            user.set_password(password)
            code = accounts.new_recovery_code(user)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:  # dois cadastros do mesmo nome ao mesmo tempo
                db.session.rollback()
                error = "Esse usuário já existe."
            else:
                throttle.record(signup_key)
                response = _start_session(user, "auth.recovery_page", primeiro=1)
                session["recovery_code"] = code
                return response
        flash(error)
    return render_template("auth.html", registro=True)


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        user_key, ip_key = _throttle_keys(username)
        if _locked(user_key, ip_key):
            return _too_many("Muitas tentativas. Aguarde 15 minutos e tente de novo.", "auth.html", registro=False)
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(request.form.get("password", "")):
            throttle.clear(user_key)
            return _start_session(user)
        throttle.record(user_key)
        throttle.record(ip_key)
        flash("Usuário ou senha incorretos.")
    return render_template("auth.html", registro=False)


@bp.route("/recuperar", methods=("GET", "POST"))
def recover():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        new = request.form.get("password", "")
        user_key, ip_key = _throttle_keys(username)
        if _locked(user_key, ip_key):
            return _too_many("Muitas tentativas. Aguarde 15 minutos e tente de novo.", "recover.html")
        error = accounts.validate_password(new, username)
        if error:
            flash(error)
            return render_template("recover.html")
        user = User.query.filter_by(username=username).first()
        new_code = user and accounts.reset_password(user, request.form.get("code", ""), new)
        if new_code:
            throttle.clear(user_key)
            response = _start_session(user, "auth.recovery_page")
            session["recovery_code"] = new_code
            return response
        throttle.record(user_key)
        throttle.record(ip_key)
        flash("Usuário ou código incorretos.")
    return render_template("recover.html")


@bp.get("/codigo")
@login_required
def recovery_page():
    """Mostra o código de recuperação uma única vez; ao recarregar a página ele não aparece de novo."""
    code = session.pop("recovery_code", None)
    if code is None:
        return redirect(url_for("game.home"))
    after = url_for("character.page", primeiro=1) if request.args.get("primeiro") else url_for("game.home")
    response = make_response(render_template("recovery_code.html", code=code, after=after))
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.post("/sair")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
