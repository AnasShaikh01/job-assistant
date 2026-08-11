import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Experience
from app.shared.skill_extractor import SkillExtractor


class ExperienceExtractor:
    """
    Production-oriented deterministic experience extractor.

    Designed to handle common resume layouts without relying on a
    fixed number of lines or arbitrary character thresholds.

    Supported layouts include:

        Role
        Company
        Date
        Description

        Role
        Date
        Company
        Description

        Company
        Date
        Role
        Description

        Role | Company | Date
        Description

        Company | Role | Date
        Description

        Role @ Company
        Date
        Description

        Role
        Date
        Remote
        Description

    The extractor is deliberately conservative:
    - Strong structural signals are preferred over prose heuristics.
    - Description text is never guessed as a company.
    - Missing company remains None.
    - Multiple experiences can be recovered from collapsed PDF text.
    """

    # ==========================================================
    # Basic Patterns
    # ==========================================================

    BULLET_PATTERN = re.compile(
        r"^[•●▪◦*\-–—]\s*"
    )

    MONTH_PATTERN = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    DATE_TOKEN = (
        rf"(?:"
        rf"{MONTH_PATTERN}\s+(?:19|20)\d{{2}}"
        rf"|"
        rf"\d{{1,2}}[/-]\d{{4}}"
        rf"|"
        rf"(?:19|20)\d{{2}}"
        rf")"
    )

    DATE_RANGE_PATTERN = re.compile(
        rf"\b("
        rf"{DATE_TOKEN}"
        rf")"
        rf"(?:"
        rf"\s*"
        rf"(?:[-–—]|to)"
        rf"\s*"
        rf"("
        rf"Present|Current|Now|{DATE_TOKEN}"
        rf")"
        rf")?",
        re.IGNORECASE,
    )

    # Allows dates without requiring a range.
    DATE_SEARCH_PATTERN = re.compile(
        rf"\b{DATE_TOKEN}\b",
        re.IGNORECASE,
    )

    ROLE_AT_COMPANY_PATTERN = re.compile(
        r"^(.*?)\s+(?:@|at)\s+(.*?)$",
        re.IGNORECASE,
    )

    # ==========================================================
    # Job Titles
    # ==========================================================

    JOB_TITLE_PATTERNS = [
        # Engineering / development
        "software engineer",
        "software developer",
        "senior software engineer",
        "senior software developer",
        "junior software engineer",
        "junior software developer",
        "full stack engineer",
        "full stack developer",
        "full-stack engineer",
        "full-stack developer",
        "frontend engineer",
        "frontend developer",
        "front end engineer",
        "front end developer",
        "backend engineer",
        "backend developer",
        "back end engineer",
        "back end developer",
        "web developer",
        "web engineer",
        "mobile developer",
        "application developer",
        "application engineer",
        "devops engineer",
        "cloud engineer",
        "platform engineer",
        "site reliability engineer",
        "sre",
        "systems engineer",
        "network engineer",
        "security engineer",

        # AI / data
        "machine learning engineer",
        "machine learning developer",
        "ml engineer",
        "ai/ml engineer",
        "ai engineer",
        "artificial intelligence engineer",
        "data scientist",
        "data engineer",
        "data analyst",
        "analytics engineer",
        "research engineer",
        "research scientist",
        "research assistant",

        # Specialized development
        "unity 3d developer",
        "unity developer",
        "game developer",
        "ar/vr developer",
        "ar developer",
        "vr developer",

        # Product / technical leadership
        "technical lead",
        "tech lead",
        "engineering lead",
        "engineering manager",
        "technical manager",
        "project manager",
        "product manager",
        "product engineer",
        "solutions architect",
        "software architect",
        "architect",
        "technical consultant",
        "consultant",

        # Business / general
        "business analyst",
        "system analyst",
        "systems analyst",
        "analyst",
        "manager",
        "director",
        "founder",
        "co-founder",

        # Freelance / internships
        "freelance developer",
        "freelancer",
        "developer",
        "engineer",
        "intern",
        "internship",
        "trainee",
        "apprentice",
    ]

    # ==========================================================
    # Non-company Metadata
    # ==========================================================

    WORK_MODE_KEYWORDS = {
        "remote",
        "hybrid",
        "on-site",
        "onsite",
        "on site",
        "full-time",
        "fulltime",
        "full time",
        "part-time",
        "parttime",
        "part time",
        "contract",
        "contractor",
        "internship",
        "freelance",
        "temporary",
        "permanent",
    }

    LOCATION_KEYWORDS = {
        "india",
        "usa",
        "us",
        "uk",
        "uae",
        "london",
        "new york",
        "bangalore",
        "bengaluru",
        "pune",
        "mumbai",
        "hyderabad",
        "chennai",
        "delhi",
        "new delhi",
        "noida",
        "gurgaon",
        "gurugram",
        "san francisco",
        "california",
        "texas",
        "seattle",
        "toronto",
        "singapore",
        "dubai",
    }

    LOCATION_PATTERN = re.compile(
        r"^[a-zA-Z\s\.\-]+,\s*[a-zA-Z\s\.\-]+$"
    )

    COMPANY_METADATA_PATTERN = re.compile(
        r"^(?:company|organization|organisation|employer|"
        r"client|employer name|company name)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    )

    # Common separators used by resume generators.
    HEADER_SEPARATOR_PATTERN = re.compile(
        r"\s*(?:\||•|·|—|–)\s*"
    )

    # ==========================================================
    # Description Signals
    # ==========================================================

    DESCRIPTION_VERBS = {
        "built",
        "developed",
        "worked",
        "managed",
        "implemented",
        "created",
        "engineered",
        "collaborated",
        "designed",
        "optimized",
        "delivered",
        "maintained",
        "developing",
        "contributed",
        "resolved",
        "translated",
        "deployed",
        "streamlined",
        "enhanced",
        "integrated",
        "utilized",
        "supported",
        "led",
        "configured",
        "automated",
        "architected",
        "migrated",
        "tested",
        "debugged",
        "improved",
        "implemented",
        "established",
        "coordinated",
        "analyzed",
        "created",
        "launched",
    }

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

        # First recover collapsed header structures.
        normalized_lines = self._expand_collapsed_experience_lines(
            lines
        )

        blocks = self._split_blocks(
            normalized_lines
        )

        experiences: List[Experience] = []

        for block in blocks:
            parsed = self._parse_block(block)

            if parsed is not None:
                experiences.append(parsed)

        return experiences

    # ==========================================================
    # Normalization
    # ==========================================================

    def _normalize_lines(
        self,
        text: str,
    ) -> List[str]:
        """
        Normalize whitespace while preserving meaningful line
        boundaries.
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

        result: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if line:
                result.append(line)

        return result

    # ==========================================================
    # Collapsed PDF Recovery
    # ==========================================================

    def _expand_collapsed_experience_lines(
        self,
        lines: List[str],
    ) -> List[str]:
        """
        PDF extraction sometimes collapses an entire experience
        onto one physical line.

        Example:

            FutureNixMedia Dec 2024 – Feb 2025 Web Developer Intern
            (On-site) Engineered responsive web applications...

        We recover the structural boundary before the role.
        """

        expanded: List[str] = []

        for line in lines:
            if self.BULLET_PATTERN.match(line):
                expanded.append(line)
                continue

            segments = self._split_collapsed_line(
                line
            )

            expanded.extend(segments)

        return expanded

    def _split_collapsed_line(
        self,
        line: str,
    ) -> List[str]:
        """
        Recover multiple logical header/description segments from
        a single physical line.

        We primarily split around strong date + role combinations.
        """

        # If line already looks like a normal single structure,
        # don't touch it.
        matches = list(
            self.DATE_RANGE_PATTERN.finditer(line)
        )

        if len(matches) <= 1:
            return [line]

        segments: List[str] = []

        cursor = 0

        for index, match in enumerate(matches):
            start = match.start()
            end = match.end()

            # Preserve content before this date.
            if start > cursor:
                prefix = line[cursor:start].strip()

                if prefix:
                    # Only split prefix if it resembles a header.
                    if self._contains_job_title(prefix):
                        segments.append(prefix)

            date_text = match.group(0).strip()

            # Find content after date.
            after_start = end
            next_match = (
                matches[index + 1]
                if index + 1 < len(matches)
                else None
            )

            after_end = (
                next_match.start()
                if next_match
                else len(line)
            )

            after = line[
                after_start:after_end
            ].strip()

            # For a date followed by a role, split it.
            if after:
                role_match = self._find_role_in_text(
                    after
                )

                if role_match:
                    role_start, role_end = role_match

                    before_role = after[
                        :role_start
                    ].strip()

                    role_text = after[
                        role_start:role_end
                    ].strip()

                    if before_role:
                        segments.append(
                            date_text
                        )
                        segments.append(
                            before_role
                        )
                    else:
                        segments.append(
                            date_text
                        )

                    segments.append(
                        role_text
                    )

                    remaining = after[
                        role_end:
                    ].strip()

                    if remaining:
                        segments.append(
                            remaining
                        )

                    cursor = (
                        after_start
                        + after_end
                        - after_end
                    )

                    # Since this method is only a recovery layer,
                    # return the reconstructed structure.
                    reconstructed = []

                    # Safer reconstruction from the original line.
                    prefix = line[
                        :start
                    ].strip()

                    if prefix:
                        reconstructed.append(
                            prefix
                        )

                    reconstructed.append(
                        date_text
                    )

                    reconstructed.append(
                        before_role
                    ) if before_role else None

                    reconstructed.append(
                        role_text
                    )

                    if remaining:
                        reconstructed.append(
                            remaining
                        )

                    return reconstructed

        return [line]

    # ==========================================================
    # Block Detection
    # ==========================================================

    def _split_blocks(
        self,
        lines: List[str],
    ) -> List[List[str]]:
        """
        Identify strong experience starts.

        We intentionally require structural evidence so description
        lines don't become fake experiences.
        """

        starts: List[int] = []

        for index, line in enumerate(lines):
            if self._is_experience_start(
                line,
                index,
                lines,
            ):
                starts.append(index)

        if not starts:
            return [lines]

        blocks: List[List[str]] = []

        for position, start in enumerate(starts):
            end = (
                starts[position + 1]
                if position + 1 < len(starts)
                else len(lines)
            )

            block = lines[start:end]

            if block:
                blocks.append(block)

        return blocks

    def _is_experience_start(
        self,
        line: str,
        index: int,
        lines: List[str],
    ) -> bool:
        if not line:
            return False

        if self.BULLET_PATTERN.match(line):
            return False

        # ------------------------------------------------------
        # Highest-confidence pattern:
        #
        # Role + Date
        # ------------------------------------------------------
        if (
            self._contains_job_title(line)
            and self.DATE_RANGE_PATTERN.search(line)
        ):
            return True

        # ------------------------------------------------------
        # Company + Date + Role
        #
        # FutureNixMedia Dec 2024 – Feb 2025
        # Web Developer Intern
        # ------------------------------------------------------
        if self.DATE_RANGE_PATTERN.search(line):
            next_line = (
                lines[index + 1]
                if index + 1 < len(lines)
                else ""
            )

            if self._contains_job_title(
                next_line
            ):
                return True

            # Same line may contain role after date.
            date_match = self.DATE_RANGE_PATTERN.search(
                line
            )

            if date_match:
                after_date = line[
                    date_match.end():
                ].strip()

                if self._contains_job_title(
                    after_date
                ):
                    return True

        # ------------------------------------------------------
        # Role followed by separate date.
        # ------------------------------------------------------
        if self._contains_job_title(line):
            next_line = (
                lines[index + 1]
                if index + 1 < len(lines)
                else ""
            )

            if self.DATE_RANGE_PATTERN.search(
                next_line
            ):
                return True

        # ------------------------------------------------------
        # Role @ Company
        # ------------------------------------------------------
        if self.ROLE_AT_COMPANY_PATTERN.match(
            line
        ):
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

        role = self._extract_role(
            header_lines
        )

        start_date, end_date = (
            self._extract_dates_from_block(
                header_lines
            )
        )

        company = self._extract_company(
            header_lines,
            role,
        )

        description = self._extract_description(
            description_lines
        )

        # If segmentation failed to find description,
        # recover any trailing prose from the header.
        if not description:
            description = self._recover_description(
                header_lines,
                role,
                company,
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

        # Do not create empty garbage records.
        if not role and not company and not description:
            return None

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
        Separate metadata from descriptions.

        This method supports both bullet and non-bullet resumes.

        Metadata includes:
        - role
        - company
        - date
        - location
        - work mode

        Once enough metadata has been collected, prose becomes
        description.
        """

        header_lines: List[str] = []
        description_lines: List[str] = []

        role_found = False
        date_found = False

        description_started = False

        for index, line in enumerate(block):
            if description_started:
                description_lines.append(line)
                continue

            clean = line.strip()

            if self.BULLET_PATTERN.match(clean):
                description_started = True
                description_lines.append(clean)
                continue

            has_date = bool(
                self.DATE_RANGE_PATTERN.search(clean)
            )

            has_role = self._contains_job_title(
                clean
            )

            if has_role:
                role_found = True
                header_lines.append(clean)
                continue

            if has_date:
                date_found = True
                header_lines.append(clean)
                continue

            if self._is_location_or_work_mode(
                clean
            ):
                header_lines.append(clean)
                continue

            if self._is_company_candidate(
                clean
            ):
                # Only treat a short metadata-looking line
                # as company before description begins.
                header_lines.append(clean)
                continue

            # Role + date found means remaining prose is
            # description.
            if role_found and date_found:
                description_started = True
                description_lines.append(clean)
                continue

            # A sentence before date/role is more likely
            # description than company.
            if self._looks_like_description(
                clean
            ):
                description_started = True
                description_lines.append(clean)
                continue

            header_lines.append(clean)

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

        # Role @ Company
        for line in header_lines:
            match = self.ROLE_AT_COMPANY_PATTERN.match(
                line
            )

            if match:
                return self._clean_role(
                    match.group(1)
                )

        candidates: List[Tuple[int, str]] = []

        for line in header_lines:
            clean = self._remove_dates(
                line
            )

            # Split common header separators.
            parts = self._split_header_parts(
                clean
            )

            for part in parts:
                part = part.strip()

                if not part:
                    continue

                score = self._role_score(
                    part
                )

                if score > 0:
                    candidates.append(
                        (
                            score,
                            part,
                        )
                    )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return self._clean_role(
            candidates[0][1]
        )

    def _find_role_in_text(
        self,
        text: str,
    ) -> Optional[Tuple[int, int]]:
        lower = text.lower()

        best: Optional[Tuple[int, int, int]] = None

        for pattern in self.JOB_TITLE_PATTERNS:
            match = re.search(
                r"\b"
                + re.escape(pattern)
                + r"\b",
                lower,
            )

            if not match:
                continue

            score = 100 + len(pattern)

            if best is None or score > best[0]:
                best = (
                    score,
                    match.start(),
                    match.end(),
                )

        if best is None:
            return None

        return (
            best[1],
            best[2],
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
        # Explicit:
        #
        # Role @ Company
        # ------------------------------------------------------
        for line in header_lines:
            match = self.ROLE_AT_COMPANY_PATTERN.match(
                line
            )

            if match:
                return self._clean_company(
                    match.group(2)
                )

        # ------------------------------------------------------
        # Explicit company metadata.
        # ------------------------------------------------------
        for line in header_lines:
            match = self.COMPANY_METADATA_PATTERN.match(
                line
            )

            if match:
                return self._clean_company(
                    match.group(1)
                )

        # ------------------------------------------------------
        # Search structured header parts.
        # ------------------------------------------------------
        for line in header_lines:
            parts = self._split_header_parts(
                line
            )

            for part in parts:
                candidate = part.strip()

                if not candidate:
                    continue

                if role and candidate.lower() == role.lower():
                    continue

                if self.DATE_RANGE_PATTERN.search(
                    candidate
                ):
                    continue

                if self._is_non_company_metadata(
                    candidate
                ):
                    continue

                if self._contains_job_title(
                    candidate
                ):
                    continue

                if self._looks_like_description(
                    candidate
                ):
                    continue

                if self._is_company_candidate(
                    candidate
                ):
                    return self._clean_company(
                        candidate
                    )

        # ------------------------------------------------------
        # Handle separate company line:
        #
        # Role
        # Company
        # Date
        # ------------------------------------------------------
        role_index: Optional[int] = None

        if role:
            for index, line in enumerate(header_lines):
                parts = self._split_header_parts(
                    self._remove_dates(line)
                )

                if any(
                    part.strip().lower()
                    == role.lower()
                    for part in parts
                ):
                    role_index = index
                    break

        if role_index is not None:
            # Prefer the immediate following metadata line.
            for index in range(
                role_index + 1,
                len(header_lines),
            ):
                candidate = self._remove_dates(
                    header_lines[index]
                ).strip()

                if not candidate:
                    continue

                if self._is_non_company_metadata(
                    candidate
                ):
                    continue

                if self._contains_job_title(
                    candidate
                ):
                    continue

                if self._looks_like_description(
                    candidate
                ):
                    continue

                if self._is_company_candidate(
                    candidate
                ):
                    return self._clean_company(
                        candidate
                    )

        return None

    def _is_company_candidate(
        self,
        line: str,
    ) -> bool:
        clean = line.strip()

        if not clean:
            return False

        if self.BULLET_PATTERN.match(clean):
            return False

        if self.DATE_RANGE_PATTERN.search(clean):
            return False

        if self._is_non_company_metadata(
            clean
        ):
            return False

        if self._contains_job_title(clean):
            return False

        if self._looks_like_description(clean):
            return False

        if len(clean.split()) > 8:
            return False

        if re.search(
            r"\b(?:built|developed|worked|managed|"
            r"implemented|created|engineered|"
            r"collaborated|designed|optimized|"
            r"delivered|maintained|resolved|"
            r"translated|deployed|streamlined|"
            r"enhanced|integrated|utilized|"
            r"supported|launched|configured|"
            r"automated|tested|debugged)\b",
            clean,
            re.IGNORECASE,
        ):
            return False

        return True

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

    def _is_location_or_work_mode(
        self,
        line: str,
    ) -> bool:
        clean = line.strip()

        if self._is_non_company_metadata(
            clean
        ):
            return True

        if "|" in clean:
            parts = [
                part.strip()
                for part in clean.split("|")
                if part.strip()
            ]

            if parts and all(
                self._is_non_company_metadata(
                    part
                )
                for part in parts
            ):
                return True

        return False

    # ==========================================================
    # Dates
    # ==========================================================

    def _extract_dates_from_block(
        self,
        header_lines: List[str],
    ) -> Tuple[
        Optional[str],
        Optional[str],
    ]:
        text = " ".join(header_lines)

        match = self.DATE_RANGE_PATTERN.search(
            text
        )

        if not match:
            return None, None

        return (
            match.group(1).strip()
            if match.group(1)
            else None,
            match.group(2).strip()
            if match.group(2)
            else None,
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
    # Header Splitting
    # ==========================================================

    def _split_header_parts(
        self,
        line: str,
    ) -> List[str]:
        """
        Split metadata lines without destroying normal company names.

        Example:

            QuickSO App | Hybrid, Mumbai

        becomes:

            QuickSO App
            Hybrid, Mumbai
        """

        if not line:
            return []

        parts = re.split(
            r"\s*(?:\||·|•)\s*",
            line,
        )

        result: List[str] = []

        for part in parts:
            part = part.strip()

            if part:
                result.append(part)

        return result

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

    def _recover_description(
        self,
        header_lines: List[str],
        role: Optional[str],
        company: Optional[str],
    ) -> str:
        """
        Safety-net for unusual layouts where the PDF parser has
        merged metadata and prose.

        Only returns lines that are clearly prose.
        """

        description: List[str] = []

        for line in header_lines:
            clean = line.strip()

            if not clean:
                continue

            if role and clean.lower() == role.lower():
                continue

            if company and clean.lower() == company.lower():
                continue

            if self.DATE_RANGE_PATTERN.search(
                clean
            ):
                continue

            if self._is_non_company_metadata(
                clean
            ):
                continue

            if self._looks_like_description(
                clean
            ):
                description.append(clean)

        return "\n".join(
            description
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
        if not header_lines:
            return []

        candidates: List[str] = []

        for line in header_lines:
            clean = self._remove_dates(
                line
            )

            if role:
                clean = re.sub(
                    re.escape(role),
                    "",
                    clean,
                    flags=re.IGNORECASE,
                )

            if company:
                clean = re.sub(
                    re.escape(company),
                    "",
                    clean,
                    flags=re.IGNORECASE,
                )

            clean = re.sub(
                r"\b(?:remote|hybrid|on-site|onsite|on site)\b",
                "",
                clean,
                flags=re.IGNORECASE,
            )

            if clean.strip():
                candidates.append(
                    clean.strip()
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
        technologies = set(
            header_technologies
        )

        if description:
            technologies.update(
                self.skill_extractor.extract(
                    description
                )
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

        # Remove location/work-mode suffixes.
        clean = re.sub(
            r"\s*\((?:remote|hybrid|on-site|onsite)\)\s*$",
            "",
            clean,
            flags=re.IGNORECASE,
        ).strip()

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

        # Remove trailing metadata after pipe.
        if "|" in clean:
            parts = [
                part.strip()
                for part in clean.split("|")
                if part.strip()
            ]

            valid = [
                part
                for part in parts
                if not self._is_non_company_metadata(
                    part
                )
            ]

            if valid:
                clean = valid[0]

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
        clean = line.strip()

        if not clean:
            return False

        if self.BULLET_PATTERN.match(clean):
            return True

        # Sentence-ending punctuation.
        if clean.endswith(
            (".", "?", "!")
        ):
            return True

        # Strong prose verbs.
        words = re.findall(
            r"[A-Za-z]+",
            clean.lower(),
        )

        if any(
            word in self.DESCRIPTION_VERBS
            for word in words
        ):
            return True

        # Long prose.
        if len(words) >= 15:
            if not self.DATE_SEARCH_PATTERN.search(
                clean
            ):
                return True

        return False