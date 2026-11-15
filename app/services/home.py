from ..errors import ApiError
from ..extensions import db
from ..models import Home
from . import room

FIELDS = ("tema", "especie", "pelagem")


def validate(choice):
    """Confere tema do quarto, espécie do mascote e a cor que existe para essa espécie."""
    data = room.load()
    if choice.get("tema") not in {theme["id"] for theme in data["temas"]}:
        raise ApiError("Quarto inválido.")
    if choice.get("especie") not in {item["id"] for item in data["mascote"]["especies"]}:
        raise ApiError("Mascote inválido.")
    if choice.get("pelagem") not in {coat["id"] for coat in room.species(choice["especie"])["pelagens"]}:
        raise ApiError("Cor inválida para esse mascote.")
    return {field: choice[field] for field in FIELDS}


def current(user):
    row = db.session.get(Home, user.id)
    return {field: getattr(row, field) for field in FIELDS} if row else dict(room.load()["padrao"])


def overview(user):
    data = room.load()
    return {
        "atual": current(user),
        "opcoes": {
            "temas": [{"id": theme["id"], "nome": theme["nome"]} for theme in data["temas"]],
            "especies": [{"id": item["id"], "nome": item["nome"],
                          "pelagens": [{"id": coat["id"], "nome": coat["nome"], "cor": coat["cores"]["o"]}
                                       for coat in item["pelagens"]]}
                         for item in data["mascote"]["especies"]],
        },
    }


def save(user, choice):
    clean = validate(choice)
    row = db.session.get(Home, user.id) or Home(user_id=user.id)
    for field, value in clean.items():
        setattr(row, field, value)
    db.session.add(row)
    db.session.commit()
    return overview(user)
