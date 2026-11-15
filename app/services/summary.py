from collections import Counter
from datetime import timedelta

from . import achievements, goals, journal, progress, rules

STEP = 7  # a evolução tem um ponto por semana, mais o dia de hoje


def _positive(snap, entries):
    return [e for e in entries if not snap["actions"][e.action_key]["tropeco"]]


def week(user, snap, today):
    start = goals.week_start(today)
    actions = snap["actions"]
    entries = [e for e in snap["entries"] if start <= e.day <= today]
    good = _positive(snap, entries)

    xp = Counter()
    for entry in entries:
        xp.update(actions[entry.action_key]["efeitos"])
    per_day = Counter(e.day for e in good)
    best = max(sorted(per_day.items()), key=lambda item: item[1], default=None)

    before = progress.compute([pair for pair in snap["historico"] if pair[0] < start], start)
    now = snap["levels"]
    previous = [e for e in snap["entries"] if start - timedelta(days=7) <= e.day < start]
    metas = goals.overview(user, snap, today)
    return {
        "inicio": start.isoformat(),
        "fim": (start + timedelta(days=6)).isoformat(),
        "acoes": len(good),
        "acoes_anterior": len(_positive(snap, previous)),
        "tropecos": len(entries) - len(good),
        "xp": sorted(({"id": a["id"], "nome": a["nome"], "icone": a["icone"], "cor": a["cor"], "xp": xp[a["id"]]}
                      for a in rules.attributes() if xp[a["id"]]), key=lambda item: -item["xp"]),
        "melhor_dia": {"dia": best[0].isoformat(), "acoes": best[1]} if best else None,
        "subiu": [{"id": a["id"], "nome": a["nome"], "de": before[a["id"]]["nivel"], "para": now[a["id"]]["nivel"]}
                  for a in rules.attributes() if now[a["id"]]["nivel"] > before[a["id"]]["nivel"]],
        "metas": {"cumpridas": sum(m["cumprida"] for m in metas), "total": len(metas)},
        "sequencia": snap["sequences"]["geral"]["atual"],
    }


def evolution(snap, today):
    """Nível geral e de cada atributo ao longo do tempo, amostrado por semana."""
    dates, levels = progress.history(snap["historico"], today)
    picks = list(range(0, len(dates), STEP))
    if picks[-1] != len(dates) - 1:
        picks.append(len(dates) - 1)
    series = {"geral": [sum(levels[attr][i] for attr in levels) for i in picks]}
    series.update({attr: [values[i] for i in picks] for attr, values in levels.items()})
    labels = [{"id": "geral", "nome": "Nível geral", "cor": "#2b2d42"}]
    labels += [{"id": a["id"], "nome": a["nome"], "cor": a["cor"]} for a in rules.attributes()]
    return {"datas": [dates[i].isoformat() for i in picks], "series": series, "rotulos": labels}


def build(user, today):
    snap = journal.snapshot(user, today)
    return {"semana": week(user, snap, today), "evolucao": evolution(snap, today),
            "conquistas": achievements.catalog(snap)}
