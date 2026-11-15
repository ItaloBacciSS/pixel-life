from collections import Counter
from datetime import timedelta

from ..errors import ApiError
from ..extensions import db
from ..models import Goal

MAX_GOALS = 20


def week_start(today):
    """Segunda-feira da semana de `today`."""
    return today - timedelta(days=today.weekday())


def create(user, action_key, vezes, actions):
    action = actions.get(action_key)
    if action is None or action["tropeco"]:
        raise ApiError("Escolha uma ação boa para a meta.")
    if isinstance(vezes, bool) or not isinstance(vezes, int) or not 1 <= vezes <= 7:
        raise ApiError("A meta vai de 1 a 7 vezes por semana.")
    if Goal.query.filter_by(user_id=user.id, action_key=action_key).first():
        raise ApiError("Você já tem uma meta para essa ação.", 409)
    if Goal.query.filter_by(user_id=user.id).count() >= MAX_GOALS:
        raise ApiError(f"O limite é de {MAX_GOALS} metas.")
    db.session.add(Goal(user_id=user.id, action_key=action_key, vezes=vezes))
    db.session.commit()


def remove(user, goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
    if goal is None:
        raise ApiError("Meta não encontrada.", 404)
    db.session.delete(goal)
    db.session.commit()


def overview(user, snap, today):
    """Metas semanais com quantas vezes a ação foi feita desde a segunda-feira."""
    start = week_start(today)
    done = Counter(e.action_key for e in snap["entries"] if start <= e.day <= today)
    return [{"id": goal.id, "key": goal.action_key, "nome": snap["actions"][goal.action_key]["nome"],
             "vezes": goal.vezes, "feitas": done[goal.action_key], "cumprida": done[goal.action_key] >= goal.vezes}
            for goal in Goal.query.filter_by(user_id=user.id).order_by(Goal.id)
            if goal.action_key in snap["actions"]]


def options(actions, attributes):
    """Ações boas que podem virar meta, com o nome do atributo."""
    names = {attr["id"]: attr["nome"] for attr in attributes}
    return [{"key": key, "nome": action["nome"], "atributo": names[next(iter(action["efeitos"]))]}
            for key, action in actions.items() if not action["tropeco"]]


def view(user, snap, today):
    start = week_start(today)
    return {"inicio": start.isoformat(), "fim": (start + timedelta(days=6)).isoformat(),
            "metas": overview(user, snap, today)}
