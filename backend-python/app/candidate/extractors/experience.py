import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Experience
from app.shared.skill_extractor import SkillExtractor


class ExperienceExtractor:
    """
    Deterministic experience extractor.

    Responsibilities:
    - Detect experience boundaries from strong role/date signals.
    - Extract role, company, dates and description.
    - Extract technologies from both experience headers and descriptions.
    - Normalize technologies through the canonical SkillExtractor.
    - Avoid treating wrapped description lines as new experiences.
    """

    BULLET_PATTERN = re.compile(
        r"^[•●▪◦*\-–—]\s*"
    )

    MONTH_PATTERN = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    # Supports:
    # Jan 2026
    # January 2026
    # 01/2026
    # 01-2026
    # 2026
    #
    # And ranges:
    # Jan 2026 - May 2026
    # Jan 2026 - Present
    DATE_RANGE_PATTERN = re.compile(
        rf"\b("
        rf"(?:{MONTH_PATTERN}\s+)?(?:19|20)\d{{2}}"
        rf"|"
        rf"\d{{1,2}}[/-]\d{{4}}"
        rf")"
        rf"(?:\s*[-–—]\s*"
        rf"("
        rf"Present|Current|Now|"
        rf"(?:{MONTH_PATTERN}\s+)?(?:19|20)\d{{2}}|"
        rf"\d{{1,2}}[/-]\d{{4}}"
        rf"))?",
        re.IGNORECASE,
    )

    ROLE_AT_COMPANY_PATTERN = re.compile(
        r"^(.*?)\s+(?:@|at)\s+(.*?)$",
        re.IGNORECASE,
    )

    # Ordered roughly from specific → generic.
    JOB_TITLE_PATTERNS = [
        "machine learning engineer",
        "full stack engineer",
        "full stack developer",
        "full-stack engineer",
        "full-stack developer",
        "software engineer",
        "software developer",
        "backend engineer",
        "backend developer",
        "frontend engineer",
        "frontend developer",
        "devops engineer",
        "cloud engineer",
        "ml engineer",
        "ai/ml engineer",
        "ai engineer",
        "data scientist",
        "data engineer",
        "research engineer",
        "research assistant",
        "unity 3d developer",
        "unity developer",
        "freelance developer",
        "developer",
        "engineer",
        "architect",
        "consultant",
        "analyst",
        "manager",
        "founder",
        "co-founder",
        "freelancer",
        "intern",
    ]

    WORK_MODE_KEYWORDS = {
        "remote",
        "hybrid",
        "on-site",
        "onsite",
        "full-time",
        "fulltime",
        "part-time",
        "parttime",
        "contract",
        "internship",
        "freelance",
    }

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
        "san francisco",
        "california",
        "texas",
    }

    LOCATION_PATTERN = re.compile(
        r"^[a-zA-Z\s\.\-]+,\s*[a-zA-Z\s\.\-]+$"
    )

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Experience]:
        if not text or not text.strip():
            return []

        lines = self._normalize_lines(text)

        if not lines:
            return []

        blocks = self._split_blocks(lines)

        experiences: List[Experience] = []

        for block in blocks:
            experience = self._parse_block(block)

            if experience is not None:
                experiences.append(experience)

        return experiences

    # ==========================================================
    # Normalization
    # ==========================================================

    def _normalize_lines(self, text: str) -> List[str]:
        """
        Normalize horizontal whitespace while preserving physical
        line boundaries.

        We intentionally do NOT merge lines because bullet structure
        and PDF line ordering are useful for experience extraction.
        """
        text = text.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
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
    # Experience Block Detection
    # ==========================================================

    def _split_blocks(
        self,
        lines: List[str],
    ) -> List[List[str]]:
        """
        Detect experience headers and use them as experience
        boundaries.

        Description lines are never treated as new experiences merely
        because they are long or short.
        """

        header_indexes = [
            index
            for index, line in enumerate(lines)
            if self._is_experience_header_candidate(
                line,
                index,
                lines,
            )
        ]

        if not header_indexes:
            return [lines]

        blocks: List[List[str]] = []

        for position, start_index in enumerate(
            header_indexes
        ):
            end_index = (
                header_indexes[position + 1]
                if position + 1 < len(header_indexes)
                else len(lines)
            )

            block = lines[
                start_index:end_index
            ]

            if block:
                blocks.append(block)

        return blocks

    def _is_experience_header_candidate(
        self,
        line: str,
        index: int,
        lines: List[str],
    ) -> bool:
        if not line:
            return False

        if self.BULLET_PATTERN.match(line):
            return False

        # A normal sentence should not become a new experience.
        if self._looks_like_description(line):
            return False

        has_date = bool(
            self.DATE_RANGE_PATTERN.search(line)
        )

        has_role = self._contains_job_title(
            line
        )

        has_role_at_company = bool(
            self.ROLE_AT_COMPANY_PATTERN.match(
                line
            )
        )

        # Strongest pattern:
        #
        # Software Developer Intern Jan 2026 - May 2026
        #
        if has_date and has_role:
            return True

        # Role @ Company
        # Role at Company
        if has_role_at_company:
            return True

        # A role followed by a separate date line.
        if has_role:
            next_line = (
                lines[index + 1]
                if index + 1 < len(lines)
                else ""
            )

            if next_line:
                next_has_date = bool(
                    self.DATE_RANGE_PATTERN.search(
                        next_line
                    )
                )

                if next_has_date:
                    return True

        return False

    # ==========================================================
    # Block Parsing
    # ==========================================================

    def _parse_block(
        self,
        block: List[str],
    ) -> Optional[Experience]:
        if not block:
            return None

        header_lines, description_lines = (
            self._segment_block(block)
        )

        if not header_lines:
            return None

        header_text = "\n".join(
            header_lines
        )

        start_date, end_date = (
            self._extract_dates(header_text)
        )

        role = self._extract_role(
            header_lines
        )

        company = self._extract_company(
            header_lines,
            role,
        )

        description = self._extract_description(
            description_lines
        )

        header_technologies = (
            self._extract_header_technologies(
                header_lines,
                role,
                company,
            )
        )

        technologies = self._extract_technologies(
            header_technologies,
            description,
        )

        return Experience(
            role=role,
            company=company,
            start_date=start_date,
            end_date=end_date,
            description=description or None,
            technologies=technologies,
        )

    # ==========================================================
    # Header Segmentation
    # ==========================================================

    def _segment_block(
        self,
        block: List[str],
    ) -> Tuple[
        List[str],
        List[str],
    ]:
        """
        The initial non-bullet region is treated as metadata/header.

        Once the first bullet is encountered, everything after it
        belongs to the description.

        This avoids using arbitrary character-length thresholds.
        """

        header_lines: List[str] = []
        description_lines: List[str] = []

        hit_description = False

        for line in block:
            if hit_description:
                description_lines.append(line)
                continue

            if self.BULLET_PATTERN.match(line):
                hit_description = True
                description_lines.append(line)
                continue

            header_lines.append(line)

        return (
            header_lines,
            description_lines,
        )

    # ==========================================================
    # Role Extraction
    # ==========================================================

    def _extract_role(
        self,
        header_lines: List[str],
    ) -> Optional[str]:
        if not header_lines:
            return None

        # First support:
        #
        # Software Developer @ Company
        #
        # Software Developer at Company
        for line in header_lines:
            match = (
                self.ROLE_AT_COMPANY_PATTERN.match(
                    line
                )
            )

            if match:
                return self._clean_role(
                    match.group(1)
                )

        best_role: Optional[str] = None
        best_score = -1

        for line in header_lines:
            clean_line = self._remove_dates(
                line
            )

            clean_line = clean_line.strip(
                " |:-,"
            )

            if not clean_line:
                continue

            score = self._role_score(
                clean_line
            )

            if score > best_score:
                best_score = score
                best_role = clean_line

        return self._clean_role(
            best_role
        )

    def _role_score(
        self,
        line: str,
    ) -> int:
        lower = line.lower()

        score = 0

        for pattern in self.JOB_TITLE_PATTERNS:
            if re.search(
                r"\b"
                + re.escape(pattern)
                + r"\b",
                lower,
            ):
                score = max(
                    score,
                    100 + len(pattern),
                )

        return score

    def _contains_job_title(
        self,
        line: str,
    ) -> bool:
        return self._role_score(line) > 0

    # ==========================================================
    # Company Extraction
    # ==========================================================

    def _extract_company(
        self,
        header_lines: List[str],
        role: Optional[str],
    ) -> Optional[str]:
        if not header_lines:
            return None

        # ------------------------------------------------------
        # Case 1:
        #
        # Software Developer @ QuickSO
        # ------------------------------------------------------
        for line in header_lines:
            match = (
                self.ROLE_AT_COMPANY_PATTERN.match(
                    line
                )
            )

            if match:
                return self._clean_company(
                    match.group(2)
                )

        # ------------------------------------------------------
        # Case 2:
        #
        # Software Developer Intern Jan 2026 - May 2026
        # QuickSO App | Hybrid, Mumbai
        #
        # The company is a separate line after the role.
        # ------------------------------------------------------

        role_index: Optional[int] = None

        if role:
            for index, line in enumerate(
                header_lines
            ):
                clean_line = self._remove_dates(
                    line
                ).strip()

                if clean_line.lower() == role.lower():
                    role_index = index
                    break

        # Prefer lines AFTER the role.
        candidate_indexes: List[int] = []

        if role_index is not None:
            candidate_indexes.extend(
                range(
                    role_index + 1,
                    len(header_lines),
                )
            )

        # Then inspect earlier lines as fallback.
        candidate_indexes.extend(
            index
            for index in range(
                len(header_lines)
            )
            if index not in candidate_indexes
        )

        for index in candidate_indexes:
            line = header_lines[index].strip()

            if not line:
                continue

            clean_line = self._remove_dates(
                line
            ).strip(
                " |:-,"
            )

            if not clean_line:
                continue

            # Never use the role as company.
            if (
                role
                and clean_line.lower()
                == role.lower()
            ):
                continue

            # --------------------------------------------------
            # Company | Hybrid, Mumbai
            # --------------------------------------------------
            if "|" in clean_line:
                parts = [
                    part.strip()
                    for part in clean_line.split("|")
                    if part.strip()
                ]

                for part in parts:
                    if self._is_non_company_metadata(
                        part
                    ):
                        continue

                    if (
                        role
                        and part.lower()
                        == role.lower()
                    ):
                        continue

                    return self._clean_company(
                        part
                    )

            # --------------------------------------------------
            # Company
            # --------------------------------------------------
            if not self._is_non_company_metadata(
                clean_line
            ):
                return self._clean_company(
                    clean_line
                )

        return None

    def _is_non_company_metadata(
        self,
        value: str,
    ) -> bool:
        lower = value.lower().strip()

        if lower in self.WORK_MODE_KEYWORDS:
            return True

        if lower in self.LOCATION_KEYWORDS:
            return True

        if self.LOCATION_PATTERN.match(
            value
        ):
            return True

        return False

    # ==========================================================
    # Date Extraction
    # ==========================================================

    def _extract_dates(
        self,
        text: str,
    ) -> Tuple[
        Optional[str],
        Optional[str],
    ]:
        match = (
            self.DATE_RANGE_PATTERN.search(
                text
            )
        )

        if not match:
            return None, None

        start_date = (
            match.group(1).strip()
            if match.group(1)
            else None
        )

        end_date = (
            match.group(2).strip()
            if match.group(2)
            else None
        )

        return (
            start_date,
            end_date,
        )

    def _remove_dates(
        self,
        text: str,
    ) -> str:
        return self.DATE_RANGE_PATTERN.sub(
            "",
            text,
        ).strip()

    # ==========================================================
    # Description
    # ==========================================================

    def _extract_description(
        self,
        lines: List[str],
    ) -> str:
        return "\n".join(
            line.strip()
            for line in lines
            if line.strip()
        ).strip()

    # ==========================================================
    # Technology Extraction
    # ==========================================================

    def _extract_header_technologies(
        self,
        header_lines: List[str],
        role: Optional[str],
        company: Optional[str],
    ) -> List[str]:
        """
        Extract technologies explicitly mentioned in the
        experience header.

        Example:

        Software Developer Intern Jan 2026 - May 2026
        QuickSO App | Hybrid, Mumbai

        If technologies appear in the header, they are passed
        through the canonical SkillExtractor.
        """

        if not header_lines:
            return []

        candidates: List[str] = []

        for line in header_lines:
            clean_line = self._remove_dates(
                line
            )

            # Remove role without affecting case.
            if role:
                clean_line = re.sub(
                    re.escape(role),
                    "",
                    clean_line,
                    flags=re.IGNORECASE,
                )

            # Remove company without affecting case.
            if company:
                clean_line = re.sub(
                    re.escape(company),
                    "",
                    clean_line,
                    flags=re.IGNORECASE,
                )

            # Remove common metadata.
            clean_line = re.sub(
                r"\b(?:remote|hybrid|on-site|onsite)\b",
                "",
                clean_line,
                flags=re.IGNORECASE,
            )

            clean_line = clean_line.replace(
                "|",
                " ",
            )

            if clean_line.strip():
                candidates.append(
                    clean_line.strip()
                )

        if not candidates:
            return []

        return self.skill_extractor.extract(
            "\n".join(candidates)
        )

    def _extract_technologies(
        self,
        header_technologies: List[str],
        description: str,
    ) -> List[str]:
        """
        Combine explicit header technologies with technologies
        found in the description.

        Canonical normalization is handled by SkillExtractor.
        """

        technologies = set(
            header_technologies
        )

        if description:
            extracted = (
                self.skill_extractor.extract(
                    description
                )
            )

            technologies.update(
                extracted
            )

        return sorted(
            technologies
        )

    # ==========================================================
    # Cleaning
    # ==========================================================

    def _clean_role(
        self,
        role: Optional[str],
    ) -> Optional[str]:
        if not role:
            return None

        clean = self.BULLET_PATTERN.sub(
            "",
            role,
        ).strip()

        clean = self._remove_dates(
            clean
        )

        clean = clean.strip(
            " |:-,"
        )

        return clean or None

    def _clean_company(
        self,
        company: Optional[str],
    ) -> Optional[str]:
        if not company:
            return None

        clean = self.BULLET_PATTERN.sub(
            "",
            company,
        ).strip()

        clean = self._remove_dates(
            clean
        )

        clean = clean.strip(
            " |:-,"
        )

        return clean or None

    # ==========================================================
    # Description Detection
    # ==========================================================

    def _looks_like_description(
        self,
        line: str,
    ) -> bool:
        """
        Conservative prose detector.

        We do NOT use an arbitrary character threshold because
        PDF extraction frequently wraps a single sentence over
        multiple physical lines.
        """

        if self.BULLET_PATTERN.match(line):
            return True

        stripped = line.strip()

        if not stripped:
            return False

        # Sentence-ending punctuation is a strong prose signal.
        if stripped.endswith(
            (".", "?", "!")
        ):
            return True

        # Long prose without metadata.
        if (
            len(stripped.split()) >= 15
            and not self.DATE_RANGE_PATTERN.search(
                stripped
            )
            and not self._contains_job_title(
                stripped
            )
        ):
            return True

        return False