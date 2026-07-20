import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Education

class EducationExtractor:
    """
    Extract structured education data from the
    education section of a resume using stateful detection and contextual parsing.
    """
    
    DURATION_PATTERN = re.compile(
        r"\b((?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4})"
        r"(?:\s*[-–—to]+\s*"
        r"(Present|Current|Now|\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4}))?\b",
        re.IGNORECASE,
    )

    CGPA_PATTERN = re.compile(
        r"\b(?:CGPA|GPA|Percentage|Score|Grade)\s*[:\-–—]?\s*(\d{1,2}(?:\.\d{1,2})?(?:\s*/\s*\d{1,2})?%?)",
        re.IGNORECASE,
    )

    METRIC_KEYWORDS_PATTERN = re.compile(r"\b(cgpa|gpa|percentage|score|grade)\b", re.IGNORECASE)
    BULLET_PATTERN = re.compile(r"^[•●▪◦*\-–—]\s*")

    DEGREE_KEYWORDS = [
        "bachelor of engineering", "bachelor of technology", "master of technology",
        "bachelor of science", "master of science", "bachelor of arts", "master of arts",
        "bachelor", "master", "bachelors", "masters", "b.tech", "m.tech", "b.e", "m.e", 
        "b.com", "m.com", "bba", "llb", "llm", "b.sc", "m.sc", "b.a", "m.a", "bca", "mca", 
        "mba", "phd", "diploma", "bs", "ms", "be", "me"
    ]

    FIELD_KEYWORDS = [
        "computer science", "information technology", "software engineering",
        "artificial intelligence", "machine learning", "data science",
        "cyber security", "electronics", "electrical engineering",
        "mechanical engineering", "civil engineering", "business administration",
        "commerce", "finance", "mathematics", "physics", "chemistry", "economics"
    ]

    INSTITUTION_KEYWORDS = [
        "university", "college", "institute", "school", "academy", "polytechnic"
    ]

    LOCATION_KEYWORDS = {
        "india", "usa", "uk", "london", "new york", "bangalore", "bengaluru",
        "pune", "mumbai", "hyderabad", "chennai", "delhi", "noida", "gurgaon", 
        "san francisco", "california", "texas"
    }
    LOCATION_PATTERN = re.compile(r"^[a-zA-Z\s\.\-]+,\s*[a-zA-Z\s\.\-]+$")

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Education]:
        if not text.strip():
            return []

        normalized_text = self._normalize_text(text)
        blocks = self._split_blocks(normalized_text)

        education_list = []

        for block in blocks:
            start_year, end_year, cleaned_block = self._extract_duration(block)
            
            lines = [line.strip() for line in cleaned_block.splitlines() if line.strip()]
            if not lines:
                continue

            degree = self._extract_degree(lines)
            institution = self._extract_institution(lines, degree)
            field_of_study = self._extract_field_of_study(lines, degree)
            cgpa = self._extract_cgpa(block)

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
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _get_header_signals(self, line: str) -> Tuple[bool, bool]:
        clean_line = self.BULLET_PATTERN.sub("", line).strip().lower()
        if not clean_line or len(line) > 80:
            return False, False
            
        is_degree = any(re.search(r"\b" + re.escape(deg) + r"\b", clean_line) for deg in self.DEGREE_KEYWORDS)
        is_date = bool(self.DURATION_PATTERN.search(line))
        return is_degree, is_date

    def _split_blocks(self, text: str) -> List[str]:
        lines = text.splitlines()
        blocks = []
        current_block = []
        seen_degree_in_current = False

        for line in lines:
            is_degree, is_date = self._get_header_signals(line)
            
            can_split = False
            if current_block:
                if seen_degree_in_current and is_degree:
                    can_split = True
                elif not seen_degree_in_current and len(current_block) >= 3 and is_degree:
                    can_split = True

            if can_split:
                blocks.append("\n".join(current_block))
                current_block = []
                seen_degree_in_current = False

            current_block.append(line)
            if is_degree:
                seen_degree_in_current = True

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_duration(self, block: str) -> Tuple[Optional[str], Optional[str], str]:
        match = self.DURATION_PATTERN.search(block)
        if match:
            start_date = match.group(1).strip() if match.group(1) else match.group(0).strip()
            end_date = match.group(2).strip() if match.group(2) else None
            
            cleaned_block = block.replace(match.group(0), "")
            return start_date, end_date, cleaned_block
            
        return None, None, block

    def _extract_degree(self, lines: List[str]) -> Optional[str]:
        for line in lines[:3]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            for degree in self.DEGREE_KEYWORDS:
                if re.search(r"\b" + re.escape(degree) + r"\b", clean_line.lower()):
                    # FIXED: Removed the hyphen from the split array to preserve fields appended with '-'
                    parts = re.split(r"[\|:,]", clean_line)
                    for part in parts:
                        if re.search(r"\b" + re.escape(degree) + r"\b", part.lower()):
                            return part.strip()
                    return clean_line
        return None

    def _extract_institution(self, lines: List[str], degree: Optional[str]) -> Optional[str]:
        candidates = []
        
        for line in lines[:4]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()

            if degree and (clean_line == degree or degree in clean_line):
                continue
            if self.DURATION_PATTERN.search(line) or self.METRIC_KEYWORDS_PATTERN.search(line):
                continue
            
            clean_no_punct = re.sub(r"[\-\|:,]+$", "", clean_line).strip()
            
            if clean_no_punct.lower() in self.LOCATION_KEYWORDS:
                continue
            if self.LOCATION_PATTERN.match(clean_no_punct):
                continue
                
            if clean_no_punct:
                candidates.append(clean_no_punct)

        for candidate in candidates:
            if any(kw in candidate.lower() for kw in self.INSTITUTION_KEYWORDS):
                return candidate
                
        if candidates:
            return candidates[0]
            
        return None

    def _extract_field_of_study(self, lines: List[str], degree: Optional[str]) -> Optional[str]:
        if degree:
            match = re.search(r"\bin\s+([a-zA-Z\s&]+?)(?:\s+at\b|\s*,|\s*\(|$)", degree, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) > 2 and not any(kw in extracted.lower() for kw in self.INSTITUTION_KEYWORDS):
                    return extracted
                    
            match = re.search(r"[\-–—]\s*([a-zA-Z\s&]+?)(?:\s+at\b|\s*,|\s*\(|$)", degree, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) > 2 and not any(kw in extracted.lower() for kw in self.INSTITUTION_KEYWORDS):
                    return extracted

        full_text = "\n".join(lines).lower()
        for field in self.FIELD_KEYWORDS:
            match = re.search(r"\b" + re.escape(field) + r"\b", full_text)
            if match:
                start, end = match.span()
                return full_text[start:end].title().strip()
                
        return None

    def _extract_cgpa(self, block: str) -> Optional[str]:
        match = self.CGPA_PATTERN.search(block)
        if match:
            return match.group(1).strip()
        return None