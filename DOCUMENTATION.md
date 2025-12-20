# Task Manager - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Phase 1: Flask + PostgreSQL + Docker Compose](#phase-1-flask--postgresql--docker-compose)
4. [Phase 2: User Authentication](#phase-2-user-authentication)
5. [Phase 3: Features (Priority, Category, Due Dates)](#phase-3-features)
6. [Phase 4: Custom Domain + HTTPS](#phase-4-custom-domain--https)
7. [File Structure](#file-structure)
8. [Complete Code Reference](#complete-code-reference)
9. [Commands Reference](#commands-reference)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

A production-ready task management application demonstrating:

- Containerization with Docker
- Multi-container orchestration with Docker Compose
- Database management with PostgreSQL
- User authentication with Flask-Login
- Reverse proxy with Nginx
- SSL/HTTPS with Let's Encrypt
- Cloud deployment on AWS EC2
- DNS management with Route 53

**Live URL:** https://katemcompanies.com
**Repository:** https://github.com/katemanu17/docker-task-manager

---

## Architecture
```
                    ┌──────────────────────────────────────────┐
                    │              AWS Cloud                    │
                    │                                          │
┌─────────┐        │  ┌─────────┐    ┌─────────┐    ┌───────┐ │
│  User   │───────▶│  │  Nginx  │───▶│  Flask  │───▶│Postgre│ │
│ Browser │  HTTPS │  │ :80/:443│    │  :5000  │    │  SQL  │ │
└─────────┘        │  └─────────┘    └─────────┘    └───────┘ │
                    │       │              │              │     │
                    │       └──────────────┴──────────────┘     │
                    │              Docker Compose               │
                    │                                          │
                    │  Route 53: katemcompanies.com            │
                    └──────────────────────────────────────────┘
```

### Components

| Component | Purpose | Port |
|-----------|---------|------|
| Nginx | Reverse proxy, SSL termination | 80, 443 |
| Flask | Web application, API | 5000 |
| PostgreSQL | Database | 5432 |

### Data Flow

1. User visits https://katemcompanies.com
2. Route 53 resolves domain to EC2 IP (13.57.200.74)
3. Nginx receives request on port 443 (HTTPS)
4. Nginx forwards to Flask on port 5000
5. Flask queries PostgreSQL on port 5432
6. Response flows back through the chain

---

## Phase 1: Flask + PostgreSQL + Docker Compose

### What We Built

- Basic Flask API with task CRUD operations
- PostgreSQL database for persistent storage
- Docker Compose to run both containers together
- Volume for database persistence

### Key Concepts

**Docker Compose** - Tool for defining and running multi-container applications. Uses a YAML file to configure services.

**Volumes** - Persistent storage that survives container restarts. Without volumes, database data would be lost when containers stop.

**depends_on** - Ensures PostgreSQL starts before Flask.

**Environment Variables** - Pass configuration (database URL) to containers without hardcoding.

### docker-compose.yml Explained
```yaml
services:
  web:                                    # Flask application service
    build: .                              # Build from Dockerfile in current directory
    ports:
      - "5000:5000"                       # Map host:container ports
    environment:
      - DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb
    depends_on:
      - db                                # Start db before web
    restart: unless-stopped               # Auto-restart on failure

  db:                                     # PostgreSQL service
    image: postgres:15-alpine             # Use official PostgreSQL image
    environment:
      - POSTGRES_USER=taskuser            # Database username
      - POSTGRES_PASSWORD=taskpass        # Database password
      - POSTGRES_DB=taskdb                # Database name
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persist data
    restart: unless-stopped

volumes:
  postgres_data:                          # Named volume for database
```

### Dockerfile Explained
```dockerfile
FROM python:3.11-slim                     # Base image

WORKDIR /app                              # Set working directory

COPY app/requirements.txt .               # Copy dependencies first (caching)

RUN pip install -r requirements.txt       # Install dependencies

COPY app/ .                               # Copy application code

EXPOSE 5000                               # Document exposed port

CMD ["python", "main.py"]                 # Start command
```

---

## Phase 2: User Authentication

### What We Built

- User registration (signup)
- User login/logout
- Password hashing (never store plain text passwords)
- Session management
- Protected routes (tasks only visible when logged in)
- User-scoped data (each user sees only their tasks)

### Key Concepts

**Password Hashing** - Using Werkzeug's `generate_password_hash()` and `check_password_hash()`. Passwords are never stored in plain text.

**Flask-Login** - Handles user session management. Provides `@login_required` decorator and `current_user` object.

**Foreign Key** - Links tasks to users. Each task has a `user_id` column referencing the users table.

### Database Schema
```
┌─────────────────┐       ┌─────────────────┐
│     users       │       │     tasks       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │──────▶│ id (PK)         │
│ email           │       │ title           │
│ password_hash   │       │ completed       │
└─────────────────┘       │ user_id (FK)    │
                          │ priority        │
                          │ category        │
                          │ due_date        │
                          └─────────────────┘
```

### Authentication Flow
```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Signup  │───▶│  Hash    │───▶│  Store   │───▶│ Redirect │
│   Form   │    │ Password │    │   User   │    │ to Login │
└──────────┘    └──────────┘    └──────────┘    └──────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Login   │───▶│  Verify  │───▶│  Create  │───▶│ Redirect │
│   Form   │    │ Password │    │ Session  │    │ to Tasks │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

---

## Phase 3: Features

### What We Built

- Task priorities (low, medium, high)
- Task categories (personal, work, shopping, health, finance)
- Due dates with date picker
- Overdue highlighting
- Client-side filtering

### Database Changes

Added three new columns to the tasks table:
```python
priority = Column(String(20), default='medium')
category = Column(String(50), default='personal')
due_date = Column(String(20), nullable=True)
```

### API Changes

Updated endpoints to handle new fields:
```python
# Creating a task
task = Task(
    title=data['title'],
    user_id=current_user.id,
    priority=data.get('priority', 'medium'),
    category=data.get('category', 'personal'),
    due_date=data.get('due_date')
)

# Returning task data
result = {
    "id": task.id,
    "title": task.title,
    "completed": task.completed,
    "priority": task.priority,
    "category": task.category,
    "due_date": task.due_date
}
```

### Frontend Filtering

Filtering happens client-side in JavaScript:
```javascript
let tasks = data.tasks;
if (filterCategory) {
    tasks = tasks.filter(t => t.category === filterCategory);
}
if (filterPriority) {
    tasks = tasks.filter(t => t.priority === filterPriority);
}
```

---

## Phase 4: Custom Domain + HTTPS

### What We Built

- DNS configuration with Route 53
- Nginx as reverse proxy
- SSL certificate with Let's Encrypt
- Automatic HTTP to HTTPS redirect

### DNS Setup (Route 53)

Created two A records:

| Record Name | Type | Value |
|-------------|------|-------|
| katemcompanies.com | A | 13.57.200.74 |
| www.katemcompanies.com | A | 13.57.200.74 |

### Nginx Configuration

**Purpose of Nginx:**
1. Terminates SSL (handles HTTPS)
2. Forwards requests to Flask
3. Serves static files efficiently
4. Adds security headers

**Configuration file:** `/etc/nginx/conf.d/taskmanager.conf`
```nginx
server {
    listen 80;
    server_name katemcompanies.com www.katemcompanies.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL with Certbot

Certbot automates Let's Encrypt certificate installation:
```bash
sudo certbot --nginx -d katemcompanies.com -d www.katemcompanies.com
```

This command:
1. Obtains SSL certificate from Let's Encrypt
2. Modifies Nginx config to use HTTPS
3. Sets up auto-renewal

### Request Flow with HTTPS
```
┌────────┐  HTTPS   ┌───────┐  HTTP    ┌───────┐
│ Browser│─────────▶│ Nginx │─────────▶│ Flask │
│        │  :443    │       │  :5000   │       │
└────────┘          └───────┘          └───────┘
                        │
                        ▼
                  SSL Termination
                  (Decrypt HTTPS)
```

---

## File Structure
```
docker-task-manager/
├── app/
│   ├── main.py                 # Flask application (routes, models, auth)
│   ├── requirements.txt        # Python dependencies
│   └── templates/
│       ├── index.html          # Task manager UI (logged in users)
│       ├── login.html          # Login page
│       └── signup.html         # Registration page
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Multi-container configuration
├── README.md                   # Project overview
└── DOCUMENTATION.md            # This file
```

---

## Complete Code Reference

### app/main.py
```python
import os
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


# User model
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    tasks = relationship('Task', backref='owner', lazy=True)


# Task model
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    priority = Column(String(20), default='medium')
    category = Column(String(50), default='personal')
    due_date = Column(String(20), nullable=True)


# Create tables
Base.metadata.create_all(engine)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(int(user_id))
    session.close()
    return user


@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    session = Session()
    
    if session.query(User).filter_by(email=data['email']).first():
        session.close()
        return jsonify({"error": "Email already registered"}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    session.add(user)
    session.commit()
    session.close()
    
    return jsonify({"message": "Account created successfully"}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    session = Session()
    user = session.query(User).filter_by(email=data['email']).first()
    session.close()
    
    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({"message": "Login successful"}), 200
    
    return jsonify({"error": "Invalid email or password"}), 401


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    session = Session()
    tasks = session.query(Task).filter_by(user_id=current_user.id).all()
    result = [{
        "id": t.id,
        "title": t.title,
        "completed": t.completed,
        "priority": t.priority,
        "category": t.category,
        "due_date": t.due_date
    } for t in tasks]
    session.close()
    return jsonify({"tasks": result})


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    session = Session()
    task = Task(
        title=data['title'],
        user_id=current_user.id,
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'personal'),
        due_date=data.get('due_date')
    )
    session.add(task)
    session.commit()
    result = {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "priority": task.priority,
        "category": task.category,
        "due_date": task.due_date
    }
    session.close()
    
    return jsonify({"task": result}), 201


@app.route('/tasks/<int:task_id>/toggle', methods=['PUT'])
@login_required
def toggle_task(task_id):
    session = Session()
    task = session.query(Task).filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        session.close()
        return jsonify({"error": "Task not found"}), 404
    
    task.completed = not task.completed
    session.commit()
    result = {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "priority": task.priority,
        "category": task.category,
        "due_date": task.due_date
    }
    session.close()
    return jsonify({"task": result})


@app.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    data = request.get_json()
    session = Session()
    task = session.query(Task).filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        session.close()
        return jsonify({"error": "Task not found"}), 404
    
    if 'title' in data:
        task.title = data['title']
    if 'priority' in data:
        task.priority = data['priority']
    if 'category' in data:
        task.category = data['category']
    if 'due_date' in data:
        task.due_date = data['due_date']
    
    session.commit()
    result = {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "priority": task.priority,
        "category": task.category,
        "due_date": task.due_date
    }
    session.close()
    return jsonify({"task": result})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    session = Session()
    task = session.query(Task).filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        session.delete(task)
        session.commit()
    session.close()
    return jsonify({"message": "Task deleted"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### app/requirements.txt
```
flask==3.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
flask-login==0.6.3
werkzeug==3.0.1
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://taskuser:taskpass@db:5432/taskdb
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=taskuser
      - POSTGRES_PASSWORD=taskpass
      - POSTGRES_DB=taskdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## Commands Reference

### Docker Commands
```bash
# Build and start containers
docker-compose up -d --build

# Stop containers
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# View running containers
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs web --tail 50

# Execute command in container
docker exec -it docker-task-manager-web-1 bash

# List all images
docker images

# Remove unused images
docker image prune
```

### Nginx Commands
```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# Enable on boot
sudo systemctl enable nginx

# Test configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Certbot Commands
```bash
# Get SSL certificate
sudo certbot --nginx -d katemcompanies.com -d www.katemcompanies.com

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# List certificates
sudo certbot certificates
```

### Git Commands
```bash
# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push origin main

# View history
git log --oneline
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Common issues:
# - Port already in use: stop other services on port 5000
# - Database connection: ensure db container is running
# - File not found: check file paths in Dockerfile
```

### Database errors
```bash
# Reset database completely
docker-compose down -v
docker-compose up -d --build

# Connect to database
docker exec -it docker-task-manager-db-1 psql -U taskuser -d taskdb

# View tables
\dt

# View users
SELECT * FROM users;

# View tasks
SELECT * FROM tasks;
```

### Nginx not forwarding
```bash
# Check config syntax
sudo nginx -t

# Check if default server block exists
cat /etc/nginx/nginx.conf

# Ensure no default.conf
ls /etc/nginx/conf.d/

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

### SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check port 443 is open in AWS Security Group
```

### VS Code saving files in wrong location
```bash
# Find file
find /home/ec2-user -name "filename.py"

# Move to correct location
mv /home/ec2-user/filename.py /home/ec2-user/docker-task-manager/app/
```

---

## Interview Discussion Points

### Docker Questions

**Q: Why use Docker?**
A: Consistency across environments. The app runs the same way on my laptop, EC2, or any server. Dependencies are packaged with the app.

**Q: What's the difference between Docker and Docker Compose?**
A: Docker runs single containers. Docker Compose orchestrates multiple containers that work together (Flask + PostgreSQL).

**Q: How do you persist data in Docker?**
A: Using volumes. Without volumes, data is lost when containers stop. I used a named volume for PostgreSQL data.

### Architecture Questions

**Q: Why use Nginx?**
A: SSL termination, reverse proxy, better performance for static files, and production-grade request handling.

**Q: How does the request flow work?**
A: Browser → Nginx (HTTPS/443) → Flask (HTTP/5000) → PostgreSQL (5432)

**Q: Why not expose Flask directly?**
A: Flask's development server isn't production-ready. Nginx handles SSL, load balancing, and serves static files efficiently.

### Security Questions

**Q: How do you handle passwords?**
A: Passwords are hashed using Werkzeug's security functions. Plain text passwords are never stored.

**Q: How do you prevent users from seeing other users' tasks?**
A: Every task query includes `user_id=current_user.id`. Users can only access their own data.

**Q: How did you implement HTTPS?**
A: Let's Encrypt with Certbot. It's free, automated, and trusted by all browsers.

---

## Next Steps (Future Improvements)

1. **Production WSGI Server** - Replace `python main.py` with Gunicorn
2. **Email Reminders** - SendGrid or AWS SES for due date notifications
3. **Password Reset** - Email-based password recovery
4. **Task Sharing** - Share tasks between users
5. **Mobile App** - React Native or Flutter frontend
6. **CI/CD Pipeline** - GitHub Actions for automated deployment
7. **Monitoring** - Add logging and health monitoring
8. **Backup Strategy** - Automated database backups

---

*Documentation created: December 2025*
*Author: Kate Manu*
