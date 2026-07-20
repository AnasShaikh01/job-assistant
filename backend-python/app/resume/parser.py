import re
from typing import Dict, List, Set

class ResumeSectionParser:
    """
    Splits a cleaned resume into logical sections.
    Maintains stateless parsing logic, relying purely on a centralized registry 
    and deterministic validation heuristics. Ensures backward compatibility 
    by pre-populating all canonical sections.
    """
    
    SECTION_REGISTRY: Dict[str, Set[str]] = {
        "summary": {"summary", "professional summary", "profile", "objective", "career objective", "executive summary", "about me", "professional profile"},
        "skills": {"skills", "technical skills", "core competencies", "technical expertise", "tech stack", "technology stack", "key skills", "professional skills", "competencies", "technical competencies", "it skills"},
        "experience": {"experience", "work experience", "professional experience", "employment history", "career history", "work history", "professional background"},
        "projects": {"projects", "academic projects", "personal projects", "key projects", "technical projects"},
        "education": {"education", "academic background", "qualifications", "academics", "academic profile", "education and credentials"},
        "certifications": {"certifications", "certificates", "licenses", "courses", "trainings"},
        "achievements": {"achievements", "awards", "honors", "accomplishments", "accolades"},
        "languages": {"languages", "language proficiency"},
        "volunteer": {"volunteer", "volunteer experience", "community service"},
        "publications": {"publications", "research publications", "papers"},
        "research": {"research", "research experience"},
        "leadership": {"leadership", "leadership experience", "extracurriculars", "extracurricular activities"}
    }

    def __init__(self):
        self._alias_map: Dict[str, str] = {
            alias: canonical
            for canonical, aliases in self.SECTION_REGISTRY.items()
            for alias in aliases
        }

    @classmethod
    def _is_valid_heading_format(cls, line: str) -> bool:
        if not line or len(line) > 100:
            return False
            
        if line.endswith(".") or line.endswith("?"):
            return False
            
        alpha_count = sum(c.isalpha() for c in line)
        if alpha_count < (len(line) * 0.5):
            return False
            
        return True

    @classmethod
    def _normalize_heading(cls, line: str) -> str:
        normalized = line.lower().strip()
        normalized = re.sub(r"[\:\-\|]+$", "", normalized).strip()
        normalized = re.sub(r"[^a-z0-9 &+]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    def parse(self, text: str) -> Dict[str, str]:
        # Pre-populate to guarantee all keys exist for downstream compatibility
        sections: Dict[str, List[str]] = {key: [] for key in self.SECTION_REGISTRY.keys()}
        sections["other_sections"] = []
        
        current_section = "other_sections"
        section_sequence: List[str] = ["other_sections"]
        
        for line in text.splitlines():
            stripped = line.strip()
            
            if not stripped:
                if sections[current_section]:
                    sections[current_section].append("")
                continue

            detected_section = None
            if self._is_valid_heading_format(stripped):
                normalized = self._normalize_heading(stripped)
                if normalized in self._alias_map:
                    detected_section = self._alias_map[normalized]
            
            if detected_section:
                if detected_section != current_section:
                    current_section = detected_section
                    if current_section not in section_sequence:
                        section_sequence.append(current_section)
                continue
                
            sections[current_section].append(line)

        # Build final dictionary with guaranteed keys
        final_output = {key: "" for key in self.SECTION_REGISTRY.keys()}
        final_output["other_sections"] = ""
        
        for sec in section_sequence:
            content = "\n".join(sections[sec]).strip()
            if content:
                final_output[sec] = content
                
        return final_output