import pytest


def criar(client, key="forca_academia", vezes=3):
    return client.post("/api/metas", json={"action_key": key, "vezes": vezes})


def registrar(client, key, dia):
    client.post("/api/registros", json={"action_key": key, "dia": dia})


def test_metas_exigem_login(client):
    assert client.get("/api/metas").status_code == 401
    assert client.post("/api/metas", json={}).status_code == 401


def test_criar_meta_comeca_com_zero_feitas(logado):
    resposta = criar(logado)
    assert resposta.status_code == 201
    meta = resposta.get_json()["metas"][0]
    assert (meta["key"], meta["nome"], meta["vezes"], meta["feitas"], meta["cumprida"]) == (
        "forca_academia", "Treino de academia", 3, 0, False)


def test_semana_vai_de_segunda_a_domingo(logado):
    dados = criar(logado).get_json()
    assert (dados["inicio"], dados["fim"]) == ("2026-01-05", "2026-01-11")


def test_so_conta_a_semana_atual(logado):
    criar(logado)
    for dia in ("2026-01-04", "2026-01-05", "2026-01-07"):  # o primeiro é domingo da semana passada
        registrar(logado, "forca_academia", dia)
    assert logado.get("/api/metas").get_json()["metas"][0]["feitas"] == 2


def test_meta_cumprida_aparece_no_estado_do_jogo(logado):
    criar(logado, vezes=2)
    registrar(logado, "forca_academia", "2026-01-05")
    assert logado.get("/api/estado").get_json()["metas"][0]["cumprida"] is False
    registrar(logado, "forca_academia", "2026-01-06")
    meta = logado.get("/api/estado").get_json()["metas"][0]
    assert meta["cumprida"] is True and meta["feitas"] == 2


def test_lista_de_acoes_so_tem_acoes_boas_com_atributo(logado):
    acoes = logado.get("/api/metas").get_json()["acoes"]
    academia = next(a for a in acoes if a["key"] == "forca_academia")
    assert academia["atributo"] == "Força"
    assert all(not a["key"].startswith("neg_") for a in acoes)


def test_acao_criada_pelo_jogador_pode_ter_meta(logado):
    logado.post("/api/acoes", json={"nome": "Inglês", "atributo": "intelecto", "intensidade": "media"})
    chave = next(a["key"] for a in logado.get("/api/metas").get_json()["acoes"] if a["nome"] == "Inglês")
    assert criar(logado, chave, 5).status_code == 201


@pytest.mark.parametrize("key, vezes", [
    ("neg_dieta", 3), ("nao_existe", 3), (None, 3),
    ("forca_academia", 0), ("forca_academia", 8), ("forca_academia", "3"), ("forca_academia", True),
])
def test_dados_invalidos_sao_recusados(logado, key, vezes):
    assert criar(logado, key, vezes).status_code == 400


def test_meta_repetida_para_a_mesma_acao_e_recusada(logado):
    criar(logado)
    assert criar(logado, vezes=5).status_code == 409


def test_limite_de_metas(logado):
    chaves = [a["key"] for a in logado.get("/api/metas").get_json()["acoes"]]
    for chave in chaves[:20]:
        assert criar(logado, chave).status_code == 201
    assert criar(logado, chaves[20]).status_code == 400


def test_excluir_meta(logado):
    meta_id = criar(logado).get_json()["metas"][0]["id"]
    assert logado.delete(f"/api/metas/{meta_id}").get_json()["metas"] == []
    assert logado.delete(f"/api/metas/{meta_id}").status_code == 404


def test_metas_sao_de_cada_usuario(app, logado):
    meta_id = criar(logado).get_json()["metas"][0]["id"]
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura", "aceito": "1"})
    assert outro.get("/api/metas").get_json()["metas"] == []
    assert outro.delete(f"/api/metas/{meta_id}").status_code == 404
