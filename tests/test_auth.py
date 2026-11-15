from app.extensions import db
from app.models import User

SENHA = "senha-segura"


def registrar(client, username="gustavo", password=SENHA):
    return client.post("/registro", data={"username": username, "password": password})


def test_home_exige_login(client):
    resposta = client.get("/")
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/login")


def test_registro_cria_usuario_entra_e_vai_criar_o_personagem(client):
    resposta = registrar(client)
    assert resposta.headers["Location"] == "/personagem?primeiro=1"
    assert client.get("/").status_code == 200


def test_senha_e_guardada_com_hash(client, app):
    registrar(client)
    with app.app_context():
        user = db.session.execute(db.select(User)).scalar_one()
        assert user.password_hash != SENHA
        assert user.check_password(SENHA)


def test_registro_rejeita_usuario_repetido(client):
    registrar(client)
    resposta = registrar(client, username="GUSTAVO")
    assert "já existe" in resposta.get_data(as_text=True)


def test_registro_rejeita_senha_curta(client):
    resposta = registrar(client, password="curta")
    assert "pelo menos 8" in resposta.get_data(as_text=True)


def test_registro_fechado_retorna_404(client, app):
    app.config["REGISTRATION_OPEN"] = False
    assert client.get("/registro").status_code == 404


def test_login_com_senha_errada_falha(client):
    registrar(client)
    client.post("/sair")
    resposta = client.post("/login", data={"username": "gustavo", "password": "errada-errada"})
    assert "incorretos" in resposta.get_data(as_text=True)
    assert client.get("/").status_code == 302


def test_login_correto_entra(client):
    registrar(client)
    client.post("/sair")
    resposta = client.post("/login", data={"username": "gustavo", "password": SENHA})
    assert resposta.headers["Location"] == "/"
    assert client.get("/").status_code == 200


def test_sair_encerra_a_sessao(client):
    registrar(client)
    client.post("/sair")
    assert client.get("/").status_code == 302
