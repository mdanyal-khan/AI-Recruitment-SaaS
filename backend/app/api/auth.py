from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user

from app.core.database import get_db

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password
)

from app.models.user import User

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse
)


from app.core.rate_limiter import rate_limit, auth_limiter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# REGISTER
# =========================

@router.post(
    "/register",
    response_model=UserResponse,
    dependencies=[Depends(rate_limit(requests_per_window=10, window_seconds=60, limiter=auth_limiter))]
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    normalized_email = data.email.strip().lower()

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user_role = data.role.upper()
    if user_role in ("RECRUITER", "OWNER"):
        user_role = "HR"

    # Create user
    user = User(
        email=normalized_email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        role=user_role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# =========================
# LOGIN
# =========================

@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit(requests_per_window=15, window_seconds=60, limiter=auth_limiter))]
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    normalized_email = data.email.strip().lower()

    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )

    # User doesn't exist
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check password
    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check account status
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    # Create JWT
    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# GET CURRENT USER
# =========================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user