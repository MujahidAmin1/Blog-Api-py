from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginDto
from app.utils.dependencies import get_current_user
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()

    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(username=body.username, email=body.email, password=hash_password(body.password))

    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})

    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": str(user.email)}
    }
# ccc
@router.post("/login")
def login(body: LoginDto, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, str(user.password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})

    # save refresh token to DB
    user.refresh_token = refresh_token
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }

@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        payload = verify_refresh_token(body.refresh_token)
    except ValueError:
        raise credentials_exception

    user_id = payload.get("user_id")

    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    # verify it matches what's stored and hasn't been cleared by logout
    if not user or str(user.refresh_token) != body.refresh_token:
        raise credentials_exception

    access_token = create_access_token({"user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=204)
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.refresh_token = None
    db.commit()


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
    "user": {"id": user.id, "username": user.username, "email": user.email}}
    
    
@router.get("/get_user_by_id/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user