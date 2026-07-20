import re
from urllib.parse import urlparse
from typing import List, Tuple
from app.candidate.schemas import Links

class LinksExtractor:
    """
    Extract GitHub, LinkedIn, Portfolio, and other URLs
    from the resume text. 
    Supports visible + embedded URLs, normalization, and deduplication.
    """

    # Matches standard http/https/www URLs, bare LinkedIn/GitHub URLs, and bare Portfolio domains
    URL_PATTERN = re.compile(
        r"\b(?:https?://|www\.)[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
        r"|\b(?:linkedin\.com|github\.com)/[-a-zA-Z0-9()@:%_\+.~#?&//=]+"
        r"|\b[-a-zA-Z0-9@:%._\+~#=]+\.(?:github\.io|vercel\.app|netlify\.app|pages\.dev|carrd\.co|notion\.site|linktr\.ee|bento\.me)\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        re.IGNORECASE
    )

    PORTFOLIO_DOMAINS = {
        "github.io", "vercel.app", "netlify.app", "pages.dev", 
        "carrd.co", "notion.site", "linktr.ee", "bento.me", 
        "about.me", "portfolio"
    }

    @classmethod
    def _is_portfolio_host(cls, hostname: str) -> bool:
        """Ensures exact domain match or valid subdomain match."""
        return any(
            hostname == domain or hostname.endswith("." + domain)
            for domain in cls.PORTFOLIO_DOMAINS
        )

    @classmethod
    def extract(cls, text: str) -> Links:
        if not text:
            return Links()

        raw_urls = cls.URL_PATTERN.findall(text)
        
        unique_urls: List[Tuple[str, str, str]] = []
        seen = set()
        
        for url in raw_urls:
            url = re.sub(r"[>.,;:\"'\)\]}]+$", "", url.strip())
            if not url:
                continue
            
            if not re.match(r"^https?://", url, re.IGNORECASE):
                normalized_url = "https://" + url
            else:
                normalized_url = url
                
            canonical = re.sub(r"^https?://(?:www\.)?", "", normalized_url.lower()).rstrip("/")
            
            if canonical not in seen:
                seen.add(canonical)
                # Parse the URL to reliably extract the hostname and path
                parsed = urlparse(normalized_url)
                hostname = parsed.hostname.lower() if parsed.hostname else ""
                unique_urls.append((normalized_url, hostname, parsed.path))

        # Classification Queues
        linkedin_candidates = []
        github_candidates = []
        portfolio_candidates = []
        other = []

        for original_url, hostname, path in unique_urls:
            if "linkedin.com" in hostname:
                linkedin_candidates.append(original_url)
            elif "github.com" in hostname:
                github_candidates.append(original_url)
            elif cls._is_portfolio_host(hostname):
                portfolio_candidates.append(original_url)
            else:
                if original_url not in other:
                    other.append(original_url)

        # ==========================================
        # Selection & Routing Logic
        # ==========================================
        
        # LinkedIn: Prefer profile (/in/) over posts/company/jobs
        linkedin = None
        if linkedin_candidates:
            linkedin = next((url for url in linkedin_candidates if "/in/" in url.lower()), linkedin_candidates[0])
            for url in linkedin_candidates:
                if url != linkedin and url not in other:
                    other.append(url)

        # GitHub: Prefer profile (exactly 1 path segment) over repositories
        github = None
        if github_candidates:
            profiles = []
            for url in github_candidates:
                path_segments = [seg for seg in urlparse(url).path.split("/") if seg]
                # A direct user profile path has exactly 1 segment (e.g., github.com/username)
                if len(path_segments) == 1:
                    profiles.append(url)
                    
            if profiles:
                github = profiles[0]
            else:
                # Fallback to the shortest path depth
                github = min(github_candidates, key=lambda u: len([seg for seg in urlparse(u).path.split("/") if seg]))
                
            for url in github_candidates:
                if url != github and url not in other:
                    other.append(url)

        # Portfolio: Pick the first valid portfolio match
        portfolio = None
        if portfolio_candidates:
            portfolio = portfolio_candidates[0]
            for url in portfolio_candidates[1:]:
                if url not in other:
                    other.append(url)

        return Links(
            github=github,
            linkedin=linkedin,
            portfolio=portfolio,
            other=other
        )