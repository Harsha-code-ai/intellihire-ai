"""
IntelliHire Pro — Main FastAPI Application
Production-grade, crash-proof backend.
"""

import os
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
)
logger = logging.getLogger("intellihire")

app = FastAPI(
    title="IntelliHire Pro API",
    description="AI-powered hiring platform — resume analysis, interview generation & smart evaluation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Reads extra allowed origins from ALLOWED_ORIGINS env var (comma-separated).
# Always includes localhost dev ports and the production Vercel domain.
_extra_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]

ALLOWED_ORIGINS = list(
    {
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://intellihire-ai.vercel.app",
        *_extra_origins,
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
    max_age=600,
)


# ─── Timing middleware ────────────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled middleware exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "path": str(request.url.path)},
        )
    response.headers["X-Process-Time"] = f"{(time.time() - start):.4f}s"
    return response


# ─── Global exception handler ────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    try:
        from app.database import engine, Base
        import app.models.user       # noqa: F401  — register models
        import app.models.resume     # noqa: F401
        import app.models.interview  # noqa: F401

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables verified/created")
    except Exception as e:
        # Log but don't crash — DB might be read-only on first cold boot
        logger.error(f"⚠️  Database startup error (non-fatal): {e}", exc_info=True)

    logger.info("🚀 IntelliHire Pro backend started")


# ─── Routers ──────────────────────────────────────────────────────────────────
try:
    from app.api import auth_routes, resume_routes, interview_routes, admin_routes

    app.include_router(auth_routes.router,      prefix="/api/auth",      tags=["Auth"])
    app.include_router(resume_routes.router,    prefix="/api/resume",    tags=["Resume"])
    app.include_router(interview_routes.router, prefix="/api/interview", tags=["Interview"])
    app.include_router(admin_routes.router,     prefix="/api/admin",     tags=["Admin"])
    logger.info("✅ All routers registered")
except Exception as e:
    logger.error(f"⚠️  Router registration error: {e}", exc_info=True)


# ─── Health endpoints ─────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "IntelliHire Pro API v2.0 running"}


@app.get("/health", tags=["Health"])
def health():
    """
    Render pings this route to keep the service alive.
    Also does a quick DB connectivity check.
    """
    db_status = "unknown"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy",
        "database": db_status,
    }