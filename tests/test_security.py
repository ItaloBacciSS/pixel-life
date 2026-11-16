import re
import sqlite3

import pytest

from app import create_app
from app.config import TestConfig
from app.routes import auth
from app.services import throttle

SENHA = "senha-segura"
CODIGO = re.compile(r"[A-Z2-9]{4}(?:-[A-Z2-9]{4}){3}")


def cadastrar(client, username="gustavo", password=SENHA, **extra):
    dados = {"username": username, "password": password, "aceito": "1", **extra}
    return client.post("/registro", data=dados)


def cadastrar_e_pegar_codigo(client, username="gustavo"):
    cadastrar(client, username)
    pagina = client.get("/codigo?primeiro=1").get_data(as_text=True)
    return CODIGO.search(pagina).group()


def recuperar(client, codigo, nova="outra-senha-forte", username="gustavo"):
    return client.post("/recuperar", data={"username": username, "code": codigo, "password": nova})


# --- cadastro ---------------------------------------------------------------

@pytest.mark.parametrize("nome", ["ab", "com espaço", "gustаvo", "emoji😀", "a" * 41, "user@mail", "nome/barra"])
def test_usuario_com_caracteres_fora_do_padrao_e_recusado(client, nome):
    resposta = cadastrar(client, username=nome)
    assert resposta.status_code == 200
    assert "letras, números" in resposta.get_data(as_text=True)


def test_usuario_com_maiuscula_vira_minuscula(client, app):
    assert cadastrar(client, username="Gustavo").status_code == 302
    assert cadastrar(client, username="GUSTAVO").status_code == 200


def test_cadastro_exige_aceitar_a_privacidade(client):
    resposta = client.post("/registro", data={"username": "gustavo", "password": SENHA})
    assert "política de privacidade" in resposta.get_data(as_text=True)


@pytest.mark.parametrize("senha", ["12345678", "PASSWORD", "senha123", "x" * 129])
def test_senhas_comuns_ou_gigantes_sao_recusadas(client, senha):
    assert cadastrar(client, password=senha).status_code == 200


def test_senha_igual_ao_usuario_e_recusada(client):
    resposta = cadastrar(client, username="usuario-longo", password="usuario-longo")
    assert resposta.status_code == 200
    assert "fácil de adivinhar" in resposta.get_data(as_text=True)


def test_cadastro_simultaneo_do_mesmo_nome_nao_vira_erro_500(client, monkeypatch):
    cadastrar(client)
    client.post("/sair")
    monkeypatch.setattr(auth, "_validate", lambda *args: None)  # a checagem passou, o banco barra
    resposta = cadastrar(client)
    assert resposta.status_code == 200
    assert "já existe" in resposta.get_data(as_text=True)


def test_limite_de_contas_novas_por_origem(client):
    for i in range(throttle.MAX_SIGNUPS):
        assert cadastrar(client, username=f"jogador{i}").status_code == 302
        client.post("/sair")
    resposta = cadastrar(client, username="jogador-extra")
    assert resposta.status_code == 429


# --- login por origem -------------------------------------------------------

def test_varios_usuarios_errados_da_mesma_origem_bloqueiam_o_login(client):
    cadastrar(client)
    client.post("/sair")
    for i in range(throttle.MAX_FAILURES_IP):
        client.post("/login", data={"username": f"fantasma{i}", "password": "x"})
    resposta = client.post("/login", data={"username": "gustavo", "password": SENHA})
    assert resposta.status_code == 429


def test_nome_fora_do_padrao_nao_cria_chave_de_bloqueio(client, app):
    client.post("/login", data={"username": "ip:abc", "password": "x"})
    with app.app_context():
        from app.models import LoginFailure
        assert "ip:abc" not in {f.username for f in LoginFailure.query}


# --- recuperação de senha ---------------------------------------------------

def test_codigo_aparece_so_uma_vez(client):
    cadastrar(client)
    primeira = client.get("/codigo?primeiro=1")
    assert CODIGO.search(primeira.get_data(as_text=True))
    assert primeira.headers["Cache-Control"] == "no-store"
    assert 'href="/personagem?primeiro=1"' in primeira.get_data(as_text=True)
    assert client.get("/codigo?primeiro=1").status_code == 302


def test_codigo_nao_fica_guardado_em_texto(client, app):
    codigo = cadastrar_e_pegar_codigo(client)
    from app.models import User
    with app.app_context():
        assert codigo.replace("-", "") not in User.query.one().recovery_hash


def test_recuperar_com_o_codigo_troca_a_senha_e_gasta_o_codigo(client):
    codigo = cadastrar_e_pegar_codigo(client)
    client.post("/sair")
    resposta = recuperar(client, codigo.lower().replace("-", " "))
    assert resposta.status_code == 302 and resposta.headers["Location"] == "/codigo"
    novo = CODIGO.search(client.get("/codigo").get_data(as_text=True)).group()
    assert novo != codigo
    client.post("/sair")
    assert client.post("/login", data={"username": "gustavo", "password": "outra-senha-forte"}).status_code == 302
    client.post("/sair")
    assert recuperar(client, codigo).status_code == 200  # o código antigo não vale mais


def test_codigo_errado_nao_troca_a_senha(client):
    cadastrar_e_pegar_codigo(client)
    client.post("/sair")
    resposta = recuperar(client, "AAAA-AAAA-AAAA-AAAA")
    assert "incorretos" in resposta.get_data(as_text=True)
    client.post("/sair")
    assert client.post("/login", data={"username": "gustavo", "password": SENHA}).status_code == 302


def test_chutar_codigos_e_bloqueado(client):
    codigo = cadastrar_e_pegar_codigo(client)
    client.post("/sair")
    for _ in range(throttle.MAX_FAILURES):
        recuperar(client, "AAAA-AAAA-AAAA-AAAA")
    assert recuperar(client, codigo).status_code == 429


def test_nova_senha_na_recuperacao_segue_as_regras(client):
    codigo = cadastrar_e_pegar_codigo(client)
    client.post("/sair")
    assert recuperar(client, codigo, nova="12345678").status_code == 200
    assert recuperar(client, codigo).status_code == 302  # o código não foi gasto pela senha recusada


def test_usuario_inexistente_na_recuperacao_da_a_mesma_resposta(client):
    resposta = recuperar(client, "AAAA-AAAA-AAAA-AAAA", username="ninguem")
    assert "incorretos" in resposta.get_data(as_text=True)


def test_perfil_gera_novo_codigo_e_invalida_o_anterior(client):
    antigo = cadastrar_e_pegar_codigo(client)
    assert client.post("/api/recuperacao", json={"senha": "errada"}).status_code == 403
    novo = client.post("/api/recuperacao", json={"senha": SENHA}).get_json()["codigo"]
    assert CODIGO.fullmatch(novo) and novo != antigo
    client.post("/sair")
    assert recuperar(client, antigo).status_code == 200
    assert recuperar(client, novo).status_code == 302


def test_conta_antiga_sem_codigo_nao_consegue_recuperar(client, app):
    cadastrar_e_pegar_codigo(client)
    from app.extensions import db
    from app.models import User
    with app.app_context():
        User.query.one().recovery_hash = None
        db.session.commit()
    client.post("/sair")
    assert recuperar(client, "AAAA-AAAA-AAAA-AAAA").status_code == 200


# --- cabeçalhos e pedidos de outros sites -----------------------------------

def test_respostas_trazem_cabecalhos_de_seguranca(client):
    cabecalhos = client.get("/login").headers
    assert "default-src 'self'" in cabecalhos["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in cabecalhos["Content-Security-Policy"]
    assert cabecalhos["X-Frame-Options"] == "DENY"
    assert cabecalhos["X-Content-Type-Options"] == "nosniff"
    assert "Strict-Transport-Security" not in cabecalhos


def test_hsts_so_na_vercel(client, monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    assert "max-age" in client.get("/login").headers["Strict-Transport-Security"]


@pytest.mark.parametrize("cabecalho", [{"Origin": "https://site-malicioso.example"}, {"Sec-Fetch-Site": "cross-site"}])
def test_pedido_que_altera_dados_vindo_de_outro_site_e_recusado(client, cabecalho):
    resposta = client.post("/login", data={"username": "a", "password": "b"}, headers=cabecalho)
    assert resposta.status_code == 403


def test_pedido_do_proprio_site_passa(client):
    resposta = client.post("/login", data={"username": "a", "password": "b"},
                           headers={"Origin": "http://localhost", "Sec-Fetch-Site": "same-origin"})
    assert resposta.status_code == 200


def test_pedido_gigante_e_recusado(client):
    assert client.post("/login", data={"username": "a" * 70000, "password": "b"}).status_code == 413


def test_pagina_de_privacidade_e_publica(client):
    resposta = client.get("/privacidade")
    assert resposta.status_code == 200 and "Excluir meu perfil" in resposta.get_data(as_text=True)


# --- banco existente --------------------------------------------------------

def test_coluna_nova_entra_em_banco_que_ja_existia(tmp_path):
    arquivo = tmp_path / "antigo.db"
    with sqlite3.connect(arquivo) as conexao:
        conexao.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, username VARCHAR(40) NOT NULL UNIQUE, "
                        "password_hash VARCHAR(255) NOT NULL, created_at DATETIME)")
        conexao.execute("INSERT INTO user (username, password_hash) VALUES ('velho', 'x')")

    class Antigo(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{arquivo}"

    create_app(Antigo)
    with sqlite3.connect(arquivo) as conexao:
        colunas = {linha[1] for linha in conexao.execute("PRAGMA table_info(user)")}
        assert "recovery_hash" in colunas
        assert conexao.execute("SELECT username FROM user").fetchone() == ("velho",)
