import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Project
from app.shared.skill_extractor import SkillExtractor


class ProjectExtractor:
    """
    Deterministic project extractor.

    Responsibilities:
    - Detect project boundaries from strong header signals.
    - Parse project title, technologies, dates and URLs from headers.
    - Preserve all description/bullet content belonging to a project.
    - Extract additional technologies from project descriptions.
    """

    BULLET_PATTERN = re.compile(r"^[•●▪◦*\-–—]\s*")

    MONTH_PATTERN = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    DATE_PATTERN = re.compile(
        rf"\b("
        rf"(?:{MONTH_PATTERN}\s+)?(?:19|20)\d{{2}}"
        rf"|"
        rf"\d{{1,2}}[/-]\d{{4}}"
        rf")\b",
        re.IGNORECASE,
    )

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

    GITHUB_PATTERN = re.compile(
        r"https?://(?:www\.)?github\.com/"
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?"
        r"|"
        r"\bgithub\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b",
        re.IGNORECASE,
    )

    LIVE_URL_PATTERN = re.compile(
        r"\b(?:https?://)?"
        r"(?:[A-Za-z0-9-]+\.)+"
        r"(?:vercel\.app|netlify\.app|render\.com|pages\.dev|"
        r"com|org|net|io|dev|ai)"
        r"(?:/[^\s]*)?\b",
        re.IGNORECASE,
    )

    TECH_PREFIX_PATTERN = re.compile(
        r"^(?:Tech(?:nology|nologies)?\s*Stack|"
        r"Technologies|Built\s*with|Tools)"
        r"\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    )

    LINK_METADATA_PATTERN = re.compile(
        r"^(?:Demo|Live|Repository|Source Code|GitHub|URL)"
        r"\s*[:\-]?\s*",
        re.IGNORECASE,
    )

    # Common separators used in resume project headers.
    HEADER_SEPARATOR_PATTERN = re.compile(r"\s*\|\s*")

    # Strong indicators that a line may be a project header.
    PROJECT_HEADER_HINT_PATTERN = re.compile(
        rf"("
        rf"\|"
        rf"|"
        rf"(?:{MONTH_PATTERN}\s+)?(?:19|20)\d{{2}}"
        rf"|"
        rf"\d{{1,2}}[/-]\d{{4}}"
        rf"|"
        rf"\b(?:github|demo|live|repository|source code|technologies|"
        rf"tech stack|built with|tools)\b"
        rf")",
        re.IGNORECASE,
    )

    # Terms that commonly identify an explicit project technology segment.
    TECH_CONTEXT_PATTERN = re.compile(
        r"\b(?:"
        r"next(?:\.js)?|react(?:\.js)?|typescript|javascript|"
        r"node(?:\.js)?|python|java|c\+\+|c#|php|"
        r"postgres(?:ql)?|mongodb|mysql|firebase|"
        r"express(?:\.js)?|strapi|prisma|"
        r"tailwind(?:\s*css)?|docker|kubernetes|"
        r"vercel|railway|razorpay|nextauth(?:\.js)?|"
        r"medusa(?:\.js)?|rest\s+apis?"
        r")\b",
        re.IGNORECASE,
    )

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Project]:
        if not text or not text.strip():
            return []

        lines = self._normalize_lines(text)

        if not lines:
            return []

        blocks = self._split_blocks(lines)

        projects: List[Project] = []

        for block in blocks:
            project = self._parse_block(block)

            if project is not None:
                projects.append(project)

        return projects

    # ==========================================================
    # Normalization
    # ==========================================================

    def _normalize_lines(self, text: str) -> List[str]:
        """
        Normalize whitespace while preserving logical line boundaries.

        IMPORTANT:
        We deliberately do not use line length to determine semantics.
        A PDF may wrap a single sentence over multiple physical lines.
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)

        lines: List[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if line:
                lines.append(line)

        return lines

    # ==========================================================
    # Project Boundary Detection
    # ==========================================================

    def _split_blocks(self, lines: List[str]) -> List[List[str]]:
        """
        Split the projects section into project blocks.

        A new project is created only when a strong project-header
        candidate is detected.

        Ordinary wrapped sentences are NEVER considered project
        boundaries merely because they are short or followed by bullets.
        """
        header_indexes = [
            index
            for index, line in enumerate(lines)
            if self._is_project_header_candidate(line, index, lines)
        ]

        if not header_indexes:
            # Graceful fallback: treat the entire section as one block.
            return [lines]

        blocks: List[List[str]] = []

        for position, start_index in enumerate(header_indexes):
            end_index = (
                header_indexes[position + 1]
                if position + 1 < len(header_indexes)
                else len(lines)
            )

            block = lines[start_index:end_index]

            if block:
                blocks.append(block)

        return blocks

    def _is_project_header_candidate(
        self,
        line: str,
        index: int,
        lines: List[str],
    ) -> bool:
        """
        Determine whether a line is likely to be a project header.

        Strong signals:
        - pipe-separated header structure
        - date on the same line
        - explicit technology metadata
        - URL metadata
        - recognizable technology names
        - project-like title followed by description/bullet content

        Weak signals alone are insufficient.
        """

        if not line:
            return False

        if self.BULLET_PATTERN.match(line):
            return False

        if self._is_description_line(line):
            return False

        has_date = bool(self.DATE_RANGE_PATTERN.search(line))
        has_pipe = "|" in line
        has_explicit_tech_prefix = bool(
            self.TECH_PREFIX_PATTERN.match(line)
        )
        has_github = bool(self.GITHUB_PATTERN.search(line))
        has_live_url = bool(self.LIVE_URL_PATTERN.search(line))
        has_link_metadata = bool(
            self.LINK_METADATA_PATTERN.match(line)
        )
        has_tech = bool(self.TECH_CONTEXT_PATTERN.search(line))

        # The strongest format for the resumes we're targeting:
        #
        # Project | Tech1, Tech2, Tech3 | Date
        #
        if has_pipe and (has_date or has_tech or has_explicit_tech_prefix):
            return True

        # Explicit metadata header.
        if has_explicit_tech_prefix or has_link_metadata:
            return True

        # Header containing a date and recognizable technology.
        if has_date and has_tech:
            return True

        # Header containing a date and a URL.
        if has_date and (has_github or has_live_url):
            return True

        # Date-only project header is acceptable if it looks structurally
        # like a title rather than a sentence.
        if has_date and self._looks_like_title(line):
            next_line = lines[index + 1] if index + 1 < len(lines) else ""

            if next_line and (
                self.BULLET_PATTERN.match(next_line)
                or self._looks_like_description(next_line)
            ):
                return True

        return False

    # ==========================================================
    # Block Parsing
    # ==========================================================

    def _parse_block(self, block: List[str]) -> Optional[Project]:
        if not block:
            return None

        header, description_lines = self._extract_header(block)

        if not header:
            return None

        title, explicit_technologies = self._parse_header(header)

        if not title:
            return None

        header_without_metadata = self._remove_header_urls(header)

        start_date, end_date = self._extract_dates(header_without_metadata)

        github_url = self._extract_github("\n".join(block))
        live_url = self._extract_live_url(
            "\n".join(block),
            github_url,
        )

        description = self._extract_description(
            description_lines,
            github_url,
            live_url,
        )

        technologies = self._extract_technologies(
            explicit_technologies,
            description,
        )

        return Project(
            title=title,
            start_date=start_date,
            end_date=end_date,
            description=description or None,
            technologies=technologies,
            github=github_url,
            live_url=live_url,
        )

    def _extract_header(
        self,
        block: List[str],
    ) -> Tuple[Optional[str], List[str]]:
        """
        The first line of a correctly detected project block is the
        semantic project header.

        We do not search later lines for another header because the
        block splitter has already established the project boundary.
        """
        if not block:
            return None, []

        header = block[0].strip()

        if self.BULLET_PATTERN.match(header):
            return None, block[1:]

        return header, block[1:]

    # ==========================================================
    # Header Parsing
    # ==========================================================

    def _parse_header(
        self,
        header: str,
    ) -> Tuple[Optional[str], List[str]]:
        """
        Parse common project-header layouts.

        Supported examples:

        Project Name | Tech1, Tech2, Tech3 | Jul 2025

        Project Name | Next.js, TypeScript, PostgreSQL Jul 2025

        Project Name
        Technologies: Next.js, TypeScript
        """
        working = header.strip()

        # Remove URLs from the header before parsing title/technologies.
        working = self.GITHUB_PATTERN.sub("", working)
        working = self.LIVE_URL_PATTERN.sub("", working)
        working = working.strip(" -|:")

        # Extract dates first.
        working_without_date, _, _ = self._remove_dates(working)

        # Explicit technology prefix.
        prefix_match = self.TECH_PREFIX_PATTERN.match(
            working_without_date
        )

        if prefix_match:
            tech_string = prefix_match.group(1).strip()

            title_part = working_without_date[
                :prefix_match.start()
            ].strip(" |:-")

            technologies = self._split_technology_string(
                tech_string
            )

            return self._clean_title(title_part), technologies

        # Pipe-separated header.
        parts = [
            part.strip()
            for part in self.HEADER_SEPARATOR_PATTERN.split(
                working_without_date
            )
            if part.strip()
        ]

        if len(parts) >= 2:
            title = self._clean_title(parts[0])

            technology_parts = parts[1:]
            technology_string = ", ".join(technology_parts)

            technologies = self._split_technology_string(
                technology_string
            )

            # If the second part doesn't look like technologies,
            # retain it as part of the title rather than throwing
            # information away.
            if not technologies:
                title = self._clean_title(
                    " | ".join(parts)
                )

            return title, technologies

        # Fallback: attempt to identify technology names in a
        # non-pipe header.
        technologies = self.skill_extractor.extract(
            working_without_date
        )

        title = self._clean_title(
            self._remove_known_technology_phrases(
                working_without_date,
                technologies,
            )
        )

        return title, technologies

    def _split_technology_string(
        self,
        value: str,
    ) -> List[str]:
        if not value:
            return []

        # Most resume project headers use commas or pipes.
        candidates = re.split(r",|\|", value)

        technologies: List[str] = []

        for candidate in candidates:
            candidate = candidate.strip()

            if not candidate:
                continue

            # If a date accidentally remained attached, remove it.
            candidate, _, _ = self._remove_dates(candidate)
            candidate = candidate.strip(" -|:")

            if candidate:
                technologies.append(candidate)

        # Normalize through the canonical SkillExtractor.
        return self._normalize_technologies(technologies)

    # ==========================================================
    # Date Handling
    # ==========================================================

    def _extract_dates(
        self,
        text: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        match = self.DATE_RANGE_PATTERN.search(text)

        if not match:
            return None, None

        start_date = match.group(1).strip() if match.group(1) else None
        end_date = match.group(2).strip() if match.group(2) else None

        return start_date, end_date

    def _remove_dates(
        self,
        text: str,
    ) -> Tuple[str, Optional[str], Optional[str]]:
        match = self.DATE_RANGE_PATTERN.search(text)

        if not match:
            return text, None, None

        start_date = match.group(1).strip() if match.group(1) else None
        end_date = match.group(2).strip() if match.group(2) else None

        cleaned = (
            text[:match.start()] +
            " " +
            text[match.end():]
        )

        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
        cleaned = cleaned.strip(" -|:")

        return cleaned, start_date, end_date

    # ==========================================================
    # Description
    # ==========================================================

    def _extract_description(
        self,
        lines: List[str],
        github: Optional[str],
        live_url: Optional[str],
    ) -> str:
        cleaned_lines: List[str] = []

        for line in lines:
            clean_line = line.strip()

            if not clean_line:
                continue

            if github and clean_line == github:
                continue

            if live_url and clean_line == live_url:
                continue

            # Remove link metadata while preserving surrounding text.
            clean_line = self.LINK_METADATA_PATTERN.sub(
                "",
                clean_line,
            ).strip()

            if github:
                clean_line = clean_line.replace(
                    github,
                    "",
                ).strip()

            if live_url:
                clean_line = clean_line.replace(
                    live_url,
                    "",
                ).strip()

            if clean_line:
                cleaned_lines.append(clean_line)

        return "\n".join(cleaned_lines).strip()

    # ==========================================================
    # Technology Extraction
    # ==========================================================

    def _extract_technologies(
        self,
        explicit_technologies: List[str],
        description: str,
    ) -> List[str]:
        """
        Explicit header technologies receive priority.

        Description extraction adds additional technologies that are
        explicitly recognized by the canonical skill dictionary.
        """
        technologies = set(
            self._normalize_technologies(
                explicit_technologies
            )
        )

        if description:
            extracted = self.skill_extractor.extract(
                description
            )

            technologies.update(extracted)

        return sorted(technologies)

    def _normalize_technologies(
        self,
        technologies: List[str],
    ) -> List[str]:
        if not technologies:
            return []

        normalized: set[str] = set()

        for technology in technologies:
            value = technology.strip()

            if not value:
                continue

            # Let the canonical dictionary resolve known aliases.
            extracted = self.skill_extractor.extract(value)

            if extracted:
                normalized.update(extracted)
            else:
                normalized.add(value.lower())

        return sorted(normalized)

    # ==========================================================
    # URL Handling
    # ==========================================================

    def _extract_github(
        self,
        text: str,
    ) -> Optional[str]:
        match = self.GITHUB_PATTERN.search(text)

        if not match:
            return None

        return match.group(0).strip().rstrip("/")

    def _extract_live_url(
        self,
        text: str,
        github_url: Optional[str],
    ) -> Optional[str]:
        for match in self.LIVE_URL_PATTERN.finditer(text):
            found_url = match.group(0).strip().rstrip("/")

            lower_url = found_url.lower()

            if "github.com" in lower_url:
                continue

            if "linkedin.com" in lower_url:
                continue

            if github_url and github_url in found_url:
                continue

            return found_url

        return None

    def _remove_header_urls(self, text: str) -> str:
        text = self.GITHUB_PATTERN.sub("", text)
        text = self.LIVE_URL_PATTERN.sub("", text)

        return text.strip()

    # ==========================================================
    # Title Helpers
    # ==========================================================

    def _clean_title(
        self,
        title: Optional[str],
    ) -> Optional[str]:
        if not title:
            return None

        clean = self.BULLET_PATTERN.sub(
            "",
            title,
        ).strip()

        clean = self.LINK_METADATA_PATTERN.sub(
            "",
            clean,
        ).strip()

        clean = re.sub(
            r"\s{2,}",
            " ",
            clean,
        )

        clean = clean.strip(" |:-,")

        if not clean:
            return None

        return clean

    def _looks_like_title(self, line: str) -> bool:
        if not line:
            return False

        if self.BULLET_PATTERN.match(line):
            return False

        if line.endswith((".", "?", "!")):
            return False

        words = line.split()

        if len(words) > 12:
            return False

        return True

    # ==========================================================
    # Description / Header Classification Helpers
    # ==========================================================

    def _is_description_line(self, line: str) -> bool:
        """
        Detect obvious prose.

        This is deliberately based on sentence characteristics,
        not raw character count.
        """
        if self.BULLET_PATTERN.match(line):
            return True

        stripped = line.strip()

        if not stripped:
            return False

        if stripped.endswith((".", "?", "!")):
            return True

        words = stripped.split()

        # Long prose without header metadata is more likely to be
        # description than a project title.
        if len(words) >= 15 and "|" not in stripped:
            return True

        return False

    def _looks_like_description(self, line: str) -> bool:
        if self.BULLET_PATTERN.match(line):
            return True

        return line.strip().endswith(
            (".", "?", "!")
        )

    # ==========================================================
    # Skill Helpers
    # ==========================================================

    def _remove_known_technology_phrases(
        self,
        text: str,
        technologies: List[str],
    ) -> str:
        """
        Conservative title cleanup.

        Only removes a technology when it appears as a complete
        phrase separated by common header punctuation.
        """
        result = text

        for technology in sorted(
            technologies,
            key=len,
            reverse=True,
        ):
            escaped = re.escape(technology)

            result = re.sub(
                rf"(?i)(?:\s*[,|]\s*){escaped}\b",
                "",
                result,
            )

        return result.strip(" |:,-")
