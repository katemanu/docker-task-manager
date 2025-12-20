# Task Manager

A production-ready task management application built with Flask, PostgreSQL, and Docker.

**Live Demo:** [https://katemcompanies.com](https://katemcompanies.com)

## Features

- **User Authentication** - Secure signup/login with password hashing
- **Task Management** - Create, complete, and delete tasks
- **Priorities** - High, medium, and low priority levels
- **Categories** - Personal, work, shopping, health, finance
- **Due Dates** - Set deadlines with overdue highlighting
- **Filters** - Filter tasks by category and priority

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Flask |
| Database | PostgreSQL |
| Authentication | Flask-Login, Werkzeug |
| Containerization | Docker, Docker Compose |
| Web Server | Nginx |
| SSL | Let's Encrypt (Certbot) |
| Cloud | AWS EC2, Route 53 |

## Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Flask     │────▶│ PostgreSQL  │
│  (HTTPS)    │     │   (App)     │     │    (DB)     │
└─────────────┘     └─────────────┘     └─────────────┘
     :443              :5000              :5432
```

## Project Structure
```
docker-task-manager/
├── app/
│   ├── main.py              # Flask application
│   ├── requirements.txt     # Python dependencies
│   └── templates/
│       ├── index.html       # Task manager UI
│       ├── login.html       # Login page
│       └── signup.html      # Signup page
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-container setup
└── README.md
```

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Run Locally
```bash
# Clone the repository
git clone https://github.com/katemanu/docker-task-manager.git
cd docker-task-manager

# Start the application
docker-compose up -d --build

# Access at http://localhost:5000
```

### Stop the Application
```bash
docker-compose down
```

### Reset Database
```bash
docker-compose down -v
docker-compose up -d --build
```

## Deployment

This application is deployed on AWS EC2 with:

- **Nginx** as reverse proxy
- **Let's Encrypt** for SSL certificates
- **Route 53** for DNS management
- **Docker Compose** for container orchestration

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/login` | Login page |
| GET | `/signup` | Signup page |
| POST | `/api/signup` | Create account |
| POST | `/api/login` | Authenticate user |
| POST | `/api/logout` | End session |
| GET | `/tasks` | List user tasks |
| POST | `/tasks` | Create new task |
| PUT | `/tasks/:id/toggle` | Toggle completion |
| PUT | `/tasks/:id` | Update task |
| DELETE | `/tasks/:id` | Delete task |

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- HTTPS encryption
- User-scoped data isolation

## Author

**Kate Manu**

- GitHub: [@katemanu](https://github.com/katemanu)
- Website: [katemcompanies.com](https://katemcompanies.com)

## License

This project is open source and available under the MIT License.
