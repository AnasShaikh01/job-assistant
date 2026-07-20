import time
import logging
from typing import List
from pydantic import ValidationError

from app.candidate.schemas import CandidateKnowledgeBase
from app.resume.extractor import ResumeExtractor
from app.resume.cleaner import ResumeCleaner
from app.resume.parser import ResumeSectionParser
from app.shared.skill_extractor import SkillExtractor
from app.candidate.builder import CandidateBuilder

logger = logging.getLogger(__name__)

# ==========================================================
# Custom Exceptions
# ==========================================================
class ResumeExtractionError(Exception):
    """Raised when text extraction fails completely or yields no usable text."""
    pass

class UnsupportedFileTypeError(Exception):
    """Raised when the uploaded file extension falls outside supported boundaries."""
    pass

class CandidateValidationError(Exception):
    """Raised when the constructed CKB object violates schema constraints."""
    pass


class ResumePipeline:
    """
    Main Orchestrator for the Candidate Engine.
    Coordinates the pipeline flow, validates state between stages, 
    collects non-fatal warnings, and handles structured logging.
    """
    def __init__(self):
        self.cleaner = ResumeCleaner()
        self.section_parser = ResumeSectionParser()
        self.skill_extractor = SkillExtractor()
        self.builder = CandidateBuilder()

    def process(self, file_bytes: bytes, filename: str) -> CandidateKnowledgeBase:
        start_time = time.perf_counter()
        
        # Warnings are collected for future API enhancements 
        warnings: List[str] = []
        
        logger.info(f"Starting resume pipeline for file: {filename}")

        # ---------------------------------------------------------
        # Stage 1: Extraction
        # ---------------------------------------------------------
        try:
            extraction_result = ResumeExtractor.extract(file_bytes, filename)
        except ValueError as ve:
            logger.error(f"Unsupported file type: {filename}")
            raise UnsupportedFileTypeError(str(ve))
        except Exception as e:
            logger.exception(f"Unexpected extraction failure for {filename}")
            raise ResumeExtractionError(f"Failed to read document: {str(e)}")

        raw_text = extraction_result.text
        metadata = extraction_result.metadata
        embedded_links = extraction_result.embedded_links
        
        if not raw_text.strip():
            raise ResumeExtractionError(f"Extraction yielded empty text boundary content for '{filename}'.")
            
        if metadata.is_scanned:
            warnings.append("Scanned PDF detected. Extraction quality may be degraded.")

        logger.info(
            f"Extraction complete for {filename} | "
            f"Pages: {metadata.pages} | "
            f"Words: {metadata.word_count} | "
            f"Scanned: {metadata.is_scanned} | "
            f"Embedded Links: {len(embedded_links)}"
        )

        # ---------------------------------------------------------
        # Stage 2: Cleaning
        # ---------------------------------------------------------
        clean_text = self.cleaner.clean(raw_text)
        
        if not clean_text.strip():
            raise ResumeExtractionError("Document yielded empty text after cleaning layer.")

        # ---------------------------------------------------------
        # Stage 3: Structural Parsing
        # ---------------------------------------------------------
        sections = self.section_parser.parse(clean_text)
        
        if not sections.get("experience"):
            warnings.append("No professional experience section detected.")
        if not sections.get("education"):
            warnings.append("No education section detected.")

        # [FUTURE AI HOOK]: If sections logic yields poor structured splits, 
        # intercept here and pass `clean_text` to an LLM fallback router.

        # ---------------------------------------------------------
        # Stage 4: Skill Extraction
        # ---------------------------------------------------------
        skills_text = (
            f"{sections.get('skills', '')}\n"
            f"{sections.get('experience', '')}\n"
            f"{sections.get('projects', '')}"
        ).strip()
        
        skills = self.skill_extractor.extract(skills_text)
        if not skills:
            warnings.append("No technical skills were explicitly detected.")

        # ---------------------------------------------------------
        # Stage 5: Assembly & Schema Validation
        # ---------------------------------------------------------
        try:
            # Inject embedded_links into the builder for downstream processing
            candidate_ckb = self.builder.build(
                sections=sections, 
                skills=skills, 
                embedded_links=embedded_links
            )
        except ValidationError as e:
            logger.error(f"CKB Schema Validation failed for {filename}: {str(e)}")
            # [FUTURE AI HOOK]: On ValidationError, pass the raw data + errors 
            # to an LLM self-correction prompt before failing completely.
            raise CandidateValidationError(f"Candidate schema validation failed: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error during Builder assembly.")
            raise CandidateValidationError(f"Assembly failed: {str(e)}")

        # ---------------------------------------------------------
        # Pipeline Finalization
        # ---------------------------------------------------------
        duration = round(time.perf_counter() - start_time, 3)
        
        if warnings:
            logger.warning(f"Pipeline completed with warnings for {filename}: {warnings}")
            
        logger.info(f"Pipeline completed successfully in {duration}s for {filename}")

        return candidate_ckb