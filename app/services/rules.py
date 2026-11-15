import json
from functools import lru_cache
from pathlib import Path

RULES_FILE = Path(__file__).resolve().parent.parent / "data" / "rules.json"


@lru_cache
def load():
    return json.loads(RULES_FILE.read_text(encoding="utf-8"))


def attributes():
    return load()["atributos"]


def cost(level):
    """XP necessário para sair do nível `level` para o próximo."""
    nivel = load()["nivel"]
    return nivel["base"] + nivel["passo"] * level


@lru_cache
def builtin_actions():
    """Mapa id -> {nome, efeitos, tropeco} com as ações positivas e os tropeços das regras."""
    actions = {}
    for attr in attributes():
        for action in attr["acoes"]:
            actions[action["id"]] = {
                "nome": action["nome"],
                "efeitos": {attr["id"]: action["xp"]},
                "tropeco": False,
            }
    for tropeco in load()["tropecos"]:
        actions[tropeco["id"]] = {
            "nome": tropeco["nome"],
            "efeitos": tropeco["efeitos"],
            "tropeco": True,
        }
    return actions


@lru_cache
def items():
    """Mapa id -> item (nome, lugar no corpo e requisito de desbloqueio)."""
    return {item["id"]: item for item in load()["itens"]}
