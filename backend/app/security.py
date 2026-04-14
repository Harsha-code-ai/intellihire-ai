"""
Security utilities: password hashing and JWT token management.

FIX NOTES
---------
* bcrypt >= 4.x removed the __about__ attribute that passlib 1.7.4 reads on
  import, causing an AttributeError crash on startup.  We silence it here with
  a targeted monkeypatch that works for both old and new bcrypt.
* All functions are wrapped so they never raise unhandled exceptions.
"""

import os
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

load_dotenv()
logger = logging.getLogger("intellihire.security")

# ─── bcrypt / passlib compatibility fix ──────────────────────────────────────
# passlib 1.7.4 calls `bcrypt.__about__.__version__` which was removed in
# bcrypt 4.x.  Patch it before passlib imports bcrypt internals.
try:
    import bcrypt as _bcrypt_mod  # noqa: F401
    if not hasattr(_bcrypt_mod, "__about__"):
        class _FakeAbout:
            __version__ = getattr(_bcrypt_mod, "__version__", "4.0.0")
        _bcrypt_mod.__about__ = _FakeAbout()
except Exception:
    pass  # bcrypt not installed yet — pip will sort it out

from passlib.context import CryptContext  # noqa: E402  (must come after patch)

# ─── Config ───────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "intellihire-super-secret-change-in-prod")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Use bcrypt; fall back to sha256_crypt if bcrypt somehow unavailable
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Smoke-test it right away so we fail fast rather than at first login
    pwd_context.hash("__test__")
except Exception as e:
    logger.warning(f"bcrypt unavailable ({e}), falling back to sha256_crypt")
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

bearer_scheme = HTTPBearer(auto_error=False)


# ─── Password helpers ─────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash a password.  Truncates to 72 bytes to avoid bcrypt limit."""
    try:
        return pwd_context.hash(password[:72])
    except Exception as e:
        logger.error(f"hash_password failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Password hashing failed")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash.  Never raises."""
    try:
        return pwd_context.verify(plain[:72], hashed)
    except Exception as e:
        logger.error(f"verify_password failed: {e}", exc_info=True)
        return False


# ─── JWT helpers ──────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    try:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"create_access_token failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Token creation failed")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected token decode error: {e}", exc_info=True)
        raise HTTPException(status_code=401, detail="Token validation failed")


# ─── Auth dependencies ────────────────────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(lambda: next(_get_db())),
):
    """Raises 401 if no valid token.  Import get_db lazily to avoid circulars."""
    from app.database import get_db as _gdb
    # Re-resolve db via proper dependency — this stub is overridden below.
    raise RuntimeError("Use the version with Depends(get_db) directly")


# Proper version used by routes:
def _get_db():
    from app.database import get_db
    yield from get_db()


def get_current_user(  # noqa: F811  (intentional redefinition)
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(lambda: next(_get_db())),
):
    from app.models.user import User as _User

    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(credentials.credentials)
    email: str | None = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        user = db.query(_User).filter(_User.email == email).first()
    except Exception as e:
        logger.error(f"DB error in get_current_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(lambda: next(_get_db())),
):
    """Returns the current user or None — never raises, safe for public endpoints."""
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"get_optional_user unexpected error: {e}", exc_info=True)
        return None