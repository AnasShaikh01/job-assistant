import re
from typing import Dict, List, Optional
from .schemas import JobKnowledgeBase, CompanyInfo, SalaryDetails

class JobBuilder:
    """
    Transforms parsed sections, skills, and keywords into a validated 
    JobKnowledgeBase (JKB) Pydantic model.
    Uses robust deterministic regex to extract deep metadata.
    """

    def build(self, sections: Dict[str, str], skills: List[str], keywords: List[str]) -> JobKnowledgeBase:
        header_text = sections.get("header", "")
        company_text = sections.get("company", "")
        qualifications_text = sections.get("qualifications", "")
        preferred_text = sections.get("preferred_qualifications", "")
        salary_text = sections.get("salary", "")
        
        full_context = "\n".join(sections.values())
        metadata_context = f"{header_text}\n{salary_text}"
        combined_quals = f"{qualifications_text}\n{preferred_text}".strip()

        # 1. Extract List-based Sections
        responsibilities = self._text_to_list(sections.get("responsibilities", ""))
        qualifications = self._text_to_list(combined_quals)
        benefits = self._text_to_list(sections.get("benefits", ""))
        education = self._extract_education(combined_quals + "\n" + header_text)

        # 2. Extract Deep Metadata
        role = self._extract_role(header_text)
        department = self._extract_department(full_context)
        locations = self._extract_locations(full_context)
        work_mode = self._extract_work_mode(full_context)
        employment_type = self._extract_employment_type(full_context)
        experience_years = self._extract_experience_years(combined_quals + "\n" + header_text)
        experience_level = self._extract_experience_level(header_text + "\n" + combined_quals)
        salary_details = self._extract_salary(metadata_context)

        # 3. Populate Company Info
        company_info = CompanyInfo(
            name=self._extract_company_name(header_text, company_text),
            about=company_text.strip() or None,
            industry=self._infer_industry(company_text)
        )

        # 4. Construct and Validate JKB
        return JobKnowledgeBase(
            company=company_info,
            role=role,
            department=department,
            locations=locations,
            employment_type=employment_type,
            work_mode=work_mode,
            experience_level=experience_level,
            years_of_experience=experience_years,
            skills=skills,
            responsibilities=responsibilities,
            education=education,
            qualifications=qualifications,
            benefits=benefits,
            salary=salary_details,
            keywords=keywords
        )

    def _text_to_list(self, text: str) -> List[str]:
        if not text:
            return []
        lines = [re.sub(r"^[\-\*•▪►]\s*", "", line.strip()) for line in text.splitlines()]
        return [line for line in lines if line]

    def _extract_role(self, header_text: str) -> Optional[str]:
        """Scores the first 5 lines to find the most likely job title."""
        lines = [line.strip() for line in header_text.splitlines() if line.strip()]
        role_keywords = r"\b(Engineer|Developer|Architect|Scientist|Analyst|Manager|Designer|Consultant|Intern|Lead|Director|Specialist|Administrator|QA|SDET|Tester|DevOps|Cloud|Security|Support|Product Owner|Researcher)\b"
        
        # 1. Prefer lines containing known role keywords
        for line in lines[:5]:
            if re.search(role_keywords, line, re.IGNORECASE):
                return line
                
        # 2. Fallback: Return first valid line that isn't obvious boilerplate
        for line in lines[:5]:
            if not re.search(r"\b(location|apply|remote|full-time|salary|company|careers?)\b", line, re.IGNORECASE):
                return line
                
        return None

    def _extract_department(self, text: str) -> Optional[str]:
        match = re.search(r"\b(Engineering|Product|Design|Sales|Marketing|HR|Human Resources|Finance|Operations|Data)\s+(?:Department|Team)\b", text, re.IGNORECASE)
        if match:
            return match.group(1).title()
        
        match_explicit = re.search(r"Department:\s*([A-Za-z\s&]+)", text, re.IGNORECASE)
        if match_explicit:
            return match_explicit.group(1).strip().title()
            
        return None

    def _extract_experience_level(self, text: str) -> Optional[str]:
        levels = {
            r"\b(intern|internship)\b": "Intern",
            r"\b(junior|entry[- ]?level|trainee|graduate)\b": "Junior",
            r"\b(mid[- ]?level|intermediate)\b": "Mid-Level",
            r"\b(senior|snr|sr\.?)\b": "Senior",
            r"\b(lead|principal|staff|manager|director|vp|head)\b": "Lead/Manager"
        }
        text_lower = text.lower()
        for pattern, level in levels.items():
            if re.search(pattern, text_lower):
                return level
        return None

    def _extract_experience_years(self, text: str) -> Optional[str]:
        match = re.search(
            r"(?:minimum\s+(?:of\s+)?|at\s+least\s+)?(\d+(?:\.\d+)?(?:\s*(?:-|to)\s*\d+(?:\.\d+)?)?)\s*(\+)?\s*(?:years?|yrs?|yoe)(?:\s*\+)?(?:\s*of\s*experience)?", 
            text, 
            re.IGNORECASE
        )
        if match:
            val = match.group(1).strip()
            if '+' in match.group(0) and '+' not in val:
                val += "+"
            return f"{val} years"
        return None

    def _extract_work_mode(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(remote|work from home|wfh|telecommute)\b", text_lower):
            return "Remote"
        if re.search(r"\b(hybrid)\b", text_lower):
            return "Hybrid"
        if re.search(r"\b(on-site|onsite|in-office|in office)\b", text_lower):
            return "On-site"
        return None

    def _extract_employment_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(full-time|full time|fulltime|permanent)\b", text_lower):
            return "Full-time"
        if re.search(r"\b(part-time|part time|parttime)\b", text_lower):
            return "Part-time"
        if re.search(r"\b(contract|contractor|freelance)\b", text_lower):
            return "Contract"
        if re.search(r"\b(fixed[- ]?term)\b", text_lower):
            return "Fixed Term"
        if re.search(r"\b(temporary|temp)\b", text_lower):
            return "Temporary"
        if re.search(r"\b(casual)\b", text_lower):
            return "Casual"
        if re.search(r"\b(intern|internship)\b", text_lower):
            return "Internship"
        return None

    def _extract_education(self, text: str) -> List[str]:
        education = set()
        if re.search(r"\b(bachelor'?s|b\.?s\.?|b\.?a\.?|b\.?e\.?|b\.?tech|undergraduate|degree)\b", text, re.IGNORECASE):
            education.add("Bachelor's Degree")
        if re.search(r"\b(master'?s|m\.?s\.?|m\.?a\.?|m\.?tech|mba)\b", text, re.IGNORECASE):
            education.add("Master's Degree")
        if re.search(r"\b(ph\.?d\.?|doctorate)\b", text, re.IGNORECASE):
            education.add("Ph.D")
        return sorted(list(education))

    def _extract_salary(self, text: str) -> SalaryDetails:
        details = SalaryDetails()
        
        western_match = re.search(
            r"([\$£€])\s*([\d,]+(?:[kKmM])?)\s*(?:-|to)\s*[\$£€]?\s*([\d,]+(?:[kKmM])?)", 
            text
        )
        if western_match:
            try:
                symbol = western_match.group(1)
                details.currency = 'USD' if symbol == '$' else 'GBP' if symbol == '£' else 'EUR'
                details.min_amount = self._parse_currency(western_match.group(2))
                details.max_amount = self._parse_currency(western_match.group(3))
            except ValueError:
                pass

        if not western_match:
            inr_match = re.search(
                r"(₹|INR)?\s*([\d,]+(?:(?:\.\d+)?))\s*(?:-|to)\s*(?:₹|INR)?\s*([\d,]+(?:(?:\.\d+)?))\s*(LPA|lakhs?)?", 
                text, 
                re.IGNORECASE
            )
            if inr_match and (inr_match.group(1) or inr_match.group(4)):
                try:
                    details.currency = 'INR'
                    min_val = float(inr_match.group(2).replace(",", ""))
                    max_val = float(inr_match.group(3).replace(",", ""))
                    
                    if inr_match.group(4) and re.search(r"LPA|lakh", inr_match.group(4), re.IGNORECASE):
                        min_val *= 100000
                        max_val *= 100000
                        details.period = "yearly"
                        
                    details.min_amount = min_val
                    details.max_amount = max_val
                except ValueError:
                    pass

        if not details.period:
            if re.search(r"\b(per year|annually|/yr|/year|p\.a\.?)\b", text, re.IGNORECASE):
                details.period = "yearly"
            elif re.search(r"\b(per hour|/hr|/hour|hourly)\b", text, re.IGNORECASE):
                details.period = "hourly"
            elif re.search(r"\b(per month|/mo|/month|monthly)\b", text, re.IGNORECASE):
                details.period = "monthly"
            
        return details

    def _parse_currency(self, value: str) -> float:
        value = value.lower().replace(",", "").replace(" ", "")
        if "k" in value:
            return float(value.replace("k", "")) * 1000
        if "m" in value:
            return float(value.replace("m", "")) * 1000000
        return float(value)

    def _extract_company_name(self, header_text: str, company_text: str) -> Optional[str]:
        text_to_search = f"{header_text}\n{company_text}"
        
        # Expanded to cover common international and regional entity suffixes
        suffixes = r"(?:Inc\.?|LLC|Ltd\.?|Corp(?:oration|\.)?|LLP|Limited|Technologies|Solutions|Pvt\.?\s*Ltd\.?)"
        
        patterns = [
            r"Company:\s*([A-Z][\w\s&.\-']+?)(?:\n|$)",
            r"\b([A-Z][\w\s&.\-']+?)\s+is hiring\b",
            rf"Join\s+([A-Z][\w\s&.\-']+?)(?:\n|\.|\s{suffixes}|$)",
            rf"About\s+([A-Z][\w\s&.\-']+?)(?:\n|\.|\s{suffixes})",
            rf"\bat\s+([A-Z][\w\s&.\-']+?)(?:\n|-|\(|{suffixes}|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_to_search)
            if match:
                candidate = match.group(1).strip()
                if 1 < len(candidate) < 40:
                    return candidate
                    
        return None

    def _extract_locations(self, text: str) -> List[str]:
        locations = set()
        
        # 1. Explicit markers (Location: Mumbai, India)
        loc_match = re.search(r"Location:\s*([A-Za-z,\s]+)(?:\n|$)", text, re.IGNORECASE)
        if loc_match:
            raw_loc = loc_match.group(1).strip()
            if raw_loc and "remote" not in raw_loc.lower():
                locations.add(raw_loc)
                
        # 2. Remote / Hybrid scoped formats
        remote_match = re.search(r"Remote\s*\(([A-Za-z\s]+)\)", text, re.IGNORECASE)
        if remote_match:
            locations.add(f"Remote ({remote_match.group(1).strip()})")
            
        hybrid_match = re.search(r"Hybrid\s*-\s*([A-Za-z\s]+)", text, re.IGNORECASE)
        if hybrid_match:
            locations.add(hybrid_match.group(1).strip())
            
        # 3. Traditional "City, State/Country" heuristics with flexible trailing terms (e.g., Bengaluru, Karnataka)
        city_state_matches = re.findall(r"\b([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)*,\s*[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)\b", text)
        for cs_match in city_state_matches:
            locations.add(cs_match.strip())
            
        # Fallback to appending "Remote" if detected
        if not locations and re.search(r"Location:\s*Remote", text, re.IGNORECASE):
            locations.add("Remote")
                
        return sorted(list(locations))

    def _infer_industry(self, company_text: str) -> Optional[str]:
        if not company_text:
            return None
            
        industries = {
            "SaaS": [r"\bsaas\b", r"software as a service"],
            "FinTech": [r"fintech", r"financial technology", r"payments", r"banking"],
            "HealthTech": [r"healthtech", r"healthcare", r"medical device", r"digital health"],
            "EdTech": [r"edtech", r"education technology", r"e-learning"],
            "E-commerce": [r"e-commerce", r"ecommerce", r"retail", r"marketplace"],
            "AI / Machine Learning": [r"artificial intelligence", r"\bai\b", r"machine learning"],
            "Cybersecurity": [r"cybersecurity", r"information security", r"infosec"]
        }
        
        text_lower = company_text.lower()
        for industry, keywords in industries.items():
            if any(re.search(kw, text_lower) for kw in keywords):
                return industry
                
        return None