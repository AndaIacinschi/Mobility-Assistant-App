
#  Mobility Assistant App – Real-Time Fall Detection System

![iOS](https://img.shields.io/badge/platform-iOS-blue)
![React](https://img.shields.io/badge/frontend-React.js-61DAFB?logo=react)
![Flask](https://img.shields.io/badge/backend-Flask-yellow?logo=flask)

This project implements a complete system for real-time fall detection and emergency alerting, specifically designed to support people with mobility impairments, such as elderly users or patients recovering from trauma. It combines motion sensor monitoring on iOS devices, real-time data processing via a secure backend, and an easy-to-use web dashboard for dispatcher coordination. When a potential fall is detected, the application immediately initiates a short voice interaction with the user to confirm th...

---

##  Project Structure

```
mobility-assistant-app/
├── mobile-app/         # iOS application (Swift)
├── web-platform/       # React.js frontend for dispatcher dashboard
├── docs/               # Thesis PDF & Presentation
└── README.md
```

> Note: Backend logic is integrated within the mobile and web apps. The iOS app handles data processing and API communication natively, while the web dashboard includes both frontend and Flask-based backend functionality.

---

##  Mobile Client (Swift – iOS)

**Sensor Input**: Uses `CoreMotion` to track accelerometer data and detect sudden impact events.

**Fall Detection Algorithm**:
- Computes acceleration magnitude: `sqrt(x² + y² + z²)`
- Detects impact if value exceeds threshold (2.5g)

**Real-Time Actions**:
- Triggers a voice prompt asking the user if they are okay
- If the user answers, their response and location are sent to the dispatcher — whether they feel fine or need help
- If there’s no response, the prompt is repeated once
- If still no response, the system sends an emergency alert with “no reply” status and location

**Frameworks**:
- `UIKit`, `UserNotifications`, `CoreMotion`
- Auth via JWT token with persistent session

**HTTP Client**: Uses native `URLSession` for REST API interaction

---

##  Backend API (Python – Flask)

**Frameworks**: Flask, Flask-SocketIO, Flask-Migrate, Flask-JWT-Extended

**Endpoints**:
- `/api/register` – user registration
- `/api/login` – authentication and JWT issuance
- `/api/report-accident` – receives incident reports

**Database**:
- MySQL with SQLAlchemy ORM
- Models: `Patient`, `Dispatcher`, `Accident`

**Real-Time Communication**:
- WebSocket alert propagation via `Flask-SocketIO`
- Events: `connect`, `disconnect`, `alert`

---

##  Web Platform (React.js)

**Architecture**: Component-based layout with real-time WebSocket hooks

**Main Features**:
- Role-based login for patients and dispatchers
- Live map with real-time alert markers
- Instant notifications via `Socket.IO` client

**Tech Stack**:
- React.js, Axios, Socket.IO-client, Leaflet.js, Bootstrap

**Security**:
- HTTPS-enabled
- JWT token verification for route protection
- Password hashing using `bcrypt`

---

##  Security Model

**Authentication**: Stateless sessions using `JWT`

**Data Protection**:
- Encrypted password storage
- API access control via route decorators

**Authorization**:
- Scoped access for dispatcher vs. patient
- Patient alerts remain private

---

##  Test Strategy

**Mobile**:
- Manual test cases and simulator scenarios

**Backend**:
- Unit tests for API responses and auth flow
- Database migration tests (Alembic)

**Web**:
- Mock API testing
- Socket message listener verification

---

##  How the Alert System Works

1. The iOS app detects a fall
2. Sends data via secure POST to backend
3. Backend stores event and notifies dashboard via WebSocket
4. Dispatcher sees alert and reacts in real time

---

##  Author

**Iacinschi Anda-Roxana**  
Bachelor of Engineering – Computer Systems  
Faculty of Automation and Computer Science, TUIASI  
📬 anda.roxana.iacinschi@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/anda-roxana-iacinschi-2ab6b426a/)
