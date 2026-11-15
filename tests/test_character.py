from datetime import timedelta

import pytest

from app.extensions import db
from app.models import Entry, User

VISUAL = {"corpo": "feminino", "pele": "#8d5524", "cabelo": "#3a86ff", "roupa": "#5fb85f", "itens": []}


def registrar_dias(app, action_key, inicio, dias):
    with app.app_context():
        user = User.query.filter_by(username="gustavo").one()
        for i in range(dias):
            db.session.add(Entry(user_id=user.id, action_key=action_key, day=inicio + timedelta(days=i)))
        db.session.commit()


def item(resposta, item_id):
    return next(i for i in resposta.get_json()["itens"] if i["id"] == item_id)


def test_visual_padrao_e_itens_bloqueados(logado):
    dados = logado.get("/api/personagem").get_json()
    assert dados["personagem"]["corpo"] == "masculino" and dados["personagem"]["itens"] == []
    assert len(dados["itens"]) == 13
    assert not any(i["liberado"] for i in dados["itens"])


def test_salvar_aparencia_persiste(logado):
    assert logado.put("/api/personagem", json=VISUAL).status_code == 200
    assert logado.get("/api/personagem").get_json()["personagem"] == VISUAL


@pytest.mark.parametrize("campo,valor", [("corpo", "alien"), ("pele", "#123456"), ("cabelo", "azul"), ("roupa", None)])
def test_opcao_invalida_e_recusada(logado, campo, valor):
    assert logado.put("/api/personagem", json={**VISUAL, campo: valor}).status_code == 400


def test_item_bloqueado_nao_pode_ser_salvo(logado):
    resposta = logado.put("/api/personagem", json={**VISUAL, "itens": ["regata"]})
    assert resposta.status_code == 403


def test_item_desconhecido_e_dois_itens_no_mesmo_lugar_sao_recusados(logado):
    assert logado.put("/api/personagem", json={**VISUAL, "itens": ["nao_existe"]}).status_code == 400
    assert logado.put("/api/personagem", json={**VISUAL, "itens": ["faixa", "fone"]}).status_code == 400


def test_item_de_atributo_libera_ao_chegar_no_nivel(app, logado, hoje):
    antes = logado.get("/api/personagem")
    assert item(antes, "regata")["liberado"] is False and item(antes, "regata")["atual"] == 0
    registrar_dias(app, "forca_academia", hoje - timedelta(days=36), 36)  # 360 XP = nível 3 de Força
    depois = logado.get("/api/personagem")
    assert item(depois, "regata")["liberado"] is True
    assert item(depois, "regata")["requisito"] == "Força nível 3"
    assert logado.put("/api/personagem", json={**VISUAL, "itens": ["regata"]}).status_code == 200
    assert logado.get("/api/personagem").get_json()["personagem"]["itens"] == ["regata"]


def test_item_de_sequencia_libera_com_dias_sem_tropecar(app, logado, hoje):
    registrar_dias(app, "vit_agua", hoje - timedelta(days=9), 1)
    medalha = item(logado.get("/api/personagem"), "medalha")
    assert medalha["liberado"] is True and medalha["requisito"] == "7 dias sem tropeçar"
    assert item(logado.get("/api/personagem"), "capa")["liberado"] is False


def test_item_equipado_volta_a_bloquear_se_o_nivel_cair(app, logado, hoje):
    registrar_dias(app, "forca_academia", hoje - timedelta(days=36), 36)
    logado.put("/api/personagem", json={**VISUAL, "itens": ["regata"]})
    with app.app_context():
        db.session.query(Entry).filter(Entry.day == hoje - timedelta(days=1)).delete()
        db.session.commit()
    assert logado.get("/api/personagem").get_json()["personagem"]["itens"] == []


def test_svg_do_personagem(logado):
    resposta = logado.get("/personagem.svg")
    assert resposta.status_code == 200 and resposta.mimetype == "image/svg+xml"
    assert resposta.headers["Cache-Control"] == "no-cache"


def test_svg_aceita_pre_visualizacao_inclusive_de_item_bloqueado(logado):
    base = logado.get("/personagem.svg").get_data(as_text=True)
    prova = logado.get("/personagem.svg", query_string={"cabelo": "#3a86ff", "itens": "capa,coroa"})
    assert prova.status_code == 200 and prova.get_data(as_text=True) != base


def test_svg_com_parametro_invalido_retorna_400(logado):
    assert logado.get("/personagem.svg", query_string={"corpo": "alien"}).status_code == 400


def test_svg_exige_login(client):
    assert client.get("/personagem.svg").status_code == 302


def test_cada_usuario_tem_seu_personagem(app, logado):
    logado.put("/api/personagem", json=VISUAL)
    outro = app.test_client()
    outro.post("/registro", data={"username": "maria", "password": "senha-segura"})
    assert outro.get("/api/personagem").get_json()["personagem"]["corpo"] == "masculino"
