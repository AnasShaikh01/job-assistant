import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Experience
from app.shared.skill_extractor import SkillExtractor

class ExperienceExtractor:
    """
    Extract structured work experience from the
    experience section of a resume using stateful header detection.
    """
    
    BULLET_PATTERN = re.compile(r"^[•●▪◦*\-–—]\s*")
    
    # Stricter matching explicitly requiring Month+Year, MM/YYYY, or YYYY (19xx/20xx)
    DATE_PATTERN = re.compile(
        r"\b((?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4})"
        r"(?:\s*[-–—to]+\s*"
        r"(Present|Current|Now|\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4}))?\b",
        re.IGNORECASE
    )

    JOB_TITLES_DICT = {
        "software engineer": 100, "backend engineer": 100, "frontend engineer": 100, 
        "full stack engineer": 100, "devops engineer": 100, "cloud engineer": 100, 
        "ml engineer": 100, "ai engineer": 100, "data scientist": 100, "data engineer": 100, 
        "backend developer": 95, "frontend developer": 95, "full stack developer": 95, 
        "architect": 90, "lead": 85, "senior": 85, "manager": 80, "consultant": 80, 
        "developer": 75, "engineer": 75, "analyst": 70, "founder": 60, "co-founder": 60, 
        "research engineer": 50, "research assistant": 40, "freelancer": 40, "junior": 30, "intern": 20
    }

    ROLE_AT_COMPANY_PATTERN = re.compile(r"^(.*?)\s+(?:@|at)\s+(.*?)$", re.IGNORECASE)

    # Filtering sets to prevent misidentifying companies
    WORK_MODE_KEYWORDS = {
        "remote", "hybrid", "on-site", "onsite", "full-time", "fulltime", 
        "part-time", "parttime", "contract", "internship", "freelance"
    }
    
    LOCATION_KEYWORDS = {
        "india", "usa", "uk", "london", "new york", "bangalore", "bengaluru",
        "pune", "mumbai", "hyderabad", "chennai", "delhi", "noida", "gurgaon", 
        "san francisco", "california", "texas"
    }
    
    # Matches formats like "Mumbai, India", "San Francisco, CA"
    LOCATION_PATTERN = re.compile(r"^[a-zA-Z\s\.\-]+,\s*[a-zA-Z\s\.\-]+$")

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Experience]:
        if not text.strip():
            return []

        normalized_text = self._normalize_text(text)
        blocks = self._split_blocks(normalized_text)

        experiences = []

        for block in blocks:
            start_date, end_date, cleaned_block = self._extract_dates(block)
            
            lines = [line.strip() for line in cleaned_block.splitlines() if line.strip()]
            if not lines:
                continue

            header_lines, description_lines = self._segment_block(lines)

            role = self._extract_role(header_lines)
            company = self._extract_company(header_lines, role)
            description = self._extract_description(description_lines)
            technologies = self._extract_technologies(description)

            experience = Experience(
                role=role,
                company=company,
                start_date=start_date,
                end_date=end_date,
                description=description,
                technologies=technologies,
            )
            experiences.append(experience)

        return experiences

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _normalize_text(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
        
    def _get_header_signals(self, line: str) -> Tuple[bool, bool]:
        """Analyzes a line to see if it acts as a role or date header anchor."""
        if len(line) > 70 or line.endswith('.'):
            return False, False
        if self.BULLET_PATTERN.search(line):
            return False, False
            
        is_role = any(re.search(r"\b" + re.escape(title) + r"\b", line.lower()) for title in self.JOB_TITLES_DICT.keys()) or \
                  bool(self.ROLE_AT_COMPANY_PATTERN.search(line))
        is_date = bool(self.DATE_PATTERN.search(line))
        
        return is_role, is_date

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 — Split Experience Blocks.
        Uses a robust state machine independent of bullets.
        """
        lines = text.splitlines()
        blocks = []
        current_block = []
        seen_date_in_current = False

        for line in lines:
            is_role, is_date = self._get_header_signals(line)
            
            can_split = False
            if current_block:
                if seen_date_in_current and (is_role or is_date):
                    can_split = True
                elif not seen_date_in_current and len(current_block) >= 3 and is_role:
                    can_split = True

            if can_split:
                blocks.append("\n".join(current_block))
                current_block = []
                seen_date_in_current = False

            current_block.append(line)
            if is_date:
                seen_date_in_current = True

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_dates(self, block: str) -> Tuple[Optional[str], Optional[str], str]:
        match = self.DATE_PATTERN.search(block)
        
        if match:
            start_date = match.group(1).strip() if match.group(1) else match.group(0).strip()
            end_date = match.group(2).strip() if match.group(2) else None
            
            cleaned_block = block.replace(match.group(0), "")
            return start_date, end_date, cleaned_block
            
        return None, None, block

    def _segment_block(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """
        Step 3.5 — Dynamically segment headers from descriptions.
        Relies on bullets and paragraph length rather than strict line counts.
        """
        header_lines = []
        description_lines = []
        hit_description = False
        
        for i, line in enumerate(lines):
            # A line is likely a description if it's a bullet, a long sentence (>70 chars), 
            # or if we've passed an unusually long header block (>5 lines) without seeing either.
            is_bullet = bool(self.BULLET_PATTERN.search(line))
            is_paragraph = len(line) > 70
            
            if not hit_description and (is_bullet or is_paragraph or i >= 5):
                hit_description = True
            
            if hit_description:
                description_lines.append(line)
            else:
                header_lines.append(line)
                
        return header_lines, description_lines

    def _extract_role(self, header_lines: List[str]) -> Optional[str]:
        if not header_lines:
            return None

        for line in header_lines:
            match = self.ROLE_AT_COMPANY_PATTERN.search(line)
            if match:
                return match.group(1).strip()

        highest_score = 0
        best_role = header_lines[0] 

        for line in header_lines:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            for title, score in self.JOB_TITLES_DICT.items():
                if re.search(r"\b" + re.escape(title) + r"\b", clean_line.lower()):
                    if score > highest_score:
                        highest_score = score
                        best_role = clean_line

        return re.sub(r"[\-\|:,]+$", "", best_role).strip()

    def _extract_company(self, header_lines: List[str], role: Optional[str]) -> Optional[str]:
        if not header_lines:
            return None

        for line in header_lines:
            match = self.ROLE_AT_COMPANY_PATTERN.search(line)
            if match:
                return match.group(2).strip()

        remaining_lines = [
            line for line in header_lines 
            if line.strip() and (not role or line.strip() != role)
        ]
        
        for r_line in remaining_lines:
            clean_line = re.sub(r"[\-\|:,]+$", "", r_line).strip()
            lower_clean = clean_line.lower()
            
            if lower_clean in self.WORK_MODE_KEYWORDS or lower_clean in self.LOCATION_KEYWORDS:
                continue
                
            if self.LOCATION_PATTERN.match(clean_line):
                continue
                
            return clean_line
            
        return None

    def _extract_description(self, description_lines: List[str]) -> str:
        return "\n".join(description_lines).strip()

    def _extract_technologies(self, description: str) -> List[str]:
        if not description:
            return []
        return self.skill_extractor.extract(description)