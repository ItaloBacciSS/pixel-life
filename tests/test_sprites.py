from app.services import rules, sprites

LOOK = {"corpo": "masculino", "pele": "#f4c7a1", "cabelo": "#5a3825", "roupa": "#ff7a59", "itens": []}


def test_todo_desenho_tem_14_colunas_e_cabe_em_20_linhas():
    dados = sprites.load()
    for corpo in dados["corpos"].values():
        mapas = [corpo["base"], *corpo["roupas"].values(), *corpo["penteados"].values()]
        assert all(len(mapa) == 20 and all(len(l) == 14 for l in mapa) for mapa in mapas)
    for item in dados["itens"].values():
        assert all(len(l) == 14 for l in item["mapa"])
        assert item["y"] + len(item["mapa"]) <= 20


def test_cada_item_das_regras_tem_desenho_e_vice_versa():
    assert set(rules.items()) == set(sprites.load()["itens"])


def test_todo_caractere_usado_tem_cor():
    dados = sprites.load()
    globais = set(dados["paleta"]) | set("shtT")
    for corpo in dados["corpos"].values():
        mapas = [corpo["base"], *corpo["roupas"].values(), *corpo["penteados"].values()]
        usados = {c for mapa in mapas for l in mapa for c in l} - {"."}
        assert usados <= globais
    for item in dados["itens"].values():
        usados = {c for l in item["mapa"] for c in l} - {"."}
        assert usados <= globais | set(item["cores"])


def test_slots_dos_itens_existem_na_ordem_de_desenho():
    ordem = set(sprites.load()["ordem"])
    assert {item["slot"] for item in rules.items().values()} <= ordem
    assert set(rules.load()["personagem"]["slots"]) == {item["slot"] for item in rules.items().values()}


def test_render_usa_as_cores_escolhidas():
    svg = sprites.render({**LOOK, "pele": "#8d5524", "cabelo": "#3a86ff", "roupa": "#5fb85f"})
    assert "#8d5524" in svg and "#3a86ff" in svg and "#5fb85f" in svg


def test_corpos_diferentes_geram_desenhos_diferentes():
    assert sprites.render(LOOK) != sprites.render({**LOOK, "corpo": "feminino"})


def test_item_aparece_no_desenho():
    assert sprites.render({**LOOK, "itens": ["tenis"]}) != sprites.render(LOOK)
    assert "#ff4d6d" in sprites.render({**LOOK, "itens": ["tenis"]})


def test_todos_os_itens_renderizam_nos_dois_corpos():
    for corpo in ("masculino", "feminino"):
        for item_id in rules.items():
            assert sprites.render({**LOOK, "corpo": corpo, "itens": [item_id]}).startswith("<svg")


def test_olhos_ficam_num_grupo_proprio_para_piscar():
    svg = sprites.render(LOOK)
    grupo = svg.split('<g class="olhos">')[1].split("</g>")[0]
    assert grupo.count("<rect") == 2
    assert "piscar" in svg and "prefers-reduced-motion" in svg


def test_sem_os_olhos_o_rosto_continua_inteiro():
    antes = sprites.render(LOOK).split('<g class="olhos">')[0]
    linha_dos_olhos = [r for r in antes.split("<rect")[1:] if 'y="3"' in r]
    assert linha_dos_olhos and all('fill="#f4c7a1"' in r or 'fill="#5a3825"' in r for r in linha_dos_olhos)
