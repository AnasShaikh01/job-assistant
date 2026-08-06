from pathlib import Path
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from spacy.util import filter_spans

class SkillExtractor:
    """
    NLP component for identifying semantic skills using spaCy PhraseMatcher.
    Powered by an external skills.csv dictionary.
    """
    def __init__(self):
        # Load the small English pipeline
        self.nlp = spacy.load("en_core_web_sm")
        # Match on the LOWER attribute to ensure case-insensitive matching
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.skill_map = {}
        self._load_skills()

    def _load_skills(self):
        # Assumes skills.csv is located at app/shared/skill_dictionary/skills.csv
        csv_path = Path(__file__).parent / "skill_dictionary" / "skills.csv"
        
        if not csv_path.exists():
            print(f"Warning: Skill dictionary not found at {csv_path}")
            return

        # Read CSV without a header row
        df = pd.read_csv(csv_path, header=None)
        patterns = []

        for _, row in df.iterrows():
            # Grab the canonical skill (column 0)
            canonical = str(row[0]).strip().lower()
            
            # Skip empty rows or pandas 'nan'
            if canonical and canonical != "nan":
                self.skill_map[canonical] = canonical
                patterns.append(self.nlp.make_doc(canonical))

            # Grab aliases (column 1) if they exist
            if len(row) > 1 and pd.notna(row[1]):
                aliases = str(row[1]).split(",")
                for alias in aliases:
                    alias = alias.strip().lower()
                    if alias:
                        self.skill_map[alias] = canonical
                        patterns.append(self.nlp.make_doc(alias))

        # Add all generated patterns to the PhraseMatcher under the label "SKILLS"
        self.matcher.add("SKILLS", patterns)

    def extract(self, text: str) -> list[str]:
        if not text.strip():
            return []
            
        doc = self.nlp(text)
        
        # filter_spans removes overlapping matches (e.g., matching "react" inside "react framework")
        # It prioritizes the longest match.
        matches = filter_spans(
            [doc[start:end] for _, start, end in self.matcher(doc)]
        )

        skills = set()
        for span in matches:
            span_text_lower = span.text.lower()
            canonical = self.skill_map.get(span_text_lower, span_text_lower)
            
            # EDGE CASE FIX: Adjusting condition to allow lowercase "c" 
            # Note: This effectively allows all "c" and "C" matches to pass.
            if canonical == "c" and span.text.upper() != "C":
                continue
                
            skills.add(canonical)
            
        return sorted(list(skills))