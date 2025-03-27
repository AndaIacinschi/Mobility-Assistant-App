# Mobility Assistant App – Real-Time Fall Detection System

![iOS](https://img.shields.io/badge/platform-iOS-blue)
![React](https://img.shields.io/badge/frontend-React.js-61DAFB?logo=react)
![Flask](https://img.shields.io/badge/backend-Flask-yellow?logo=flask)

This project implements a complete system for real-time fall detection and emergency alerting, specifically designed to support people with mobility impairments, such as elderly users or patients recovering from trauma. It combines motion sensor monitoring on iOS devices, real-time data processing via a secure backend, and an easy-to-use web dashboard for dispatcher coordination. When a potential fall is detected, the application immediately initiates a short voice interaction with the user to confirm their status. The system automatically sends an alert containing the user’s status and real-time location to the dispatcher platform ensuring rapid intervention in critical situations.

# Project Structure
mobility-assistant-app/
├── mobile-app/         # iOS application (Swift)
├── web-platform/       # React.js frontend for dispatcher dashboard
├── docs/               # Thesis PDF & Presentation
└── README.md

Note: Backend logic is integrated within the mobile and web apps. The iOS app handles data processing and API communication natively, while the web dashboard includes both frontend and Flask-based backend functionality for real-time monitoring and alert management.

#  Mobile Client (Swift – iOS)
**Sensor Input**: Uses CoreMotion to track accelerometer data and detect sudden impact events.
**Fall Detection Algorithm**:
  - Computes acceleration magnitude: `sqrt(x² + y² + z²)`
  - Threshold-based impact detection (2.5g)
**Real-Time Actions**:
The app triggers a voice prompt asking the user if they are okay.
-If the user answers, their response and location are sent to the dispatcher — whether they feel fine or need help.
-If there is no response, the prompt is repeated once.
-If the user still doesn't reply, the system automatically alerts the dispatcher, indicating no response and sharing the real-time location.
**Frameworks**:
  - UIKit, UserNotifications, CoreMotion
  - Auth via JWT token with persistent session
**HTTP Client**: Native URLSession for REST API interaction

# Backend API (Python – Flask)
**Frameworks**: Flask, Flask-SocketIO, Flask-Migrate, Flask-JWT-Extended
**Endpoints**:
  - /api/register – user registration
  - /api/login – authentication and JWT issuance
  - /api/report-accident – receives incident reports (POST)
**Database**:
  - MySQL with SQLAlchemy ORM
  - Models: Patient, Dispatcher, Accident
**Real-Time Communication**:
  - WebSocket alert propagation via Flask-SocketIO
  - Event hooks: connect, disconnect, alert

#  Web Platform (React.js)
**Architecture**: Component-based layout with real-time hooks
**Main Features**:
  - Role-based login (patients, dispatchers)
  - Live map with alert markers
  - Real-time notification via `Socket.IO` client
**Tech Stack**:
  - React.js, Axios, Socket.IO-client, Leaflet.js, Bootstrap
  - Token-based session persistence
**Security**:
  - HTTPS-ready
  - JWT token verification on each route
  - Password hashing using bcrypt

# Security Model
**Authentication**: Stateless with `JWT`
**Data Protection**:
  - Encrypted storage for passwords
  - API access control via decorators
**Authorization**:
  - Dispatcher vs. Patient scoped access
  - Patient alerts cannot be viewed by other patients

# Test Strategy
**Mobile**: Manual test cases + simulator fall scenarios
**Backend**:
  - Unit tests on endpoint response + auth flow
  - DB model migration tests (Alembic)
**Web**:
  - Mock API tests
  - Socket message listener verification

# How the Alert System Works
-The mobile app detects a potential fall.
-It sends an alert to the backend via a secured POST request.
-The backend stores the event in the database.
-A WebSocket notification is instantly sent to the web dashboard.
-The dispatcher is notified in real-time and can respond accordingly.

## Author

**Iacinschi Anda-Roxana**  
Bachelor of Engineering – Computer Systems  
Faculty of Automation and Computer Science, TUIASI  
Email: [anda.roxana.iacinschi@gmail.com] • LinkedIn: [https://www.linkedin.com/in/anda-roxana-iacinschi-2ab6b426a/]
