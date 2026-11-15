from ..errors import ApiError
from ..extensions import db
from ..models import Character
from . import items, journal, rules

FIELDS = (("corpo", "corpos"), ("pele", "peles"), ("cabelo", "cabelos"), ("roupa", "roupas"))


def _defaults():
    options = rules.load()["personagem"]
    return {**{field: options[choices][0] for field, choices in FIELDS}, "itens": []}


def _stored(user):
    row = db.session.get(Character, user.id)
    if row is None:
        return _defaults()
    return {**{field: getattr(row, field) for field, _ in FIELDS}, "itens": list(row.itens)}


def validate(look):
    """Confere corpo, cores e itens (um por lugar do corpo). Não confere se os itens estão liberados."""
    options = rules.load()["personagem"]
    clean = {}
    for field, choices in FIELDS:
        if look.get(field) not in options[choices]:
            raise ApiError(f"Opção inválida: {field}.")
        clean[field] = look[field]
    ids = look.get("itens") or []
    catalog = rules.items()
    if not isinstance(ids, list) or any(not isinstance(i, str) or i not in catalog for i in ids):
        raise ApiError("Item desconhecido.")
    slots = [catalog[i]["slot"] for i in ids]
    if len(set(ids)) != len(ids) or len(set(slots)) != len(slots):
        raise ApiError("Só dá para usar um item por lugar do corpo.")
    clean["itens"] = ids
    return clean


def _overview(user, catalog):
    unlocked = {item["id"] for item in catalog if item["liberado"]}
    look = _stored(user)
    look["itens"] = [i for i in look["itens"] if i in unlocked]
    return {"personagem": look, "opcoes": rules.load()["personagem"], "itens": catalog}


def overview(user, today):
    return _overview(user, items.catalog(journal.snapshot(user, today)))


def current_look(user, today):
    return overview(user, today)["personagem"]


def save(user, look, today):
    clean = validate(look)
    catalog = items.catalog(journal.snapshot(user, today))
    unlocked = {item["id"] for item in catalog if item["liberado"]}
    if not set(clean["itens"]) <= unlocked:
        raise ApiError("Esse item ainda está bloqueado.", 403)
    row = db.session.get(Character, user.id) or Character(user_id=user.id)
    for field, _ in FIELDS:
        setattr(row, field, clean[field])
    row.itens = clean["itens"]
    db.session.add(row)
    db.session.commit()
    return _overview(user, catalog)
