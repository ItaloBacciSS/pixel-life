from datetime import timedelta

from app.services import throttle


def _login(client, senha):
    return client.post("/login", data={"username": "gustavo", "password": senha})


def _criar(client):
    client.post("/registro", data={"username": "gustavo", "password": "senha-segura", "aceito": "1"})
    client.post("/sair")


def test_bloqueia_apos_cinco_erros_mesmo_com_senha_certa(client):
    _criar(client)
    for _ in range(throttle.MAX_FAILURES):
        assert _login(client, "errada").status_code == 200
    resposta = _login(client, "senha-segura")
    assert resposta.status_code == 429
    assert "Muitas tentativas" in resposta.get_data(as_text=True)


def test_acerto_zera_o_contador(client):
    _criar(client)
    for _ in range(throttle.MAX_FAILURES - 1):
        _login(client, "errada")
    assert _login(client, "senha-segura").status_code == 302
    client.post("/sair")
    for _ in range(throttle.MAX_FAILURES - 1):
        assert _login(client, "errada").status_code == 200


def test_bloqueio_expira_apos_a_janela(client, monkeypatch):
    _criar(client)
    for _ in range(throttle.MAX_FAILURES):
        _login(client, "errada")
    agora = throttle.now()
    monkeypatch.setattr(throttle, "now", lambda: agora + throttle.WINDOW + timedelta(seconds=1))
    assert _login(client, "senha-segura").status_code == 302


def test_usuario_inexistente_tambem_e_limitado(client):
    for _ in range(throttle.MAX_FAILURES):
        client.post("/login", data={"username": "fantasma", "password": "x"})
    resposta = client.post("/login", data={"username": "fantasma", "password": "x"})
    assert resposta.status_code == 429


def test_bloqueio_de_um_usuario_nao_afeta_outro(client):
    _criar(client)
    for _ in range(throttle.MAX_FAILURES):
        _login(client, "errada")
    resposta = client.post("/login", data={"username": "outro", "password": "x"})
    assert resposta.status_code == 200
