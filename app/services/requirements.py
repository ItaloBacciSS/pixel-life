from . import rules


def evaluate(req, snap):
    """Progresso de um requisito: (valor atual, meta, texto). Usado por itens e conquistas."""
    names = {attr["id"]: attr["nome"] for attr in rules.attributes()}
    if "vezes" in req:
        attr = req["atributo"]
        return snap["por_atributo"].get(attr, 0), req["vezes"], f"{req['vezes']} ações de {names[attr]}"
    if "nivel" in req:
        attr = req["atributo"]
        return snap["levels"][attr]["nivel"], req["nivel"], f"{names[attr]} nível {req['nivel']}"
    if "sequencia" in req:
        where = "" if req["sequencia"] == "geral" else f" na {names[req['sequencia']]}"
        return snap["sequences"][req["sequencia"]]["recorde"], req["dias"], f"{req['dias']} dias sem tropeçar{where}"
    if "nivel_geral" in req:
        return snap["nivel_geral"], req["nivel_geral"], f"Nível geral {req['nivel_geral']}"
    if "registros" in req:
        return snap["registros"], req["registros"], f"{req['registros']} registro{'' if req['registros'] == 1 else 's'}"
    if "dias_ativos" in req:
        return snap["dias_ativos"], req["dias_ativos"], f"{req['dias_ativos']} dias de jogo"
    if "todos" in req:
        lowest = min(level["nivel"] for level in snap["levels"].values())
        return lowest, req["todos"], f"Todos os atributos no nível {req['todos']}"
    raise ValueError(f"Requisito desconhecido: {req}")


def status(req, snap):
    current, goal, text = evaluate(req, snap)
    return {"requisito": text, "atual": min(current, goal), "meta": goal, "liberado": current >= goal}
