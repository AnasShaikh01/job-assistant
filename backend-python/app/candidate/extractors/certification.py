import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Certification

class CertificationExtractor:
    """
    Extract structured credential and certification information from the
    certifications section of a resume using stateful detection and contextual parsing.
    """
    
    # Expanded Date Pattern supporting prefixes (Issued, Earned, Expires) + standard formats
    DATE_PATTERN = re.compile(
        r"\b(?:Issued|Earned|Completed|Expires)?\s*[:\-]?\s*"
        r"(?:(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4})\b",
        re.IGNORECASE
    )

    # Credential URL Regex (Base pattern to grab all URLs)
    CREDENTIAL_URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)

    # Metadata Keywords Pattern to skip Credential IDs, Verify links, etc.
    METADATA_PATTERN = re.compile(
        r"^(?:credential\s*id|credential\s*url|verify|badge|license\s*no|expires|issued|earned)\b",
        re.IGNORECASE
    )

    # Known Issuer Keywords for priority extraction (Name/Issuer logic)
    ISSUER_KEYWORDS = {
        "google", "microsoft", "coursera", "udemy", "aws", "amazon web services",
        "cisco", "oracle", "ibm", "comptia", "linkedin", "hackerrank", "edx",
        "hubspot", "salesforce", "meta", "freecodecamp", "scrum.org", "pmi"
    }

    # Matches prefixes like "Issued by Microsoft" to strip them cleanly
    ISSUER_PREFIX_PATTERN = re.compile(r"^(?:Issued\s*by|By|Issuer|Organization|Authority)\s*[:\-]?\s*", re.IGNORECASE)

    BULLET_PATTERN = re.compile(r"^[•●▪◦*\-–—]\s*")

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

            # Step 4 — Extract Issuer
            issuer = self._extract_issuer(lines, name)

            # Step 5 — Extract Issue Date
            issue_date = self._extract_issue_date(block)

            # Step 6 — Extract Credential URL
            credential_url = self._extract_credential_url(block)

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
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 & 7 — Split Blocks & Handle Merged Certs.
        State machine that splits on strong combinations (Name + Date, Name + Issuer prefix, Name + URL).
        """
        lines = text.splitlines()
        blocks = []
        current_block = []
        seen_metadata = False

        for i, line in enumerate(lines):
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            # Lookahead context
            next_line = lines[i+1] if i+1 < len(lines) else ""
            combined_context = clean_line + " " + next_line
            
            has_date = bool(self.DATE_PATTERN.search(combined_context))
            has_url = bool(self.CREDENTIAL_URL_PATTERN.search(combined_context)) or bool(self.METADATA_PATTERN.match(clean_line))
            
            # 2. FIXED: Use explicit structural prefixes for splitting, not just any recognized brand keyword.
            has_issuer = bool(self.ISSUER_PREFIX_PATTERN.match(clean_line)) or bool(self.ISSUER_PREFIX_PATTERN.match(next_line))
            
            is_potential_name = len(clean_line) < 80 and not bool(self.METADATA_PATTERN.match(clean_line)) and not self.CREDENTIAL_URL_PATTERN.search(clean_line)

            can_split = False
            if current_block:
                if seen_metadata and is_potential_name and (has_date or has_url or has_issuer):
                    can_split = True
                elif not seen_metadata and len(current_block) >= 3 and is_potential_name:
                    can_split = True

            if can_split:
                blocks.append("\n".join(current_block))
                current_block = []
                seen_metadata = False

            current_block.append(line)
            
            # 2. FIXED: Mark metadata as seen ONLY if the current line actually contains structural metadata signals
            if self.DATE_PATTERN.search(clean_line) or self.CREDENTIAL_URL_PATTERN.search(clean_line) or self.ISSUER_PREFIX_PATTERN.match(clean_line):
                seen_metadata = True

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_name(self, lines: List[str]) -> Optional[str]:
        for line in lines[:3]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            if not clean_line or len(clean_line) > 100:
                continue
                
            if self.CREDENTIAL_URL_PATTERN.search(clean_line):
                continue
            if self.DATE_PATTERN.search(clean_line):
                continue
            if self.METADATA_PATTERN.search(clean_line):
                continue
                
            return clean_line
        return None

    def _extract_issuer(self, lines: List[str], name: Optional[str]) -> Optional[str]:
        candidates = []
        
        for line in lines[:4]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            if name and (clean_line == name or clean_line in name):
                continue
            if self.CREDENTIAL_URL_PATTERN.search(clean_line):
                continue
            if self.DATE_PATTERN.search(clean_line):
                continue
            if self.METADATA_PATTERN.search(clean_line):
                continue
                
            clean_line = self.ISSUER_PREFIX_PATTERN.sub("", clean_line).strip()
            
            if clean_line:
                candidates.append(clean_line)

        # Pass 1: Look for explicit known issuers
        for candidate in candidates:
            if any(kw in candidate.lower() for kw in self.ISSUER_KEYWORDS):
                return candidate
                
        # Pass 2: Fallback to the first valid clean line
        if candidates:
            return candidates[0]
            
        return None

    def _extract_issue_date(self, block: str) -> Optional[str]:
        match = self.DATE_PATTERN.search(block)
        if match:
            raw_date = match.group(0).strip()
            clean_date = re.sub(r"^(?:Issued|Earned|Completed|Expires)?\s*[:\-]?\s*", "", raw_date, flags=re.IGNORECASE)
            return clean_date.strip()
        return None

    def _extract_credential_url(self, block: str) -> Optional[str]:
        """
        1. FIXED: Extract Credential URL with smart filtering. 
        Ignores generalized profile links and prioritizes known credential authorities.
        """
        matches = self.CREDENTIAL_URL_PATTERN.finditer(block)
        valid_urls = []
        
        # Non-credential domains to filter out completely
        ignore_domains = ["linkedin.com", "github.com", "twitter.com", "medium.com", "portfolio"]
        # Known credential platforms to prioritize
        credential_domains = [
            "credly.com", "coursera.org", "udemy.com", "microsoft.com/learn", 
            "accredible", "skillsoft", "oracle", "cisco", "aws.amazon", 
            "badgr", "credential", "cert", "badge"
        ]

        for match in matches:
            url = match.group(0).strip()
            if any(domain in url.lower() for domain in ignore_domains):
                continue
            valid_urls.append(url)

        # Pass 1: Prioritize known credential platforms
        for url in valid_urls:
            if any(domain in url.lower() for domain in credential_domains):
                return url
                
        # Pass 2: Fallback to the first valid URL
        if valid_urls:
            return valid_urls[0]
            
        return None