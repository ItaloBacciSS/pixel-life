from sqlalchemy import func

from ..errors import ApiError
from ..extensions import db
from ..models import MoneyMove

LIMIT = 10**12  # em centavos
RECENT = 50


def _cents(value, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, int) or abs(value) > LIMIT or (value == 0 and not allow_zero):
        raise ApiError("Valor inválido.")
    return value


def balance(user):
    return db.session.query(func.coalesce(func.sum(MoneyMove.cents), 0)).filter_by(user_id=user.id).scalar()


def add(user, cents, day, note=None):
    db.session.add(MoneyMove(user_id=user.id, day=day, cents=_cents(cents), note=(note or "").strip()[:100] or None))
    db.session.commit()


def set_balance(user, target, day):
    """Ajusta o saldo para `target` registrando a diferença como um movimento."""
    diff = _cents(target, allow_zero=True) - balance(user)
    if diff == 0:
        raise ApiError("O saldo já é esse.")
    add(user, diff, day, "Ajuste de saldo")


def remove(user, move_id):
    move = MoneyMove.query.filter_by(id=move_id, user_id=user.id).first()
    if move is None:
        raise ApiError("Movimento não encontrado.", 404)
    db.session.delete(move)
    db.session.commit()


def overview(user, today):
    """Saldo, últimos movimentos e a evolução do saldo (um ponto por dia com movimento)."""
    moves = MoneyMove.query.filter_by(user_id=user.id).order_by(MoneyMove.day, MoneyMove.id).all()
    series, total = {}, 0
    for move in moves:
        total += move.cents
        series[move.day] = total
    if moves and today not in series:
        series[today] = total
    return {
        "hoje": today.isoformat(),
        "saldo": total,
        "movimentos": [{"id": m.id, "dia": m.day.isoformat(), "centavos": m.cents, "nota": m.note}
                       for m in reversed(moves[-RECENT:])],
        "serie": [{"dia": day.isoformat(), "saldo": value} for day, value in series.items()],
    }
