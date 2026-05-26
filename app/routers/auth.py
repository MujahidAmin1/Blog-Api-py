from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginDto
from app.utils.dependencies import get_current_user
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201, response_model=UserResponse)
def register(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()

    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(username=body.username, email=body.email, password=hash_password(body.password))

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login")
def login(body: LoginDto, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, str(user.password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": (user.email, user.password)}

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