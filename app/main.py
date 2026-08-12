from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth
from app.routers import posts
from app.utils import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.types import ExceptionHandler
from typing import cast
Base.metadata.create_all(bind=engine)  # creates tables if they don't exist

app = FastAPI(title="Blog API")
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, cast(ExceptionHandler,_rate_limit_exceeded_handler))

app.include_router(auth.router)
app.include_router(posts.router)

@app.get("/")
def read_root():
    return {"message: Blog Api is working"}

