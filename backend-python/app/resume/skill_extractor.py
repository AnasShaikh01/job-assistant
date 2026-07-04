from pathlib import Path
import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher
from spacy.util import filter_spans

class SkillExtractor:
    """
    NLP component for identifying semantic skills using spaCy PhraseMatcher.
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.skill_map = {}
        self._load_skills()

    def _load_skills(self):
        csv_path = Path(__file__).parent.parent / "shared" / "skill_dictionary" / "skills.csv"
        if not csv_path.exists():
            return

        df = pd.read_csv(csv_path, header=None)
        patterns = []

        for _, row in df.iterrows():
            canonical = str(row[0]).strip().lower()
            if canonical:
                self.skill_map[canonical] = canonical
                patterns.append(self.nlp.make_doc(canonical))

            if len(row) > 1 and pd.notna(row[1]):
                aliases = str(row[1]).split(",")
                for alias in aliases:
                    alias = alias.strip().lower()
                    self.skill_map[alias] = canonical
                    patterns.append(self.nlp.make_doc(alias))

        self.matcher.add("SKILLS", patterns)

    def extract(self, text: str) -> list[str]:
        if not text.strip():
            return []
            
        doc = self.nlp(text)
        matches = filter_spans(
            [doc[start:end] for _, start, end in self.matcher(doc)]
        )

        skills = {
            self.skill_map.get(span.text.lower(), span.text.lower())
            for span in matches
        }
        return sorted(skills)