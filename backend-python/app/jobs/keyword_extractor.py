import re
from pathlib import Path
import pandas as pd

class KeywordExtractor:
    """
    Extracts ATS keywords, methodologies, soft skills, and business domains.
    Reads from the shared skills dictionary and supplements it with core soft skills.
    Normalizes aliases to their canonical forms (e.g., JS -> JavaScript).
    """
    
    # Core ATS soft skills & methodologies to supplement the technical skills.csv
    DEFAULT_KEYWORDS = {
        "Agile", "Scrum", "Kanban", "SaaS", "B2B", "B2C", "Enterprise",
        "Cross-functional", "Leadership", "Mentorship", "Startup",
        "Fast-paced", "Distributed Systems", "Microservices",
        "CI/CD", "DevOps", "TDD", "SDLC", "Problem Solving",
        "Analytical Skills", "Communication", "Team Player", "Remote"
    }

    def __init__(self):
        # Maps lowercase search terms (aliases & canonicals) to their true Canonical string
        self.keyword_map = {kw.lower(): kw for kw in self.DEFAULT_KEYWORDS}
        self._load_keywords()
        
        # Precompile regex for fast \b (word boundary) matching based on all known variations
        self.compiled_patterns = {
            search_term: re.compile(rf"\b{re.escape(search_term)}\b", re.IGNORECASE)
            for search_term in self.keyword_map.keys()
        }

    def _load_keywords(self):
        """
        Loads from the shared skill dictionary to ensure ATS keyword extraction 
        captures all known technical entities and normalizes their aliases.
        """
        csv_path = Path(__file__).parent.parent / "shared" / "skill_dictionary" / "skills.csv"
        if not csv_path.exists():
            return

        try:
            df = pd.read_csv(csv_path, header=None)
            for _, row in df.iterrows():
                canonical = str(row[0]).strip()
                if canonical:
                    self.keyword_map[canonical.lower()] = canonical
                
                # Normalize any aliases directly to the canonical term
                if len(row) > 1 and pd.notna(row[1]):
                    aliases = str(row[1]).split(",")
                    for alias in aliases:
                        alias = alias.strip()
                        if alias:
                            self.keyword_map[alias.lower()] = canonical
        except Exception:
            pass  # Fail gracefully to DEFAULT_KEYWORDS alone

    def extract(self, text: str) -> list[str]:
        """
        Scans the text for ATS keywords and returns a sorted, normalized list of canonical terms.
        """
        if not text.strip():
            return []
            
        found_keywords = set()
        
        # Fast regex search across the text
        for search_term, pattern in self.compiled_patterns.items():
            if pattern.search(text):
                canonical_kw = self.keyword_map[search_term]
                found_keywords.add(canonical_kw)
                
        return sorted(list(found_keywords))