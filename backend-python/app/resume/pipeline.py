from pydantic import ValidationError
from app.candidate.schemas import CandidateKnowledgeBase

# Import Engine Components
from app.resume.extractor import ResumeExtractor
from app.resume.cleaner import ResumeCleaner
from app.resume.parser import ResumeSectionParser
from app.resume.skill_extractor import SkillExtractor
from app.candidate.builder import CandidateBuilder

# Custom Exceptions for Structured Control Flow
class ResumeExtractionError(Exception):
    """Raised when text extraction from a valid file layout fails completely."""
    pass

class UnsupportedFileTypeError(Exception):
    """Raised when the uploaded file extension falls outside supported boundaries."""
    pass

class CandidateValidationError(Exception):
    """Raised when the constructed CKB object violates Pydantic schema constraints."""
    pass

class ResumePipeline:
    """
    Main Orchestrator for the Candidate Engine.
    Coordinates the pipeline flow from raw input file bytes to a validated 
    canonical CandidateKnowledgeBase (CKB) instance without embedding internal business logic.
    """
    def __init__(self):
        # We retain the class-based initializations for the rest of the deterministic tools
        self.cleaner = ResumeCleaner()
        self.section_parser = ResumeSectionParser()
        self.skill_extractor = SkillExtractor()
        self.builder = CandidateBuilder()

    # ==========================================================
    # Public API
    # ==========================================================

    def process(self, file_bytes: bytes, filename: str) -> CandidateKnowledgeBase:
        """
        Executes the top-down sequential processing of an incoming resume file.
        """
        # Step 1: Extract text with targeted type validation
        try:
            raw_text = ResumeExtractor.extract(file_bytes, filename)
        except ValueError as ve:
            raise UnsupportedFileTypeError(f"File validation rejected for '{filename}': {str(ve)}")
        except Exception as e:
            raise ResumeExtractionError(f"Failed to read data structural frames from '{filename}': {str(e)}")

        if not raw_text.strip():
            raise ResumeExtractionError(f"Extraction yielded empty text boundary content for '{filename}'.")

        # Step 2: Clean Text
        clean_text = self.cleaner.clean(raw_text)

        # Step 3: Parse Sections
        sections = self.section_parser.parse(clean_text)

        # Step 4: Extract Skills (Targeted high-signal injection to avoid global resume noise)
        skills_text = (
            f"{sections.get('skills', '')}\n"
            f"{sections.get('experience', '')}\n"
            f"{sections.get('projects', '')}"
        )
        skills = self.skill_extractor.extract(skills_text)

        # Step 5 & 6: Build and Validate Candidate Knowledge Base
        # Pydantic validation handles implicit verification natively on schema composition.
        # Future AI Fallback Integration Point:
        # If a ValidationError is raised here, it can be caught to route the failed 
        # sections/skills block to an AI Fallback sub-process.
        candidate_ckb = self.builder.build(sections, skills)

        # Step 7: Return Verified CKB Instance
        return candidate_ckb