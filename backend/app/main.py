"""
IntelliHire Pro - Main FastAPI Application
Production-grade AI hiring platform backend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from app.database import engine, Base
import app.models.user
import app.models.resume
import app.models.interview

from app.api import auth_routes, resume_routes, interview_routes, admin_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("intellihire")

app = FastAPI(
    title="IntelliHire Pro API",
    description="AI-powered hiring platform — resume analysis, interview generation & smart evaluation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ✅ FIXED CORS (FINAL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://intellihire-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.time() - start):.4f}s"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("IntelliHire Pro backend started")


app.include_router(auth_routes.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(resume_routes.router,    prefix="/api/resume",    tags=["Resume"])
app.include_router(interview_routes.router, prefix="/api/interview", tags=["Interview"])
app.include_router(admin_routes.router,     prefix="/api/admin",     tags=["Admin"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "IntelliHire Pro API v2.0 running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}