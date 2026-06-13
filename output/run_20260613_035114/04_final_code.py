```python
# Import necessary libraries
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from marshmallow import validate, Schema, fields
from flask import abort

# Create a new Flask app instance
app = Flask(__name__)

# Configure the app with database connection and JWT secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this to a random secret key

# Initialize the database, Marshmallow, and JWTManager
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    reminder = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, description, priority, due_date, reminder, user_id):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.reminder = reminder
        self.user_id = user_id

# Define the TaskSchema for marshalling and unmarshalling tasks
class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True

# Define the UserSchema for marshalling and unmarshalling users
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

# Define the RegisterSchema for marshalling and unmarshalling user registration data
class RegisterSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

# Define the LoginSchema for marshalling and unmarshalling user login data
class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

# Create the TaskSchema and UserSchema instances
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
register_schema = RegisterSchema()
login_schema = LoginSchema()

# Define the routes for user authentication
@app.route('/register', methods=['POST'])
def register():
    try:
        data = register_schema.load(request.get_json())
        user = User.query.filter_by(username=data['username']).first()
        if user:
            return jsonify({'message': 'Username already exists'}), 400
        new_user = User(data['username'], data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating user'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.get_json())
        user = User.query.filter_by(username=data['username']).first()
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'message': 'Error creating access token'}), 500

# Define the routes for task management
@app.route('/tasks', methods=['GET'])
@jwt_required
def get_tasks():
    try:
        tasks = Task.query.all()
        return jsonify(tasks_schema.dump(tasks))
    except Exception as e:
        return jsonify({'message': 'Error fetching tasks'}), 500

@app.route('/tasks', methods=['POST'])
@jwt_required
def create_task():
    try:
        data = request.get_json()
        new_task = Task(data['title'], data['description'], data['priority'], data['due_date'], data['reminder'], request.user_id)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating task'}), 500

@app.route('/tasks/<id>', methods=['GET'])
@jwt_required
def get_task(id):
    try:
        task = Task.query.get(id)
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        return jsonify(task_schema.dump(task))
    except Exception as e:
        return jsonify({'message': 'Error fetching task'}), 500

@app.route('/tasks/<id>', methods=['PUT'])
@jwt_required
def update_task(id):
    try:
        task = Task.query.get(id)
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        data = request.get_json()
        task.title = data['title']
        task.description = data['description']
        task.priority = data['priority']
        task.due_date = data['due_date']
        task.reminder = data['reminder']
        db.session.commit()
        return jsonify({'message': 'Task updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error updating task'}), 500

@app.route('/tasks/<id>', methods=['DELETE'])
@jwt_required
def delete_task(id):
    try:
        task = Task.query.get(id)
        if not task:
            return jsonify({'message': 'Task not found'}), 404
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error deleting task'}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
```