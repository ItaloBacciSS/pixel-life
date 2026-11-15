import json
import re
from functools import lru_cache
from pathlib import Path

from . import rules, sprites

DATA = Path(__file__).resolve().parent.parent / "data" / "quarto.json"
BACKGROUND = Path(__file__).resolve().parents[2] / "static" / "img" / "cenario.svg"
WIDTH, HEIGHT = 48, 28
HUMORS = ("normal", "feliz", "triste")
STYLE = (".pet.feliz{animation:pulo .6s steps(1) infinite}"
         "@keyframes pulo{50%{transform:translateY(-1px)}}"
         "@media (prefers-reduced-motion:reduce){.pet{animation:none}}")


@lru_cache
def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def species(species_id):
    return next(item for item in load()["mascote"]["especies"] if item["id"] == species_id)


def mood(snap, today):
    """Humor do mascote: feliz com dia produtivo, triste depois de dias parado."""
    settings = rules.load()["mascote"]
    done_today = sum(1 for e in snap["entries"] if e.day == today and not snap["actions"][e.action_key]["tropeco"])
    idle = (today - snap["ultimo_dia"]).days if snap["ultimo_dia"] else 0
    if done_today >= settings["feliz"]["registros_hoje"]:
        humor = "feliz"
    elif idle >= settings["triste"]["dias_parado"]:
        humor = "triste"
    else:
        humor = "normal"
    return {"nome": settings["nome"], "humor": humor, "frase": settings[humor]["frase"]}


def _paint(pixels, rows, x0, y0, colors):
    for dy, row in enumerate(rows):
        for dx, char in enumerate(row):
            if char != ".":
                pixels[(x0 + dx, y0 + dy)] = colors[char]


def pet_colors(species_id, coat_id):
    """Cores do mascote: as comuns mais as da pelagem escolhida."""
    coat = next(item for item in species(species_id)["pelagens"] if item["id"] == coat_id)
    return {**load()["mascote"]["cores"], **coat["cores"]}


def render(levels, humor, home):
    """Objetos do quarto (um por atributo que chegou ao nível mínimo) e o mascote escolhido."""
    data = load()
    props, pet = {}, {}
    for prop in data["props"]:
        if levels[prop["atributo"]]["nivel"] >= data["nivel_minimo"]:
            _paint(props, prop["mapa"], prop["x"], prop["y"], prop["cores"])
    mascot = data["mascote"]
    _paint(pet, species(home["especie"])["mapas"][humor], mascot["x"], mascot["y"],
           pet_colors(home["especie"], home["pelagem"]))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" shape-rendering="crispEdges">'
            f"<style>{STYLE}</style>{sprites.to_rects(props, WIDTH, HEIGHT)}"
            f'<g class="pet {humor}">{sprites.to_rects(pet, WIDTH, HEIGHT)}</g></svg>')


def background(theme_id):
    """Cenário do quarto com as cores do tema (e os detalhes extras dele, como as estrelas)."""
    theme = next(item for item in load()["temas"] if item["id"] == theme_id)
    svg = re.sub(r'fill="(#[0-9a-fA-F]{6})"',
                 lambda m: f'fill="{theme["trocas"].get(m.group(1).lower(), m.group(1))}"',
                 BACKGROUND.read_text(encoding="utf-8"))
    extras = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
                     for x, y, w, h, color in theme.get("extras", []))
    return svg.replace("</svg>", extras + "</svg>")
