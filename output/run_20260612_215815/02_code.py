```python
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todo_items = db.relationship('ToDoItem', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class ToDoItem(db.Model):
    """To-Do item model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ToDoItem('{self.title}', '{self.description}', '{self.due_date}')"


@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'Username already exists'}), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'error': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200


@app.route('/todo', methods=['POST'])
@jwt_required
def create_todo():
    """Create a new to-do item."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    if not title or not description or not due_date:
        return jsonify({'error': 'Title, description, and due date are required'}), 400
    user_id = User.query.filter_by(username=get_jwt_identity()).first().id
    new_todo = ToDoItem(title=title, description=description, due_date=due_date, user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'To-do item created successfully'}), 201


@app.route('/todo', methods=['GET'])
@jwt_required
def get_todos():
    """Get all to-do items for a user."""
    user_id = User.query.filter_by(username=get_jwt_identity()).first().id
    todos = ToDoItem.query.filter_by(user_id=user_id).all()
    output = []
    for todo in todos:
        todo_data = {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'due_date': todo.due_date
        }
        output.append(todo_data)
    return jsonify({'todos': output}), 200


@app.route('/todo/<id>', methods=['GET'])
@jwt_required
def get_todo(id):
    """Get a to-do item by ID."""
    user_id = User.query.filter_by(username=get_jwt_identity()).first().id
    todo = ToDoItem.query.filter_by(id=id, user_id=user_id).first()
    if not todo:
        return jsonify({'error': 'To-do item not found'}), 404
    todo_data = {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'due_date': todo.due_date
    }
    return jsonify({'todo': todo_data}), 200


@app.route('/todo/<id>', methods=['PUT'])
@jwt_required
def update_todo(id):
    """Update a to-do item."""
    user_id = User.query.filter_by(username=get_jwt_identity()).first().id
    todo = ToDoItem.query.filter_by(id=id, user_id=user_id).first()
    if not todo:
        return jsonify({'error': 'To-do item not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    if title:
        todo.title = title
    if description:
        todo.description = description
    if due_date:
        todo.due_date = due_date
    db.session.commit()
    return jsonify({'message': 'To-do item updated successfully'}), 200


@app.route('/todo/<id>', methods=['DELETE'])
@jwt_required
def delete_todo(id):
    """Delete a to-do item."""
    user_id = User.query.filter_by(username=get_jwt_identity()).first().id
    todo = ToDoItem.query.filter_by(id=id, user_id=user_id).first()
    if not todo:
        return jsonify({'error': 'To-do item not found'}), 404
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'To-do item deleted successfully'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```