from pydantic import ValidationError
from .schemas import JobKnowledgeBase

# Import Job Engine Components
from .cleaner import JobCleaner
from .parser import JobParser
from app.shared.skill_extractor import SkillExtractor
from .keyword_extractor import KeywordExtractor
from .builder import JobBuilder

# Custom Exceptions for Structured Control Flow
class JobProcessingError(Exception):
    """Raised when the text processing pipeline fails."""
    pass

class JobPipeline:
    """
    Main Orchestrator for the Job Engine.
    Coordinates the synchronous pipeline flow from raw extracted text to a 
    validated canonical JobKnowledgeBase (JKB) instance.
    """
    def __init__(self):
        # Initialize components once to keep pipeline execution fast
        self.cleaner = JobCleaner()
        self.parser = JobParser()
        self.skill_extractor = SkillExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.builder = JobBuilder()

    # ==========================================================
    # Public API
    # ==========================================================

    def process(self, raw_text: str) -> JobKnowledgeBase:
        """
        Executes the top-down sequential processing of a job description.
        Expects raw text (extraction I/O should be handled prior to this call).
        """
        if not raw_text or not raw_text.strip():
            raise JobProcessingError("Extraction yielded empty text. Cannot process job description.")

        try:
            # Step 1: Clean Text
            clean_text = self.cleaner.clean(raw_text)

            # Step 2: Parse Sections
            sections = self.parser.parse(clean_text)

            # Step 3: Extract Skills & Keywords
            # We target high-signal sections to avoid noise from 'company about' or 'benefits'
            extraction_target_text = (
                f"{sections.get('header', '')}\n"
                f"{sections.get('responsibilities', '')}\n"
                f"{sections.get('qualifications', '')}\n"
                f"{sections.get('preferred_qualifications', '')}\n"
                f"{sections.get('skills', '')}"
            )
            
            skills = self.skill_extractor.extract(extraction_target_text)
            keywords = self.keyword_extractor.extract(extraction_target_text)

            # Step 4: Build and Validate Job Knowledge Base
            # Pydantic validation natively handles schema constraints inside the Builder
            job_jkb = self.builder.build(sections, skills, keywords)

            # Step 5: Return Verified JKB Instance
            return job_jkb

        except ValidationError as ve:
            # Future AI Fallback Integration Point:
            # Catch validation errors here to route to an LLM fallback
            raise JobProcessingError(f"Job Knowledge Base validation failed: {str(ve)}")
            
        except JobProcessingError:
            # Prevent re-wrapping if a custom error is explicitly raised in the pipeline
            raise
            
        except Exception as e:
            raise JobProcessingError(f"Unexpected error during job pipeline processing: {str(e)}")