import re
from app.shared.keyword_constants import METHODOLOGIES, SOFT_SKILLS, ATS_KEYWORDS

class KeywordExtractor:
    """
    Extracts Methodologies, Soft Skills, and ATS Business Keywords.
    (Technical skills are handled separately by the shared SkillExtractor).
    
    Uses a single, highly-optimized, length-sorted regex pattern.
    Handles optional punctuation (spaces vs hyphens) and normalizes 
    everything centrally to ensure lookup map consistency.
    """
    
    def __init__(self):
        self.keyword_map = {}
        
        # Build the alias-to-canonical map from the external config
        self._register_category(METHODOLOGIES)
        self._register_category(SOFT_SKILLS)
        self._register_category(ATS_KEYWORDS)

        # Sort all search terms by length, descending, to match phrases before single words
        all_search_terms = sorted(self.keyword_map.keys(), key=len, reverse=True)
        
        escaped_terms = []
        for term in all_search_terms:
            escaped = re.escape(term)
            # Make spaces and hyphens interchangeable/optional.
            # re.escape converts spaces to '\ ' and hyphens to '\-'
            flexible_escaped = escaped.replace(r"\ ", r"[\s\-]+").replace(r"\-", r"[\s\-]+")
            escaped_terms.append(flexible_escaped)
            
        # Build a single regex using negative lookarounds instead of \b boundaries
        pattern_str = r"(?<!\w)(?:" + "|".join(escaped_terms) + r")(?!\w)"
        
        self.pattern = re.compile(pattern_str, re.IGNORECASE)

    def _normalize(self, term: str) -> str:
        """
        Normalizes a term by lowercasing and replacing any combination of 
        spaces and hyphens with a single space.
        """
        return re.sub(r"[\s\-]+", " ", term.lower()).strip()

    def _register_category(self, category_dict: dict):
        """Populates the map with canonical terms and their aliases, normalized."""
        for canonical, aliases in category_dict.items():
            # Normalize the canonical term for the dictionary key
            self.keyword_map[self._normalize(canonical)] = canonical
            for alias in aliases:
                # Normalize the alias term for the dictionary key
                self.keyword_map[self._normalize(alias)] = canonical

    def extract(self, text: str) -> list[str]:
        """
        Scans the text in a single O(N) pass and returns a sorted, 
        normalized list of canonical keywords, free of duplicates.
        """
        if not text.strip():
            return []
            
        raw_matches = self.pattern.findall(text)
        
        found_keywords = set()
        for match in raw_matches:
            # Normalize the raw match from the text so it perfectly aligns with our map keys
            normalized_match = self._normalize(match)
            if normalized_match in self.keyword_map:
                found_keywords.add(self.keyword_map[normalized_match])
                
        return sorted(list(found_keywords))