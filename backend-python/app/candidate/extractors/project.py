import re
from typing import List, Tuple, Optional
from app.candidate.schemas import Project
from app.resume.skill_extractor import SkillExtractor

class ProjectExtractor:
    """
    Extract structured project information from the
    projects section of a resume using pure deterministic methods.
    """
    # Step 6 - GitHub Pattern
    GITHUB_PATTERN = re.compile(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?|\bgithub\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b",
        re.IGNORECASE
    )

    # Step 7 - Live Deployment URL Pattern supporting common platforms and general domains
    LIVE_URL_PATTERN = re.compile(
        r"\b(?:https?://)?(?:[A-Za-z0-9-]+\.)+(?:vercel\.app|netlify\.app|render\.com|pages\.dev|com|org|net|io|dev|ai)(?:/[^\s]*)?\b",
        re.IGNORECASE
    )

    # Patterns to match lines that indicate project links or metadata rather than actual titles
    LINK_METADATA_PATTERN = re.compile(
        r"\b(github|live|demo|repository|https://)\b", 
        re.IGNORECASE
    )

    BULLET_PATTERN = re.compile(r"^[•●▪◦*-]\s*")

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Project]:
        if not text.strip():
            return []

        # Step 1 — Normalize (Preserves blank lines for blocking)
        normalized_text = self._normalize_text(text)

        # Step 2 — Split Project Blocks
        blocks = self._split_blocks(normalized_text)

        projects_list = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            # Step 3 — Extract Title
            title = self._extract_title(lines)

            # Step 6 — Extract GitHub URL
            github = self._extract_github(block)

            # Step 7 — Extract Live URL
            live_url = self._extract_live_url(block, github)

            # Step 4 — Extract Description
            description = self._extract_description(lines, title, github, live_url)

            # Step 5 — Extract Technologies
            technologies = self._extract_technologies(description)

            # Step 8 — Build Object
            project_obj = Project(
                title=title,
                description=description,
                technologies=technologies,
                github=github,
                live_url=live_url
            )
            projects_list.append(project_obj)

        return projects_list

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _normalize_text(self, text: str) -> str:
        """
        Step 1 — Normalize: Clean inline whitespace spacing rules.
        CRITICAL FIX: Keeps explicit empty structural rows to prevent blocking bugs.
        """
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 — Split Blocks.
        Splits text into chunks using blank separators as raw anchors.
        """
        return [
            block.strip()
            for block in re.split(r"\n\s*\n", text)
            if block.strip()
        ]

    def _extract_title(self, lines: List[str]) -> Optional[str]:
        """Step 3 — Extract Title from the first 2 metadata lines."""
        for line in lines[:2]:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            # 5. Title Validation: If title length is > 120 chars, it's likely part of the description
            if len(clean_line) > 120:
                continue

            # 2. Improved Title Extraction: Skip metadata/link references
            if self.LINK_METADATA_PATTERN.search(clean_line.lower()):
                continue
                
            return clean_line
            
        return None

    def _extract_github(self, block: str) -> Optional[str]:
        """Step 6 — Extract GitHub URL via text pattern matching."""
        match = self.GITHUB_PATTERN.search(block)
        if match:
            return match.group(0).strip()
        return None

    def _extract_live_url(self, block: str, github_url: Optional[str]) -> Optional[str]:
        """Step 7 — Extract Live Deployment URL while avoiding developer profiles."""
        matches = self.LIVE_URL_PATTERN.finditer(block)
        for match in matches:
            found_url = match.group(0).strip()
            
            # 3. Live URL Filters: Strip platforms containing github or professional socials
            if any(site in found_url.lower() for site in ["github.com", "linkedin.com"]):
                continue
                
            if github_url and github_url in found_url:
                continue
                
            return found_url
        return None

    def _extract_description(self, lines: List[str], title: Optional[str], github: Optional[str], live_url: Optional[str]) -> str:
        """Step 4 — Extract Description by isolating lines from header and url blocks."""
        description_lines = []
        
        for line in lines:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            # Skip title match
            if title and clean_line == title:
                continue
            # Skip lines matching or containing your structural URL tags
            if github and github in line:
                continue
            if live_url and live_url in line:
                continue
                
            # 4. Description Update: Append clean lines without bullet character tags
            description_lines.append(clean_line)

        return "\n".join(description_lines).strip()

    def _extract_technologies(self, description: str) -> List[str]:
        """Step 5 — Extract Technologies using SkillExtractor pipeline utility."""
        if not description:
            return []
        return self.skill_extractor.extract(description)