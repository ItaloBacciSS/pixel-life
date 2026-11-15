import pytest


def registrar(client, key, **extra):
    return client.post("/api/registros", json={"action_key": key, **extra})


def atributo(resposta, attr_id):
    return next(a for a in resposta.get_json()["atributos"] if a["id"] == attr_id)


def test_api_exige_login(client):
    resposta = client.get("/api/estado")
    assert resposta.status_code == 401
    assert "erro" in resposta.get_json()


def test_estado_inicial_tem_nove_atributos_zerados(logado):
    dados = logado.get("/api/estado").get_json()
    assert len(dados["atributos"]) == 9
    assert dados["nivel_geral"] == 0
    assert any(a["key"] == "forca_academia" for a in dados["acoes"])


def test_registrar_acao_soma_xp_e_marca_como_feita(logado):
    resposta = registrar(logado, "forca_academia")
    assert resposta.status_code == 201
    assert atributo(resposta, "forca")["xp"] == 10
    acao = next(a for a in resposta.get_json()["acoes"] if a["key"] == "forca_academia")
    assert acao["registro_id"] is not None


def test_mesma_acao_no_mesmo_dia_e_recusada(logado):
    registrar(logado, "forca_academia")
    assert registrar(logado, "forca_academia").status_code == 409


def test_registrar_dia_passado_funciona(logado):
    resposta = registrar(logado, "forca_academia", dia="2026-01-08")
    assert resposta.status_code == 201
    assert resposta.get_json()["dia"] == "2026-01-08"


def test_dia_futuro_e_data_invalida_sao_recusados(logado):
    assert registrar(logado, "forca_academia", dia="2026-01-11").status_code == 400
    assert registrar(logado, "forca_academia", dia="ontem").status_code == 400


def test_acao_desconhecida_retorna_404(logado):
    assert registrar(logado, "nao_existe").status_code == 404


def test_desfazer_registro_devolve_o_xp(logado):
    resposta = registrar(logado, "forca_academia")
    registro_id = next(a["registro_id"] for a in resposta.get_json()["acoes"] if a["registro_id"])
    desfeito = logado.delete(f"/api/registros/{registro_id}")
    assert atributo(desfeito, "forca")["xp"] == 0


def test_nao_desfaz_registro_de_outro_usuario(app, logado):
    resposta = registrar(logado, "forca_academia")
    registro_id = next(a["registro_id"] for a in resposta.get_json()["acoes"] if a["registro_id"])
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura"})
    assert outro.delete(f"/api/registros/{registro_id}").status_code == 404


def test_criar_acao_personalizada_e_usar(logado):
    dados = {"nome": "Aula de inglês", "atributo": "intelecto", "intensidade": "media", "tropeco": False}
    criada = logado.post("/api/acoes", json=dados)
    assert criada.status_code == 201
    nova = next(a for a in criada.get_json()["acoes"] if a["nome"] == "Aula de inglês")
    assert nova["efeitos"] == {"intelecto": 10}
    assert atributo(registrar(logado, nova["key"]), "intelecto")["xp"] == 10


def test_acao_personalizada_e_so_de_quem_criou(app, logado):
    logado.post("/api/acoes", json={"nome": "Só minha", "atributo": "foco", "intensidade": "leve"})
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura"})
    assert all(a["nome"] != "Só minha" for a in outro.get("/api/estado").get_json()["acoes"])


@pytest.mark.parametrize("dados", [
    {"nome": "", "atributo": "foco", "intensidade": "leve"},
    {"nome": "X", "atributo": "inexistente", "intensidade": "leve"},
    {"nome": "X", "atributo": "foco", "intensidade": "gigante"},
])
def test_acao_personalizada_invalida_e_recusada(logado, dados):
    assert logado.post("/api/acoes", json=dados).status_code == 400


def test_tropeco_na_fe_zera_a_sequencia_da_fe_e_a_geral(logado):
    registrar(logado, "fe_oracao", dia="2026-01-01")
    sequencias = registrar(logado, "neg_fe").get_json()["sequencias"]
    assert sequencias["fe"]["atual"] == sequencias["geral"]["atual"] == 0


def test_outro_tropeco_zera_so_a_sequencia_geral(logado):
    registrar(logado, "fe_oracao", dia="2026-01-01")
    sequencias = registrar(logado, "neg_dieta").get_json()["sequencias"]
    assert sequencias["geral"]["atual"] == 0
    assert sequencias["fe"]["atual"] == 9


def test_sequencia_geral_vem_antes_da_sequencia_da_fe(logado):
    assert list(logado.get("/api/estado").get_json()["sequencias"]) == ["geral", "fe"]
