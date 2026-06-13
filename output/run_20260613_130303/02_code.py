```python
# Import necessary libraries
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///todo.db"

# Create a SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    tasks = relationship("Task", back_populates="user")

# Define the Task model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    due_date = Column(DateTime)
    priority = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")

# Define the User schema
class UserSchema(BaseModel):
    id: int
    name: str
    email: str

# Define the Task schema
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    due_date: datetime
    priority: int

# Define the UserCreate schema
class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str

# Define the TaskCreate schema
class TaskCreateSchema(BaseModel):
    title: str
    description: str
    due_date: datetime
    priority: int
    user_id: int

# Initialize the FastAPI application
app = FastAPI()

# Initialize the JWT authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize the password context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# Define the get_db function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the authenticate_user function
def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Define the create_access_token function
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret_key", algorithm="HS256")
    return encoded_jwt

# Define the get_current_user function
async def get_current_user(token: str = Depends(oauth2_scheme)):
    db = next(get_db())
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        user = db.query(User).get(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user

# Define the get_current_active_user function
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

# Define the token endpoint
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Define the user endpoint
@app.get("/users/{user_id}")
async def read_user(user_id: int, db: SessionLocal = Depends(get_db)):
    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Define the user create endpoint
@app.post("/users/")
async def create_user(user: UserCreateSchema, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Define the task endpoint
@app.get("/tasks/{task_id}")
async def read_task(task_id: int, db: SessionLocal = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Define the task create endpoint
@app.post("/tasks/")
async def create_task(task: TaskCreateSchema, db: SessionLocal = Depends(get_db)):
    db_task = db.query(Task).filter(Task.title == task.title).first()
    if db_task:
        raise HTTPException(status_code=400, detail="Task already exists")
    new_task = Task(title=task.title, description=task.description, due_date=task.due_date, priority=task.priority, user_id=task.user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Define the task update endpoint
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskCreateSchema, db: SessionLocal = Depends(get_db)):
    db_task = db.query(Task).get(task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    return db_task

# Define the task delete endpoint
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: SessionLocal = Depends(get_db)):
    db_task = db.query(Task).get(task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

# Define the main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```