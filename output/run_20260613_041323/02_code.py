```python
# Import necessary libraries
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_cors import CORS
import datetime

# Create a Flask application instance
app = Flask(__name__)

# Configure the application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['CORS_HEADERS'] = 'Content-Type'

# Initialize the database, Marshmallow, Bcrypt, and JWTManager
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
cors = CORS(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, description, due_date, user_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.user_id = user_id

# Define the Reminder model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    reminder_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, task_id, reminder_date):
        self.task_id = task_id
        self.reminder_date = reminder_date

# Define the UserSchema for marshalling and unmarshalling
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

# Define the TaskSchema for marshalling and unmarshalling
class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task

# Define the ReminderSchema for marshalling and unmarshalling
class ReminderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reminder

# Create the UserSchema instance
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Create the TaskSchema instance
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Create the ReminderSchema instance
reminder_schema = ReminderSchema()
reminders_schema = ReminderSchema(many=True)

# Define the route for user registration
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Define the route for user login
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# Define the route for task creation
@app.route('/tasks', methods=['POST'])
@jwt_required
def create_task():
    title = request.json['title']
    description = request.json['description']
    due_date = datetime.datetime.strptime(request.json['due_date'], '%Y-%m-%d').date()
    user_id = get_jwt_identity()
    new_task = Task(title, description, due_date, user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201

# Define the route for task retrieval
@app.route('/tasks', methods=['GET'])
@jwt_required
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify(tasks_schema.dump(tasks)), 200

# Define the route for task update
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    task.title = request.json['title']
    task.description = request.json['description']
    task.due_date = datetime.datetime.strptime(request.json['due_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200

# Define the route for task deletion
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

# Define the route for reminder creation
@app.route('/reminders', methods=['POST'])
@jwt_required
def create_reminder():
    task_id = request.json['task_id']
    reminder_date = datetime.datetime.strptime(request.json['reminder_date'], '%Y-%m-%d').date()
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    new_reminder = Reminder(task_id, reminder_date)
    db.session.add(new_reminder)
    db.session.commit()
    return jsonify({'message': 'Reminder created successfully'}), 201

# Define the route for reminder retrieval
@app.route('/reminders', methods=['GET'])
@jwt_required
def get_reminders():
    user_id = get_jwt_identity()
    reminders = Reminder.query.join(Task).filter_by(user_id=user_id).all()
    return jsonify(reminders_schema.dump(reminders)), 200

# Define the entry point
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
```

Note: This code is a simplified version of the Todo App and does not include all the features mentioned in the development plan. It is intended to demonstrate the basic structure and functionality of the application.