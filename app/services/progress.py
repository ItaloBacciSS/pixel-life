from collections import defaultdict
from datetime import timedelta

from . import rules


def _level_up(level, bar, gain):
    """Aplica o ganho (ou perda) à barra. O nível nunca cai; a barra para em 0."""
    bar = max(0, bar + gain)
    while bar >= rules.cost(level):
        bar -= rules.cost(level)
        level += 1
    return level, bar


def _daily_effects(entries):
    """(dia, efeitos) -> {dia: {atributo: [ganho líquido, teve ação positiva]}}"""
    days = defaultdict(lambda: defaultdict(lambda: [0, False]))
    for day, effects in entries:
        for attr_id, xp in effects.items():
            days[day][attr_id][0] += xp
            days[day][attr_id][1] |= xp > 0
    return days


def _walk(attr, days, first, today):
    """Nível e barra de um atributo ao fim de cada dia, de `first` até `today`.

    O decaimento começa depois da carência (dias sem ação positiva no atributo)
    e nunca é aplicado no dia de hoje, que ainda pode receber registros.
    """
    level = bar = idle = 0
    decay = attr["decaimento"]
    for offset in range((today - first).days + 1):
        day = first + timedelta(days=offset)
        net, positive = days[day][attr["id"]] if day in days else (0, False)
        idle = 0 if positive else idle + 1
        if decay and not positive and day < today and idle > decay["carencia"]:
            net -= decay["perda"]
        level, bar = _level_up(level, bar, net)
        yield level, bar


def compute(entries, today):
    """Reconstrói nível e barra de cada atributo a partir do histórico.

    `entries` é uma lista de (dia, efeitos). O estado é sempre derivado do
    histórico, então ajustar as regras ou registrar dias passados recalcula tudo.
    """
    state = {attr["id"]: {"nivel": 0, "xp": 0} for attr in rules.attributes()}
    if entries:
        days = _daily_effects(entries)
        first = min(day for day, _ in entries)
        for attr in rules.attributes():
            for level, bar in _walk(attr, days, first, today):
                state[attr["id"]] = {"nivel": level, "xp": bar}
    for current in state.values():
        current["custo"] = rules.cost(current["nivel"])
    return state


def history(entries, today):
    """Nível de cada atributo ao fim de cada dia: ([dias], {atributo: [níveis]})."""
    if not entries:
        return [today], {attr["id"]: [0] for attr in rules.attributes()}
    days = _daily_effects(entries)
    first = min(day for day, _ in entries)
    dates = [first + timedelta(days=n) for n in range((today - first).days + 1)]
    return dates, {attr["id"]: [level for level, _ in _walk(attr, days, first, today)]
                   for attr in rules.attributes()}
