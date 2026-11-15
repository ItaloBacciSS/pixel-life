from ..errors import ApiError
from ..extensions import db
from ..models import Character, CustomAction, Entry, Goal, Home, MoneyMove

MIN_PASSWORD = 8


def validate_password(password):
    if len(password) < MIN_PASSWORD:
        return f"A senha precisa ter pelo menos {MIN_PASSWORD} caracteres."


def _check_current(user, password):
    if not user.check_password(password or ""):
        raise ApiError("Senha atual incorreta.", 403)


def change_password(user, current, new):
    _check_current(user, current)
    error = validate_password(new or "")
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
