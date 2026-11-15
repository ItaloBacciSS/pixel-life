from collections import Counter
from datetime import date

from ..errors import ApiError
from ..extensions import db
from ..models import CustomAction, Entry
from . import achievements, goals, progress, room, rules, streaks, wealth


def parse_day(value, today):
    if not value:
        return today
    try:
        day = date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ApiError("Data inválida.")
    if day > today:
        raise ApiError("Não dá para registrar dias futuros.")
    return day


def available_actions(user):
    """Ações das regras mais as criadas pelo jogador, por chave."""
    actions = dict(rules.builtin_actions())
    for custom in CustomAction.query.filter_by(user_id=user.id):
        actions[f"custom-{custom.id}"] = {
            "nome": custom.nome,
            "efeitos": custom.efeitos,
            "tropeco": custom.tropeco,
        }
    return actions


def record(user, action_key, day, note=None):
    if action_key not in available_actions(user):
        raise ApiError("Ação desconhecida.", 404)
    if Entry.query.filter_by(user_id=user.id, action_key=action_key, day=day).first():
        raise ApiError("Você já registrou isso nesse dia.", 409)
    note = (note or "").strip()[:500] or None
    db.session.add(Entry(user_id=user.id, action_key=action_key, day=day, note=note))
    db.session.commit()


def remove(user, entry_id):
    entry = Entry.query.filter_by(id=entry_id, user_id=user.id).first()
    if entry is None:
        raise ApiError("Registro não encontrado.", 404)
    day = entry.day
    db.session.delete(entry)
    db.session.commit()
    return day


def create_action(user, nome, atributo, intensidade, tropeco):
    nome = (nome or "").strip()
    if not 1 <= len(nome) <= 60:
        raise ApiError("O nome precisa ter de 1 a 60 caracteres.")
    if atributo not in {attr["id"] for attr in rules.attributes()}:
        raise ApiError("Atributo inválido.")
    tabela = rules.load()["intensidades"]["negativo" if tropeco else "positivo"]
    if intensidade not in tabela:
        raise ApiError("Intensidade inválida.")
    db.session.add(CustomAction(user_id=user.id, nome=nome, tropeco=bool(tropeco),
                                efeitos={atributo: tabela[intensidade]}))
    db.session.commit()


def snapshot(user, today):
    """Foto do jogador hoje: ações, registros, nível de cada atributo e sequências."""
    actions = available_actions(user)
    entries = [e for e in Entry.query.filter_by(user_id=user.id) if e.action_key in actions]
    history = [(e.day, actions[e.action_key]["efeitos"]) for e in entries]
    levels = progress.compute(history, today)

    first_day = min((e.day for e in entries), default=None)
    stumbles = [(e.day, actions[e.action_key]["efeitos"])
                for e in entries if actions[e.action_key]["tropeco"]]
    sequences = {"geral": streaks.compute(first_day, [d for d, _ in stumbles], today)}
    for attr_id in rules.load()["sequencias"]:
        days = [d for d, efeitos in stumbles if attr_id in efeitos]
        sequences[attr_id] = streaks.compute(first_day, days, today)

    return {
        "actions": actions,
        "entries": entries,
        "historico": history,
        "levels": levels,
        "registros": len(entries),
        "dias_ativos": len({e.day for e in entries}),
        "por_atributo": Counter(attr for _, effects in history for attr, xp in effects.items() if xp > 0),
        "ultimo_dia": max((e.day for e in entries), default=None),
        "sequences": sequences,
        "nivel_geral": sum(level["nivel"] for level in levels.values()),
    }


def state(user, day, today):
    """Tudo o que a tela do jogo precisa, com o que já foi feito em `day`."""
    snap = snapshot(user, today)
    done = {e.action_key: e.id for e in snap["entries"] if e.day == day}
    return {
        "dia": day.isoformat(),
        "hoje": today.isoformat(),
        "nivel_geral": snap["nivel_geral"],
        "atributos": [{"id": a["id"], "nome": a["nome"], "icone": a["icone"], "cor": a["cor"],
                       **snap["levels"][a["id"]]} for a in rules.attributes()],
        "acoes": [{"key": key, **action, "registro_id": done.get(key)}
                  for key, action in snap["actions"].items()],
        "sequencias": snap["sequences"],
        "conquistas": achievements.catalog(snap),
        "metas": goals.overview(user, snap, today),
        "saldo": wealth.balance(user),
        "mascote": room.mood(snap, today),
    }
