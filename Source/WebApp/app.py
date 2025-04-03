from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, disconnect
import requests
import jwt

app = Flask(__name__)

# Configurațiile aplicației
app.config['SECRET_KEY'] = 'your_secret_key'  # Cheie pentru criptarea datelor
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Conexiunea la baza de date
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Dezactivează notificările inutile


# Inițializarea bazei de date și a migrărilor
db = SQLAlchemy(app)  # Gestionarea bazei de date
migrate = Migrate(app, db)  # Gestionarea migrărilor bazei de date
socketio = SocketIO(app, cors_allowed_origins="*")  # Notificări în timp real prin WebSockets
JWT_SECRET = 'your_jwt_secret_key'

# Funcția pentru generarea unui token JWT
def generate_token(user_id):
    # Crează un token JWT pentru utilizator, care va fi utilizat pentru autentificare
    payload = {
        'user_id': user_id,  # ID-ul utilizatorului
        'exp': datetime.utcnow() + timedelta(hours=1)  # Expiră în 1 oră
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')  # Crearea token-ului
    return token

# Funcția pentru verificarea unui token JWT
def verify_token(token):
    # Verifică valabilitatea token-ului
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])  # Decodează token-ul
        return payload['user_id']  # Returnează ID-ul utilizatorului
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):  # Dacă token-ul a expirat sau nu este valid
        return None  # Returnează None în caz de eroare

# Funcția care se execută când un client se conectează la server
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Nu se face verificare de token pentru conectările WebSocket

# Funcția care se execută când un client se deconectează de la server
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    
# Modelele bazei de date
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    prenume = db.Column(db.String(150), nullable=True)
    nume = db.Column(db.String(150), nullable=True)
    data_nasterii = db.Column(db.Date, nullable=True)
    boala = db.Column(db.String(500), nullable=True)
    medicamente = db.Column(db.String(500), nullable=True)
    ultimul_incident = db.Column(db.String(500), nullable=True)
    tara = db.Column(db.String(100), nullable=True)
    judet = db.Column(db.String(100), nullable=True)
    oras = db.Column(db.String(100), nullable=True)
    strada = db.Column(db.String(200), nullable=True)
    numar = db.Column(db.String(50), nullable=True)
    cod_postal = db.Column(db.String(20), nullable=True)
    telefon = db.Column(db.String(20), nullable=True)  
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    este_logat = db.Column(db.Boolean, default=False)

class Dispatcher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Accident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    details = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

# Pagina principală de alegere
@app.route('/')
def index():
    return render_template('index.html')

# Alegerea tipului de logare
@app.route('/login_choice', methods=['POST'])
def login_choice():
    role = request.form.get('role')
    if role == 'patient':
        return redirect(url_for('login_patient'))
    elif role == 'dispatcher':
        return redirect(url_for('login_dispatcher'))
    else:
        flash('Invalid choice')
        return redirect(url_for('index'))

# Funcția pentru logarea pacientului
@app.route('/login_patient', methods=['GET', 'POST'])
def login_patient():
    # Logarea pacientului în aplicație
    if request.method == 'POST':
        username = request.form.get('username')  # Capturăm username-ul din formular
        password = request.form.get('password')  # Capturăm parola din formular
        
        # Căutăm pacientul în baza de date după username
        patient = Patient.query.filter_by(username=username).first()

        # Verificăm dacă pacientul există și parola este corectă
        if patient and check_password_hash(patient.password, password):
            session['patient_id'] = patient.id  # Stocăm ID-ul pacientului în sesiune
            session['username'] = patient.username  # Stocăm username-ul pacientului în sesiune

            # Generăm un token JWT pentru pacientul autentificat
            token = generate_token(patient.id)
            session['auth_token'] = token  # Stocăm token-ul în sesiune
            
            patient.este_logat = True  # Actualizăm statusul de logare al pacientului
            db.session.commit()  # Salvăm în baza de date
            
            return redirect(url_for('dashboard_pacient'))  # Redirecționăm pacientul către dashboard
        else:
            flash('Nume de utilizator sau parolă incorectă.', 'danger')  # Afișăm un mesaj de eroare dacă autentificarea a eșuat
            return redirect(url_for('login_patient'))  # Redirecționăm înapoi la pagina de login

    return render_template('login_patient.html')  # Dacă cererea este GET, redirecționăm către pagina de login


# Logare dispecerat
@app.route('/login_dispatcher', methods=['GET', 'POST'])
def login_dispatcher():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        dispatcher = Dispatcher.query.filter_by(username=username).first()

        if dispatcher and check_password_hash(dispatcher.password, password):
            session['dispatcher_id'] = dispatcher.id
            return redirect(url_for('dashboard_dispatcher'))
        else:
            flash('Username sau parolă incorectă.')
    return render_template('login_dispatcher.html')

# Înregistrare pacient
@app.route('/inregistrare_pacient', methods=['POST'])
def inregistrare_pacient_api():
    try:
        # Extrage datele din cererea POST
        data = request.get_json()  # Așteaptă date în format JSON
        username = data.get('username')
        email = data.get('email')
        parola = data.get('parola')
        confirma_parola = data.get('confirma_parola')

        # Verifică dacă toate câmpurile sunt furnizate
        if not all([username, email, parola, confirma_parola]):
            return jsonify({"error": "Toate câmpurile sunt obligatorii!"}), 400

        # Verifică parolele
        if parola != confirma_parola:
            return jsonify({"error": "Parolele nu se potrivesc!"}), 400

        # Verifică dacă email-ul există deja
        if Patient.query.filter_by(email=email).first():
            return jsonify({"error": "Email-ul este deja utilizat!"}), 400

        # Hash-uiește parola folosind generate_password_hash
        hashed_password = generate_password_hash(parola)

        # Creează un nou pacient
        pacient = Patient(
            username=username,
            email=email,
            password=hashed_password,  # Salvează parola hash-uită
        )
        db.session.add(pacient)
        db.session.commit()  # Salvează în baza de date

        # Returnează un răspuns de succes
        return jsonify({"message": "Cont creat cu succes!", "patient_id": pacient.id}), 201
    except Exception as e:
        print(f"Eroare la înregistrare: {str(e)}")
        return jsonify({"error": "A apărut o eroare la înregistrare"}), 500


@app.route('/inregistrare_pacient_web', methods=['GET', 'POST'])
def inregistrare_pacient_web():
    if request.method == 'GET':
        return render_template('inregistrare_pacient_web.html')  # Afișează formularul HTML

    elif request.method == 'POST':
        try:
            # Extrage datele din formular
            username = request.form.get('username')
            email = request.form.get('email')
            parola = request.form.get('parola')
            confirma_parola = request.form.get('confirma_parola')

            # Validări
            if not all([username, email, parola, confirma_parola]):
                flash("Toate câmpurile sunt obligatorii!", "danger")
                return redirect(url_for('inregistrare_pacient_web'))

            if parola != confirma_parola:
                flash("Parolele nu se potrivesc!", "danger")
                return redirect(url_for('inregistrare_pacient_web'))

            if Patient.query.filter_by(email=email).first():
                flash("Email-ul este deja utilizat!", "danger")
                return redirect(url_for('inregistrare_pacient_web'))

            # Creează utilizatorul
            hashed_password = generate_password_hash(parola)
            pacient = Patient(username=username, email=email, password=hashed_password, este_logat=True)
            db.session.add(pacient)
            db.session.commit()

            # Adaugă utilizatorul în sesiune
            session['patient_id'] = pacient.id
            session['username'] = pacient.username

            # Mesaj de succes și redirecționare
            flash("Cont creat cu succes și pacient conectat!", "success")
            return redirect(url_for('dashboard_pacient'))
        except Exception as e:
            print(f"Eroare la înregistrare web: {str(e)}")
            flash("A apărut o eroare la înregistrare", "danger")
            return redirect(url_for('inregistrare_pacient_web'))



# Dashboard pacient
@app.route('/dashboard_pacient')
def dashboard_pacient():
    if 'patient_id' not in session:
        return redirect(url_for('login_patient'))
    pacient = Patient.query.get(session['patient_id'])
    return render_template('dashboard_pacient.html', pacient=pacient)

# Dashboard dispecerat
@app.route('/dashboard_dispatcher')
def dashboard_dispatcher():
    if 'dispatcher_id' not in session:
        return redirect(url_for('login_dispatcher'))

    logged_in_patients = Patient.query.filter_by(este_logat=True).all()

    # Transformă fiecare obiect `Patient` într-un dicționar serializabil
    patients_data = []
    for patient in logged_in_patients:
        patients_data.append({
            'prenume': patient.prenume,
            'nume': patient.nume,
            'latitude': patient.latitude,
            'longitude': patient.longitude,
            'boala': patient.boala
        })

    return render_template('dashboard_dispatcher.html', logged_in_patients=patients_data)

# Rute pentru afișarea pacienților logați
@app.route('/pacienti_logati')
def pacienti_logati():
    if 'dispatcher_id' not in session:
        return redirect(url_for('login_dispatcher'))

    pacienti_logati = Patient.query.filter_by(este_logat=True).all()

    # Asigură-te că aici lista se numește `patients`, exact ca în șablon
    return render_template('pacienti_logati.html', patients=pacienti_logati)

# Funcție de geocodificare pentru adrese
def geocode_address(tara, judet, oras, strada, numar, cod_postal):
    address = f"{judet} {oras} {strada} {numar}"
    print(f"Trying to geocode: {address}")
    api_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json'
    }
    
    headers = {
        'User-Agent': 'YourAppName/1.0'
    }
    
    response = requests.get(api_url, params=params, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Răspuns primit: {data}")
            if len(data) > 0:
                location = data[0]
                lat, lon = float(location['lat']), float(location['lon'])
                print(f"Geocoding successful: {address} -> ({lat}, {lon})")
                return lat, lon
            else:
                print(f"Geocoding failed: No results found for {address}")
        except ValueError:
            print("Eroare la decodificarea JSON, răspuns invalid")
    else:
        print(f"Geocoding failed: HTTP status code {response.status_code} for {address}")

    return None, None

# Rute pentru actualizarea profilului pacientului
@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'patient_id' not in session:
        return redirect(url_for('login_patient'))

    pacient = Patient.query.get(session['patient_id'])

    if request.method == 'POST':
        pacient.prenume = request.form['prenume']
        pacient.nume = request.form['nume']
        pacient.data_nasterii = datetime.strptime(request.form['data_nasterii'], '%Y-%m-%d').date()
        pacient.boala = request.form['boala']
        pacient.medicamente = request.form['medicamente']
        pacient.ultimul_incident = request.form['ultimul_incident']
        pacient.tara = request.form['tara']
        pacient.judet = request.form['judet']
        pacient.oras = request.form['oras']
        pacient.strada = request.form['strada']
        pacient.numar = request.form['numar']
        pacient.cod_postal = request.form['cod_postal']
        pacient.telefon = request.form['telefon']

        # Geocodifică adresa și salvează coordonatele în baza de date
        lat, lon = geocode_address(pacient.tara, pacient.judet, pacient.oras, pacient.strada, pacient.numar, pacient.cod_postal)
        print(f"Coordonatele obținute: latitudine={lat}, longitudine={lon}")  # Debugging
        if lat and lon:
            pacient.latitude = lat
            pacient.longitude = lon
        else:
            flash("Nu s-au putut obține coordonatele pentru această adresă.", 'danger')

        # Verificăm dacă latitudinea și longitudinea au fost setate corect
        if pacient.latitude and pacient.longitude:
            print(f"Latitudinea și longitudinea au fost setate corect: ({pacient.latitude}, {pacient.longitude})")
        else:
            print("Latitudinea și longitudinea nu au fost setate corect.")

        db.session.commit()
        flash('Profil actualizat cu succes!', 'success')
        return redirect(url_for('dashboard_pacient'))

    return render_template('update_profile.html', pacient=pacient)
    
 # Rute API pentru actualizarea profilului pacientului prin POST (API pentru aplicația mobilă)   
@app.route('/api/update-profile', methods=['POST'])
def api_update_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]
    patient_id = verify_token(token)
    if not patient_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    
    # Log for debugging
    print(f"Received data for profile update: {data}")
    
    if not data:
        return jsonify({"error": "No data provided"}), 400

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    try:
        patient.prenume = data.get('prenume')
        patient.nume = data.get('nume')
        patient.data_nasterii = datetime.strptime(data.get('data_nasterii'), '%Y-%m-%d').date() if data.get('data_nasterii') else None
        patient.boala = data.get('boala')
        patient.medicamente = data.get('medicamente')
        patient.ultimul_incident = data.get('ultimul_incident')
        patient.tara = data.get('tara')
        patient.judet = data.get('judet')
        patient.oras = data.get('oras')
        patient.strada = data.get('strada')
        patient.numar = data.get('numar')
        patient.cod_postal = data.get('cod_postal')
        patient.telefon = data.get('telefon')

        # Log to see the updated patient information before geocoding
        print(f"Updated patient data (before geocoding): {patient.__dict__}")

        lat, lon = geocode_address(patient.tara, patient.judet, patient.oras, patient.strada, patient.numar, patient.cod_postal)
        if lat and lon:
            patient.latitude = lat
            patient.longitude = lon
        else:
            return jsonify({"error": "Failed to geocode address"}), 400

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        print(f"Error updating profile: {str(e)}")  # Log the exception
        return jsonify({"error": str(e)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Funcție pentru a prelua pacienții din baza de date    
@app.route('/api/get-patients')
def get_patients():
    patients = Patient.query.all()  # Preia toți pacienții din baza de date
    patient_data = []
    for patient in patients:
        if patient.latitude and patient.longitude:
            patient_info = {
                "prenume": patient.prenume,
                "nume": patient.nume,
                "boala": patient.boala,
                "telefon": patient.telefon,
                "latitude": patient.latitude,
                "longitude": patient.longitude
            }
            print(f"Patient data: {patient_info}")  # Mesaj de debug
            patient_data.append(patient_info)

    return jsonify({"patients": patient_data})
def parse_time(time_string):
    try:
        return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")  # Cu microsecunde
    except ValueError:
        return datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")  # Fără microsecunde

# Ruta pentru raportarea accidentelor de la aplicația mobilă
@app.route('/api/report-accident', methods=['POST'])
def report_accident():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]
    patient_id = verify_token(token)
    if not patient_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    location = data.get("location")
    details = data.get("details")
    time = data.get("time")
    stare = data.get("stare", "necunoscut") 

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    new_accident = Accident(
        latitude=location['latitude'],
        longitude=location['longitude'],
        details=details,
        time=datetime.utcnow()
    )

    db.session.add(new_accident)
    db.session.commit()

    accident_notification = {
        'prenume': patient.prenume,
        'nume': patient.nume,
        'boala': patient.boala,
        'telefon': patient.telefon,
        'latitude': location['latitude'],
        'longitude': location['longitude'],
        'details': details,
        'stare': stare
    }

    print(f"Sending accident alert: {accident_notification}")  # Debugging log
    socketio.emit('accident_alert', accident_notification)  # Trimite notificarea către clienții conectați
    
    return jsonify({"message": "Accident reported successfully"}), 200

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Email și parola sunt necesare."}), 400

    email = data['email']
    password = data['password']

    # Găsește pacientul după email
    patient = Patient.query.filter_by(email=email).first()

    if patient and check_password_hash(patient.password, password):
        # Autentificare reușită
        token = generate_token(patient.id)  # Generăm un token JWT care conține ID-ul pacientului
        return jsonify({"success": True, "token": token})
    else:
        # Autentificare eșuată
        return jsonify({"success": False, "message": "Nume de utilizator sau parolă incorectă."}), 401

@app.route('/api/get-patient-profile', methods=['GET'])
def get_patient_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(" ")[1]  # Extrage token-ul din antetul Authorization
    patient_id = verify_token(token)
    if not patient_id:
        return jsonify({"error": "Unauthorized"}), 401

    patient = Patient.query.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    patient_data = {
        "prenume": patient.prenume,
        "nume": patient.nume,
        "data_nasterii": patient.data_nasterii.strftime('%Y-%m-%d') if patient.data_nasterii else None,
        "tara": patient.tara,
        "judet": patient.judet,
        "oras": patient.oras,
        "strada": patient.strada,
        "numar": patient.numar,
        "cod_postal": patient.cod_postal,
        "boala": patient.boala,
        "medicamente": patient.medicamente,
        "telefon": patient.telefon,
        "ultimul_incident": patient.ultimul_incident
    }

    return jsonify(patient_data), 200

@app.route('/api/send-mobile-update', methods=['POST'])
def receive_mobile_update():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extrage datele trimise de aplicația mobilă
    update_message = data.get("message")
    patient_id = data.get("patient_id")

    # Găsește pacientul în baza de date
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    # Pregătește notificarea pentru a fi trimisă către clienții web
    update_data = {
        "patient_id": patient_id,
        "message": update_message,
        "patient_name": f"{patient.prenume} {patient.nume}",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Trimiterea notificării către toți clienții conectați la WebSocket
    print(f"Emitting mobile_update with data: {update_data}")
    socketio.emit('mobile_update', update_data)

    return jsonify({"message": "Update received and broadcasted successfully"}), 200

# Pornirea aplicației Flask cu WebSockets
@app.route('/logout')
def logout():
    session.pop('patient_id', None)
    session.pop('dispatcher_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)