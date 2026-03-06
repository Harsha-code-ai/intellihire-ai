from app.models import interview
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.database import engine, Base
from app.api import interview_history_routes

import app.models.user
import app.models.interview
import app.models.resume

from app.api import auth_routes
from app.api import interview_routes
from app.api import resume_routes
from app.api import admin_routes



app = FastAPI(title="IntelliHire API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(interview_routes.router)
app.include_router(resume_routes.router)
app.include_router(admin_routes.router)
app.include_router(interview_history_routes.router)

@app.get("/")
def home():
    return {"message": "IntelliHire Backend Running"}