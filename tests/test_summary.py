def registrar(client, key, dia):
    client.post("/api/registros", json={"action_key": key, "dia": dia})


def resumo(client):
    return client.get("/api/progresso").get_json()


def test_progresso_exige_login(client):
    assert client.get("/api/progresso").status_code == 401


def test_sem_registros_tudo_zerado(logado):
    dados = resumo(logado)
    semana = dados["semana"]
    assert (semana["acoes"], semana["tropecos"], semana["xp"], semana["melhor_dia"], semana["subiu"]) == (0, 0, [], None, [])
    assert (semana["inicio"], semana["fim"]) == ("2026-01-05", "2026-01-11")
    evolucao = dados["evolucao"]
    assert evolucao["datas"] == ["2026-01-10"]
    assert [r["id"] for r in evolucao["rotulos"]] == list(evolucao["series"])
    assert "geral" in evolucao["series"] and all(valores == [0] for valores in evolucao["series"].values())


def test_resumo_da_semana_conta_acoes_tropecos_e_xp(logado):
    for dia in ("2026-01-05", "2026-01-06", "2026-01-07"):
        registrar(logado, "forca_academia", dia)
    registrar(logado, "neg_dieta", "2026-01-07")
    semana = resumo(logado)["semana"]
    assert (semana["acoes"], semana["tropecos"]) == (3, 1)
    assert [(a["id"], a["xp"]) for a in semana["xp"]] == [("forca", 25), ("vitalidade", -3)]
    assert semana["melhor_dia"] == {"dia": "2026-01-05", "acoes": 1}  # empate: o dia mais antigo


def test_melhor_dia_e_o_de_mais_acoes(logado):
    registrar(logado, "forca_academia", "2026-01-05")
    registrar(logado, "forca_alongamento", "2026-01-06")
    registrar(logado, "foco_sessao", "2026-01-06")
    assert resumo(logado)["semana"]["melhor_dia"] == {"dia": "2026-01-06", "acoes": 2}


def test_semana_passada_nao_entra_mas_vira_comparacao(logado):
    registrar(logado, "forca_academia", "2026-01-02")
    registrar(logado, "foco_sessao", "2025-12-30")
    registrar(logado, "foco_sessao", "2025-12-20")  # duas semanas atrás: fora
    semana = resumo(logado)["semana"]
    assert (semana["acoes"], semana["acoes_anterior"]) == (0, 2)


def test_atributo_que_subiu_de_nivel_na_semana(logado):
    for dia in range(25, 32):
        registrar(logado, "forca_academia", f"2025-12-{dia}")
    for dia in ("2026-01-01", "2026-01-02"):
        registrar(logado, "forca_academia", dia)  # 90 XP: ainda no nível 0
    assert resumo(logado)["semana"]["subiu"] == []
    registrar(logado, "forca_academia", "2026-01-05")
    assert resumo(logado)["semana"]["subiu"] == [{"id": "forca", "nome": "Força", "de": 0, "para": 1}]


def test_metas_cumpridas_na_semana(logado):
    logado.post("/api/metas", json={"action_key": "forca_academia", "vezes": 1})
    logado.post("/api/metas", json={"action_key": "foco_sessao", "vezes": 2})
    registrar(logado, "forca_academia", "2026-01-06")
    assert resumo(logado)["semana"]["metas"] == {"cumpridas": 1, "total": 2}


def test_evolucao_tem_um_ponto_por_semana_e_termina_hoje(logado):
    registrar(logado, "forca_academia", "2025-12-01")  # 41 dias até hoje
    evolucao = resumo(logado)["evolucao"]
    assert evolucao["datas"][0] == "2025-12-01" and evolucao["datas"][-1] == "2026-01-10"
    assert len(evolucao["datas"]) == 7  # dias 0, 7, 14, 21, 28, 35 e o último (40)
    assert all(len(valores) == 7 for valores in evolucao["series"].values())


def test_nivel_geral_e_a_soma_dos_atributos_e_bate_com_o_jogo(logado):
    for dia in range(1, 11):
        registrar(logado, "forca_treino_pesado", f"2026-01-{dia:02d}")
        registrar(logado, "foco_sessao", f"2026-01-{dia:02d}")
    series = resumo(logado)["evolucao"]["series"]
    assert series["geral"] == [sum(s[i] for k, s in series.items() if k != "geral") for i in range(len(series["geral"]))]
    assert series["geral"][-1] == logado.get("/api/estado").get_json()["nivel_geral"] > 0


def test_resposta_inclui_as_conquistas(logado):
    assert len(resumo(logado)["conquistas"]) == len(logado.get("/api/estado").get_json()["conquistas"])
