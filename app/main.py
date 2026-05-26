from fastapi import FastAPI, HTTPException
from app.database import engine, Base
from app.models import post  # noqa: F401 — must import so Base sees the models
from app.routers import auth
from app.routers import posts

Base.metadata.create_all(bind=engine)  # creates tables if they don't exist

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/")
def read_root():
    return {"message: Blog Api is working"}

