
from fastapi import Depends, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from models import Todo, TodoUpdate
import database_models
from database import SessionLocal, engine



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return {"message": "welcome to this page"}

todos_seed = [
    {"id": 1, "title": "Finish FastAPI project", "description": "Complete CRUD endpoints", "completed": False},
    {"id": 2, "title": "Write README", "description": None, "completed": False},
]

def init_db():
    db = SessionLocal()
    count = db.query(database_models.Todo).count()
    if count == 0:
        for todo in todos_seed:
            db.add(database_models.Todo(**todo))
        db.commit()
    db.close()

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/todos", response_model=list[Todo])
def get_all_todos(db: Session = Depends(get_db)):
    return db.query(database_models.Todo).all()


@app.get("/todos/{id}", response_model=Todo)
def get_todos_by_id(id: int, db: Session = Depends(get_db)):
    db_todo = db.query(database_models.Todo).filter(database_models.Todo.id == id).first()
    if db_todo:
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo list not found")


@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo, db: Session = Depends(get_db)):
    existing = db.query(database_models.Todo).filter(database_models.Todo.id == todo.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="A todo with this ID already exists")

    db_todo = database_models.Todo(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{id}", response_model=Todo)
def update_todo(id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(database_models.Todo).filter(database_models.Todo.id == id).first()

    if db_todo:
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.completed = todo.completed

        db.commit()
        db.refresh(db_todo)
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@app.delete("/todos/{id}")
def delete_todo(id: int, db: Session = Depends(get_db)):
    db_todo = db.query(database_models.Todo).filter(database_models.Todo.id == id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return "todo deleted"
    else:
        raise HTTPException(status_code=404, detail="todo not found")