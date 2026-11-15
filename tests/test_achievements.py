import pytest

from app.services import requirements, rules


def foto(**mudancas):
    base = {
        "levels": {a["id"]: {"nivel": 0} for a in rules.attributes()},
        "sequences": {"geral": {"atual": 0, "recorde": 0}, "fe": {"atual": 0, "recorde": 0}},
        "nivel_geral": 0, "registros": 0, "dias_ativos": 0, "por_atributo": {},
    }
    return {**base, **mudancas}


@pytest.mark.parametrize("requisito, snap, esperado", [
    ({"registros": 10}, foto(registros=4), (4, 10, "10 registros")),
    ({"dias_ativos": 7}, foto(dias_ativos=2), (2, 7, "7 dias de jogo")),
    ({"atributo": "forca", "vezes": 20}, foto(por_atributo={"forca": 5}), (5, 20, "20 ações de Força")),
    ({"atributo": "forca", "vezes": 20}, foto(), (0, 20, "20 ações de Força")),
    ({"atributo": "fe", "nivel": 5}, foto(levels={**foto()["levels"], "fe": {"nivel": 2}}), (2, 5, "Fé nível 5")),
    ({"sequencia": "geral", "dias": 7}, foto(sequences={"geral": {"atual": 1, "recorde": 4}}), (4, 7, "7 dias sem tropeçar")),
    ({"sequencia": "fe", "dias": 30}, foto(), (0, 30, "30 dias sem tropeçar na Fé")),
    ({"nivel_geral": 10}, foto(nivel_geral=6), (6, 10, "Nível geral 10")),
])
def test_evaluate(requisito, snap, esperado):
    assert requirements.evaluate(requisito, snap) == esperado


def test_um_registro_no_singular():
    assert requirements.evaluate({"registros": 1}, foto())[2] == "1 registro"


def test_todos_usa_o_menor_nivel():
    niveis = {a["id"]: {"nivel": 3} for a in rules.attributes()}
    niveis["foco"] = {"nivel": 1}
    assert requirements.evaluate({"todos": 3}, foto(levels=niveis)) == (1, 3, "Todos os atributos no nível 3")


def test_requisito_desconhecido_falha_alto():
    with pytest.raises(ValueError):
        requirements.evaluate({"inventado": 1}, foto())


def test_status_limita_o_progresso_a_meta_e_marca_liberado():
    assert requirements.status({"registros": 10}, foto(registros=25)) == {
        "requisito": "10 registros", "atual": 10, "meta": 10, "liberado": True}
    assert requirements.status({"registros": 10}, foto(registros=3))["liberado"] is False


def registrar(client, key, dia=None):
    return client.post("/api/registros", json={"action_key": key, "dia": dia})


def conquistas(client):
    return {c["id"]: c for c in client.get("/api/estado").get_json()["conquistas"]}


def test_ids_das_conquistas_sao_unicos_e_todas_avaliam(logado):
    ids = [c["id"] for c in rules.load()["conquistas"]]
    assert len(ids) == len(set(ids))
    assert set(conquistas(logado)) == set(ids)


def test_primeiro_registro_libera_a_primeira_conquista(logado):
    assert not conquistas(logado)["primeiro_passo"]["liberado"]
    registrar(logado, "forca_academia")
    assert conquistas(logado)["primeiro_passo"]["liberado"]


def test_sete_dias_diferentes_liberam_a_semana_de_jogo(logado):
    for dia in range(1, 8):
        registrar(logado, "forca_academia", f"2026-01-0{dia}")
    assert conquistas(logado)["semana_de_jogo"]["liberado"]
    assert not conquistas(logado)["mes_de_jogo"]["liberado"]


def test_mais_de_um_registro_no_mesmo_dia_conta_um_dia_de_jogo(logado):
    registrar(logado, "forca_academia", "2026-01-01")
    registrar(logado, "foco_sessao", "2026-01-01")
    assert conquistas(logado)["semana_de_jogo"]["atual"] == 1


def test_desfazer_registro_tira_a_conquista(logado):
    registro = registrar(logado, "forca_academia").get_json()
    id_registro = next(a["registro_id"] for a in registro["acoes"] if a["key"] == "forca_academia")
    logado.delete(f"/api/registros/{id_registro}")
    assert not conquistas(logado)["primeiro_passo"]["liberado"]
