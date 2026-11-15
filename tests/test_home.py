import pytest

from app.services import room, rules

ESCOLHA = {"tema": "noite", "especie": "cachorro", "pelagem": "marrom"}


def salvar(client, **mudancas):
    return client.put("/api/quarto", json={**ESCOLHA, **mudancas})


def test_api_do_quarto_exige_login(client):
    assert client.get("/api/quarto").status_code == 401
    assert client.put("/api/quarto", json=ESCOLHA).status_code == 401


def test_pagina_do_quarto_carrega(logado):
    resposta = logado.get("/quarto")
    assert resposta.status_code == 200 and "Quarto e mascote" in resposta.get_data(as_text=True)


def test_comeca_com_o_visual_padrao_e_lista_as_opcoes(logado):
    dados = logado.get("/api/quarto").get_json()
    assert dados["atual"] == room.load()["padrao"]
    opcoes = dados["opcoes"]
    assert [t["id"] for t in opcoes["temas"]][0] == "classico" and len(opcoes["temas"]) == 6
    assert [e["id"] for e in opcoes["especies"]] == ["gato", "cachorro"]
    assert all(len(e["pelagens"]) == 5 and all(p["cor"].startswith("#") for p in e["pelagens"]) for e in opcoes["especies"])


def test_salvar_e_ler_de_volta(logado):
    assert salvar(logado).get_json()["atual"] == ESCOLHA
    assert logado.get("/api/quarto").get_json()["atual"] == ESCOLHA


def test_salvar_de_novo_troca_a_escolha(logado):
    salvar(logado)
    assert salvar(logado, especie="gato", pelagem="cinza", tema="rosa").get_json()["atual"] == {
        "tema": "rosa", "especie": "gato", "pelagem": "cinza"}


@pytest.mark.parametrize("mudanca", [
    {"tema": "inexistente"}, {"tema": None}, {"especie": "dragao"}, {"pelagem": "azul"},
    {"especie": "gato", "pelagem": "caramelo"},  # caramelo só existe para cachorro
    {"especie": "cachorro", "pelagem": "laranja"},
])
def test_escolha_invalida_e_recusada(logado, mudanca):
    assert salvar(logado, **mudanca).status_code == 400
    assert logado.get("/api/quarto").get_json()["atual"] == room.load()["padrao"]


def test_corpo_vazio_e_recusado(logado):
    assert logado.put("/api/quarto", json={}).status_code == 400
    assert logado.put("/api/quarto", data="x").status_code == 400


def test_cenario_e_mascote_seguem_a_escolha_salva(logado):
    salvar(logado)
    assert logado.get("/cenario.svg").get_data(as_text=True) == room.background("noite")
    esperado = room.render({a["id"]: {"nivel": 0} for a in rules.attributes()}, "normal", ESCOLHA)
    assert logado.get("/quarto.svg").get_data(as_text=True) == esperado


def test_parametros_na_url_so_pre_visualizam(logado):
    previa = logado.get("/cenario.svg?tema=verde").get_data(as_text=True)
    assert previa == room.background("verde")
    assert logado.get("/api/quarto").get_json()["atual"]["tema"] == "classico"
    cachorro = logado.get("/quarto.svg?especie=cachorro&pelagem=preto").get_data(as_text=True)
    assert cachorro != logado.get("/quarto.svg").get_data(as_text=True)


def test_previa_invalida_e_recusada(logado):
    assert logado.get("/cenario.svg?tema=nada").status_code == 400
    assert logado.get("/quarto.svg?especie=gato&pelagem=caramelo").status_code == 400


def test_previa_do_humor(logado):
    assert 'class="pet triste"' in logado.get("/quarto.svg?humor=triste").get_data(as_text=True)
    assert 'class="pet normal"' in logado.get("/quarto.svg?humor=qualquer").get_data(as_text=True)  # inválido: usa o real


def test_cada_pessoa_tem_o_seu_quarto(app, logado):
    salvar(logado)
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura"})
    assert outro.get("/api/quarto").get_json()["atual"] == room.load()["padrao"]


def test_telas_do_jogo_usam_o_cenario_do_tema(logado):
    for caminho in ("/", "/personagem"):
        assert "/cenario.svg" in logado.get(caminho).get_data(as_text=True)
