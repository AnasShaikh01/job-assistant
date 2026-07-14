class TextExtractor:
    """Pass-through extractor for raw pasted Job Descriptions."""
    
    @staticmethod
    async def extract(content: str) -> str:
        return content.strip() if content else ""