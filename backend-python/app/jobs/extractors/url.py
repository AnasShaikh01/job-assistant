import httpx
from bs4 import BeautifulSoup

class URLExtractor:
    """
    Stage 1: Downloads career page HTML and extracts visible text.
    
    TODO: Replace with Playwright for JS-rendered career pages 
    (e.g., Workday, Lever, Greenhouse) in Stage 2.
    """
    
    @staticmethod
    async def extract(url: str) -> str:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        for element in soup(["script", "style", "noscript", "meta", "nav", "footer", "header"]):
            element.extract()
            
        text = soup.get_text(separator="\n")
        return text.strip()