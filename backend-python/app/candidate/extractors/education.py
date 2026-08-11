import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Education


class EducationExtractor:
    """
    Deterministic education extractor.

    Designed to handle common resume layouts including:

        Bachelor of Engineering (B.E.) in Computer Science (AI & ML)
        M.H. Saboo Siddik College of Engineering, Mumbai
        2023 - 2026
        CGPA: 9.21/10

        Diploma in Information Technology
        M.H. Saboo Siddik Polytechnic, Mumbai
        2020 - 2023
        83.50%

    Extraction goals:
        - degree
        - field of study / specialization
        - start year
        - end year
        - CGPA / GPA / percentage / score
        - institution

    The extractor is intentionally conservative:
    it prefers returning None over inventing education data.
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
        r"\b"
        r"((?:19|20)\d{2})"
        r"\s*"
        r"(?:[-–—]|to)"
        r"\s*"
        r"(Present|Current|Now|(?:19|20)\d{2})"
        r"\b",
        re.IGNORECASE,
    )

    # Supports:
    #   CGPA: 9.21/10
    #   GPA 3.8/4
    #   Percentage: 83.50%
    #   Score: 92
    #   Grade: A
    #
    # Grade is handled separately because it is not numeric.
    METRIC_PATTERN = re.compile(
        r"\b(?:CGPA|GPA|Percentage|Percent|Score)"
        r"\s*[:\-–—]?\s*"
        r"("
        r"\d{1,3}"
        r"(?:\.\d{1,3})?"
        r"(?:\s*/\s*\d{1,3}(?:\.\d{1,3})?)?"
        r"%?"
        r")",
        re.IGNORECASE,
    )

    GRADE_PATTERN = re.compile(
        r"\bGrade"
        r"\s*[:\-–—]?\s*"
        r"([A-F][+-]?|[A-F])\b",
        re.IGNORECASE,
    )

    # Unlabelled academic percentages:
    #
    # 83.50%
    # 83.5 %
    UNLABELED_PERCENTAGE_PATTERN = re.compile(
        r"(?<![\w.])"
        r"(\d{1,3}(?:\.\d{1,3})?)"
        r"\s*%"
    )

    METRIC_KEYWORDS_PATTERN = re.compile(
        r"\b(?:cgpa|gpa|percentage|percent|score|grade)\b",
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
            r"\bmaster\s+of\s+engineering\b",
            "Master of Engineering",
        ),
        (
            r"\bmaster\s+of\s+technology\b",
            "Master of Technology",
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
        "deep learning",
        "ai & ml",
        "ai and ml",
        "data science",
        "data analytics",
        "data engineering",
        "cyber security",
        "cybersecurity",
        "electronics and telecommunication",
        "electronics and communication",
        "electronics engineering",
        "electronics",
        "electrical engineering",
        "mechanical engineering",
        "civil engineering",
        "chemical engineering",
        "aerospace engineering",
        "biomedical engineering",
        "business administration",
        "business management",
        "commerce",
        "finance",
        "accounting",
        "mathematics",
        "physics",
        "chemistry",
        "economics",
        "statistics",
        "computer applications",
        "information science",
    ]

    FIELD_CANONICAL_MAP = {
        "computer science": "Computer Science",
        "computer engineering": "Computer Engineering",
        "information technology": "Information Technology",
        "information systems": "Information Systems",
        "software engineering": "Software Engineering",
        "artificial intelligence": "Artificial Intelligence",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "ai & ml": "Artificial Intelligence & Machine Learning",
        "ai and ml": "Artificial Intelligence & Machine Learning",
        "data science": "Data Science",
        "data analytics": "Data Analytics",
        "data engineering": "Data Engineering",
        "cyber security": "Cyber Security",
        "cybersecurity": "Cyber Security",
        "electronics and telecommunication": "Electronics and Telecommunication",
        "electronics and communication": "Electronics and Communication",
        "electronics engineering": "Electronics Engineering",
        "electronics": "Electronics",
        "electrical engineering": "Electrical Engineering",
        "mechanical engineering": "Mechanical Engineering",
        "civil engineering": "Civil Engineering",
        "chemical engineering": "Chemical Engineering",
        "aerospace engineering": "Aerospace Engineering",
        "biomedical engineering": "Biomedical Engineering",
        "business administration": "Business Administration",
        "business management": "Business Management",
        "commerce": "Commerce",
        "finance": "Finance",
        "accounting": "Accounting",
        "mathematics": "Mathematics",
        "physics": "Physics",
        "chemistry": "Chemistry",
        "economics": "Economics",
        "statistics": "Statistics",
        "computer applications": "Computer Applications",
        "information science": "Information Science",
    }

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
        r"^[a-zA-Z\s.\-]+,\s*[a-zA-Z\s.\-]+$"
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
        Degree lines are the strongest education-entry anchors.

        Example:

            Bachelor of Engineering...
            College...
            2023 - 2026

            Diploma...
            Polytechnic...
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

        # Prevent long prose from becoming education headings.
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

        match = self.YEAR_RANGE_PATTERN.search(
            text
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

        # Remove duplicate years while preserving order.
        unique_years = list(
            dict.fromkeys(years)
        )

        if len(unique_years) == 1:
            return unique_years[0], None

        return (
            unique_years[0],
            unique_years[1],
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

            Bachelor of Engineering (B.E.) in Computer Science
                -> Bachelor of Engineering (B.E.)

            Diploma in Information Technology
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

                # Preserve abbreviation immediately after
                # the long-form degree.
                #
                # Bachelor of Engineering (B.E.)
                remainder = clean_line[
                    match.end():
                ]

                suffix_match = re.match(
                    r"\s*\([^)]*\)",
                    remainder,
                )

                if suffix_match:
                    degree_text = clean_line[
                        match.start():
                        match.end()
                        + suffix_match.end()
                    ].strip()

                return self._clean_degree(
                    degree_text
                )

        return None

    def _clean_degree(
        self,
        degree_text: str,
    ) -> str:

        clean = degree_text.strip()

        # Remove specialization from degree.
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

        return clean

    # ==========================================================
    # Field Extraction
    # ==========================================================

    def _extract_field_of_study(
        self,
        lines: List[str],
        degree: Optional[str],
    ) -> Optional[str]:

        if not lines:
            return None

        # ------------------------------------------------------
        # 1. Explicit "in ..."
        #
        # Degree may already have been cleaned, so inspect
        # the ORIGINAL education lines as well.
        # ------------------------------------------------------

        for line in lines:

            clean_line = self.BULLET_PATTERN.sub(
                "",
                line,
            ).strip()

            field = self._field_from_text(
                clean_line
            )

            if field:
                return field

        # ------------------------------------------------------
        # 2. Known field anywhere in block.
        # ------------------------------------------------------

        full_text = "\n".join(lines)

        return self._find_known_field(
            full_text
        )

    def _field_from_text(
        self,
        text: str,
    ) -> Optional[str]:

        if not text:
            return None

        # ------------------------------------------------------
        # Explicit "in <field>"
        #
        # IMPORTANT:
        # Keep parenthetical specialization.
        #
        # Computer Science (AI & ML)
        # stays intact.
        # ------------------------------------------------------

        match = re.search(
            r"\b(?:in|major(?:ed)?\s+in|"
            r"specialization\s+in)\s+(.+?)"
            r"(?=\s+\b(?:19|20)\d{2}\b|$)",
            text,
            re.IGNORECASE,
        )

        if match:

            candidate = match.group(1).strip()

            candidate = candidate.rstrip(
                ".,;"
            ).strip()

            # Remove trailing institution-like fragments
            # if they accidentally occur on the same line.
            candidate = re.split(
                r"\s+\b(?:at|from)\s+",
                candidate,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

            # First try to preserve a recognized field +
            # specialization.
            combined = self._extract_field_with_specialization(
                candidate
            )

            if combined:
                return combined

            known_field = self._find_known_field(
                candidate
            )

            if known_field:
                return known_field

            candidate = re.sub(
                r"\s*\([^)]*\)",
                "",
                candidate,
            ).strip()

            return self._clean_field(
                candidate
            )

        # ------------------------------------------------------
        # Degree – Field
        #
        # Bachelor of Engineering – Computer Science
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
        # Degree, Field
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
        # Parenthetical field
        #
        # B.E. (Computer Science)
        # ------------------------------------------------------

        for candidate in re.findall(
            r"\(([^()]+)\)",
            text,
        ):

            cleaned = self._clean_field(
                candidate
            )

            if cleaned:
                return cleaned

        return None

    def _extract_field_with_specialization(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Preserve:

            Computer Science (AI & ML)

        rather than reducing it to:

            Computer Science
        """

        match = re.search(
            r"^(.*?)\s*\(([^()]+)\)\s*$",
            text,
        )

        if not match:
            return None

        primary = self._find_known_field(
            match.group(1)
        )

        if not primary:
            return None

        specialization = match.group(2).strip()

        if not specialization:
            return primary

        # Normalize common AI/ML shorthand.
        specialization_lower = (
            specialization.lower()
        )

        if specialization_lower in {
            "ai & ml",
            "ai and ml",
        }:
            specialization = (
                "AI & ML"
            )

        return f"{primary} ({specialization})"

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

        return self.FIELD_CANONICAL_MAP.get(
            lower,
            value.strip(),
        )

    # ==========================================================
    # Institution Extraction
    # ==========================================================

    def _extract_institution(
        self,
        lines: List[str],
        degree: Optional[str],
        field_of_study: Optional[str],
    ) -> Optional[str]:
        """
        Conservative institution extraction.

        Institution extraction is intentionally kept separate
        from degree/field detection to prevent contamination.

        For now, this method returns None unless the line is
        strongly identifiable as an institution.
        """

        candidates: List[str] = []

        for line in lines:

            clean_line = self.BULLET_PATTERN.sub(
                "",
                line,
            ).strip()

            if not clean_line:
                continue

            # Never classify degree lines as institutions.
            if self._contains_degree(
                clean_line
            ):
                continue

            # Remove explicit academic metrics first.
            clean_line = self._remove_metric_from_line(
                clean_line
            )

            if not clean_line:
                continue

            # Skip pure field lines.
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

        # Strong institution signal.
        for candidate in candidates:

            lower = candidate.lower()

            if any(
                keyword in lower
                for keyword in self.INSTITUTION_KEYWORDS
            ):
                return self._clean_institution(
                    candidate
                )

        # Conservative fallback.
        #
        # We intentionally do not aggressively guess
        # arbitrary text as an institution.
        return None

    def _clean_institution(
        self,
        institution: str,
    ) -> Optional[str]:

        clean = institution.strip()

        clean = self._remove_metric_from_line(
            clean
        )

        clean = re.sub(
            r"\s{2,}",
            " ",
            clean,
        )

        clean = clean.strip(
            " |,:;()-"
        )

        return clean or None

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
    # Academic Metrics
    # ==========================================================

    def _extract_cgpa(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Extract academic score in priority order:

            1. Explicit CGPA/GPA/Percentage/Score
            2. Explicit Grade
            3. Unlabelled percentage

        Examples:

            CGPA: 9.21/10 -> 9.21/10
            GPA: 3.8/4    -> 3.8/4
            Percentage: 83.5% -> 83.5%
            83.50% -> 83.50%
        """

        # ------------------------------------------------------
        # 1. Explicit numeric metric
        # ------------------------------------------------------

        match = self.METRIC_PATTERN.search(
            text
        )

        if match:
            return match.group(1).strip()

        # ------------------------------------------------------
        # 2. Explicit grade
        # ------------------------------------------------------

        grade_match = self.GRADE_PATTERN.search(
            text
        )

        if grade_match:
            return grade_match.group(1).strip()

        # ------------------------------------------------------
        # 3. Unlabelled percentage
        #
        # Important for:
        #
        # M.H. Saboo Siddik Polytechnic, Mumbai 83.50%
        # ------------------------------------------------------

        percentage_match = (
            self.UNLABELED_PERCENTAGE_PATTERN.search(
                text
            )
        )

        if percentage_match:

            return (
                percentage_match.group(1)
                + "%"
            )

        return None

    def _remove_metric_from_line(
        self,
        line: str,
    ) -> str:
        """
        Remove academic score fragments from institution
        candidates.

        Example:

            M.H. Saboo Siddik Polytechnic, Mumbai 83.50%

        becomes:

            M.H. Saboo Siddik Polytechnic, Mumbai
        """

        cleaned = self.METRIC_PATTERN.sub(
            "",
            line,
        )

        cleaned = self.GRADE_PATTERN.sub(
            "",
            cleaned,
        )

        cleaned = (
            self.UNLABELED_PERCENTAGE_PATTERN.sub(
                "",
                cleaned,
            )
        )

        cleaned = re.sub(
            r"\s{2,}",
            " ",
            cleaned,
        )

        return cleaned.strip(
            " |,:;()-"
        )