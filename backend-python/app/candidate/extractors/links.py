import re
from app.candidate.schemas import Links

class LinksExtractor:
    """
    Extract GitHub, LinkedIn, Portfolio and other URLs
    from the resume.
    """

    URL_REGEX = r"https?://[^\s]+"

    @classmethod
    def extract(cls, text: str) -> Links:
        urls = re.findall(cls.URL_REGEX, text)

        github = None
        linkedin = None
        portfolio = None
        other = []

        for url in urls:
            url = url.strip()

            if "github.com" in url.lower():
                github = url

            elif "linkedin.com" in url.lower():
                linkedin = url

            elif any(
                domain in url.lower()
                for domain in [
                    "vercel.app",
                    "netlify.app",
                    "portfolio",
                    "pages.dev"
                ]
            ):
                portfolio = url

            else:
                other.append(url)

        return Links(
            github=github,
            linkedin=linkedin,
            portfolio=portfolio,
            other=other
        )