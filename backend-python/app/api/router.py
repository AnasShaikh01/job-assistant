from fastapi import APIRouter
from app.api.routes import health, resume, job

api_router = APIRouter()

# Register the health endpoint
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Register the resume parsing endpoint
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])

# Register the job parsing endpoint
# Note: Since we defined prefix="/api/v1/job" and tags=["Job Engine"] inside job.py, 
# we don't need to pass them here again.
api_router.include_router(job.router)