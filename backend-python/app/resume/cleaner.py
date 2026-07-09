import re
from collections import Counter

class ResumeCleaner:
    """
    Cleans extracted resume text while preserving structure and case-sensitivity.
    """
    PAGE_REGEX = re.compile(r"page\s*\d+(\s*of\s*\d+)?", re.IGNORECASE)

    @staticmethod
    def clean(text: str) -> str:
        text = ResumeCleaner._remove_headers_footers(text)

        # Preserve structural markers (+, #, -, /)
        text = re.sub(r"[^\w\s,.\-+#/&\n]", "", text)

        # Collapse multiple spaces safely without deleting lines
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # FIX: DO NOT .lower() here. Preserve casing for entity and token processing.
        return text.strip()

    @staticmethod
    def _remove_headers_footers(text: str, repeat_threshold: int = 2) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        counts = Counter(lines)

        repeated = {
            line for line, count in counts.items()
            if count >= repeat_threshold and len(line) < 120
        }

        cleaned = [
            line for line in lines
            if line not in repeated and not ResumeCleaner.PAGE_REGEX.search(line)
        ]
        return "\n".join(cleaned)