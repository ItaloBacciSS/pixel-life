from datetime import date

from app.services import streaks

D = date(2026, 1, 1)


def test_sem_registros_tudo_zero():
    assert streaks.compute(None, [], D) == {"atual": 0, "recorde": 0}


def test_sem_tropecos_conta_desde_o_primeiro_registro():
    assert streaks.compute(D, [], date(2026, 1, 11)) == {"atual": 10, "recorde": 10}


def test_tropeco_hoje_zera_a_sequencia_atual():
    hoje = date(2026, 1, 11)
    assert streaks.compute(D, [hoje], hoje) == {"atual": 0, "recorde": 10}


def test_recorde_guarda_o_maior_intervalo():
    tropecos = [date(2026, 1, 5), date(2026, 1, 20)]
    resultado = streaks.compute(D, tropecos, date(2026, 1, 22))
    assert resultado == {"atual": 2, "recorde": 15}
