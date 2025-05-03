🚀 Hospital Backend API for course SWE 455

This is the Django backend API for the Hospital application. We are using Docker for containerization and Test-Driven Development (TDD).
This project is part of the course SWE 455 focusing on implimenting DevOps practices in software development.

---

📱 Features

    🗓️ Appointment Management: Book, view, and cancel appointments with medical professionals.
    🚨 SOS Requests: Instantly request emergency medical assistance.
    👤 Personal Information: View and manage your medical profile and personal data.
    🧾 Medical Records: Access your medical history, lab results, and diagnoses.
    👨‍👩‍👧 Family Members: Add and manage dependent family members' medical data.
    💬 Online Consultation: Chat with medical doctor for remote consultations.

---

🛠️ Tech Stack

    Python
    Django
    Django REST Framework
    PostgreSQL
    Redis for task queue (& chat system)
    Django Channels for WebSocket support
    Celery for background tasks
    Celery Beat for periodic tasks
    Docker
    Docker Compose
    GitHub Actions for CI/CD
    Flake8 for code linting
    Isort for import sorting
    CodeQL for security analysis
    betterstack for monitoring and logging dachboard
    The application server is Caddy for providing SSL and reverse proxying
    The server is hosted on droplet on Digital Ocean

---

## System Architecture

The Hospital Backend API is designed with a modular architecture to ensure scalability, maintainability, and ease of deployment. Below is an overview of the system's architecture:

### 1. **Core Components**

- **Django Framework**: The backend is built using Django, leveraging its ORM, authentication, and admin capabilities.
- **Django REST Framework (DRF)**: Used for building RESTful APIs for client communication.
- **PostgreSQL**: A robust relational database for storing structured data such as user profiles, appointments, and schedules.
- **Redis**: Used as a message broker for Celery tasks and as a backend for Django Channels to support WebSocket communication.

### 2. **Microservices**

- **Appointment Management**: Handles booking, rescheduling, and canceling appointments.
- **Chat System**: Enables real-time communication between doctors and patients for online consultations using Django Channels and WebSockets.
- **Delivery Service**: Manages prescription deliveries to patients.
- **Dependent Management**: Allows users to manage medical data for their dependents.
- **Medical Records**: Provides access to patient medical history, lab results, and diagnoses.

### 3. **Task Management**

- **Celery**: Used for asynchronous task processing, such as sending email notifications and managing background jobs.
- **Celery Beat**: Schedules periodic tasks, such as purging old chat sessions or sending reminders.

### 4. **Authentication and Security**

- **JWT Authentication**: Secures API endpoints using JSON Web Tokens.
- **Role-Based Access Control**: Differentiates access levels for patients, doctors, and admins.
- **Caddy Server**: Provides SSL termination and reverse proxying for secure communication.

### 5. **DevOps and Deployment**

- **Docker**: Containerizes the application for consistent deployment across environments.
- **Docker Compose**: Orchestrates multi-container setups for the application, database, Redis, and Celery.
- **GitHub Actions**: Implements CI/CD pipelines for automated testing and deployment.
- **DigitalOcean Droplet**: Hosts the application server with Caddy for SSL and reverse proxying.

### 6. **Monitoring and Logging**

- **BetterStack**: Provides monitoring and logging dashboards for system health and error tracking.

### 7. **Communication Protocols**

- **REST API**: Exposes endpoints for client applications to interact with the backend.
- **WebSocket**: Supports real-time communication for chat sessions.

### 8. **Directory Structure**

- **`app/`**: Contains the core Django application code.
  - **`appointment/`**: Manages appointment-related logic.
  - **`chat/`**: Handles chat sessions and messages.
  - **`delivery/`**: Manages delivery requests.
  - **`profiles/`**: Stores user profile models for doctors and patients.
  - **`schedules/`**: Manages doctor schedules and availability.
  - **`user/`**: Handles user authentication and management.
- **`docker/`**: Contains Docker-related configuration files.
- **`tests/`**: Includes unit and integration tests for the application.

![Mermaid SVG](https://www.mermaidchart.com/raw/f90048d5-b5ca-433a-93c1-7597ed63e548?theme=light&version=v0.1&format=svg)

This architecture ensures a clean separation of concerns, making the system easy to extend and maintain.

---

🎬 Start the Application (run commands)

⭐️ `docker compose build`

🔹 When to use it:

✅ Run it when you change the Dockerfile or dependencies (e.g., requirements.txt).

✅ Before starting the project for the first time.

⭐️ `docker compose up`

🔹 When to use it:

✅ Run it every time you want to start the application.

⭐️ `docker compose down`

🔹 When to use it:

✅ When you want to fully stop and remove the containers.

✅ If you need a fresh restart of the project.

---

👀 Development Approach: TDD

We are following Test-Driven Development (TDD).

🧪 Test command:

`docker-compose run --rm app sh -c "python manage.py test"` # run all tests

For running Linting and formatting checks, use:

`docker-compose run --rm app sh -c "flake8 . && isort . && black ."` # run all checks

---
