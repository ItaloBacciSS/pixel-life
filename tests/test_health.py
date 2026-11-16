def test_saude_nao_exige_login_e_mostra_os_tempos(client):
    resposta = client.get("/saude")
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert {"instancia_ligada_ha_s", "requisicoes_nesta_instancia", "primeira_consulta_ms",
            "segunda_consulta_ms", "regiao"} <= set(dados)


def test_toda_resposta_traz_o_tempo_do_servidor(logado):
    for caminho in ("/", "/api/estado", "/login"):
        assert "app;dur=" in logado.get(caminho).headers["Server-Timing"]
