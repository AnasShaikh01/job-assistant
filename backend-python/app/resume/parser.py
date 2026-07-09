import re
from typing import Dict

class ResumeSectionParser:
    """
    Splits a cleaned resume into logical sections.
    """
    SECTION_PATTERNS = {
        "summary": {"summary", "professional summary", "profile", "objective", "career objective"},
        "skills": {"skills", "technical skills", "core competencies", "technical expertise"},
        "experience": {"experience", "work experience", "professional experience", "employment history"},
        "projects": {"projects", "academic projects", "personal projects"},
        "education": {"education", "academic background", "qualifications"},
        "certifications": {"certifications", "certificates", "licenses"},
        "achievements": {"achievements", "awards", "honors"}
    }

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^a-zA-Z ]", "", text).strip().lower()

    def parse(self, text: str) -> Dict[str, str]:
        sections = {key: "" for key in self.SECTION_PATTERNS.keys()}
        current_section = None
        lines = text.splitlines()

        for line in lines:
            if not line.strip():
                if current_section:
                    sections[current_section] += "\n"
                continue

            normalized = self._normalize(line)
            detected = None

            # FIX: Check for exact matches to avoid mid-line false positives
            for section, headings in self.SECTION_PATTERNS.items():
                if normalized in headings or any(normalized == h for h in headings):
                    detected = section
                    break

            if detected:
                current_section = detected
                continue

            if current_section:
                sections[current_section] += line + "\n"

        return {key: value.strip() for key, value in sections.items()}