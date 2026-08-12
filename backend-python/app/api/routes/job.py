import logging
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.jobs.schemas import JobParseRequest, JobKnowledgeBase
from app.jobs.extractor import JobExtractorFactory
from app.jobs.pipeline import JobPipeline, JobProcessingError

# Set up module-level logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate the pipeline once at module load. 
# This prevents reloading the heavy spaCy model into memory on every single API request.
job_pipeline = JobPipeline()

@router.post("/parse", response_model=JobKnowledgeBase)
async def parse_job(request: JobParseRequest):
    try:
        return await job_pipeline.process(request)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except JobProcessingError as jpe:
        raise HTTPException(status_code=422, detail=str(jpe))

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="This website blocks automated scraping. Please use the PDF upload or paste the job description instead."
            )

        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch the job posting ({e.response.status_code})."
        )