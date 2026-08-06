import logging
import time
from .schemas import JobParseRequest, JobKnowledgeBase
from .extractor import JobExtractorFactory
from .cleaner import JobCleaner
from .parser import JobParser
from .builder import JobBuilder
from .validator import JobValidator
from app.shared.skill_extractor import SkillExtractor
from .keyword_extractor import KeywordExtractor

logger = logging.getLogger(__name__)

class JobProcessingError(Exception):
    """Custom exception to ensure internal stack traces don't leak to the API client."""
    pass

class JobPipeline:
    """
    Orchestrates the end-to-end extraction of a Job Description.
    Strictly follows: Extractor -> Cleaner -> Parser -> ML Extractors -> Builder -> Validator.
    Includes stage timings and global error handling.
    """

    def __init__(self):
        # Initialize components once to keep memory footprint low
        self.parser = JobParser()
        self.skill_extractor = SkillExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.builder = JobBuilder()
        self.validator = JobValidator()

    async def process(self, request: JobParseRequest) -> JobKnowledgeBase:
        try:
            start_time = time.perf_counter()

            # 1. Fetch raw text (URL, PDF, or Text)
            raw_text = await JobExtractorFactory.extract_raw_text(request)
            ext_time = time.perf_counter()
            logger.info(f"Extraction completed in {ext_time - start_time:.4f}s")

            # Failsafe for empty document parsing
            if not raw_text.strip():
                raise ValueError("No job description could be extracted. The source may be empty or blocked.")

            # 2. Clean UI remnants, boilerplate, and Unicode
            clean_text = JobCleaner.clean(raw_text)
            cln_time = time.perf_counter()
            logger.info(f"Cleaning completed in {cln_time - ext_time:.4f}s")

            # 3. Parse into logical sections
            sections = self.parser.parse(clean_text)
            prs_time = time.perf_counter()
            logger.info(f"Parsing completed in {prs_time - cln_time:.4f}s")

            # 4. Extract Skills & Keywords
            # Explicitly EXCLUDE the company section so we don't extract historical tech stacks.
            # Explicitly INCLUDE the skills section to catch dedicated tech lists.
            target_extraction_text = "\n".join([
                sections.get("header", ""),
                sections.get("responsibilities", ""),
                sections.get("qualifications", ""),
                sections.get("preferred_qualifications", ""),
                sections.get("skills", "")
            ])
            
            skills = self.skill_extractor.extract(target_extraction_text)
            keywords = self.keyword_extractor.extract(target_extraction_text)
            ml_time = time.perf_counter()
            logger.info(f"ML Extraction completed in {ml_time - prs_time:.4f}s")

            # 5. Build the raw Knowledge Base
            raw_jkb = self.builder.build(sections, skills, keywords)
            bld_time = time.perf_counter()
            logger.info(f"Builder completed in {bld_time - ml_time:.4f}s")

            # 6. Validate and recover missing data
            validated_jkb = self.validator.validate(raw_jkb, sections)
            val_time = time.perf_counter()
            logger.info(f"Validator completed in {val_time - bld_time:.4f}s")
            
            logger.info(f"Total Pipeline execution: {val_time - start_time:.4f}s")

            return validated_jkb

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            # Wrap all internal errors into a predictable API exception
            raise JobProcessingError(f"Job processing failed: {str(e)}") from e