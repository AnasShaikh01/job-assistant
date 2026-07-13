import re
import unicodedata

class JobCleaner:
    """
    Cleans extracted job description text while preserving structure and case-sensitivity.
    Isolated from Resume Engine to allow JD-specific rules later.
    """
    
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
            
        # 1. Normalize Unicode
        text = unicodedata.normalize("NFKD", text)

        # 2. Preserve structural markers (+, -, /, &) — Removed #
        text = re.sub(r"[^\w\s,.\-+/&\n]", "", text)

        # 3. Normalize bullets commonly found in JDs
        text = re.sub(r'[•·▪►]', '-', text)

        # 4. Collapse multiple spaces safely without deleting lines
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()