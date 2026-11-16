from sqlalchemy import inspect, text

from .extensions import db


def add_missing_columns():
    """O create_all não altera tabelas que já existem: acrescenta as colunas novas (sempre opcionais)."""
    inspector = inspect(db.engine)
    dialect = db.engine.dialect
    quote = dialect.identifier_preparer.quote
    for table in db.metadata.sorted_tables:
        existing = {column["name"] for column in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name not in existing:
                assert column.nullable, f"{table.name}.{column.name} precisa ser opcional para entrar numa tabela existente"
                db.session.execute(text(
                    f"ALTER TABLE {quote(table.name)} ADD COLUMN {quote(column.name)} {column.type.compile(dialect)}"))
    db.session.commit()
