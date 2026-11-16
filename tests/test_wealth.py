import pytest


def mover(client, centavos, **extra):
    return client.post("/api/riqueza", json={"centavos": centavos, **extra})


def test_riqueza_exige_login(client):
    assert client.get("/api/riqueza").status_code == 401


def test_comeca_zerado(logado):
    assert logado.get("/api/riqueza").get_json() == {"hoje": "2026-01-10", "saldo": 0, "movimentos": [], "serie": []}


def test_entradas_e_saidas_somam_no_saldo(logado):
    assert mover(logado, 10000).status_code == 201
    dados = mover(logado, -2550, nota="Mercado").get_json()
    assert dados["saldo"] == 7450
    assert dados["movimentos"][0]["nota"] == "Mercado"  # o mais recente primeiro
    assert dados["movimentos"][0]["centavos"] == -2550


def test_definir_saldo_registra_a_diferenca(logado):
    mover(logado, 7450)
    dados = logado.post("/api/riqueza/saldo", json={"saldo": 20000}).get_json()
    assert dados["saldo"] == 20000
    assert (dados["movimentos"][0]["centavos"], dados["movimentos"][0]["nota"]) == (12550, "Ajuste de saldo")


def test_definir_saldo_para_zero_ou_negativo_funciona(logado):
    mover(logado, 5000)
    assert logado.post("/api/riqueza/saldo", json={"saldo": 0}).get_json()["saldo"] == 0
    assert logado.post("/api/riqueza/saldo", json={"saldo": -1500}).get_json()["saldo"] == -1500


def test_definir_o_mesmo_saldo_e_recusado(logado):
    mover(logado, 5000)
    assert logado.post("/api/riqueza/saldo", json={"saldo": 5000}).status_code == 400


@pytest.mark.parametrize("valor", [0, "10", 1.5, True, None, 10**12 + 1, -(10**12) - 1])
def test_valores_invalidos_sao_recusados(logado, valor):
    assert mover(logado, valor).status_code == 400


def test_saldo_invalido_e_recusado(logado):
    assert logado.post("/api/riqueza/saldo", json={"saldo": "10"}).status_code == 400
    assert logado.post("/api/riqueza/saldo", json={}).status_code == 400


def test_dia_futuro_e_recusado_e_passado_funciona(logado):
    assert mover(logado, 100, dia="2026-01-11").status_code == 400
    assert mover(logado, 100, dia="2026-01-01").status_code == 201


def test_serie_tem_um_ponto_por_dia_e_termina_hoje(logado):
    mover(logado, 10000, dia="2026-01-01")
    mover(logado, -3000, dia="2026-01-01")
    mover(logado, 500, dia="2026-01-05")
    assert logado.get("/api/riqueza").get_json()["serie"] == [
        {"dia": "2026-01-01", "saldo": 7000}, {"dia": "2026-01-05", "saldo": 7500}, {"dia": "2026-01-10", "saldo": 7500}]


def test_nota_longa_e_cortada(logado):
    assert mover(logado, 100, nota="x" * 300).get_json()["movimentos"][0]["nota"] == "x" * 100


def test_lista_mostra_so_os_ultimos_50(logado):
    for _ in range(55):
        mover(logado, 1)
    dados = logado.get("/api/riqueza").get_json()
    assert len(dados["movimentos"]) == 50 and dados["saldo"] == 55


def test_excluir_movimento_desfaz_o_saldo(logado):
    movimento = mover(logado, 4000).get_json()["movimentos"][0]
    assert logado.delete(f"/api/riqueza/{movimento['id']}").get_json()["saldo"] == 0
    assert logado.delete(f"/api/riqueza/{movimento['id']}").status_code == 404


def test_saldo_aparece_no_estado_do_jogo(logado):
    mover(logado, 1234)
    assert logado.get("/api/estado").get_json()["saldo"] == 1234


def test_dinheiro_e_de_cada_usuario(app, logado):
    movimento = mover(logado, 9900).get_json()["movimentos"][0]
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura", "aceito": "1"})
    assert outro.get("/api/riqueza").get_json()["saldo"] == 0
    assert outro.delete(f"/api/riqueza/{movimento['id']}").status_code == 404
