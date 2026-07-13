import re
import string
from collections import defaultdict

class JobParser:
    """
    Parses a cleaned job description into logical sections using a 3-level approach:
    1. Exact / Regex matches against known domains.
    2. Heuristic fallback for unknown headers (prevents swallowing).
    3. Paragraph appending for normal text.
    """
    
    SECTION_MAPPING = {
        "responsibilities": [
            r"responsibilities", r"what you'll do", r"what you will do", r"your impact",
            r"your role", r"duties", r"day-to-day", r"key responsibilities", r"what you'll build",
            r"the role"
        ],
        "qualifications": [
            r"requirements", r"qualifications", r"what we're looking for", 
            r"what you need", r"who you are", r"must have", r"minimum qualifications"
        ],
        "preferred_qualifications": [
            r"preferred qualifications", r"nice to have", r"bonus points", 
            r"preferred", r"ideal candidate", r"pluses"
        ],
        "skills": [
            r"skills", r"technologies", r"tech stack", r"technical requirements", r"core competencies"
        ],
        "benefits": [
            r"benefits", r"perks", r"what we offer", r"why join us", r"compensation and benefits"
        ],
        "company": [
            r"about us", r"about the company", r"who we are", r"company overview", r"about"
        ],
        "salary": [
            r"salary", r"compensation", r"pay", r"pay range"
        ]
    }

    def __init__(self):
        self.compiled_patterns = {}
        for canonical, patterns in self.SECTION_MAPPING.items():
            combined_pattern = "|".join(patterns)
            self.compiled_patterns[canonical] = re.compile(rf"^\s*({combined_pattern})\s*:?\s*$", re.IGNORECASE)
            
        # Pre-compute forbidden punctuation (everything except colon)
        self.forbidden_punct = set(string.punctuation) - {':'}

    def _is_heuristic_header(self, text: str, lines: list[str], current_index: int) -> bool:
        """
        Detects if a line is likely an unknown header based on length, 
        punctuation, and line proximity.
        """
        words = text.split()
        word_count = len(words)
        
        # Must be a short phrase (1 to 6 words)
        if not (1 <= word_count <= 6):
            return False
            
        # No punctuation except ':' allowed in headers
        if any(char in self.forbidden_punct for char in text):
            return False
            
        # Check structural layout: is it followed by a blank line?
        is_followed_by_blank = True
        if current_index + 1 < len(lines):
            # If the next line has text, it's not followed by a blank line
            if lines[current_index + 1].strip():
                is_followed_by_blank = False
                
        if is_followed_by_blank:
            return True
            
        # Fallbacks for explicit markers (even if formatting is cramped)
        if text.endswith(":") or text.isupper():
            return True
            
        return False

    def parse(self, text: str) -> dict[str, str]:
        sections = defaultdict(list)
        current_section = "header" 
        
        lines = text.splitlines()
        
        for i, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line:
                continue
                
            header_check_line = re.sub(r"^#+\s*|^\*\*\s*|\s*\*\*$", "", clean_line)
            
            # Level 1 & 2: Regex / Dictionary Variation Match
            matched_section = None
            for canonical, regex in self.compiled_patterns.items():
                if regex.match(header_check_line):
                    matched_section = canonical
                    break
            
            if matched_section:
                current_section = matched_section
            
            # Level 2.5: Heuristic Unknown Header Fallback
            elif self._is_heuristic_header(header_check_line, lines, i):
                # Slugify and namespace the unknown header
                dynamic_key = re.sub(r'[^a-z0-9]', '_', header_check_line.lower()).strip('_')
                current_section = f"unknown::{dynamic_key}"
            
            # Level 3: Fallback (Append to current section)
            else:
                sections[current_section].append(clean_line)
                
        return {section: "\n".join(content) for section, content in sections.items()}