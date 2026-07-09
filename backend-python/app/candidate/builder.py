import re
from typing import Dict, List

# Import the Canonical CKB Schemas
from app.candidate.schemas import (
    CandidateKnowledgeBase,
    Experience,
    Education,
    Project,
    Certification,
    Links
)

# Import the Independent Extraction Microservices
from app.candidate.extractors.experience import ExperienceExtractor
from app.candidate.extractors.education import EducationExtractor
from app.candidate.extractors.project import ProjectExtractor
from app.candidate.extractors.certification import CertificationExtractor
from app.candidate.extractors.links import LinksExtractor

class CandidateBuilder:
    """
    Orchestration Engine that aggregates unstructured, sectioned resume text 
    and builds the canonical CandidateKnowledgeBase (CKB) schema[cite: 4, 134, 332].
    
    Following the 'Parse Once' development philosophy, everything is converted 
    into structured data at this step so the raw resume is discarded[cite: 87, 303, 309].
    """

    def __init__(self):
        # Initialize the deterministic extraction engines
        self.experience_extractor = ExperienceExtractor()
        self.education_extractor = EducationExtractor()
        self.project_extractor = ProjectExtractor()
        self.certification_extractor = CertificationExtractor()
        self.links_extractor = LinksExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def build(self, sections: Dict[str, str], skills: List[str]) -> CandidateKnowledgeBase:
        """
        Orchestrates top-down processing over isolated textual data segments
        to return a validated, structured CandidateKnowledgeBase instance[cite: 74, 332].
        """
        return CandidateKnowledgeBase(
            summary=self._build_summary(sections),
            skills=self._build_skills(skills),
            experience=self._build_experience(sections),
            education=self._build_education(sections),
            projects=self._build_projects(sections),
            certifications=self._build_certifications(sections),
            links=self._build_links(sections)
        )

    # ==========================================================
    # Private Section-Specific Builders
    # ==========================================================

    def _build_summary(self, sections: Dict[str, str]) -> str:
        """Extracts and sanitizes the candidate's professional profile summary[cite: 78]."""
        raw_summary = sections.get("summary", "").strip()
        return raw_summary

    def _build_skills(self, skills: List[str]) -> List[str]:
        """Passes through the validated downstream skill extraction collection[cite: 79]."""
        return sorted(set(skill.strip() for skill in skills if skill.strip()))

    def _build_experience(self, sections: Dict[str, str]) -> List[Experience]:
        """Routes the raw experience string segment to the ExperienceExtractor[cite: 81]."""
        experience_text = sections.get("experience", "").strip()
        if not experience_text:
            return []
        return self.experience_extractor.extract(experience_text)

    def _build_education(self, sections: Dict[str, str]) -> List[Education]:
        """Routes the raw education string segment to the EducationExtractor[cite: 82]."""
        education_text = sections.get("education", "").strip()
        if not education_text:
            return []
        return self.education_extractor.extract(education_text)

    def _build_projects(self, sections: Dict[str, str]) -> List[Project]:
        """Routes the raw project string segment to the ProjectExtractor[cite: 80]."""
        project_text = sections.get("projects", "").strip()
        if not project_text:
            return []
        return self.project_extractor.extract(project_text)

    def _build_certifications(self, sections: Dict[str, str]) -> List[Certification]:
        """Routes the raw certifications string segment to the CertificationExtractor[cite: 83]."""
        certifications_text = sections.get("certifications", "").strip()
        if not certifications_text:
            return []
        return self.certification_extractor.extract(certifications_text)

    def _build_links(self, sections: Dict[str, str]) -> Links:
        """
        Extracts structural, personal social and portfolio anchors 
        scanned across the entire consolidated resume data mapping[cite: 84, 85].
        """
        text_to_scan = "\n".join(sections.values())
        return self.links_extractor.extract(text_to_scan)