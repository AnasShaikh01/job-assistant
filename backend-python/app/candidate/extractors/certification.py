import re
from typing import List, Tuple, Optional
from app.candidate.schemas import Certification

class CertificationExtractor:
    """
    Extract structured credential and certification information from the
    certifications section of a resume using pure deterministic methods.
    """
    # Step 4 - Date Pattern supporting: "Issued: Jan 2024", "May 2025", "2024", "05/2025"
    DATE_PATTERN = re.compile(
        r"\b(?:Issued:\s*)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\s/]?\d{4}|\b\d{4}\b",
        re.IGNORECASE
    )

    # 1. Cleaned Credential URL Regex
    CREDENTIAL_URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)

    # Keywords used to identify lines that are metadata rather than names/issuers
    METADATA_KEYWORDS_PATTERN = re.compile(
        r"\b(issued by|by|issuer|organization|authority|at|url|date|issued)\b",
        re.IGNORECASE
    )

    BULLET_PATTERN = re.compile(r"^[•●▪◦*-]\s*")

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Certification]:
        if not text.strip():
            return []

        # Step 1 — Normalize
        normalized_text = self._normalize_text(text)

        # Step 2 — Split Certification Blocks
        blocks = self._split_blocks(normalized_text)

        certifications_list = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            # Step 3 — Extract Certification Name
            name = self._extract_name(lines)

            # Step 5 — Extract Issue Date
            issue_date = self._extract_issue_date(block)

            # Step 6 — Extract Credential URL
            credential_url = self._extract_credential_url(block)

            # Step 4 — Extract Issuer
            issuer = self._extract_issuer(lines, name)

            # Build Object
            certification_obj = Certification(
                name=name,
                issuer=issuer,
                issue_date=issue_date,
                credential_url=credential_url
            )
            certifications_list.append(certification_obj)

        return certifications_list

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _normalize_text(self, text: str) -> str:
        """Step 1 — Normalize: Clean multi-spacing elements while leaving layout rows separate."""
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 — Split Blocks.
        Splits distinct certification credentials on blank structural rows.
        """
        return [
            block.strip()
            for block in re.split(r"\n\s*\n", text)
            if block.strip()
        ]

    def _extract_name(self, lines: List[str]) -> Optional[str]:
        """2. Improve _extract_name() to skip metadata/link line types entirely."""
        for line in lines[:2]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            if self.CREDENTIAL_URL_PATTERN.search(clean_line):
                continue
            if self.DATE_PATTERN.search(clean_line):
                continue
            if self.METADATA_KEYWORDS_PATTERN.search(clean_line.lower()):
                continue
                
            return clean_line
        return None

    def _extract_issuer(self, lines: List[str], name: Optional[str]) -> Optional[str]:
        """3. Improve _extract_issuer() by evaluating the first 3 lines against filters."""
        for line in lines[:3]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            if name and clean_line == name:
                continue
            if self.CREDENTIAL_URL_PATTERN.search(clean_line):
                continue
            if self.DATE_PATTERN.search(clean_line):
                continue
                
            # If it explicitly contains metadata words, clean the prefix text away 
            if self.METADATA_KEYWORDS_PATTERN.search(clean_line.lower()):
                return self.METADATA_KEYWORDS_PATTERN.sub("", clean_line).replace(":", "").strip()
                
            return clean_line
            
        return None

    def _extract_issue_date(self, block: str) -> Optional[str]:
        """Step 5 — Extract Issue Date via timeline regex matching."""
        match = self.DATE_PATTERN.search(block)
        if match:
            return match.group(0).strip()
        return None

    def _extract_credential_url(self, block: str) -> Optional[str]:
        """Step 6 — Extract Credential URL verifying the badge authority."""
        match = self.CREDENTIAL_URL_PATTERN.search(block)
        if match:
            return match.group(0).strip()
        return None