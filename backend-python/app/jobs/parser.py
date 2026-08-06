import re
from collections import defaultdict

class JobParser:
    """
    Parses a cleaned job description into logical sections deterministically.
    Maps ATS-specific headings, merges similar sections, and safely appends 
    unknown sub-headings to the active section to preserve context.
    Strictly NO metadata extraction occurs here.
    """
    
    SECTION_MAPPING = {
        "responsibilities": [
            r"responsibilities", r"what you'll do", r"what you will do", r"your impact",
            r"your role", r"duties", r"day-to-day", r"key responsibilities", r"what you'll build",
            r"the role", r"what you will be doing", r"what you'll be doing", r"core responsibilities",
            r"role & responsibilities", r"accountabilities", r"essential functions",
            r"about the role", r"job description", r"job summary", r"overview",
            r"role and responsibility brief", r"role summary", r"primary responsibilities",
            r"responsibilities and duties", r"your responsibilities", r"job responsibilities", 
            r"primary duties"
        ],
        "qualifications": [
            r"requirements", r"qualifications", r"what we're looking for", 
            r"what you need", r"who you are", r"minimum qualifications",
            r"eligibility", r"what you bring", r"skills & experience", r"what it takes",
            r"basic qualifications", r"experience", r"your profile",
            r"essential qualifications", r"minimum requirements", r"work experience",
            r"must have skill", r"must have skills", r"must have", r"essential skills",
            r"certifications", r"required certifications"
        ],
        "preferred_qualifications": [
            r"preferred qualifications", r"nice to have", r"bonus points", 
            r"preferred", r"ideal candidate", r"pluses", r"what makes you stand out",
            r"desired skills", r"advantageous", r"extra credit", r"preferred skills",
            r"preferred experience", r"nice to have skill", r"nice to have skills",
            r"good to have", r"preferred certifications"
        ],
        "skills": [
            r"skills", r"technologies", r"tech stack", r"technical requirements", 
            r"core competencies", r"our stack", r"tools you'll use", r"technologies we use",
            r"key skills", r"technical skill", r"technical skills", r"programming languages",
            r"tools", r"required skills"
        ],
        "benefits": [
            r"benefits", r"perks", r"what we offer", r"why join us", r"compensation and benefits",
            r"what's in it for you", r"our benefits", r"life at", r"benefits & perks",
            r"employee benefits", r"additional benefits", r"benefits at\s+.+?"
        ],
        "company": [
            r"about us", r"about the company", r"who we are", r"company overview", 
            r"about", r"our mission", r"our story", r"about the team", r"company profile",
            r"about team", r"about company", r"our company", r"how we work", 
            r"about\s+.+?"
        ],
        "salary": [
            r"salary", r"compensation", r"pay", r"pay range", r"remuneration",
            r"compensation & benefits"
        ]
    }

    # Decorative headers to completely skip (keeps section state intact)
    IGNORE_MAPPING = [
        r"apply now", r"how to apply", r"equal opportunity", r"diversity", r"inclusion",
        r"equal opportunity employer", r"interview process", r"next steps",
        r"eoe", r"accessibility", r"commitment to diversity", r"about this job",
        r"share this job", r"similar jobs", r"related jobs", r"privacy policy",
        r"terms of use", r"cookie policy", r"follow us", r"connect with us"
    ]

    def __init__(self):
        self.compiled_patterns = {}
        for canonical, patterns in self.SECTION_MAPPING.items():
            combined_pattern = "|".join(patterns)
            self.compiled_patterns[canonical] = re.compile(rf"^\s*(?:{combined_pattern})\s*:?\s*$", re.IGNORECASE)
            
        combined_ignore = "|".join(self.IGNORE_MAPPING)
        self.compiled_ignore = re.compile(rf"^\s*(?:{combined_ignore})\s*:?\s*$", re.IGNORECASE)

    def _clean_header_line(self, line: str) -> str:
        clean = re.sub(r"^([#\*\-•]+|\d+[\.\)])\s*", "", line)
        clean = re.sub(r"\s*\*+$", "", clean)
        return clean.strip()

    def parse(self, text: str) -> dict[str, str]:
        sections = defaultdict(list)
        current_section = "header" 
        
        lines = text.splitlines()
        
        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            header_check_line = self._clean_header_line(clean_line)
            
            # Skip decorative headers but keep current_section state
            if self.compiled_ignore.match(header_check_line):
                continue
            
            matched_section = None
            for canonical, regex in self.compiled_patterns.items():
                if regex.match(header_check_line):
                    matched_section = canonical
                    break
            
            if matched_section:
                current_section = matched_section
            else:
                # Normal text and unknown sub-headings fall here. 
                # This perfectly preserves things like "Why You'll Love Working Here".
                sections[current_section].append(clean_line)
                
        return {section: "\n".join(content) for section, content in sections.items()}