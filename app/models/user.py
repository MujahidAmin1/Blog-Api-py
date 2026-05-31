from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Optional
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False, server_default="Anonymous")
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True, default=None)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner", cascade="all, delete")