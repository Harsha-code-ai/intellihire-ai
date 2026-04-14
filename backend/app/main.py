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

# ─── CORS ─────────────────────────────────────────────────────────────────────
_extra_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]

ALLOWED_ORIGINS = list({
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://intellihire-ai.vercel.app",
    *_extra_origins,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
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


# ─── Global exception handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    try:
        from app.database import engine, Base
        import app.models.user
        import app.models.resume
        import app.models.interview

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables verified/created")
    except Exception as e:
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
# ✅ FIX: Added HEAD method so Render's health monitor doesn't get 405 errors
@app.api_route("/", methods=["GET", "HEAD"], tags=["Health"])
def root():
    return {"status": "ok", "message": "IntelliHire Pro API v2.0 running"}


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
def health():
    """Render pings this to keep the service alive. Also checks DB."""
    db_status = "unknown"
    try:
        from app.database import SessionLocal
        import sqlalchemy
        db = SessionLocal()
        db.execute(sqlalchemy.text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy",
        "database": db_status,
    }