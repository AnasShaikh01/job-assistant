import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Education


class EducationExtractor:
    """
    Deterministic education extractor.

    Responsibilities:
    - Detect individual education records.
    - Extract degree independently from field of study.
    - Extract institution cleanly.
    - Extract start/end years.
    - Extract CGPA/GPA/percentage/grade when explicitly present.
    - Handle common Indian and international resume formats.
    """

    # ==========================================================
    # Core Patterns
    # ==========================================================

    BULLET_PATTERN = re.compile(
        r"^[•●▪◦*\-–—]\s*"
    )

    YEAR_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b"
    )

    YEAR_RANGE_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})"
        r"\s*(?:[-–—]|to)\s*"
        r"(Present|Current|Now|(?:19|20)\d{2})\b",
        re.IGNORECASE,
    )

    CGPA_PATTERN = re.compile(
        r"\b(?:CGPA|GPA|Percentage|Score|Grade)"
        r"\s*[:\-–—]?\s*"
        r"("
        r"\d{1,2}"
        r"(?:\.\d{1,2})?"
        r"(?:\s*/\s*\d{1,3})?"
        r"%?"
        r")",
        re.IGNORECASE,
    )

    METRIC_KEYWORDS_PATTERN = re.compile(
        r"\b(?:cgpa|gpa|percentage|score|grade)\b",
        re.IGNORECASE,
    )

    # ==========================================================
    # Degree Patterns
    # ==========================================================

    DEGREE_PATTERNS = [
        (
            r"\bbachelor\s+of\s+engineering\b",
            "Bachelor of Engineering",
        ),
        (
            r"\bbachelor\s+of\s+technology\b",
            "Bachelor of Technology",
        ),
        (
            r"\bmaster\s+of\s+technology\b",
            "Master of Technology",
        ),
        (
            r"\bmaster\s+of\s+engineering\b",
            "Master of Engineering",
        ),
        (
            r"\bbachelor\s+of\s+science\b",
            "Bachelor of Science",
        ),
        (
            r"\bmaster\s+of\s+science\b",
            "Master of Science",
        ),
        (
            r"\bbachelor\s+of\s+arts\b",
            "Bachelor of Arts",
        ),
        (
            r"\bmaster\s+of\s+arts\b",
            "Master of Arts",
        ),
        (
            r"\bbachelor\s+of\s+commerce\b",
            "Bachelor of Commerce",
        ),
        (
            r"\bmaster\s+of\s+commerce\b",
            "Master of Commerce",
        ),
        (
            r"\bbachelor(?:'s)?\b",
            "Bachelor",
        ),
        (
            r"\bmaster(?:'s)?\b",
            "Master",
        ),
        (
            r"\bb\.?\s*tech\b",
            "B.Tech",
        ),
        (
            r"\bm\.?\s*tech\b",
            "M.Tech",
        ),
        (
            r"\bb\.?\s*e\b",
            "B.E.",
        ),
        (
            r"\bm\.?\s*e\b",
            "M.E.",
        ),
        (
            r"\bb\.?\s*sc\b",
            "B.Sc.",
        ),
        (
            r"\bm\.?\s*sc\b",
            "M.Sc.",
        ),
        (
            r"\bb\.?\s*a\b",
            "B.A.",
        ),
        (
            r"\bm\.?\s*a\b",
            "M.A.",
        ),
        (
            r"\bb\.?\s*com\b",
            "B.Com.",
        ),
        (
            r"\bm\.?\s*com\b",
            "M.Com.",
        ),
        (
            r"\bbba\b",
            "BBA",
        ),
        (
            r"\bmba\b",
            "MBA",
        ),
        (
            r"\bbca\b",
            "BCA",
        ),
        (
            r"\bmca\b",
            "MCA",
        ),
        (
            r"\bllb\b",
            "LLB",
        ),
        (
            r"\bllm\b",
            "LLM",
        ),
        (
            r"\bph\.?\s*d\b",
            "PhD",
        ),
        (
            r"\bdoctorate\b",
            "Doctorate",
        ),
        (
            r"\bdiploma\b",
            "Diploma",
        ),
        (
            r"\bassociate(?:'s)?\s+degree\b",
            "Associate Degree",
        ),
    ]

    # ==========================================================
    # Field Patterns
    # ==========================================================

    FIELD_PATTERNS = [
        "computer science",
        "computer engineering",
        "information technology",
        "information systems",
        "software engineering",
        "artificial intelligence",
        "machine learning",
        "ai & ml",
        "ai and ml",
        "data science",
        "data analytics",
        "cyber security",
        "cybersecurity",
        "electronics engineering",
        "electronics",
        "electrical engineering",
        "mechanical engineering",
        "civil engineering",
        "chemical engineering",
        "business administration",
        "business management",
        "commerce",
        "finance",
        "mathematics",
        "physics",
        "chemistry",
        "economics",
        "statistics",
        "computer applications",
    ]

    # ==========================================================
    # Institution Signals
    # ==========================================================

    INSTITUTION_KEYWORDS = {
        "university",
        "college",
        "institute",
        "school",
        "academy",
        "polytechnic",
        "campus",
        "institution",
    }

    # ==========================================================
    # Location Signals
    # ==========================================================

    LOCATION_KEYWORDS = {
        "india",
        "usa",
        "uk",
        "london",
        "new york",
        "bangalore",
        "bengaluru",
        "pune",
        "mumbai",
        "hyderabad",
        "chennai",
        "delhi",
        "noida",
        "gurgaon",
        "gurugram",
        "san francisco",
        "california",
        "texas",
    }

    LOCATION_PATTERN = re.compile(
        r"^[a-zA-Z\s\.\-]+,\s*[a-zA-Z\s\.\-]+$"
    )

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(
        self,
        text: str,
    ) -> List[Education]:
        if not text or not text.strip():
            return []

        lines = self._normalize_lines(text)

        if not lines:
            return []

        blocks = self._split_blocks(lines)

        education_list: List[Education] = []

        for block in blocks:
            education = self._parse_block(block)

            if education is not None:
                education_list.append(education)

        return education_list

    # ==========================================================
    # Normalization
    # ==========================================================

    def _normalize_lines(
        self,
        text: str,
    ) -> List[str]:
        """
        Normalize horizontal whitespace while preserving
        logical line boundaries.
        """

        text = (
            text.replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        lines: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if line:
                lines.append(line)

        return lines

    # ==========================================================
    # Block Detection
    # ==========================================================

    def _split_blocks(
        self,
        lines: List[str],
    ) -> List[List[str]]:
        """
        Split education entries using degree lines as anchors.

        Example:

        Bachelor of Engineering (B.E.) in Computer Science (AI & ML)
        M.H. Saboo Siddik College of Engineering, Mumbai
        2023 - 2026

        Diploma in Computer Engineering
        Thakur Polytechnic, Mumbai
        2020 - 2023
        """

        degree_indexes: List[int] = []

        for index, line in enumerate(lines):
            if self._is_degree_line(line):
                degree_indexes.append(index)

        if not degree_indexes:
            return [lines]

        blocks: List[List[str]] = []

        for position, start_index in enumerate(
            degree_indexes
        ):
            end_index = (
                degree_indexes[position + 1]
                if position + 1 < len(degree_indexes)
                else len(lines)
            )

            block = lines[
                start_index:end_index
            ]

            if block:
                blocks.append(block)

        return blocks

    def _is_degree_line(
        self,
        line: str,
    ) -> bool:
        if not line:
            return False

        if self.BULLET_PATTERN.match(line):
            return False

        # Prevent long prose from being interpreted as
        # an education heading.
        if len(line.split()) > 20:
            return False

        return self._contains_degree(line)

    def _contains_degree(
        self,
        text: str,
    ) -> bool:
        lower = text.lower()

        for pattern, _ in self.DEGREE_PATTERNS:
            if re.search(
                pattern,
                lower,
            ):
                return True

        return False

    # ==========================================================
    # Block Parsing
    # ==========================================================

    def _parse_block(
        self,
        block: List[str],
    ) -> Optional[Education]:
        if not block:
            return None

        start_year, end_year = (
            self._extract_years(block)
        )

        cleaned_lines = self._remove_years(
            block
        )

        degree = self._extract_degree(
            cleaned_lines
        )

        field_of_study = (
            self._extract_field_of_study(
                cleaned_lines,
                degree,
            )
        )

        institution = (
            self._extract_institution(
                cleaned_lines,
                degree,
                field_of_study,
            )
        )

        cgpa = self._extract_cgpa(
            "\n".join(block)
        )

        if not any(
            [
                degree,
                institution,
                field_of_study,
                start_year,
                end_year,
                cgpa,
            ]
        ):
            return None

        return Education(
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            start_year=start_year,
            end_year=end_year,
            cgpa=cgpa,
        )

    # ==========================================================
    # Date Extraction
    # ==========================================================

    def _extract_years(
        self,
        lines: List[str],
    ) -> Tuple[
        Optional[str],
        Optional[str],
    ]:
        text = " ".join(lines)

        match = (
            self.YEAR_RANGE_PATTERN.search(
                text
            )
        )

        if match:
            return (
                match.group(1),
                match.group(2),
            )

        years = self.YEAR_PATTERN.findall(
            text
        )

        if not years:
            return None, None

        if len(years) == 1:
            return years[0], None

        return (
            years[0],
            years[1],
        )

    def _remove_years(
        self,
        lines: List[str],
    ) -> List[str]:
        cleaned_lines: List[str] = []

        for line in lines:
            cleaned = (
                self.YEAR_RANGE_PATTERN.sub(
                    "",
                    line,
                )
            )

            cleaned = re.sub(
                r"\b(?:19|20)\d{2}\b",
                "",
                cleaned,
            )

            cleaned = re.sub(
                r"\s{2,}",
                " ",
                cleaned,
            )

            cleaned = cleaned.strip(
                " |,:;–—-"
            )

            if cleaned:
                cleaned_lines.append(
                    cleaned
                )

        return cleaned_lines

    # ==========================================================
    # Degree Extraction
    # ==========================================================

    def _extract_degree(
        self,
        lines: List[str],
    ) -> Optional[str]:
        """
        Extract only the qualification.

        Examples:

        Bachelor of Engineering (B.E.) in Computer Science (AI & ML)
            -> Bachelor of Engineering (B.E.)

        Diploma in Computer Engineering
            -> Diploma
        """

        for line in lines:
            clean_line = self.BULLET_PATTERN.sub(
                "",
                line,
            ).strip()

            if not clean_line:
                continue

            lower = clean_line.lower()

            for pattern, canonical in (
                self.DEGREE_PATTERNS
            ):
                match = re.search(
                    pattern,
                    lower,
                )

                if not match:
                    continue

                degree_text = clean_line[
                    match.start():match.end()
                ].strip()

                # Preserve abbreviations in parentheses:
                #
                # Bachelor of Engineering (B.E.)
                #
                remainder = clean_line[
                    match.end():
                ]

                suffix_match = re.match(
                    r"\s*\([^)]*\)",
                    remainder,
                )

                if suffix_match:
                    degree_text = (
                        clean_line[
                            match.start():
                            match.end()
                            + suffix_match.end()
                        ]
                    ).strip()

                return self._clean_degree(
                    degree_text,
                    canonical,
                )

        return None

    def _clean_degree(
        self,
        degree_text: str,
        canonical: str,
    ) -> str:
        clean = degree_text.strip()

        # Remove field/specialization from degree.
        clean = re.split(
            r"\s+(?:in|with|major(?:ing)?\s+in|"
            r"specialization\s+in)\s+",
            clean,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        clean = clean.strip(
            " |,:;-"
        )

        return clean or canonical

    # ==========================================================
    # Field Extraction
    # ==========================================================

    def _extract_field_of_study(
        self,
        lines: List[str],
        degree: Optional[str],
    ) -> Optional[str]:
        """
        Extract the primary field/specialization.

        Examples:

        Bachelor of Engineering (B.E.) in Computer Science (AI & ML)
            -> Computer Science

        Diploma in Computer Engineering
            -> Computer Engineering
        """

        if not lines:
            return None

        # ------------------------------------------------------
        # 1. Explicit "in ..." field.
        # ------------------------------------------------------

        for line in lines:
            clean_line = self.BULLET_PATTERN.sub(
                "",
                line,
            ).strip()

            field = self._field_from_text(
                clean_line,
                degree,
            )

            if field:
                return field

        # ------------------------------------------------------
        # 2. Search known fields across the block.
        # ------------------------------------------------------

        full_text = "\n".join(lines)

        field = self._find_known_field(
            full_text
        )

        if field:
            return field

        return None

    def _field_from_text(
        self,
        text: str,
        degree: Optional[str],
    ) -> Optional[str]:
        if not text:
            return None

        # ------------------------------------------------------
        # "Degree in Computer Science (AI & ML)"
        # ------------------------------------------------------
        match = re.search(
            r"\b(?:in|major(?:ed)?\s+in|"
            r"specialization\s+in)\s+(.+)$",
            text,
            re.IGNORECASE,
        )

        if match:
            candidate = match.group(1).strip()

            # Remove trailing punctuation.
            candidate = candidate.rstrip(
                ".,;"
            ).strip()

            # Prefer the primary recognized field.
            known_field = self._find_known_field(
                candidate
            )

            if known_field:
                return known_field

            # Remove balanced parenthetical specialization
            # only when it follows a recognized primary field.
            candidate = re.sub(
                r"\s*\([^)]*\)",
                "",
                candidate,
            ).strip()

            if candidate:
                return self._canonical_field(
                    candidate
                )

        # ------------------------------------------------------
        # "Degree - Computer Science"
        # ------------------------------------------------------

        match = re.search(
            r"\s[-–—]\s(.+)$",
            text,
        )

        if match:
            candidate = self._clean_field(
                match.group(1)
            )

            if candidate:
                return candidate

        # ------------------------------------------------------
        # "Degree, Computer Science"
        # ------------------------------------------------------

        if "," in text:
            parts = [
                part.strip()
                for part in text.split(",")
                if part.strip()
            ]

            if len(parts) >= 2:
                for part in parts[1:]:
                    candidate = self._clean_field(
                        part
                    )

                    if candidate:
                        return candidate

        # ------------------------------------------------------
        # "(Computer Science)"
        # ------------------------------------------------------

        matches = re.findall(
            r"\(([^()]+)\)",
            text,
        )

        for candidate in matches:
            cleaned = self._clean_field(
                candidate
            )

            if cleaned:
                return cleaned

        return None

    def _find_known_field(
        self,
        text: str,
    ) -> Optional[str]:
        lower_text = text.lower()

        fields = sorted(
            self.FIELD_PATTERNS,
            key=len,
            reverse=True,
        )

        for field in fields:
            if re.search(
                r"\b"
                + re.escape(field)
                + r"\b",
                lower_text,
            ):
                return self._canonical_field(
                    field
                )

        return None

    def _clean_field(
        self,
        value: str,
    ) -> Optional[str]:
        if not value:
            return None

        clean = value.strip(
            " |,:;()-"
        )

        clean = re.sub(
            r"\s{2,}",
            " ",
            clean,
        )

        if len(clean) < 2:
            return None

        lower = clean.lower()

        if any(
            keyword in lower
            for keyword in self.INSTITUTION_KEYWORDS
        ):
            return None

        if lower in self.LOCATION_KEYWORDS:
            return None

        # Prefer known canonical fields.
        known_field = self._find_known_field(
            clean
        )

        if known_field:
            return known_field

        return clean

    def _canonical_field(
        self,
        value: str,
    ) -> str:
        lower = value.lower().strip()

        canonical_map = {
            "ai & ml":
                "Artificial Intelligence & Machine Learning",
            "ai and ml":
                "Artificial Intelligence & Machine Learning",
            "cybersecurity":
                "Cyber Security",
            "computer science":
                "Computer Science",
            "computer engineering":
                "Computer Engineering",
            "information technology":
                "Information Technology",
            "software engineering":
                "Software Engineering",
            "data science":
                "Data Science",
            "machine learning":
                "Machine Learning",
            "artificial intelligence":
                "Artificial Intelligence",
        }

        if lower in canonical_map:
            return canonical_map[lower]

        return value.strip()

    # ==========================================================
    # Institution Extraction
    # ==========================================================

    def _extract_institution(
        self,
        lines: List[str],
        degree: Optional[str],
        field_of_study: Optional[str],
    ) -> Optional[str]:
        candidates: List[str] = []

        for line in lines:
            clean_line = self.BULLET_PATTERN.sub(
                "",
                line,
            ).strip()

            if not clean_line:
                continue

            # CRITICAL:
            #
            # Skip ANY line containing a degree.
            #
            # This prevents:
            #
            # "Bachelor of Engineering (B.E.) in Computer Science"
            #
            # from being returned as the institution.
            if self._contains_degree(
                clean_line
            ):
                continue

            # Skip CGPA/GPA/percentage lines.
            if self.METRIC_KEYWORDS_PATTERN.search(
                clean_line
            ):
                continue

            # Skip field-only lines.
            if (
                field_of_study
                and clean_line.lower().strip()
                == field_of_study.lower().strip()
            ):
                continue

            clean_line = clean_line.strip(
                " |,:;()-"
            )

            if not clean_line:
                continue

            if self._is_location_only(
                clean_line
            ):
                continue

            candidates.append(
                clean_line
            )

        if not candidates:
            return None

        # Prefer an explicit institution signal.
        for candidate in candidates:
            lower = candidate.lower()

            if any(
                keyword in lower
                for keyword in self.INSTITUTION_KEYWORDS
            ):
                return self._clean_institution(
                    candidate
                )

        # Fallback to first reasonable candidate.
        return self._clean_institution(
            candidates[0]
        )

    def _clean_institution(
        self,
        institution: str,
    ) -> Optional[str]:
        clean = institution.strip()

        if not clean:
            return None

        clean = re.sub(
            r"\s{2,}",
            " ",
            clean,
        )

        return clean

    def _is_location_only(
        self,
        value: str,
    ) -> bool:
        lower = value.lower().strip()

        if lower in self.LOCATION_KEYWORDS:
            return True

        if self.LOCATION_PATTERN.match(
            value
        ):
            return True

        return False

    # ==========================================================
    # CGPA / GPA / Percentage
    # ==========================================================

    def _extract_cgpa(
        self,
        text: str,
    ) -> Optional[str]:
        match = self.CGPA_PATTERN.search(
            text
        )

        if not match:
            return None

        return match.group(1).strip()