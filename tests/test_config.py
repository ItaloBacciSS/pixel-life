import pytest

from app import config


@pytest.mark.parametrize("entrada", [
    "postgres://u:p@host/db",
    "postgresql://u:p@host/db",
    "postgresql+psycopg://u:p@host/db",
    "postgresql+psycopg2://u:p@host/db",
])
def test_postgres_sempre_usa_psycopg2(monkeypatch, entrada):
    monkeypatch.setenv("DATABASE_URL", entrada)
    assert config._database_url() == "postgresql+psycopg2://u:p@host/db"


def test_sqlite_fica_como_esta(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    assert config._database_url() == "sqlite:///jogo.db"


def test_postgres_url_e_usada_quando_nao_ha_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_URL", "postgres://u:p@host/db")
    assert config._database_url() == "postgresql+psycopg2://u:p@host/db"


def test_arquivos_estaticos_sao_conferidos_a_cada_uso_e_nao_ficam_velhos(client):
    primeira = client.get("/static/js/ui.js")
    assert "no-cache" in primeira.headers["Cache-Control"]
    etag = primeira.headers["ETag"]
    repetida = client.get("/static/js/ui.js", headers={"If-None-Match": etag})
    assert repetida.status_code == 304  # nada é baixado de novo se o arquivo não mudou
