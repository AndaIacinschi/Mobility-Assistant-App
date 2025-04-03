// Inițializează harta și setează locația și nivelul de zoom
var map = L.map('map').setView([45.9432, 24.9668], 7); // Harta este centrată pe România, cu nivel de zoom 7

// Setează stratul de hărți OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,  // Nivelul maxim de zoom al hărții
    attribution: '© OpenStreetMap contributors'  // Atribuirea pentru datele OpenStreetMap
}).addTo(map);  // Adaugă stratul de hărți pe hartă

// Funcție pentru adăugarea unui marker pe hartă cu detalii în popup
function addMarker(latitude, longitude, details) {
    // Creează un icon personalizat pentru marker
    var icon = L.icon({
        iconUrl: '/static/ambulance_b.png', // URL-ul pentru iconița ambulanței (verifică dacă calea imaginii este corectă)
        iconSize: [30, 30],  // Dimensiunea iconiței
        iconAnchor: [15, 30],  // Punctul din icon care va reprezenta locația exactă a marker-ului
        popupAnchor: [0, -30]  // Punctul din care apare popup-ul relativ la marker
    });

    // Creează markerul cu latitudinea, longitudinea și iconița personalizată
    var marker = L.marker([latitude, longitude], { icon: icon }).addTo(map);

    // Adaugă un eveniment de tip 'click' pentru a deschide popup-ul cu informațiile pacientului
    marker.on('click', function() {
        marker.bindPopup(details).openPopup();  // Leagă popup-ul de marker și îl deschide
    });
}

// Cerere fetch pentru a obține datele pacienților și a adăuga markerii pe hartă
fetch('/api/get-patients')
    .then(response => response.json())  // Parsează răspunsul ca JSON
    .then(data => {
        data.patients.forEach(patient => {
            if (patient.latitude && patient.longitude) {  // Verifică dacă latitudinea și longitudinea sunt disponibile
                // Creează un string formatat cu detaliile pacientului care vor apărea în popup
                var details = `
                    <strong>${patient.prenume} ${patient.nume}</strong><br>
                    <strong>Boala:</strong> ${patient.boala}<br>
                    <strong>Medicamente:</strong> ${patient.medicamente}<br>
                    <strong>Ultimul incident:</strong> ${patient.ultimul_incident}<br>
                    <strong>Telefon:</strong> ${patient.telefon}
                `;
                // Adaugă markerul pe hartă
                addMarker(patient.latitude, patient.longitude, details);
            }
        });
    })
    .catch(error => {
        console.error('Eroare la obținerea datelor pacienților:', error);  // Afișează eroarea în caz de eșec
    });
