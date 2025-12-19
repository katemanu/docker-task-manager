import os
from flask import Flask, jsonify, request, render_template
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Task model
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(engine)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    session = Session()
    tasks = session.query(Task).all()
    result = [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]
    session.close()
    return jsonify({"tasks": result})

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    session = Session()
    task = Task(title=data['title'])
    session.add(task)
    session.commit()
    result = {"id": task.id, "title": task.title, "completed": task.completed}
    session.close()
    
    return jsonify({"task": result}), 201

@app.route('/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    session = Session()
    task = session.query(Task).filter_by(id=task_id).first()
    if not task:
        session.close()
        return jsonify({"error": "Task not found"}), 404
    
    task.completed = not task.completed
    session.commit()
    result = {"id": task.id, "title": task.title, "completed": task.completed}
    session.close()
    return jsonify({"task": result})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    session = Session()
    task = session.query(Task).filter_by(id=task_id).first()
    if task:
        session.delete(task)
        session.commit()
    session.close()
    return jsonify({"message": "Task deleted"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
