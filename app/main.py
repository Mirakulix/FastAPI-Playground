from fastapi import FastAPI, Depends
from .database import SessionLocal, engine, Base
from .models import CourseMatch

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()