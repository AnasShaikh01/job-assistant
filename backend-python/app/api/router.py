from fastapi import APIRouter
from app.api.routes import health, resume, job

api_router = APIRouter()

# Register the health endpoint
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Register the resume parsing endpoint
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])

# Register the job parsing endpoint
api_router.include_router(job.router, prefix="/job", tags=["Job Engine"])