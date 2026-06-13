**Bug Report**

1. **Issue:** In the `register()` function, the `password` field is not validated. An attacker can exploit this by sending a large password, causing the database to store a hashed password that is too long for the `password` column.

**Code Section:**
```python
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
```

**Fix:**
```python
def register():
    username = request.json['username']
    password = request.json['password']
    if len(password) > 100:  # Check if password is too long
        return jsonify({'message': 'Password too long'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
```

2. **Issue:** In the `login()` function, the `password` field is not validated. An attacker can exploit this by sending a large password, causing the database to store a hashed password that is too long for the `password` column.

**Code Section:**
```python
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200
```

**Fix:**
```python
def login():
    username = request.json['username']
    password = request.json['password']
    if len(password) > 100:  # Check if password is too long
        return jsonify({'message': 'Password too long'}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200
```

3. **Issue:** In the `create_task()` function, the `due_date` field is not validated. An attacker can exploit this by sending a date that is in the past, causing the task to be created with an invalid due date.

**Code Section:**
```python
def create_task():
    title = request.json['title']
    description = request.json['description']
    due_date = datetime.datetime.strptime(request.json['due_date'], '%Y-%m-%d').date()
    user_id = get_jwt_identity()
    new_task = Task(title, description, due_date, user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201
```

**Fix:**
```python
def create_task():
    title = request.json['title']
    description = request.json['description']
    due_date = datetime.datetime.strptime(request.json['due_date'], '%Y-%m-%d').date()
    if due_date < datetime.date.today():  # Check if due date is in the past
        return jsonify({'message': 'Due date cannot be in the past'}), 400
    user_id = get_jwt_identity()
    new_task = Task(title, description, due_date, user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201
```

**Edge Cases**

1. **Empty inputs:** The `register()` function does not handle empty inputs. An attacker can exploit this by sending empty `username` or `password` fields.

**Code Section:**
```python
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
```

**Fix:**
```python
def register():
    username = request.json['username']
    password = request.json['password']
    if not username or not password:  # Check if inputs are empty
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
```

2. **Invalid data types:** The `create_task()` function does not handle invalid data types. An attacker can exploit this by sending a `due_date` field that is not a date.

**Code Section:**
```python
def create_task():
    title = request.json['title']
    description = request.json['description']
    due_date = datetime.datetime.strptime(request.json['due_date'], '%Y-%m-%d').date()
    user_id = get_jwt_identity()
    new_task = Task(title, description, due_date, user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201
```

**Fix:**
```python
def create_task():
    title = request.json['title']
    description = request.json['description']
    due_date = request.json['due_date']
    try:
        due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
    except ValueError:  # Handle invalid date format
        return jsonify({'message': 'Invalid date format'}), 400
    if due_date < datetime.date.today():  # Check if due date is in the past
        return jsonify({'message': 'Due date cannot be in the past'}), 400
    user_id = get_jwt_identity()
    new_task = Task(title, description, due_date, user_id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201
```

**Security Concerns**

1. **Input validation gaps:** The `register()` function does not validate the `username` field. An attacker can exploit this by sending a long `username` field.

**Code Section:**
```python
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
```

**Fix:**
```python
def register():
    username = request.json['username']
    password = request.json['password']
    if len(username) > 100:  # Check if username is too long
        return jsonify({'message': 'Username too long'}), 400
    if not username or not password:  # Check if inputs are empty
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
```

2. **SQL injection risks:** The `register()` function uses the `username` field directly in a SQL query. An attacker can exploit this by sending a malicious `username` field that contains SQL code.

**Code Section:**
```python
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
```

**Fix:**
```python
def register():
    username = request.json['username']
    password = request.json['password']
    if not username or not password:  # Check if inputs are empty
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Username already exists'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201
```

**Test Cases**

```python
import pytest
from your_app import app, db
from your_app.models import User, Task

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register(client):
    response = client.post('/register', json={'username': 'test