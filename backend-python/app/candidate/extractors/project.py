import re
from typing import List, Tuple, Optional

from app.candidate.schemas import Project
from app.shared.skill_extractor import SkillExtractor

class ProjectExtractor:
    """
    Extract structured project information from the
    projects section of a resume using stateful detection and contextual parsing.
    """
    
    BULLET_PATTERN = re.compile(r"^[•●▪◦*\-–—]\s*")
    
    # Date Pattern to help identify Project boundaries
    DATE_PATTERN = re.compile(
        r"\b((?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4})"
        r"(?:\s*[-–—to]+\s*"
        r"(Present|Current|Now|\b(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+)?\b(?:19|20)\d{2}\b|\d{1,2}[/\-]\d{4}))?\b",
        re.IGNORECASE
    )

    # GitHub & Live URL Patterns
    GITHUB_PATTERN = re.compile(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?|\bgithub\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b",
        re.IGNORECASE
    )

    LIVE_URL_PATTERN = re.compile(
        r"\b(?:https?://)?(?:[A-Za-z0-9-]+\.)+(?:vercel\.app|netlify\.app|render\.com|pages\.dev|com|org|net|io|dev|ai)(?:/[^\s]*)?\b",
        re.IGNORECASE
    )

    # Tech Stack Explicit Prefix Pattern & Pipe-separated layouts (e.g., React | Node | MongoDB)
    TECH_PREFIX_PATTERN = re.compile(r"^(?:Tech(?:nology|nologies)?\s*Stack|Technologies|Built\s*with|Tools)\s*[:\-]\s*(.+)$", re.IGNORECASE)
    TECH_PIPE_PATTERN = re.compile(r"^[A-Za-z0-9\s\.#\+]+(?:\s*\|\s*[A-Za-z0-9\s\.#\+]+){2,}$")

    # Metadata Link Pattern to clean up titles
    LINK_METADATA_PATTERN = re.compile(
        r"^(?:Demo|Live|Repository|Source Code|GitHub|URL)\s*[:\-]?\s*", 
        re.IGNORECASE
    )

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    # ==========================================================
    # Public API
    # ==========================================================

    def extract(self, text: str) -> List[Project]:
        if not text.strip():
            return []

        normalized_text = self._normalize_text(text)
        blocks = self._split_blocks(normalized_text)

        projects_list = []

        for block in blocks:
            start_date, end_date, cleaned_block = self._extract_dates(block)
            
            lines = [line.strip() for line in cleaned_block.splitlines() if line.strip()]
            if not lines:
                continue

            header_lines, description_lines = self._segment_block(lines)

            explicit_tech, remaining_headers = self._extract_explicit_tech(header_lines)

            github_url = self._extract_github("\n".join(remaining_headers + description_lines))
            live_url = self._extract_live_url("\n".join(remaining_headers + description_lines), github_url)

            title = self._extract_title(remaining_headers, github_url, live_url)

            description = self._extract_description(description_lines, github_url, live_url)
            technologies = self._extract_technologies(explicit_tech, description)

            project_obj = Project(
                title=title,
                start_date=start_date,
                end_date=end_date,
                description=description,
                technologies=technologies,
                github=github_url,
                live_url=live_url
            )
            projects_list.append(project_obj)

        return projects_list

    # ==========================================================
    # Private Helpers
    # ==========================================================

    def _normalize_text(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _split_blocks(self, text: str) -> List[str]:
        """
        Step 2 & 8 — Split Blocks & Handle Merged Projects.
        Splits dynamically using state-machine combinations of Title + (Date/Link/Tech) OR structural transitions.
        """
        lines = text.splitlines()
        blocks = []
        current_block = []
        seen_metadata_in_current = False

        for i, line in enumerate(lines):
            is_bullet = bool(self.BULLET_PATTERN.search(line))
            is_paragraph = len(line) >= 80
            
            # Lookahead context
            next_line = lines[i+1] if i+1 < len(lines) else ""
            combined_context = line + " " + next_line
            next_is_bullet = bool(self.BULLET_PATTERN.search(next_line)) if next_line else False
            next_is_paragraph = len(next_line) >= 80 if next_line else False
            
            has_date = bool(self.DATE_PATTERN.search(combined_context))
            has_link = bool(self.GITHUB_PATTERN.search(combined_context)) or bool(self.LIVE_URL_PATTERN.search(combined_context)) or bool(self.LINK_METADATA_PATTERN.match(line))
            has_tech = bool(self.TECH_PREFIX_PATTERN.search(combined_context)) or bool(self.TECH_PIPE_PATTERN.search(combined_context))
            
            # 1. FIXED: Handle plain projects (Title followed immediately by bullet/paragraph without metadata)
            is_structural_transition = not is_bullet and not is_paragraph and (next_is_bullet or next_is_paragraph)
            
            is_potential_header = not is_bullet and not is_paragraph and (has_date or has_link or has_tech or is_structural_transition)

            can_split = False
            if current_block:
                if seen_metadata_in_current and is_potential_header:
                    can_split = True
                elif not seen_metadata_in_current and len(current_block) >= 3 and is_potential_header:
                    can_split = True

            if can_split:
                blocks.append("\n".join(current_block))
                current_block = []
                seen_metadata_in_current = False

            current_block.append(line)
            
            if not is_bullet and not is_paragraph and (
                bool(self.DATE_PATTERN.search(line)) or 
                bool(self.GITHUB_PATTERN.search(line)) or 
                bool(self.LIVE_URL_PATTERN.search(line)) or 
                bool(self.TECH_PREFIX_PATTERN.match(line)) or 
                bool(self.TECH_PIPE_PATTERN.match(line))
            ):
                seen_metadata_in_current = True

        if current_block:
            blocks.append("\n".join(current_block))

        return blocks

    def _extract_dates(self, block: str) -> Tuple[Optional[str], Optional[str], str]:
        match = self.DATE_PATTERN.search(block)
        if match:
            start_date = match.group(1).strip() if match.group(1) else match.group(0).strip()
            end_date = match.group(2).strip() if match.group(2) else None
            cleaned_block = block.replace(match.group(0), "")
            return start_date, end_date, cleaned_block
        return None, None, block

    def _segment_block(self, lines: List[str]) -> Tuple[List[str], List[str]]:
        """
        2. FIXED: Pattern-driven segmentation. Uses known metadata patterns rather than strict line counts.
        """
        header_lines = []
        description_lines = []
        hit_description = False
        
        for i, line in enumerate(lines):
            is_bullet = bool(self.BULLET_PATTERN.search(line))
            is_paragraph = len(line) > 80
            
            # Identify lines that explicitly belong in the header (Dates, Tech, Links)
            is_metadata = (
                bool(self.DATE_PATTERN.search(line)) or 
                bool(self.GITHUB_PATTERN.search(line)) or 
                bool(self.LIVE_URL_PATTERN.search(line)) or 
                bool(self.TECH_PREFIX_PATTERN.match(line)) or 
                bool(self.TECH_PIPE_PATTERN.match(line)) or
                bool(self.LINK_METADATA_PATTERN.match(line))
            )
            
            if not hit_description:
                if is_bullet or is_paragraph:
                    hit_description = True
                elif i >= 3 and not is_metadata:
                    # Once we have a decent header, unrecognized short lines become description
                    hit_description = True
            
            if hit_description:
                description_lines.append(line)
            else:
                header_lines.append(line)
                
        return header_lines, description_lines

    def _extract_explicit_tech(self, header_lines: List[str]) -> Tuple[List[str], List[str]]:
        explicit_tech = []
        remaining_headers = []
        
        for line in header_lines:
            prefix_match = self.TECH_PREFIX_PATTERN.match(line)
            if prefix_match:
                tech_string = prefix_match.group(1)
                explicit_tech.extend([t.strip() for t in re.split(r"[,\|]", tech_string) if t.strip()])
                continue
                
            pipe_match = self.TECH_PIPE_PATTERN.match(line)
            if pipe_match:
                explicit_tech.extend([t.strip() for t in line.split("|") if t.strip()])
                continue
                
            remaining_headers.append(line)
            
        return explicit_tech, remaining_headers

    def _extract_title(self, header_lines: List[str], github: Optional[str], live_url: Optional[str]) -> Optional[str]:
        for line in header_lines:
            clean_line = self.BULLET_PATTERN.sub("", line).strip()
            
            if not clean_line or len(clean_line) > 80:
                continue

            clean_line = self.LINK_METADATA_PATTERN.sub("", clean_line).strip()
            if not clean_line:
                continue

            if (github and clean_line in github) or (live_url and clean_line in live_url):
                continue
                
            if github:
                clean_line = clean_line.replace(github, "").strip()
            if live_url:
                clean_line = clean_line.replace(live_url, "").strip()
                
            clean_line = re.sub(r"[\-\|:,]+$", "", clean_line).strip()

            if clean_line:
                return clean_line
                
        return None

    def _extract_github(self, text: str) -> Optional[str]:
        match = self.GITHUB_PATTERN.search(text)
        return match.group(0).strip() if match else None

    def _extract_live_url(self, text: str, github_url: Optional[str]) -> Optional[str]:
        matches = self.LIVE_URL_PATTERN.finditer(text)
        for match in matches:
            found_url = match.group(0).strip()
            
            if any(site in found_url.lower() for site in ["github.com", "linkedin.com"]):
                continue
            if github_url and github_url in found_url:
                continue
                
            return found_url
        return None

    def _extract_description(self, description_lines: List[str], github: Optional[str], live_url: Optional[str]) -> str:
        cleaned_lines = []
        for line in description_lines:
            if github and line.strip() == github:
                continue
            if live_url and line.strip() == live_url:
                continue
            
            has_github = github and github in line
            has_live = live_url and live_url in line
            
            if has_github or has_live:
                clean_line = self.LINK_METADATA_PATTERN.sub("", line).strip()
            else:
                clean_line = line
                
            cleaned_lines.append(clean_line)
            
        return "\n".join(cleaned_lines).strip()

    def _extract_technologies(self, explicit_tech: List[str], description: str) -> List[str]:
        tech_set = set(explicit_tech)
        
        if description:
            extracted = self.skill_extractor.extract(description)
            tech_set.update(extracted)
            
        return sorted(list(tech_set))