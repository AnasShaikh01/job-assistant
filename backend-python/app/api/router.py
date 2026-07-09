from fastapi import APIRouter
from app.api.routes import health, resume

api_router = APIRouter()

# Register the health endpoint under /api/v1/health
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Register the resume parsing endpoint under /api/v1/resume
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])