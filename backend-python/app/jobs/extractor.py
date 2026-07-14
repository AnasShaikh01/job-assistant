from .schemas import JobParseRequest
from .extractors.text import TextExtractor
from .extractors.url import URLExtractor
from .extractors.pdf import PDFExtractor

class JobExtractorFactory:
    """
    Dispatcher mapping source types to their respective extractors.
    Transforms all inputs into a unified raw text string.
    """
    
    EXTRACTORS = {
        "text": TextExtractor,
        "pdf": PDFExtractor,
        "url": URLExtractor,
    }
    
    @classmethod
    async def extract_raw_text(cls, request: JobParseRequest) -> str:
        extractor_class = cls.EXTRACTORS.get(request.source_type)
        
        if not extractor_class:
            raise ValueError(f"Invalid extraction source_type: {request.source_type}")
            
        # Standardized interface allows a clean await across all extractors
        return await extractor_class.extract(request.content)