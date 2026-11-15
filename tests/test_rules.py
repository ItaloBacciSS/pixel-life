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
