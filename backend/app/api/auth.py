from datetime import datetime
import secrets
import string
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    LoginRateLimiter,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.access_request import AccessRequest
from app.models.company import Company
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
rate_limiter = LoginRateLimiter(
    max_attempts=settings.LOGIN_RATE_LIMIT_MAX,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RequestAccessRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    requester_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=50)
    message: Optional[str] = Field(default=None, max_length=2000)


class ApproveRequest(BaseModel):
    request_id: int
    role: Optional[str] = "client"


class SetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == email).one_or_none()
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def _generate_temp_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    limiter_key = f"{client_ip}:{payload.email.lower()}"
    if not rate_limiter.is_allowed(limiter_key, time.time()):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts")

    user = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()

    token = create_access_token(
        subject=user.email,
        extra={"uid": user.id, "role": user.role, "company_id": user.company_id},
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "company_id": user.company_id,
        },
    }


@router.post("/request-access")
def request_access(payload: RequestAccessRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    existing = (
        db.query(AccessRequest)
        .filter(AccessRequest.email == email, AccessRequest.status == "pending")
        .one_or_none()
    )
    if existing:
        return {"status": "pending", "request_id": existing.id}

    access_request = AccessRequest(
        company_name=payload.company_name,
        requester_name=payload.requester_name.strip(),
        email=email,
        phone=payload.phone,
        message=payload.message,
        status="pending",
    )
    db.add(access_request)
    db.commit()
    db.refresh(access_request)
    return {"status": "pending", "request_id": access_request.id}


@router.post("/admin/approve-request")
def approve_request(
    payload: ApproveRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    access_request = db.query(AccessRequest).filter(AccessRequest.id == payload.request_id).one_or_none()
    if not access_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if access_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request already handled")

    if payload.role and payload.role != "client":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    company = db.query(Company).filter(Company.name == access_request.company_name).one_or_none()
    if not company:
        company = Company(name=access_request.company_name)
        db.add(company)
        db.flush()

    temp_password = _generate_temp_password(16)
    user = User(
        company=company,
        email=access_request.email.lower(),
        name=access_request.requester_name,
        password_hash=get_password_hash(temp_password),
        role="client",
        status="active",
        must_change_password=True,
    )

    access_request.status = "approved"
    access_request.handled_at = datetime.utcnow()
    access_request.handled_by = current_user.id

    db.add(user)
    db.add(access_request)
    db.commit()
    db.refresh(user)
    return {
        "status": "approved",
        "temp_password": temp_password,
        "user_email": user.email,
        "user_id": user.id,
        "company_id": company.id,
    }


@router.post("/set-password")
def set_password(
    payload: SetPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.must_change_password = False
    db.add(current_user)
    db.commit()
    return {"status": "ok"}
