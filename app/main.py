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
    result = [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]
    session.close()
    return jsonify({"tasks": result})


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    session = Session()
    task = Task(title=data['title'], user_id=current_user.id)
    session.add(task)
    session.commit()
    result = {"id": task.id, "title": task.title, "completed": task.completed}
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
    result = {"id": task.id, "title": task.title, "completed": task.completed}
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