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
    and builds the canonical CandidateKnowledgeBase (CKB) schema.
    
    Following the 'Parse Once' development philosophy, everything is converted 
    into structured data at this step so the raw resume is discarded.
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

    def build(self, sections: Dict[str, str], skills: List[str], embedded_links: List[str]) -> CandidateKnowledgeBase:
        """
        Orchestrates top-down processing over isolated textual data segments
        to return a validated, structured CandidateKnowledgeBase instance.
        """
        return CandidateKnowledgeBase(
            summary=self._build_summary(sections),
            skills=self._build_skills(skills),
            experience=self._build_experience(sections),
            education=self._build_education(sections),
            projects=self._build_projects(sections),
            certifications=self._build_certifications(sections),
            links=self._build_links(sections, embedded_links)
        )

    # ==========================================================
    # Private Section-Specific Builders
    # ==========================================================

    def _build_summary(self, sections: Dict[str, str]) -> str:
        """Extracts and sanitizes the candidate's professional profile summary."""
        raw_summary = sections.get("summary", "").strip()
        return raw_summary

    def _build_skills(self, skills: List[str]) -> List[str]:
        """Passes through the validated downstream skill extraction collection."""
        return sorted(set(skill.strip() for skill in skills if skill.strip()))

    def _build_experience(self, sections: Dict[str, str]) -> List[Experience]:
        """Routes the raw experience string segment to the ExperienceExtractor."""
        experience_text = sections.get("experience", "").strip()
        if not experience_text:
            return []
        return self.experience_extractor.extract(experience_text)

    def _build_education(self, sections: Dict[str, str]) -> List[Education]:
        """Routes the raw education string segment to the EducationExtractor."""
        education_text = sections.get("education", "").strip()
        if not education_text:
            return []
        return self.education_extractor.extract(education_text)

    def _build_projects(self, sections: Dict[str, str]) -> List[Project]:
        """Routes the raw project string segment to the ProjectExtractor."""
        project_text = sections.get("projects", "").strip()
        if not project_text:
            return []
        return self.project_extractor.extract(project_text)

    def _build_certifications(self, sections: Dict[str, str]) -> List[Certification]:
        """Routes the raw certifications string segment to the CertificationExtractor."""
        certifications_text = sections.get("certifications", "").strip()
        if not certifications_text:
            return []
        return self.certification_extractor.extract(certifications_text)

    def _build_links(self, sections: Dict[str, str], embedded_links: List[str]) -> Links:
        """
        Extracts structural, personal social and portfolio anchors 
        scanned across the entire consolidated resume data mapping, 
        plus any hidden URLs extracted via metadata parsing.
        """
        text_to_scan = "\n".join(sections.values())
        
        parts = [text_to_scan]
        if embedded_links:
            parts.extend(embedded_links)
            
        combined = "\n".join(parts)
        
        return self.links_extractor.extract(combined)