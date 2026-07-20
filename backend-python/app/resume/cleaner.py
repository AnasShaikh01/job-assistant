import re
import unicodedata
from collections import Counter
from typing import List

class ResumeCleaner:
    """
    Standardizes raw extraction text without losing semantic meaning.
    Normalizes unicode, whitespace, and removes noisy headers/footers.
    """
    
    # Matches patterns like "Page 1", "page 1 of 2", "1 of 4", or "- 1 -"
    PAGE_REGEX = re.compile(r"^(?:page\s*\d+(?:\s*of\s*\d+)?|\d+\s*of\s*\d+|-\s*\d+\s*-)$", re.IGNORECASE)
    
    @classmethod
    def clean(cls, raw_text: str) -> str:
        # Normalize line endings to avoid platform-specific parsing issues
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Resolve ligatures (e.g., 'ﬁ' -> 'fi') and standardize quotes/dashes
        text = unicodedata.normalize("NFKC", text)
        
        # Strip non-printable control characters, preserving \n and \t
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        text = cls._remove_headers_footers(text)
        
        # Collapse horizontal space (tabs/spaces) safely
        text = re.sub(r"[ \t]+", " ", text)
        # Cap vertical space at 2 newlines to maintain paragraph separation cleanly
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text.strip()

    @classmethod
    def _remove_headers_footers(cls, text: str, repeat_threshold: int = 2) -> str:
        lines = text.splitlines()
        content_lines = [line.strip() for line in lines if line.strip()]
        counts = Counter(content_lines)
        
        # Heuristic: Repeated lines across pages are typically navigational noise.
        # Constrained between 15 and 100 chars to avoid dropping valid repeated 
        # short entities (like job titles or section headers) or full paragraphs.
        repeated_noise = {
            line for line, count in counts.items()
            if count >= repeat_threshold and 15 < len(line) < 100
        }
        
        cleaned_lines: List[str] = []
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                cleaned_lines.append("")
                continue
                
            if cls.PAGE_REGEX.search(stripped):
                continue
                
            if stripped in repeated_noise:
                continue
                
            cleaned_lines.append(line.rstrip())
            
        return "\n".join(cleaned_lines)