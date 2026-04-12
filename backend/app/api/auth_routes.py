"""
Authentication routes: register, login, profile.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.user import User
from app.schemas.schemas import UserCreate, UserLogin, UserOut, TokenOut
from app.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


# ✅ REGISTER
@router.post("/register", response_model=dict, summary="Register a new user")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 🔍 Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 🔐 Hash password safely
        hashed_password = hash_password(user.password)

        # 👤 Create new user
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            is_admin=False,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


# ✅ LOGIN
@router.post("/login", response_model=TokenOut, summary="Login and receive JWT token")
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()

        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"sub": db_user.email})

        return TokenOut(
            access_token=token,
            token_type="bearer",
            user=UserOut.from_orm(db_user),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# ✅ GET CURRENT USER
@router.get("/me", response_model=UserOut, summary="Get current user profile")
def me(current_user: User = Depends(get_current_user)):
    return current_user