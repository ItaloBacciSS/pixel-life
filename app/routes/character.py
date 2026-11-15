from flask import Blueprint, Response, g, jsonify, render_template, request

from ..services import character, clock, sprites
from .auth import login_required

bp = Blueprint("character", __name__)


@bp.get("/personagem")
@login_required
def page():
    return render_template("character.html", first_time=bool(request.args.get("primeiro")))


@bp.get("/personagem.svg")
@login_required
def svg():
    """Desenho do personagem salvo; parâmetros na URL servem para pré-visualizar mudanças."""
    look = character.current_look(g.user, clock.today())
    look.update({k: v for k, v in request.args.items() if k in ("corpo", "pele", "cabelo", "roupa")})
    if "itens" in request.args:
        look["itens"] = [i for i in request.args["itens"].split(",") if i]
    return Response(sprites.render(character.validate(look)), mimetype="image/svg+xml",
                    headers={"Cache-Control": "no-cache"})


@bp.get("/api/personagem")
@login_required
def get_character():
    return jsonify(character.overview(g.user, clock.today()))


@bp.put("/api/personagem")
@login_required
def save_character():
    data = request.get_json(silent=True) or {}
    return jsonify(character.save(g.user, data, clock.today()))
