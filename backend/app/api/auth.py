from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database import get_db
from ...crud import create_user, get_user_by_email
from ...models import UserCreate
from ...auth import verify_password, create_access_token, get_current_user
import os

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(form_data: dict, db: Session = Depends(get_db)):  # Use form or body
    email = form_data.get("email")
    password = form_data.get("password")
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

@router.post("/register")
def register(user: UserCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admin only
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return create_user(db, user)

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
