from datetime import date, timedelta

from app.services import progress

D = date(2026, 1, 1)


def dia(n):
    return D + timedelta(days=n)


def estado(entries, hoje):
    return progress.compute(entries, hoje)


def test_sem_registros_tudo_zerado():
    assert all(a["nivel"] == 0 and a["xp"] == 0 for a in estado([], D).values())


def test_dez_treinos_nao_chegam_ao_nivel_dois():
    entries = [(dia(i), {"forca": 10}) for i in range(10)]
    forca = estado(entries, dia(9))["forca"]
    assert (forca["nivel"], forca["xp"]) == (1, 0)


def test_nove_treinos_ficam_no_nivel_zero():
    entries = [(dia(i), {"forca": 10}) for i in range(9)]
    forca = estado(entries, dia(8))["forca"]
    assert (forca["nivel"], forca["xp"], forca["custo"]) == (0, 90, 100)


def test_varios_efeitos_no_mesmo_dia_somam():
    forca = estado([(D, {"forca": 10}), (D, {"forca": 5})], D)["forca"]
    assert forca["xp"] == 15


def test_decaimento_comeca_depois_da_carencia():
    # Vitalidade: carência 2, perda 4. Dias 3 e 4 perdem; o dia 5 é hoje e não perde.
    entries = [(D, {"vitalidade": 10})]
    assert estado(entries, dia(2))["vitalidade"]["xp"] == 10
    assert estado(entries, dia(4))["vitalidade"]["xp"] == 6
    assert estado(entries, dia(5))["vitalidade"]["xp"] == 2


def test_decaimento_nao_passa_de_zero_nem_derruba_o_nivel():
    entries = [(D, {"fe": 100})]
    fe = estado(entries, dia(60))["fe"]
    assert (fe["nivel"], fe["xp"]) == (1, 0)


def test_atributos_sem_decaimento_nao_perdem_com_o_tempo():
    entries = [(D, {"intelecto": 10}), (D, {"carreira": 10})]
    resultado = estado(entries, dia(200))
    assert resultado["intelecto"]["xp"] == resultado["carreira"]["xp"] == 10


def test_acao_positiva_reinicia_a_carencia():
    entries = [(D, {"vitalidade": 10}), (dia(2), {"vitalidade": 10})]
    assert estado(entries, dia(4))["vitalidade"]["xp"] == 20


def test_tropeco_nao_reinicia_a_carencia():
    entries = [(D, {"vitalidade": 20}), (dia(2), {"vitalidade": -1})]
    # dias 3 e 4 decaem mesmo com o tropeço no dia 2
    assert estado(entries, dia(5))["vitalidade"]["xp"] == 20 - 1 - 4 - 4


def test_tropeco_tira_da_barra_mas_nunca_abaixo_de_zero():
    entries = [(D, {"fe": 10}), (dia(1), {"fe": -25})]
    assert estado(entries, dia(1))["fe"]["xp"] == 0


def test_registro_de_dia_passado_recalcula_o_estado():
    sem = estado([(D, {"vitalidade": 10})], dia(5))["vitalidade"]["xp"]
    com = estado([(D, {"vitalidade": 10}), (dia(3), {"vitalidade": 10})], dia(5))["vitalidade"]["xp"]
    assert com > sem


def test_historico_termina_no_mesmo_nivel_do_estado_atual():
    entries = [(dia(i), {"forca": 20}) for i in range(30)]
    dias, niveis = progress.history(entries, dia(29))
    assert len(dias) == 30 and dias[0] == dia(0) and dias[-1] == dia(29)
    assert niveis["forca"][-1] == estado(entries, dia(29))["forca"]["nivel"] > 0
    assert niveis["forca"] == sorted(niveis["forca"])  # o nível nunca cai


def test_historico_sem_registros():
    dias, niveis = progress.history([], D)
    assert dias == [D] and all(valores == [0] for valores in niveis.values())
