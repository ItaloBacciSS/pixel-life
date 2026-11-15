import pytest


def test_tela_do_jogo_referencia_seus_arquivos(logado):
    html = logado.get("/").get_data(as_text=True)
    assert "js/ui.js" in html and "css/scene.css" in html and "/cenario.svg" in html
    assert "/personagem.svg" in html and "/quarto.svg" in html and "/cenario.svg" in html
    assert 'id="estante"' in html and 'id="balao"' in html and 'id="metas"' in html


def test_telas_tem_o_menu_do_topo(logado):
    links = ('href="/"', 'href="/progresso"', 'href="/metas"', 'href="/riqueza"', 'href="/personagem"', 'href="/quarto"', 'href="/perfil"')
    for caminho in ("/", "/progresso", "/metas", "/riqueza", "/personagem", "/quarto", "/perfil"):
        html = logado.get(caminho).get_data(as_text=True)
        assert all(link in html for link in links), caminho


def test_tela_do_personagem_muda_no_primeiro_acesso(logado):
    assert "Crie seu personagem" in logado.get("/personagem?primeiro=1").get_data(as_text=True)
    assert "Seu personagem" in logado.get("/personagem").get_data(as_text=True)


def test_criacao_da_conta_mostra_so_o_personagem(logado):
    primeiro = logado.get("/personagem?primeiro=1").get_data(as_text=True)
    assert 'id="salvar"' in primeiro and 'id="corpos"' in primeiro and "Começar!" in primeiro
    assert 'id="itens"' not in primeiro and 'class="menu"' not in primeiro
    depois = logado.get("/personagem").get_data(as_text=True)
    assert 'id="itens"' in depois and 'class="menu"' in depois


def test_tela_de_perfil_mostra_o_usuario(logado):
    html = logado.get("/perfil").get_data(as_text=True)
    assert "gustavo" in html and "Trocar senha" in html and "Excluir perfil" in html


@pytest.mark.parametrize("caminho, texto", [
    ("/progresso", "Resumo da semana"), ("/metas", "Nova meta"), ("/riqueza", "Saldo atual"),
])
def test_paginas_novas_carregam(logado, caminho, texto):
    resposta = logado.get(caminho)
    assert resposta.status_code == 200 and texto in resposta.get_data(as_text=True)


@pytest.mark.parametrize("caminho", ["/progresso", "/metas", "/riqueza"])
def test_paginas_novas_exigem_login(client, caminho):
    assert client.get(caminho).status_code == 302


@pytest.mark.parametrize("caminho", [
    "js/ui.js", "js/api.js", "js/dom.js", "js/effects.js", "js/character.js", "js/profile.js",
    "js/format.js", "js/chart.js", "js/progress.js", "js/goals.js", "js/wealth.js", "js/home.js",
    "css/base.css", "css/auth.css", "css/game.css", "css/scene.css", "css/wardrobe.css", "css/profile.css",
    "css/chart.css", "css/progress.css", "css/goals.css", "css/wealth.css", "css/home.css",
    "img/cenario.svg", "fonts/press-start-2p.woff2",
])
def test_arquivos_estaticos_sao_servidos(client, caminho):
    assert client.get(f"/static/{caminho}").status_code == 200


def test_regras_incluem_a_cor_de_cada_atributo(logado):
    atributos = logado.get("/api/estado").get_json()["atributos"]
    assert all(a["cor"].startswith("#") for a in atributos)
