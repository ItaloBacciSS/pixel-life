import json
import re
import secrets
from functools import lru_cache
from pathlib import Path

from werkzeug.security import generate_password_hash

from ..errors import ApiError
from ..extensions import db
from ..models import Character, CustomAction, Entry, Goal, Home, MoneyMove

MIN_PASSWORD = 8
MAX_PASSWORD = 128
USERNAME = re.compile(r"[a-z0-9_.-]{3,40}")
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sem 0/O e 1/I, que se confundem
CODE_LENGTH = 16
COMMON = Path(__file__).resolve().parent.parent / "data" / "senhas_comuns.json"


@lru_cache
def _common_passwords():
    return set(json.loads(COMMON.read_text(encoding="utf-8")))


def validate_username(username):
    if not USERNAME.fullmatch(username):
        return "O usuário precisa ter de 3 a 40 caracteres: letras, números, _ . ou -."


def validate_password(password, username=""):
    if len(password) < MIN_PASSWORD:
        return f"A senha precisa ter pelo menos {MIN_PASSWORD} caracteres."
    if len(password) > MAX_PASSWORD:
        return f"A senha pode ter no máximo {MAX_PASSWORD} caracteres."
    if password.lower() in _common_passwords() or password.lower() == username:
        return "Essa senha é muito comum ou fácil de adivinhar. Escolha outra."


def _normalize_code(code):
    return re.sub(r"[^A-Z0-9]", "", (code or "").upper())


def _issue_recovery_code(user):
    """Gera um código novo (só o hash fica guardado) e devolve o texto para mostrar uma única vez."""
    code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
    user.recovery_hash = generate_password_hash(code)
    return "-".join(code[i:i + 4] for i in range(0, CODE_LENGTH, 4))


def new_recovery_code(user):
    return _issue_recovery_code(user)


def regenerate_recovery_code(user, password):
    _check_current(user, password)
    code = _issue_recovery_code(user)
    db.session.commit()
    return code


def reset_password(user, code, new):
    """Troca a senha com o código de recuperação; o código usado deixa de valer e um novo é emitido."""
    if not user.check_recovery(_normalize_code(code)):
        return None
    user.set_password(new)
    new_code = _issue_recovery_code(user)
    db.session.commit()
    return new_code


def _check_current(user, password):
    if not user.check_password(password or ""):
        raise ApiError("Senha atual incorreta.", 403)


def change_password(user, current, new):
    _check_current(user, current)
    error = validate_password(new or "", user.username)
    if error:
        raise ApiError(error)
    user.set_password(new)
    db.session.commit()


def delete_account(user, password):
    _check_current(user, password)
    for model in (Entry, CustomAction, Character, Goal, Home, MoneyMove):
        model.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
