from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        print("Tabela `alembic_version` a fost ștearsă cu succes.")