import io
import re
import httpx
import fitz  # PyMuPDF
from collections import Counter

class PDFExtractor:
    """
    Downloads and extracts text from a PDF Job Description.
    Includes advanced handling for 2-column layouts, repeated headers/footers, 
    and broken sentences.
    """
    
    @staticmethod
    async def extract(pdf_url: str) -> str:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            
            # Strict validation to prevent parsing arbitrary files
            if "application/pdf" not in response.headers.get("content-type", "").lower():
                raise ValueError("Invalid PDF: The provided URL does not point to a valid PDF document.")
            
        pdf_stream = io.BytesIO(response.content)
        
        try:
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            raw_pages = []
            
            for page in doc:
                # Using blocks instead of plain text handles two-column layouts natively
                blocks = page.get_text("blocks", sort=True)
                page_text = "\n".join([b[4] for b in blocks if b[6] == 0])
                raw_pages.append(page_text)
                
            # Clean up document layout artifacts
            text = PDFExtractor._remove_page_headers_footers(raw_pages)
            text = PDFExtractor._merge_broken_sentences(text)
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")
            
        finally:
            if 'doc' in locals():
                doc.close()

    @staticmethod
    def _remove_page_headers_footers(pages: list[str]) -> str:
        """Finds identical lines repeating across multiple pages and removes them."""
        if len(pages) <= 1:
            return pages[0] if pages else ""
            
        all_lines = [line.strip() for page in pages for line in page.splitlines() if line.strip()]
        line_counts = Counter(all_lines)
        
        threshold = max(2, len(pages) - 1)
        repeats = {line for line, count in line_counts.items() if count >= threshold and len(line) < 100}
        
        cleaned_pages = []
        for page in pages:
            page_lines = []
            for line in page.splitlines():
                if line.strip() not in repeats:
                    page_lines.append(line)
            cleaned_pages.append("\n".join(page_lines))
            
        return "\n\n".join(cleaned_pages)

    @staticmethod
    def _merge_broken_sentences(text: str) -> str:
        """Merges sentences that were physically wrapped to a new line in the PDF."""
        pattern = r"([a-z,])\n\s*([a-z])"
        return re.sub(pattern, r"\1 \2", text)