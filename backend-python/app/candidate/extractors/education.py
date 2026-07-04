import re
from typing import List, Tuple, Optional
from app.candidate.schemas import Education

class EducationExtractor:
    """
    Extract structured education data from the
    education section of a resume using pure deterministic methods.
    """
    # Step 6 - Duration Regex supporting multi-formats (Year Only, Text Month + Year)
    DURATION_PATTERN = re.compile(
        r"\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4})"
        r"\s*[-–—]\s*"
        r"(Present|Current|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\d{4})\b",
        re.IGNORECASE,
    )

    # Step 7 - Improved CGPA / Percentage Regex targeting explicit prefixes
    CGPA_PATTERN = re.compile(
        r"\b(?:CGPA|GPA|Percentage|Score|Grade)\s*[:\-–—]?\s*(\d{1,2}(?:\.\d{1,2})?(?:\s*/\s*\d{1,2})?%?)",
        re.IGNORECASE,
    )

    # Contextual check to safely filter headers from metrics lines
    METRIC_KEYWORDS_PATTERN = re.compile(r"\b(cgpa|gpa|percentage|score|grade)\b", re.IGNORECASE)

    BULLET_PATTERN = re.compile(r"^[•●▪◦*-]\s*")

    # Step 3 - Expanded Degree Keywords (Ordered by length/specificity to avoid substring collisions)
    DEGREE_KEYWORDS = [
        "bachelor of engineering", "bachelor of technology", "master of technology",
        "bachelor", "master", "bachelors", "masters", "b.tech", "m.tech", 
        "b.com", "m.com", "bba", "llb", "llm", "b.sc", "m.sc", "bca", "mca", 
        "mba", "phd", "diploma", "bs", "ms", "be", "me"
    ]

    # Step 5 - Expanded Field of Study Keywords
    FIELD_KEYWORDS = [
        "computer science", "information technology", "software engineering",
        "artificial intelligence", "machine learning", "data science",
        "cyber security", "electronics", "electrical engineering",
        "mechanical engineering", "civil engineering", "business administration",
        "commerce", "finance", "mathematics", "physics", "chemistry"
    ]

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Education]:
        if not text.strip():
            return []

        # Step 1 — Normalize
        normalized_text = self._normalize_text(text)

        # Step 2 — Split Education Blocks
        blocks = self._split_blocks(normalized_text)

        education_list = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            # Step 3 — Extract Degree
            degree = self._extract_degree(lines)

            # Step 6 — Extract Duration
            start_year, end_year = self._extract_duration(block)

            # Step 4 — Extract Institution
            institution = self._extract_institution(lines, degree)

            # Step 5 — Extract Field of Study
            field_of_study = self._extract_field_of_study(block)

            # Step 7 — Extract CGPA / Percentage
            cgpa = self._extract_cgpa(block)

            # Step 8 — Build Object
            education_obj = Education(
                institution=institution,
                degree=degree,
                field_of_study=field_of_study,
                start_year=start_year,
                end_year=end_year,
                cgpa=cgpa
            )
            education_list.append(education_obj)

        return education_list

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _normalize_text(self, text: str) -> str:
        """Step 1 — Normalize: Clean whitespace constraints while protecting line orders."""
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 — Split Blocks.
        Slices entries cleanly using strict degree keyword boundaries as anchors.
        """
        lines = text.splitlines()
        blocks = []
        current_block = []

        for line in lines:
            clean_line = self.BULLET_PATTERN.sub("", line).strip().lower()
            if not clean_line:
                continue
            
            # Strict boundary check: Match standalone keywords only to prevent 
            # short abbreviations (like 'be', 'me', 'ms') from triggering on normal words.
            is_new_degree = False
            for degree in self.DEGREE_KEYWORDS:
                # Use strict word boundaries mapping on the clean line context
                if re.search(r"^\b" + re.escape(degree) + r"\b|\b" + re.escape(degree) + r"\b$", clean_line):
                    is_new_degree = True
                    break

            # If we detect a new degree title header and a block is already processing, flush it
            if is_new_degree and current_block:
                blocks.append("\n".join(current_block))
                current_block = []

            current_block.append(line)

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_degree(self, lines: List[str]) -> Optional[str]:
        """Step 3 — Extract Degree via lookup scan inside first 3 rows."""
        for line in lines[:3]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            for degree in self.DEGREE_KEYWORDS:
                if re.search(r"\b" + re.escape(degree) + r"\b", clean_line.lower()):
                    return clean_line
        return None

    def _extract_institution(self, lines: List[str], degree: Optional[str]) -> Optional[str]:
        """Step 4 — Extract Institution from remaining non-degree headers while skipping metrics."""
        remaining_lines = [
            self.BULLET_PATTERN.sub("", l).strip()
            for l in lines[:3]
            if (degree is None or self.BULLET_PATTERN.sub("", l).strip() != degree) 
            and not self.DURATION_PATTERN.search(l)
            and not self.METRIC_KEYWORDS_PATTERN.search(l)
        ]

        if remaining_lines:
            return remaining_lines[0]
        return None

    def _extract_field_of_study(self, block: str) -> Optional[str]:
        """Step 5 — Extract Field of Study via explicit keyword sequence lookup."""
        for field in self.FIELD_KEYWORDS:
            match = re.search(r"\b" + re.escape(field) + r"\b", block.lower())
            if match:
                start, end = match.span()
                return block[start:end].strip()
        return None

    def _extract_duration(self, block: str) -> Tuple[Optional[str], Optional[str]]:
        """Step 6 — Extract Duration bounds."""
        match = self.DURATION_PATTERN.search(block)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None, None

    def _extract_cgpa(self, block: str) -> Optional[str]:
        """Step 7 — Extract CGPA / Percentage data configurations via metrics matching."""
        match = self.CGPA_PATTERN.search(block)
        if match:
            return match.group(1).strip()
        return None