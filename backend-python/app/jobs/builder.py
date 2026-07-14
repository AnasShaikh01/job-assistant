import re
from typing import Dict, List, Optional
from .schemas import JobKnowledgeBase, CompanyInfo, SalaryDetails

class JobBuilder:
    """
    Transforms parsed sections, skills, and keywords into a validated 
    JobKnowledgeBase (JKB) Pydantic model.
    Uses deterministic regex to extract metadata like salary, experience, and work mode.
    """

    def build(self, sections: Dict[str, str], skills: List[str], keywords: List[str]) -> JobKnowledgeBase:
        # Combine header and salary sections for metadata extraction
        header_text = sections.get("header", "")
        salary_text = sections.get("salary", "")
        metadata_context = f"{header_text}\n{salary_text}"
        
        # 1. Extract List-based Sections
        responsibilities = self._text_to_list(sections.get("responsibilities", ""))
        
        # Merge qualifications and preferred_qualifications seamlessly
        combined_qualifications = sections.get("qualifications", "")
        preferred_qualifications = sections.get("preferred_qualifications", "")
        if preferred_qualifications:
            combined_qualifications += f"\n{preferred_qualifications}"
            
        qualifications = self._text_to_list(combined_qualifications)
        benefits = self._text_to_list(sections.get("benefits", ""))
        
        education = self._extract_education(combined_qualifications + "\n" + header_text)

        # 2. Extract Metadata via Regex
        role = self._extract_role(header_text)
        work_mode = self._extract_work_mode(header_text)
        employment_type = self._extract_employment_type(header_text)
        years_of_experience = self._extract_experience(combined_qualifications + "\n" + header_text)
        salary_details = self._extract_salary(metadata_context)
        locations = self._extract_locations(header_text)

        # 3. Populate Company Info
        # TODO: Extract company name from header, company section, or URL in a future pass
        company_info = CompanyInfo(
            name=None, 
            about=sections.get("company", "").strip() or None,
            industry=None
        )

        # 4. Construct and Validate JKB
        return JobKnowledgeBase(
            company=company_info,
            role=role,
            locations=locations,
            employment_type=employment_type,
            work_mode=work_mode,
            years_of_experience=years_of_experience,
            skills=skills,
            responsibilities=responsibilities,
            education=education,
            qualifications=qualifications,
            benefits=benefits,
            salary=salary_details,
            keywords=keywords
        )

    def _text_to_list(self, text: str) -> List[str]:
        """Converts a section block into a clean list of bullet points."""
        if not text:
            return []
        # Split by newlines and remove leading bullet dashes/markers
        lines = [re.sub(r"^[\-\*•▪►]\s*", "", line.strip()) for line in text.splitlines()]
        return [line for line in lines if line]

    def _extract_role(self, header_text: str) -> Optional[str]:
        """Assumes the first non-empty line of the header is the job title."""
        lines = [line.strip() for line in header_text.splitlines() if line.strip()]
        return lines[0] if lines else None

    def _extract_work_mode(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(remote|work from home|wfh)\b", text_lower):
            return "Remote"
        if re.search(r"\b(hybrid)\b", text_lower):
            return "Hybrid"
        if re.search(r"\b(on-site|onsite|in-office|in office)\b", text_lower):
            return "On-site"
        return None

    def _extract_employment_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(full-time|full time|fulltime)\b", text_lower):
            return "Full-time"
        if re.search(r"\b(part-time|part time|parttime)\b", text_lower):
            return "Part-time"
        if re.search(r"\b(contract|contractor)\b", text_lower):
            return "Contract"
        if re.search(r"\b(intern|internship)\b", text_lower):
            return "Internship"
        if re.search(r"\b(freelance|freelancer)\b", text_lower):
            return "Freelance"
        if re.search(r"\b(temporary|temp)\b", text_lower):
            return "Temporary"
        return None

    def _extract_experience(self, text: str) -> Optional[str]:
        """Looks for patterns like '3-5 years', '5+ years', etc."""
        match = re.search(r"(\d+\+?(?:\s*(?:-|to)\s*\d+)?)\s*(?:\+)?\s*years?(?:\s*of\s*experience)?", text, re.IGNORECASE)
        if match:
            return f"{match.group(1).strip()} years"
        return None

    def _extract_education(self, text: str) -> List[str]:
        """Deterministic extraction of common degree requirements."""
        education = []
        if re.search(r"\b(bachelor'?s|b\.?s\.?|b\.?a\.?|b\.?e\.?|undergraduate)\b", text, re.IGNORECASE):
            education.append("Bachelor's Degree")
        if re.search(r"\b(master'?s|m\.?s\.?|m\.?a\.?|mba)\b", text, re.IGNORECASE):
            education.append("Master's Degree")
        if re.search(r"\b(ph\.?d\.?|doctorate)\b", text, re.IGNORECASE):
            education.append("Ph.D")
        return education

    def _extract_salary(self, text: str) -> SalaryDetails:
        """
        Extracts basic salary ranges. 
        Example: '$100,000 - $120,000' or '$100k - $120k'
        """
        details = SalaryDetails()
        
        range_match = re.search(
            r"\$\s*([\d,]+(?:k)?)\s*(?:-|to)\s*\$\s*([\d,]+(?:k)?)", 
            text, 
            re.IGNORECASE
        )
        
        if range_match:
            try:
                min_val = self._parse_currency(range_match.group(1))
                max_val = self._parse_currency(range_match.group(2))
                details.min_amount = min_val
                details.max_amount = max_val
            except ValueError:
                pass
                
        if re.search(r"\b(per year|annually|/yr|/year)\b", text, re.IGNORECASE):
            details.period = "yearly"
        elif re.search(r"\b(per hour|/hr|/hour|hourly)\b", text, re.IGNORECASE):
            details.period = "hourly"
        elif re.search(r"\b(per month|/mo|/month|monthly)\b", text, re.IGNORECASE):
            details.period = "monthly"
            
        return details

    def _parse_currency(self, value: str) -> float:
        """Converts strings like '100,000' or '100k' to floats."""
        value = value.lower().replace(",", "")
        if "k" in value:
            return float(value.replace("k", "")) * 1000
        return float(value)

    def _extract_locations(self, text: str) -> List[str]:
        """
        TODO: Implement geocoding or NER to extract multiple locations.
        Returning an empty list for now.
        """
        return []