from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Verify that the API is up and running.
    """
    return {
        "status": "ok",
        "message": "Job Assistant AI API is running perfectly."
    }