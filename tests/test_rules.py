from app.services import rules


def test_custo_dos_niveis_segue_a_curva():
    assert [rules.cost(n) for n in (0, 1, 9, 49)] == [100, 120, 280, 1080]


def test_ids_de_acoes_sao_unicos():
    ids = [a["id"] for attr in rules.attributes() for a in attr["acoes"]]
    ids += [t["id"] for t in rules.load()["tropecos"]]
    assert len(ids) == len(set(ids))


def test_efeitos_apontam_para_atributos_existentes():
    validos = {attr["id"] for attr in rules.attributes()}
    for acao in rules.builtin_actions().values():
        assert set(acao["efeitos"]) <= validos


def test_ha_nove_atributos():
    assert len(rules.attributes()) == 9


def test_tropecos_tiram_xp_e_acoes_dao_xp():
    for acao in rules.builtin_actions().values():
        sinal = all(xp < 0 for xp in acao["efeitos"].values())
        assert sinal == acao["tropeco"]


def test_o_personagem_tem_muitas_falas_curtas_e_sem_repeticao():
    mascote = rules.load()["mascote"]
    grupos = {
        **{humor: mascote[humor]["falas"] for humor in ("normal", "feliz", "triste")},
        **mascote["periodos"],
        "sequencia": mascote["sequencia"],
    }
    assert set(mascote["periodos"]) == {"madrugada", "manha", "tarde", "noite"}
    todas = [fala for falas in grupos.values() for fala in falas]
    assert len(todas) == len(set(todas)), "fala repetida"
    assert all(len(fala) <= 40 for fala in todas), "o balão é pequeno: máximo 40 caracteres"
    assert all(len(grupos[humor]) >= 8 for humor in ("normal", "feliz", "triste"))
    assert all(len(falas) >= 5 for falas in mascote["periodos"].values()) and len(mascote["sequencia"]) >= 5
