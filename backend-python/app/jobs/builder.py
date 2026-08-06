import re
from typing import Dict, List, Optional
from .schemas import JobKnowledgeBase, CompanyInfo, SalaryDetails

class JobBuilder:
    """
    Transforms parsed sections, skills, and keywords into a validated JobKnowledgeBase (JKB).
    Uses strict priority cascading for experience, hierarchical scoring for seniority, 
    and robust title/location/salary cleaning.
    """

    def build(self, sections: Dict[str, str], skills: List[str], keywords: List[str]) -> JobKnowledgeBase:
        header_text = sections.get("header", "")
        company_text = sections.get("company", "")
        qualifications_text = sections.get("qualifications", "")
        preferred_text = sections.get("preferred_qualifications", "")
        responsibilities_text = sections.get("responsibilities", "")
        salary_text = sections.get("salary", "")
        
        # We exclude company_text from the search_context to avoid extracting
        # the company's "25 years in business" as candidate experience, 
        # or their "HQ in New York" as the job location.
        search_context = "\n".join([header_text, responsibilities_text, qualifications_text, preferred_text, salary_text])
        combined_quals = f"{qualifications_text}\n{preferred_text}".strip()

        # 1. Extract List-based Sections
        responsibilities = self._text_to_list(responsibilities_text)
        qualifications = self._text_to_list(combined_quals)
        benefits = self._text_to_list(sections.get("benefits", ""))
        education = self._extract_education(search_context)

        # 2. Cascading & Scored Metadata
        role = self._extract_role(header_text)
        department = self._extract_department(search_context)
        
        # Pass header separately to prioritize it
        locations = self._extract_locations(header_text, search_context)
        
        work_mode = self._extract_work_mode(search_context)
        employment_type = self._extract_employment_type(search_context)
        
        # Priority Extraction: Quals -> Work Exp -> Responsibilities -> Header
        # Evaluates all matches in a section and returns the largest requirement
        experience_years = self._extract_experience_years([qualifications_text, preferred_text, responsibilities_text, header_text])
        
        # Scored Extraction: Highest seniority found wins
        experience_level = self._extract_experience_level(search_context)
        
        salary_details = self._extract_salary(f"{header_text}\n{salary_text}")

        # 3. Populate Company Info (Uses company_text)
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
        """Scores lines for role keywords, then aggressively cleans the selected title."""
        lines = [line.strip() for line in header_text.splitlines() if line.strip()]
        
        role_keywords = r"\b(Program Manager|Project Manager|Software Engineer(?: II| III)?|Technical Program Manager|Solution Architect|Engineer|Developer|Architect|Scientist|Analyst|Manager|Designer|Consultant|Intern|Lead|Director|Specialist|Administrator|QA|SDET|Tester|DevOps|Cloud|Security|Support|Product Owner|Researcher)\b"
        
        raw_role = None
        for line in lines[:5]:
            if re.search(role_keywords, line, re.IGNORECASE):
                raw_role = line
                break
                
        if not raw_role:
            for line in lines[:5]:
                if not re.search(r"\b(location|apply|remote|full-time|salary|company|careers?)\b", line, re.IGNORECASE):
                    raw_role = line
                    break
                    
        if not raw_role:
            return None
            
        # Clean garbage suffixes cautiously to avoid stripping "Engineer in Test"
        # We explicitly target known tech hubs and generic markers
        known_hubs = r"(Pune|Bengaluru|Bangalore|Hyderabad|Chennai|Mumbai|Delhi|Noida|Gurugram|India|USA|UK|London|New York|Remote)"
        clean_role = re.sub(rf"(?i)\s+(?:in|at)\s+{known_hubs}\b.*$", "", raw_role)
        clean_role = re.sub(r"(?i)\s*[-|]?\s*(category|department|job id).*$", "", clean_role)
        clean_role = re.sub(r"(?i)(http|www)\S+", "", clean_role)
        
        return clean_role.strip(" -|,:*")

    def _extract_department(self, text: str) -> Optional[str]:
        match = re.search(r"\b(Engineering|Product|Design|Sales|Marketing|HR|Human Resources|Finance|Operations|Data|IT|R&D|Quality|Infrastructure|Platform|Security|Customer Success|Professional Services)\s+(?:Department|Team|Group)\b", text, re.IGNORECASE)
        if match:
            return match.group(1).title()
        match_explicit = re.search(r"Department:\s*([A-Za-z\s&]+)", text, re.IGNORECASE)
        if match_explicit:
            return match_explicit.group(1).strip().title()
        return None

    def _extract_experience_level(self, text: str) -> Optional[str]:
        """Scores levels so 'Senior Manager' registers as Lead/Manager, not just Senior."""
        levels = {
            r"\b(lead|principal|staff|manager|director|vp|head)\b": (5, "Lead/Manager"),
            r"\b(senior|snr|sr\.?)\b": (4, "Senior"),
            r"\b(mid[- ]?level|intermediate)\b": (3, "Mid-Level"),
            r"\b(junior|entry[- ]?level|trainee|graduate)\b": (2, "Junior"),
            r"\b(intern|internship)\b": (1, "Intern")
        }
        
        highest_score = 0
        best_level = None
        text_lower = text.lower()
        
        for pattern, (score, level_name) in levels.items():
            if re.search(pattern, text_lower):
                if score > highest_score:
                    highest_score = score
                    best_level = level_name
                    
        return best_level

    def _extract_experience_years(self, priority_texts: List[str]) -> Optional[str]:
        """Cascades through sections, evaluates all matches, and returns the highest requirement."""
        pattern = r"(?:minimum\s+(?:of\s+)?|at\s+least\s+)?(\d+(?:\.\d+)?)(?:\s*(?:-|to)\s*(\d+(?:\.\d+)?))?\s*(\+)?\s*(?:years?|yrs?|yoe)(?:\s*\+)?(?:\s*of\s*experience)?"
        
        for text in priority_texts:
            if not text:
                continue
                
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                max_val = -1
                best_match_str = None
                
                for match in matches:
                    val1 = float(match.group(1))
                    val2 = float(match.group(2)) if match.group(2) else val1
                    high_val = max(val1, val2)
                    
                    if high_val > max_val:
                        max_val = high_val
                        fmt1 = int(val1) if val1.is_integer() else val1
                        
                        if match.group(2):
                            fmt2 = float(match.group(2))
                            fmt2 = int(fmt2) if fmt2.is_integer() else fmt2
                            best_match_str = f"{fmt1}-{fmt2} years"
                        else:
                            has_plus = '+' in match.group(0)
                            best_match_str = f"{fmt1}{'+' if has_plus else ''} years"
                            
                return best_match_str
                
        return None

    def _extract_work_mode(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(remote|work from home|wfh|telecommute)\b", text_lower): return "Remote"
        if re.search(r"\b(hybrid)\b", text_lower): return "Hybrid"
        if re.search(r"\b(on-site|onsite|in-office|in office)\b", text_lower): return "On-site"
        return None

    def _extract_employment_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if re.search(r"\b(full-time|full time|fulltime|permanent)\b", text_lower): return "Full-time"
        if re.search(r"\b(part-time|part time|parttime)\b", text_lower): return "Part-time"
        if re.search(r"\b(contract|contractor|freelance)\b", text_lower): return "Contract"
        if re.search(r"\b(fixed[- ]?term)\b", text_lower): return "Fixed Term"
        if re.search(r"\b(temporary|temp)\b", text_lower): return "Temporary"
        if re.search(r"\b(casual)\b", text_lower): return "Casual"
        if re.search(r"\b(intern|internship)\b", text_lower): return "Internship"
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
        
        # 1. Range Matches: $100k - $120k
        western_match = re.search(r"([\$£€])\s*([\d,]+(?:[kKmM])?)\s*(?:-|to)\s*[\$£€]?\s*([\d,]+(?:[kKmM])?)", text)
        if western_match:
            try:
                symbol = western_match.group(1)
                details.currency = 'USD' if symbol == '$' else 'GBP' if symbol == '£' else 'EUR'
                details.min_amount = self._parse_currency(western_match.group(2))
                details.max_amount = self._parse_currency(western_match.group(3))
            except ValueError:
                pass
        else:
            # 2. Single Bound Matches: Up to $120k, From $80k, $120k+
            single_bound = re.search(r"(?i)(up\s+to|from|starts?\s+at)?\s*([\$£€])\s*([\d,]+(?:[kKmM])?)\s*(\+)?", text)
            if single_bound:
                modifier = single_bound.group(1)
                symbol = single_bound.group(2)
                amount_str = single_bound.group(3)
                plus = single_bound.group(4)
                
                try:
                    amount = self._parse_currency(amount_str)
                    details.currency = 'USD' if symbol == '$' else 'GBP' if symbol == '£' else 'EUR'
                    
                    if modifier and "up to" in modifier.lower():
                        details.max_amount = amount
                    elif (modifier and ("from" in modifier.lower() or "start" in modifier.lower())) or plus:
                        details.min_amount = amount
                    else:
                        details.min_amount = amount
                        details.max_amount = amount
                except ValueError:
                    pass

        # 3. INR Ranges & Single Bounds
        if not details.currency:
            inr_range = re.search(r"(₹|INR)?\s*([\d,]+(?:(?:\.\d+)?))\s*(?:-|to)\s*(?:₹|INR)?\s*([\d,]+(?:(?:\.\d+)?))\s*(LPA|lakhs?)?", text, re.IGNORECASE)
            if inr_range and (inr_range.group(1) or inr_range.group(4)):
                try:
                    details.currency = 'INR'
                    min_val = float(inr_range.group(2).replace(",", ""))
                    max_val = float(inr_range.group(3).replace(",", ""))
                    
                    if inr_range.group(4) and re.search(r"LPA|lakh", inr_range.group(4), re.IGNORECASE):
                        min_val *= 100000
                        max_val *= 100000
                        details.period = "yearly"
                        
                    details.min_amount = min_val
                    details.max_amount = max_val
                except ValueError:
                    pass
            else:
                inr_single = re.search(r"(?i)(up\s+to|from|starts?\s+at)?\s*(₹|INR)\s*([\d,]+(?:(?:\.\d+)?))\s*(LPA|lakhs?)?\s*(\+)?", text)
                if not inr_single:
                    inr_single = re.search(r"(?i)(up\s+to|from|starts?\s+at)?\s*([\d,]+(?:(?:\.\d+)?))\s*(LPA|lakhs?)\s*(\+)?", text)
                
                if inr_single:
                    modifier = inr_single.group(1)
                    amount_str = inr_single.group(3) if len(inr_single.groups()) == 5 else inr_single.group(2)
                    lpa_flag = inr_single.group(4) if len(inr_single.groups()) == 5 else inr_single.group(3)
                    plus = inr_single.group(5) if len(inr_single.groups()) == 5 else inr_single.group(4)
                    
                    try:
                        amount = float(amount_str.replace(",", ""))
                        if lpa_flag and re.search(r"LPA|lakh", lpa_flag, re.IGNORECASE):
                            amount *= 100000
                            details.period = "yearly"
                            
                        details.currency = 'INR'
                        
                        if modifier and "up to" in modifier.lower():
                            details.max_amount = amount
                        elif (modifier and ("from" in modifier.lower() or "start" in modifier.lower())) or plus:
                            details.min_amount = amount
                        else:
                            details.min_amount = amount
                            details.max_amount = amount
                    except ValueError:
                        pass

        # 4. Period Inference
        if not details.period and details.currency:
            if re.search(r"\b(per year|annually|/yr|/year|p\.a\.?)\b", text, re.IGNORECASE):
                details.period = "yearly"
            elif re.search(r"\b(per hour|/hr|/hour|hourly)\b", text, re.IGNORECASE):
                details.period = "hourly"
            elif re.search(r"\b(per month|/mo|/month|monthly)\b", text, re.IGNORECASE):
                details.period = "monthly"
            
        return details

    def _parse_currency(self, value: str) -> float:
        value = value.lower().replace(",", "").replace(" ", "")
        if "k" in value: return float(value.replace("k", "")) * 1000
        if "m" in value: return float(value.replace("m", "")) * 1000000
        return float(value)

    def _extract_company_name(self, header_text: str, company_text: str) -> Optional[str]:
        text_to_search = f"{header_text}\n{company_text}"
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
                    # Strip ATS trailing words including Careers Portal / Career Site
                    candidate = re.sub(r"(?i)\s+(Careers?|Jobs|Hiring|Employment|Careers? Portal|Careers? Site)$", "", candidate).strip()
                    return candidate
        return None

    def _extract_locations(self, header_text: str, body_text: str) -> List[str]:
        locations = set()
        
        # 1. Prioritize explicit markers in header
        loc_match = re.search(r"Location:\s*([A-Za-z,\s]+)(?:\n|$)", header_text, re.IGNORECASE)
        if loc_match:
            raw_loc = loc_match.group(1).strip()
            if raw_loc and "remote" not in raw_loc.lower():
                locations.add(raw_loc)
                
        # 2. Iterate through both text sections for heuristics
        # Future Enhancement: Integrate a geocoder or static city list to validate these matches
        for text in [header_text, body_text]:
            remote_match = re.search(r"Remote\s*\(([A-Za-z\s]+)\)", text, re.IGNORECASE)
            if remote_match: locations.add(f"Remote ({remote_match.group(1).strip()})")
                
            hybrid_match = re.search(r"Hybrid\s*-\s*([A-Za-z\s]+)", text, re.IGNORECASE)
            if hybrid_match: locations.add(hybrid_match.group(1).strip())
                
            city_state_matches = re.findall(r"\b([A-Z][a-zA-Z]+(?:[\s-][A-Z][a-zA-Z]+)*,\s*[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)\b", text)
            for cs_match in city_state_matches:
                locations.add(cs_match.strip())
                
        # 3. Final remote fallback
        if not locations and re.search(r"Location:\s*Remote", header_text + body_text, re.IGNORECASE):
            locations.add("Remote")
                
        return sorted(list(locations))

    def _infer_industry(self, company_text: str) -> Optional[str]:
        if not company_text: return None
        industries = {
            "Engineering Services": [r"engineering services", r"consulting engineering"],
            "SaaS": [r"\bsaas\b", r"software as a service"],
            "FinTech": [r"fintech", r"financial technology", r"payments", r"banking"],
            "HealthTech": [r"healthtech", r"healthcare", r"medical device", r"digital health"],
            "EdTech": [r"edtech", r"education technology", r"e-learning"],
            "E-commerce": [r"e-commerce", r"ecommerce", r"retail", r"marketplace"],
            "AI / Machine Learning": [r"artificial intelligence", r"\bai\b", r"machine learning"],
            "Cybersecurity": [r"cybersecurity", r"information security", r"infosec"],
            "Manufacturing": [r"manufacturing", r"industrial production"],
            "Automotive": [r"automotive", r"vehicles", r"mobility"],
            "Aerospace": [r"aerospace", r"aviation", r"defense"],
            "Telecom": [r"telecom", r"telecommunications", r"networking"],
            "Cloud Services": [r"cloud services", r"cloud provider", r"cloud computing", r"iaas", r"paas"]
        }
        text_lower = company_text.lower()
        for industry, keywords in industries.items():
            if any(re.search(kw, text_lower) for kw in keywords):
                return industry
        return None