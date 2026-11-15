from app.extensions import db
from app.models import Character, CustomAction, Entry, Goal, Home, MoneyMove, User

SENHA = "senha-segura"


def entrar(app, username, senha=SENHA):
    cliente = app.test_client()
    cliente.post("/login", data={"username": username, "password": senha})
    return cliente


def test_trocar_senha(app, logado):
    resposta = logado.post("/api/senha", json={"atual": SENHA, "nova": "outra-senha-boa"})
    assert resposta.status_code == 200
    assert entrar(app, "gustavo", SENHA).get("/api/estado").status_code == 401
    assert entrar(app, "gustavo", "outra-senha-boa").get("/api/estado").status_code == 200


def test_trocar_senha_exige_a_senha_atual(logado):
    assert logado.post("/api/senha", json={"atual": "errada-errada", "nova": "outra-senha-boa"}).status_code == 403


def test_nova_senha_curta_e_recusada(logado):
    assert logado.post("/api/senha", json={"atual": SENHA, "nova": "curta"}).status_code == 400


def test_excluir_conta_apaga_tudo_do_usuario(app, logado):
    logado.post("/api/registros", json={"action_key": "forca_academia"})
    logado.post("/api/acoes", json={"nome": "X", "atributo": "foco", "intensidade": "leve"})
    logado.put("/api/personagem", json={"corpo": "feminino", "pele": "#f4c7a1", "cabelo": "#5a3825",
                                        "roupa": "#ff7a59", "itens": []})
    logado.post("/api/metas", json={"action_key": "forca_academia", "vezes": 3})
    logado.post("/api/riqueza", json={"centavos": 5000})
    logado.put("/api/quarto", json={"tema": "noite", "especie": "cachorro", "pelagem": "marrom"})
    assert logado.delete("/api/conta", json={"senha": SENHA}).status_code == 200
    with app.app_context():
        tabelas = (User, Entry, CustomAction, Character, Goal, Home, MoneyMove)
        assert [modelo.query.count() for modelo in tabelas] == [0] * len(tabelas)
    assert logado.get("/api/estado").status_code == 401
    assert entrar(app, "gustavo").get("/api/estado").status_code == 401


def test_excluir_conta_exige_a_senha(app, logado):
    assert logado.delete("/api/conta", json={"senha": "errada-errada"}).status_code == 403
    with app.app_context():
        assert User.query.count() == 1


def test_excluir_conta_nao_mexe_nos_dados_dos_outros(app, logado):
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": SENHA})
    outro.post("/api/registros", json={"action_key": "forca_academia"})
    logado.delete("/api/conta", json={"senha": SENHA})
    with app.app_context():
        assert User.query.count() == 1 and Entry.query.count() == 1


def test_perfil_exige_login(client):
    assert client.get("/perfil").status_code == 302
