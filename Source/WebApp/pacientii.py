from app import app, db, Patient 

with app.app_context():
    all_patients = Patient.query.all()

    # Afișează detalii despre fiecare cont
    for patient in all_patients:
        print(f'ID: {patient.id}, Username: {patient.username}, Email: {patient.email}, Password Hash: {patient.password}')