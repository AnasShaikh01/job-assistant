import re
import unicodedata
from collections import Counter

class JobCleaner:
    """
    Cleans extracted job description text while preserving structure, 
    tech names (C#, C++, .NET), and case-sensitivity.
    """
    
    # Matches explicit strings like "Page 1", "page 2 of 4", etc.
    PAGE_REGEX = re.compile(r"^page\s*\d+(\s*of\s*\d+)?$", re.IGNORECASE)

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
            
        # 1. Normalize Unicode (fixes smart quotes, non-breaking spaces)
        text = unicodedata.normalize("NFKD", text)

        # 2. Normalize bullets consistently (do this before stripping punctuation)
        text = re.sub(r'^[ \t]*[•·▪►➢✓✔]\s*', '- ', text, flags=re.MULTILINE)
        text = re.sub(r'[•·▪►➢✓✔]', '-', text)

        # 3. Safely strip junk characters while preserving tech names and structure
        # Explicitly keeping: % (percentages), ' (apostrophes), # (C#), + (C++), etc.
        text = re.sub(r"[^\w\s,.\-+/&#*@:()[\]'%|\n]", "", text)

        # 4. Remove repeated boilerplate and page numbers
        text = JobCleaner._remove_headers_footers(text)

        # 5. Collapse multiple spaces safely without deleting lines
        text = re.sub(r"[ \t]+", " ", text)
        
        # 6. Normalize line endings and cap consecutive blank lines at two
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def _is_boilerplate(line: str) -> bool:
        """Helper to determine if a line looks like standard document boilerplate."""
        line_lower = line.lower()
        if "page" in line_lower:
            return True
        if "copyright" in line_lower or "©" in line_lower:
            return True
        if "all rights reserved" in line_lower:
            return True
        if "confidential" in line_lower:
            return True
        # Safer domain detection using word boundaries and modern TLDs
        if re.search(r"https?://|www\.|\b[a-z0-9-]+\.(com|org|net|io|co|ai|dev)\b", line_lower):
            return True
        return False

    @staticmethod
    def _remove_headers_footers(text: str, repeat_threshold: int = 2) -> str:
        """
        Removes lines that repeat multiple times AND look like standard 
        headers/footers, preventing the accidental deletion of valid repeating bullets.
        """
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        counts = Counter(lines)

        # Only target short repeated lines that match boilerplate signatures
        repeated_boilerplate = {
            line for line, count in counts.items()
            if count >= repeat_threshold 
            and len(line) < 120 
            and JobCleaner._is_boilerplate(line)
        }

        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            # Drop explicit page counts or identified repeated boilerplate
            if stripped in repeated_boilerplate or JobCleaner.PAGE_REGEX.match(stripped):
                continue
            cleaned_lines.append(line)
            
        return "\n".join(cleaned_lines)