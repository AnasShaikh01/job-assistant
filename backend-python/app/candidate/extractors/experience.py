import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Experience
from app.shared.skill_extractor import SkillExtractor

class ExperienceExtractor:
    """
    Extract structured work experience from the
    experience section of a resume.
    """
    # Step 5 - Expanded Date Pattern supporting multi-formats (MM/YYYY, Year Only, Text Month)
    DATE_PATTERN = re.compile(
        r"\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\s/]?\d{2,4}|\d{4})"
        r"\s*[-–—]\s*"
        r"(Present|Current|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\s/]?\d{2,4}|\d{4})\b",
        re.IGNORECASE,
    )

    BULLET_PATTERN = re.compile(r"^[•●▪◦*-]\s*")

    # Step 3 - Job Title Dictionary with matching scoring weights
    JOB_TITLES_DICT = {
        "software engineer": 100,
        "backend engineer": 100,
        "frontend engineer": 100,
        "full stack engineer": 100,
        "devops engineer": 100,
        "cloud engineer": 100,
        "ml engineer": 100,
        "ai engineer": 100,
        "data scientist": 100,
        "data engineer": 100,
        "backend developer": 95,
        "frontend developer": 95,
        "full stack developer": 95,
        "architect": 90,
        "lead": 85,
        "senior": 85,
        "manager": 80,
        "consultant": 80,
        "developer": 75,
        "engineer": 75,
        "analyst": 70,
        "founder": 60,
        "co-founder": 60,
        "research engineer": 50,
        "research assistant": 40,
        "freelancer": 40,
        "junior": 30,
        "intern": 20
    }

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Experience]:
        if not text.strip():
            return []

        # Step 1 — Normalize
        normalized_text = self._normalize_text(text)

        # Step 2 — Split Experience Blocks
        blocks = self._split_blocks(normalized_text)

        experiences = []

        for block in blocks:
            # Step 5 — Extract Dates & Isolate Text
            # We extract dates first and strip them from the block to prevent dates 
            # from appearing inside company names or description heuristics.
            start_date, end_date, cleaned_block = self._extract_dates(block)
            
            lines = [line.strip() for line in cleaned_block.splitlines() if line.strip()]
            if not lines:
                continue

            # Step 3 — Extract Role
            role, _ = self._extract_role(lines)

            # Step 4 — Extract Company
            company = self._extract_company(lines, role)

            # Step 6 — Extract Description (everything except role and company)
            description = self._extract_description(lines, role, company)

            # Step 7 — Extract Technologies
            technologies = self._extract_technologies(description)

            # Step 8 — Build Experience Object
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
        """Step 1 — Normalize text formatting while preserving structural bounds."""
        # Collapse multiple inline spaces/tabs into a single space
        text = re.sub(r"[ \t]+", " ", text)
        # Remove weird characters but preserve line ends, words, metrics, and standard bullet markers
        text = re.sub(r"[^\w\s\.\,\-\–\—\•\●\▪\◦\*\/\:\(\)]", "", text)
        
        # Eliminate empty lines completely
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 — Split Experience Blocks.
        Detects transitions using high-confidence job titles or date boundaries.
        """
        lines = text.splitlines()
        blocks = []
        current_block = []

        for line in lines:
            # Heuristic: Does this line look like the beginning of a brand new job section?
            is_new_job_header = (
                any(title in line.lower() for title in self.JOB_TITLES_DICT.keys()) 
                or self.DATE_PATTERN.search(line)
            )

            if is_new_job_header and current_block and len(current_block) > 1:
                blocks.append("\n".join(current_block))
                current_block = []

            current_block.append(line)

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_role(self, lines: List[str]) -> Tuple[str, int]:
        """Step 3 — Extract Role using a weighted Job Title scoring dictionary."""
        highest_score = 0
        best_role = ""
        target_index = 0

        # Scan the first 3 lines of the block (typical header layout context)
        for idx, line in enumerate(lines[:3]):
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            for title, score in self.JOB_TITLES_DICT.items():
                if re.search(r"\b" + re.escape(title) + r"\b", clean_line.lower()):
                    if score > highest_score:
                        highest_score = score
                        best_role = clean_line
                        target_index = idx

        # Fallback Strategy: If no title keywords match, pick the top line
        if not best_role and lines:
            best_role = self.BULLET_PATTERN.sub("", lines[0]).strip()
            target_index = 0

        return best_role, target_index

    def _extract_company(self, lines: List[str], role: str) -> Optional[str]:
        """Step 4 — Extract Company from remaining early header lines."""
        # Filter out the structural role layout line
        remaining_header_lines = [
            self.BULLET_PATTERN.sub("", l).strip() 
            for l in lines[:3] 
            if self.BULLET_PATTERN.sub("", l).strip() != role
        ]
        
        if remaining_header_lines:
            return remaining_header_lines[0]
            
        return None

    def _extract_dates(self, block: str) -> Tuple[Optional[str], Optional[str], str]:
        """Step 5 — Extract Dates via Regex and strip them from the block body."""
        match = self.DATE_PATTERN.search(block)
        if match:
            start_date = match.group(1).strip()
            end_date = match.group(2).strip()
            # Clean out the exact date segment to isolate pure textual contexts
            cleaned_block = block.replace(match.group(0), "")
            return start_date, end_date, cleaned_block
            
        return None, None, block

    def _extract_description(self, lines: List[str], role: str, company: Optional[str]) -> str:
        """Step 6 — Extract Description (everything minus headers)."""
        description_lines = []
        for line in lines:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            # If the text matches header configurations, bypass it
            if clean_line == role or clean_line == company:
                continue
            description_lines.append(clean_line)

        return "\n".join(description_lines).strip()

    def _extract_technologies(self, description: str) -> List[str]:
        """Step 7 — Run SkillExtractor on description data."""
        if not description:
            return []
        return self.skill_extractor.extract(description)