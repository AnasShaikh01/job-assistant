import re
import unicodedata
from collections import Counter

class JobCleaner:
    """
    Cleans extracted job description text while preserving structure, 
    tech names (C#, C++, .NET), and case-sensitivity.
    Removes website UI remnants, normalizes bullets, and clears repeated boilerplate.
    Strictly NO metadata extraction occurs here.
    """
    
    PAGE_REGEX = re.compile(r"^page\s*\d+(\s*of\s*\d+)?$", re.IGNORECASE)
    
    # Matches common ATS timestamps like "Posted 3 days ago", "30+ days ago", "posted yesterday"
    POSTED_REGEX = re.compile(r"^(?:posted\s+)?(?:just\s+now|today|yesterday|\d+\+?\s+(?:days?|hours?|minutes?|weeks?|months?)\s+ago)$", re.IGNORECASE)
    
    # Matches decorative separator lines (----, ====, ****)
    SEPARATOR_REGEX = re.compile(r"^[\-=_*]{4,}$")

    # Exact matches for common UI buttons that survive HTML extraction
    UI_REMNANTS = {
        "apply now", "share", "back", "save job", "view more", 
        "apply", "save", "copy link", "report job", "return to search",
        "see more", "show more", "loading...", "sign in", "login", 
        "create account", "continue", "submit application", "easy apply"
    }

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
            
        # 1. Normalize Unicode
        text = unicodedata.normalize("NFKD", text)

        # 2. Normalize bullets consistently (do this before stripping punctuation)
        text = re.sub(r'^[ \t]*[•·▪►➢✓✔]\s*', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'[•·▪►➢✓✔]', '-', text)

        # 3. Safely strip junk characters while preserving tech names and structure (C#, C++, 25%)
        text = re.sub(r"[^\w\s,.\-+/&#*@:()[\]'%|\n]", "", text)

        # 4. Remove repeated boilerplate, page numbers, and UI remnants
        text = JobCleaner._remove_headers_footers_and_ui(text)

        # 5. Collapse multiple spaces safely without deleting lines
        text = re.sub(r"[ \t]+", " ", text)
        
        # 6. Normalize line endings and cap consecutive blank lines at two
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def _is_boilerplate(line: str) -> bool:
        line_lower = line.lower()
        if "page" in line_lower: return True
        if "copyright" in line_lower or "©" in line_lower: return True
        if "all rights reserved" in line_lower: return True
        if "confidential" in line_lower: return True
        if re.search(r"https?://|www\.|\b[a-z0-9-]+\.(com|org|net|io|co|ai|dev)\b", line_lower): return True
        return False

    @staticmethod
    def _remove_headers_footers_and_ui(text: str, repeat_threshold: int = 2) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        counts = Counter(lines)

        repeated_boilerplate = {
            line for line, count in counts.items()
            if count >= repeat_threshold 
            and len(line) < 120 
            and JobCleaner._is_boilerplate(line)
        }

        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            stripped_lower = stripped.lower()
            
            if (stripped in repeated_boilerplate or 
                JobCleaner.PAGE_REGEX.match(stripped) or 
                JobCleaner.POSTED_REGEX.match(stripped) or
                JobCleaner.SEPARATOR_REGEX.match(stripped) or
                stripped_lower in JobCleaner.UI_REMNANTS):
                continue
                
            cleaned_lines.append(line)
            
        return "\n".join(cleaned_lines)