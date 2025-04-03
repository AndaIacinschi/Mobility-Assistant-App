from app import app, db, Dispatcher
from werkzeug.security import generate_password_hash


# Datele contului dispeceratului
username = 'Dispecerat112'
password = 'Ambulanta112'  # Setează parola dorită

# Generăm hash-ul parolei
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

# Creăm un nou utilizator de tip Dispatcher
dispatcher = Dispatcher(username=username, password=hashed_password)

# Contextul aplicației Flask
with app.app_context():
    db.session.add(dispatcher)
    db.session.commit()

print('Contul dispeceratului a fost creat cu succes.')

