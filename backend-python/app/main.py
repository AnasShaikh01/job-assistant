from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Mount the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Optional: A simple root redirect or welcome message
@app.get("/")
async def root():
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}