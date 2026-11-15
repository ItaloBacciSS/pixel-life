def compute(first_day, stumble_days, today):
    """Dias sem tropeçar: sequência atual e recorde.

    Conta os dias desde o último tropeço (ou desde o primeiro registro).
    O recorde é o maior intervalo entre dois marcos consecutivos.
    """
    if first_day is None:
        return {"atual": 0, "recorde": 0}
    marks = [first_day, *sorted(set(stumble_days)), today]
    gaps = [(later - earlier).days for earlier, later in zip(marks, marks[1:])]
    return {"atual": gaps[-1], "recorde": max(gaps)}
