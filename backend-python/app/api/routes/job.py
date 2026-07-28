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
    """
    Parses a Job Description from text, a PDF URL, or a career page URL.
    Returns a structured JobKnowledgeBase (JKB).
    """
    try:
        # Step 1: Async extraction (I/O bound: downloading PDF, scraping URL, etc.)
        raw_text = await JobExtractorFactory.extract_raw_text(request)
        
        # Step 2: Sync processing (CPU bound: cleaning, regex parsing, NLP extraction, building)
        # Offloaded to a thread pool to keep FastAPI's async event loop highly responsive
        jkb = await run_in_threadpool(job_pipeline.process, raw_text)
        
        return jkb
        
    except ValueError as ve:
        # Client errors: Invalid source_type, bad URL, invalid PDF content type, etc.
        raise HTTPException(status_code=400, detail=str(ve))
        
    except JobProcessingError as jpe:
        # Pipeline errors: Empty text extracted, Pydantic validation failures
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