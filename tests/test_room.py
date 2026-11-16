import re
import xml.etree.ElementTree as ET
from datetime import timedelta
from types import SimpleNamespace

import pytest

from app.services import room, rules

PERSONAGEM = (17, 6, 14, 20)
ESTANTE = (33, 3, 14, 7)
NIVEL = (2, 1, 7, 6)
PADRAO = room.load()["padrao"]


def pixels(rows, x0, y0):
    return {(x0 + dx, y0 + dy) for dy, row in enumerate(rows) for dx, char in enumerate(row) if char != "."}


def retangulo(x, y, w, h):
    return {(i, j) for i in range(x, x + w) for j in range(y, y + h)}


def todos_os_desenhos():
    dados = room.load()
    desenhos = {prop["id"]: pixels(prop["mapa"], prop["x"], prop["y"]) for prop in dados["props"]}
    pet = dados["mascote"]
    for especie in pet["especies"]:
        for humor, mapa in especie["mapas"].items():
            desenhos[f"mascote-{especie['id']}-{humor}"] = pixels(mapa, pet["x"], pet["y"])
    return desenhos


def test_cada_atributo_tem_no_maximo_um_objeto():
    atributos = [prop["atributo"] for prop in room.load()["props"]]
    assert len(atributos) == len(set(atributos)) and set(atributos) <= {a["id"] for a in rules.attributes()}


def test_objetos_tem_cor_para_cada_caractere_e_linhas_do_mesmo_tamanho():
    for prop in room.load()["props"]:
        assert len({len(linha) for linha in prop["mapa"]}) == 1
        assert {c for linha in prop["mapa"] for c in linha} - {"."} <= set(prop["cores"])


def test_todo_mascote_tem_os_tres_humores_e_cor_para_cada_caractere():
    pet = room.load()["mascote"]
    assert {e["id"] for e in pet["especies"]} == {"gato", "cachorro"}
    for especie in pet["especies"]:
        assert set(especie["mapas"]) == set(room.HUMORS)
        assert len(especie["pelagens"]) >= 4
        for mapa in especie["mapas"].values():
            assert len(mapa) == 8 and {len(linha) for linha in mapa} == {8}
            for pelagem in especie["pelagens"]:
                usados = {c for linha in mapa for c in linha} - {"."}
                assert usados <= set(room.pet_colors(especie["id"], pelagem["id"])), (especie["id"], pelagem["id"])


def test_ids_de_pelagem_sao_unicos_por_especie():
    for especie in room.load()["mascote"]["especies"]:
        ids = [p["id"] for p in especie["pelagens"]]
        assert len(ids) == len(set(ids))


def test_tudo_cabe_no_quarto():
    for nome, desenho in todos_os_desenhos().items():
        assert all(0 <= x < room.WIDTH and 0 <= y < room.HEIGHT for x, y in desenho), nome


def test_objetos_nao_se_sobrepoem_nem_cobrem_o_personagem_a_estante_e_o_nivel():
    desenhos = todos_os_desenhos()
    props = {n: d for n, d in desenhos.items() if not n.startswith("mascote")}
    reservados = [retangulo(*PERSONAGEM), retangulo(*ESTANTE), retangulo(*NIVEL)]
    for nome, desenho in desenhos.items():
        assert not any(desenho & area for area in reservados), nome
        for outro, outro_desenho in desenhos.items():
            if nome < outro and not (nome.startswith("mascote") and outro.startswith("mascote")):
                assert not desenho & outro_desenho, (nome, outro)
    assert len(props) == 9


def niveis(nivel=0, **por_atributo):
    return {a["id"]: {"nivel": por_atributo.get(a["id"], nivel)} for a in rules.attributes()}


def test_quarto_comeca_vazio_e_ganha_objetos_ao_chegar_no_nivel_minimo():
    vazio = room.render(niveis(), "normal", PADRAO)
    minimo = room.load()["nivel_minimo"]
    assert room.render(niveis(forca=minimo - 1), "normal", PADRAO) == vazio
    assert room.render(niveis(forca=minimo), "normal", PADRAO).count("<rect") > vazio.count("<rect")


def test_quarto_completo_tem_todos_os_objetos():
    completo = room.render(niveis(room.load()["nivel_minimo"]), "normal", PADRAO)
    vazio = room.render(niveis(), "normal", PADRAO)
    assert completo.count("<rect") > vazio.count("<rect") + 25


@pytest.mark.parametrize("humor", room.HUMORS)
def test_mascote_aparece_com_o_humor(humor):
    assert f'class="pet {humor}"' in room.render(niveis(), humor, PADRAO)


def test_humores_tem_desenhos_diferentes():
    assert len({room.render(niveis(), h, PADRAO) for h in room.HUMORS}) == 3


def test_especies_e_pelagens_geram_desenhos_diferentes():
    gato = {"tema": "classico", "especie": "gato", "pelagem": "laranja"}
    desenhos = {
        room.render(niveis(), "normal", gato),
        room.render(niveis(), "normal", {**gato, "pelagem": "cinza"}),
        room.render(niveis(), "normal", {**gato, "especie": "cachorro", "pelagem": "caramelo"}),
    }
    assert len(desenhos) == 3


def test_toda_combinacao_de_mascote_renderiza_em_xml_valido():
    for especie in room.load()["mascote"]["especies"]:
        for pelagem in especie["pelagens"]:
            for humor in room.HUMORS:
                svg = room.render(niveis(room.load()["nivel_minimo"]), humor,
                                  {"tema": "classico", "especie": especie["id"], "pelagem": pelagem["id"]})
                ET.fromstring(svg)
                assert pelagem["cores"]["o"] in svg


def cores_do_fundo(svg):
    return re.findall(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)" fill="(#[0-9a-f]{6})"', svg)


def test_temas_tem_ids_unicos_e_o_padrao_existe():
    ids = [t["id"] for t in room.load()["temas"]]
    assert len(ids) == len(set(ids)) >= 5 and PADRAO["tema"] in ids


def test_tema_classico_e_o_cenario_original():
    assert room.background("classico") == room.BACKGROUND.read_text(encoding="utf-8")


@pytest.mark.parametrize("tema", [t["id"] for t in room.load()["temas"]])
def test_cada_tema_troca_so_as_cores_dele(tema):
    dados = next(t for t in room.load()["temas"] if t["id"] == tema)
    original = cores_do_fundo(room.BACKGROUND.read_text(encoding="utf-8"))
    usadas = {cor for *_, cor in original}
    assert set(dados["trocas"]) <= usadas  # nada de cor digitada errada
    svg = room.background(tema)
    ET.fromstring(svg)
    esperado = [(*pos, dados["trocas"].get(cor, cor)) for *pos, cor in original]
    extras = [tuple(map(str, extra)) for extra in dados.get("extras", [])]
    assert cores_do_fundo(svg) == esperado + extras
    assert all(0 <= x < room.WIDTH and 0 <= y < room.HEIGHT for x, y, *_ in dados.get("extras", []))


def test_temas_diferentes_tem_cenarios_diferentes():
    assert len({room.background(t["id"]) for t in room.load()["temas"]}) == len(room.load()["temas"])


def foto(entradas, ultimo_dia):
    acoes = {"bom": {"tropeco": False}, "ruim": {"tropeco": True}}
    return {"entries": [SimpleNamespace(day=dia, action_key=chave) for dia, chave in entradas],
            "actions": acoes, "ultimo_dia": ultimo_dia}


def test_humor_do_mascote(hoje):
    dia = lambda n: hoje - timedelta(days=n)
    assert room.mood(foto([], None), hoje)["humor"] == "normal"
    assert room.mood(foto([(hoje, "bom")] * 3, hoje), hoje)["humor"] == "feliz"
    assert room.mood(foto([(hoje, "bom")] * 2, hoje), hoje)["humor"] == "normal"
    assert room.mood(foto([(hoje, "ruim")] * 3, hoje), hoje)["humor"] == "normal"  # tropeço não alegra
    assert room.mood(foto([(dia(2), "bom")], dia(2)), hoje)["humor"] == "normal"
    assert room.mood(foto([(dia(3), "bom")], dia(3)), hoje)["humor"] == "triste"


def test_quarto_exige_login(client):
    for caminho in ("/quarto.svg", "/cenario.svg", "/quarto"):
        resposta = client.get(caminho)
        assert resposta.status_code == 302 and "/login" in resposta.headers["Location"], caminho


def test_rota_do_quarto_acompanha_o_progresso(logado):
    antes = logado.get("/quarto.svg")
    assert antes.mimetype == "image/svg+xml" and antes.headers["Cache-Control"] == "no-cache"
    logado.post("/api/registros", json={"action_key": "forca_treino_pesado", "dia": "2025-12-31"})
    for dia in range(1, 11):
        logado.post("/api/registros", json={"action_key": "forca_treino_pesado", "dia": f"2026-01-{dia:02d}"})
    depois = logado.get("/quarto.svg").get_data(as_text=True)
    assert depois.count("<rect") > antes.get_data(as_text=True).count("<rect")


def test_mascote_fica_feliz_depois_de_tres_acoes_hoje(logado):
    assert logado.get("/api/estado").get_json()["mascote"]["humor"] == "normal"
    for chave in ("forca_academia", "foco_sessao", "eq_hobby"):
        logado.post("/api/registros", json={"action_key": chave})
    assert logado.get("/api/estado").get_json()["mascote"]["humor"] == "feliz"
    assert 'class="pet feliz"' in logado.get("/quarto.svg").get_data(as_text=True)


@pytest.mark.parametrize("humor", room.HUMORS)
def test_mascote_tem_animacao_e_respeita_reduzir_movimento(humor):
    levels = {a["id"]: {"nivel": 1} for a in rules.load()["atributos"]}
    svg = room.render(levels, humor, room.load()["padrao"])
    assert f'class="pet {humor}"' in svg and 'class="quique"' in svg
    assert "prefers-reduced-motion" in svg


def test_so_o_mascote_triste_fica_parado_no_lugar():
    assert ".pet.normal{animation:passear" in room.STYLE
    assert ".pet.feliz{animation:passear" in room.STYLE
    assert ".pet.triste" not in room.STYLE
