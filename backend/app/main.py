"""
IntelliHire Pro — Main FastAPI Application
Production-grade, crash-proof backend.
"""

import os
import time
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
)
logger = logging.getLogger("intellihire")

app = FastAPI(
    title="IntelliHire Pro API",
    description="AI-powered hiring platform",
    version="2.0.0",
)

# ─── CORS (FINAL FIX) ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all (safe for testing)
    allow_credentials=False,    # IMPORTANT (no crash)
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PREFLIGHT FIX (VERY IMPORTANT) ───────────────────────────────────────────
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(status_code=200)

# ─── Middleware ───────────────────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    response.headers["X-Process-Time"] = f"{(time.time() - start):.4f}s"
    return response

# ─── Global Exception ─────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
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
        logger.info("✅ DB ready")
    except Exception as e:
        logger.error(f"DB error: {e}", exc_info=True)

    logger.info("🚀 Backend started")

# ─── Routers ──────────────────────────────────────────────────────────────────
try:
    from app.api import auth_routes, resume_routes, interview_routes, admin_routes

    app.include_router(auth_routes.router, prefix="/api/auth")
    app.include_router(resume_routes.router, prefix="/api/resume")
    app.include_router(interview_routes.router, prefix="/api/interview")
    app.include_router(admin_routes.router, prefix="/api/admin")

    logger.info("✅ Routers loaded")
except Exception as e:
    logger.error(f"Router error: {e}", exc_info=True)

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}