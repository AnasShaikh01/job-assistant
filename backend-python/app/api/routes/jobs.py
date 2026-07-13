import logging
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.jobs.schemas import JobParseRequest, JobKnowledgeBase
from app.jobs.extractor import JobExtractorFactory
from app.jobs.pipeline import JobPipeline, JobProcessingError

# Set up module-level logger
logger = logging.getLogger(__name__)

# Prefix aligns with standard REST v1 standards
router = APIRouter(prefix="/api/v1/job", tags=["Job Engine"])

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
        
    except Exception as e:
        # Unhandled server errors (logged for debugging with full stack trace)
        logger.exception("Unhandled Job Engine Error")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while parsing the job description.")