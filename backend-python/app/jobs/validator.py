import re
from typing import Dict
from .schemas import JobKnowledgeBase

class JobValidator:
    """
    Applies post-build sanity checks and recovery rules to the JobKnowledgeBase.
    Catches anomalies like excessively long roles, unrealistic experience years, 
    and incomplete salary data.
    """

    def validate(self, jkb: JobKnowledgeBase, sections: Dict[str, str]) -> JobKnowledgeBase:
        
        # 1. Role length & structure validation
        if jkb.role:
            word_count = len(jkb.role.split())
            # Matches a period, exclamation, or question mark followed by a space and a capital letter.
            # This identifies actual sentences rather than abbreviations like "Sr. Engineer"
            has_multiple_sentences = bool(re.search(r"[.!?]\s+[A-Z]", jkb.role))
            
            # Reject if it's >12 words or contains multiple full sentences (likely a paragraph leak)
            if word_count > 12 or has_multiple_sentences:
                jkb.role = None
            
        # 2. Experience sanity check
        if jkb.years_of_experience:
            match = re.search(r"(\d+(?:\.\d+)?)", jkb.years_of_experience)
            # Increased to 30 to safely accommodate genuine executive/VP level requirements
            if match and float(match.group(1)) > 30:
                jkb.years_of_experience = None

        # 3. Salary Cleanup: Remove currency if no amounts were found
        if jkb.salary and jkb.salary.currency:
            if jkb.salary.min_amount is None and jkb.salary.max_amount is None:
                jkb.salary.currency = None
                jkb.salary.period = None

        # 4. Recover empty responsibilities
        if not jkb.responsibilities:
            # Broaden search to include header and qualifications if the parser missed it
            fallback_text = "\n".join([
                sections.get("header", ""),
                sections.get("responsibilities", ""),
                sections.get("qualifications", "")
            ])
            bullets = self._extract_bullets(fallback_text)
            if len(bullets) >= 3:
                jkb.responsibilities = bullets

        # 5. Recover empty qualifications
        if not jkb.qualifications:
            # Search the raw parsed sections directly rather than checking the JKB model
            fallback_text = "\n".join([
                sections.get("qualifications", ""),
                sections.get("preferred_qualifications", ""),
                sections.get("header", "")
            ])
            bullets = self._extract_bullets(fallback_text)
            if len(bullets) >= 3:
                jkb.qualifications = bullets

        return jkb

    def _extract_bullets(self, text: str) -> list[str]:
        """Extracts bulleted lines from a block of text."""
        if not text:
            return []
        lines = text.splitlines()
        bullets = []
        for line in lines:
            line = line.strip()
            # Match standard ATS bullets
            if line.startswith("-") or line.startswith("•"):
                clean_line = re.sub(r"^[\-\*•▪►]\s*", "", line)
                if len(clean_line) > 10:  # Ignore tiny artifact bullets
                    bullets.append(clean_line)
        return bullets