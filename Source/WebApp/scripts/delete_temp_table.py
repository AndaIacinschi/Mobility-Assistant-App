from app import db, app
from sqlalchemy import text

# Creează un context de aplicație pentru a putea accesa baza de date
with app.app_context():
    # Creează o conexiune și execută comanda SQL
    with db.engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS _alembic_tmp_patient"))
        print("Tabelul '_alembic_tmp_patient' a fost șters.")