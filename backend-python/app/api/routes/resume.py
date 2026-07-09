from fastapi import APIRouter, HTTPException

from app.schemas.resume import ResumeParseRequest, ResumeParseResponse
from app.services.downloader import ResumeDownloader
from app.resume.pipeline import (
    ResumePipeline,
    ResumeExtractionError,
    UnsupportedFileTypeError,
    CandidateValidationError,
)

router = APIRouter()
pipeline = ResumePipeline()

@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(request: ResumeParseRequest):
    """
    POST /api/v1/resume/parse
    Flow: Receive Request -> Download Bytes -> Parse Pipeline -> Return Wrapped JSON
    """
    try:
        # 1. Download the PDF/DOCX bytes into memory
        file_bytes = await ResumeDownloader.download(str(request.file_url))
        
        # 2. Process through the AI Pipeline
        candidate_ckb = pipeline.process(file_bytes, request.filename)
        
        # 3. Return the structured JSON paired with the tracking ID
        return ResumeParseResponse(
            resume_file_id=request.resume_file_id,
            candidate=candidate_ckb
        )
        
    except HTTPException:
        # If the downloader raised an HTTPException (e.g., 404, 504), let it pass through exactly as is
        raise
        
    except (
        ResumeExtractionError,
        UnsupportedFileTypeError,
        CandidateValidationError,
    ) as e:
        # 422 Unprocessable Entity - Node will know the file was bad/unparsable
        raise HTTPException(status_code=422, detail=str(e))
        
    except Exception as e:
        # 500 Internal Server Error - Node will know our Python server crashed unexpectedly
        raise HTTPException(status_code=500, detail=f"Unexpected Internal Error: {str(e)}")