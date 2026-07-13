import io
import httpx
import fitz  # PyMuPDF

class PDFExtractor:
    """
    Downloads and extracts text from a PDF Job Description.
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
            extracted_text = [page.get_text("text", sort=True) for page in doc]
            return "\n".join(extracted_text).strip()
            
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")
            
        finally:
            if 'doc' in locals():
                doc.close()