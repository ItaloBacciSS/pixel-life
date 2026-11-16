import json
import re
from pathlib import Path

import pytest

from app.models import User
from app.services import styles

STATIC = Path(__file__).resolve().parent.parent / "static" / "css"
IDS = [estilo["id"] for estilo in styles.catalog()]


def _blocks():
    css = (STATIC / "temas.css").read_text(encoding="utf-8")
    result = {}
    for style_id, body in re.findall(r'\[data-estilo="([\w-]+)"\]\s*\{(.*?)\}', css, re.S):
        result[style_id] = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})\s*;", body))
    return result


def _luminance(color):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    channels = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a, b):
    high, low = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


VARIABLES = {"sky", "paper", "surface", "ink", "text", "muted", "brand", "on-brand", "danger",
             "danger-texto", "line", "titulo", "ok", "locked"}


def test_todo_estilo_tem_css_e_o_css_nao_tem_sobras():
    assert set(_blocks()) == set(IDS)


@pytest.mark.parametrize("style_id", IDS)
def test_estilo_define_todas_as_variaveis(style_id):
    assert set(_blocks()[style_id]) == VARIABLES


@pytest.mark.parametrize("style_id", IDS)
@pytest.mark.parametrize("front,back,minimum", [
    ("text", "paper", 4.5), ("text", "surface", 4.5), ("muted", "paper", 4.5), ("muted", "surface", 4.5),
    ("on-brand", "brand", 4.5), ("danger-texto", "paper", 4.5), ("ok", "paper", 4.5), ("ok", "surface", 4.5),
    ("text", "locked", 4.5), ("muted", "locked", 3.0), ("titulo", "ink", 4.5),
])
def test_estilo_tem_contraste_legivel(style_id, front, back, minimum):
    colors = _blocks()[style_id]
    assert contrast(colors[front], colors[back]) >= minimum, f"{style_id}: {front} sobre {back}"


@pytest.mark.parametrize("style_id", IDS)
def test_botao_de_perigo_tem_texto_branco_legivel(style_id):
    assert contrast("#ffffff", _blocks()[style_id]["danger"]) >= 4.5


def test_ids_sao_unicos_e_curtos():
    assert len(set(IDS)) == len(IDS) and all(re.fullmatch(r"[a-z]{3,20}", i) for i in IDS)


def test_novo_usuario_usa_o_classico(logado):
    assert 'data-estilo="classico"' in logado.get("/").get_data(as_text=True)


def test_escolher_estilo_salva_e_vale_em_todas_as_paginas(logado, app):
    assert logado.put("/api/estilo", json={"estilo": "noite"}).status_code == 200
    with app.app_context():
        assert User.query.one().estilo == "noite"
    for caminho in ("/", "/perfil", "/personagem"):
        assert 'data-estilo="noite"' in logado.get(caminho).get_data(as_text=True)


@pytest.mark.parametrize("valor", ["", "nada", None, 3, "<script>", "classico\"><b>"])
def test_estilo_desconhecido_e_recusado(logado, valor):
    assert logado.put("/api/estilo", json={"estilo": valor}).status_code == 400


def test_estilo_exige_login(client):
    assert client.put("/api/estilo", json={"estilo": "noite"}).status_code == 401


def test_perfil_lista_todos_os_estilos(logado):
    html = logado.get("/perfil").get_data(as_text=True)
    assert all(f'data-id="{i}"' in html for i in IDS)


def test_paginas_sem_login_usam_o_classico(client):
    assert 'data-estilo="classico"' in client.get("/login").get_data(as_text=True)


def test_arquivo_de_estilos_e_json_valido():
    assert json.loads((Path(styles.STYLES_FILE)).read_text(encoding="utf-8"))
