import json
from functools import lru_cache
from pathlib import Path

from . import rules

STYLE = (".olhos{animation:piscar 4.5s steps(1) infinite}"
         "@keyframes piscar{96%{opacity:0}99%{opacity:1}}"
         "@media (prefers-reduced-motion:reduce){.olhos{animation:none}}")

SPRITES_FILE = Path(__file__).resolve().parent.parent / "data" / "sprites.json"


@lru_cache
def load():
    return json.loads(SPRITES_FILE.read_text(encoding="utf-8"))


def to_rects(pixels, width, height):
    """Junta pixels vizinhos da mesma cor em retângulos horizontais (SVG menor)."""
    rects = []
    for y in range(height):
        x = 0
        while x < width:
            color = pixels.get((x, y))
            end = x + 1
            while color and end < width and pixels.get((end, y)) == color:
                end += 1
            if color:
                rects.append(f'<rect x="{x}" y="{y}" width="{end - x}" height="1" fill="{color}"/>')
            x = end
    return "".join(rects)


def render(look):
    """Monta o SVG do personagem por camadas. `look` já deve estar validado."""
    data = load()
    palette = {**data["paleta"], "s": look["pele"], "h": look["cabelo"], "t": look["roupa"]}
    worn = {rules.items()[item_id]["slot"]: item_id for item_id in look["itens"]}
    pixels = {}
    eyes = set()

    def paint(rows, y0=0, colors=None):
        for dy, row in enumerate(rows):
            for x, char in enumerate(row):
                if char != ".":
                    pixels[(x, y0 + dy)] = (colors or {}).get(char) or palette[char]
                    eyes.discard((x, y0 + dy))

    body = data["corpos"][look["corpo"]]
    for step in data["ordem"]:
        if step == "base":
            paint(body["base"])
            paint(body["roupa"])
            eyes |= {(x, y) for y, row in enumerate(body["base"])
                     for x, char in enumerate(row) if char == "e"}
        elif step == "cabelo":
            paint(body["cabelo"])
        elif step in worn:
            sprite = data["itens"][worn[step]]
            paint(sprite["mapa"], sprite["y"], sprite["cores"])

    open_eyes = {pos: pixels[pos] for pos in eyes}
    pixels.update({pos: look["pele"] for pos in eyes})
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 20" shape-rendering="crispEdges">'
            f"<style>{STYLE}</style>" + to_rects(pixels, 14, 20)
            + f'<g class="olhos">{to_rects(open_eyes, 14, 20)}</g></svg>')
