import httpx
from bs4 import BeautifulSoup

class URLExtractor:
    """
    Stage 1: Downloads career page HTML and extracts visible text.
    Targeted extraction for ATS providers (LinkedIn, Greenhouse, Lever, Workday)
    with semantic fallbacks and aggressive noise removal.
    
    TODO: Replace with Playwright for JS-rendered career pages in Stage 2.
    """
    
    ATS_SELECTORS = {
        "linkedin.com": [".jobs-description", ".jobs-description__content", "article"],
        "greenhouse.io": ["#content", "#job_details", ".job__description"],
        "lever.co": [".postings-wrapper", ".posting-page", "div[data-qa='job-description']"],
        "myworkdayjobs.com": ["[data-automation-id='jobPostingDescription']"],
        "smartrecruiters.com": [".job-desc", "#st-jobDescription"]
    }

    FALLBACK_SELECTORS = [
        "main", "article", 
        "[id*='job-description']", "[class*='job-description']",
        ".description"
    ]

    NOISE_SELECTORS = [
        "nav", "footer", "aside", "header", "script", "style", "noscript", "meta",
        ".breadcrumb", "[class*='breadcrumb']",
        "[class*='recommend']", "[class*='similar']", "[class*='related']",
        "[class*='cookie']", "[id*='cookie']", "[class*='banner']",
        "[class*='share']", "[class*='social']"
    ]

    @staticmethod
    async def extract(url: str) -> str:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 1. Aggressive noise removal (removes breadcrumbs, footers, related jobs)
        for noise in soup.select(", ".join(URLExtractor.NOISE_SELECTORS)):
            noise.decompose()
            
        # 2. Target specific ATS containers or semantic HTML
        job_container = None
        url_lower = url.lower()
        
        for ats_domain, selectors in URLExtractor.ATS_SELECTORS.items():
            if ats_domain in url_lower:
                for selector in selectors:
                    job_container = soup.select_one(selector)
                    if job_container: break
            if job_container: break
                
        if not job_container:
            for selector in URLExtractor.FALLBACK_SELECTORS:
                job_container = soup.select_one(selector)
                if job_container: break
                
        # Fallback to body if no specific container is found
        target = job_container if job_container else soup.body
        
        if not target:
            raise ValueError("Could not extract meaningful content from the provided URL.")
            
        text = target.get_text(separator="\n")
        return text.strip()